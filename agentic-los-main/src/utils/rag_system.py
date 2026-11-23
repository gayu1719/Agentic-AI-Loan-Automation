"""RAG (Retrieval-Augmented Generation) system for loan underwriting guidelines."""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
import structlog
from config import settings
from .document_processor import DocumentProcessor

logger = structlog.get_logger()


class RAGSystem:
    """RAG system for retrieving relevant guidelines and context."""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.embeddings_model,
            openai_api_key=settings.openai_api_key
        )
        self.document_processor = DocumentProcessor()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        self.logger = logger.bind(component="rag_system")
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=settings.vector_store_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create or get collection
        self.collection_name = "loan_guidelines"
        try:
            self.collection = self.chroma_client.get_collection(self.collection_name)
            self.logger.info("Loaded existing vector collection")
        except Exception:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Loan underwriting guidelines and rules"}
            )
            self.logger.info("Created new vector collection")
    
    async def initialize_knowledge_base(self, rules_directory: str) -> None:
        """Initialize the knowledge base with loan guidelines."""
        try:
            rules_path = Path(rules_directory)
            if not rules_path.exists():
                raise FileNotFoundError(f"Rules directory not found: {rules_directory}")
            
            documents = []
            
            # Process all PDF files in the rules directory
            for pdf_file in rules_path.glob("*.pdf"):
                self.logger.info(f"Processing guideline document: {pdf_file.name}")
                
                doc_result = await self.document_processor.process_document(str(pdf_file))
                
                # Create documents from the processed content
                doc = Document(
                    page_content=doc_result['text'],
                    metadata={
                        'source': str(pdf_file),
                        'file_type': doc_result['file_type'],
                        'pages': doc_result['pages'],
                        'file_size': doc_result['file_size'],
                        'title': pdf_file.stem
                    }
                )
                documents.append(doc)
            
            if not documents:
                self.logger.warning("No documents found to process")
                return
            
            # Split documents into chunks
            all_chunks = []
            for doc in documents:
                chunks = self.text_splitter.split_documents([doc])
                all_chunks.extend(chunks)
            
            self.logger.info(f"Created {len(all_chunks)} document chunks")
            
            # Add chunks to vector store
            await self._add_chunks_to_store(all_chunks)
            
            self.logger.info("Knowledge base initialization completed")
            
        except Exception as e:
            self.logger.error("Knowledge base initialization failed", error=str(e))
            raise
    
    async def _add_chunks_to_store(self, chunks: List[Document]) -> None:
        """Add document chunks to the vector store."""
        try:
            # Prepare data for ChromaDB
            texts = [chunk.page_content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            ids = [f"chunk_{i}" for i in range(len(chunks))]
            
            # Generate embeddings
            embeddings = self.embeddings.embed_documents(texts)
            
            # Add to collection
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            self.logger.info(f"Added {len(chunks)} chunks to vector store")
            
        except Exception as e:
            self.logger.error("Failed to add chunks to vector store", error=str(e))
            raise
    
    async def retrieve_relevant_context(
        self, 
        query: str, 
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant context for a query."""
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filters
            )
            
            # Format results
            contexts = []
            for i in range(len(results['documents'][0])):
                contexts.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
            
            self.logger.info(
                "Retrieved relevant context",
                query_length=len(query),
                results_count=len(contexts)
            )
            
            return contexts
            
        except Exception as e:
            self.logger.error("Context retrieval failed", error=str(e))
            raise
    
    async def get_guidelines_for_category(self, category: str) -> List[Dict[str, Any]]:
        """Get specific guidelines for a category (e.g., financial analysis, QCA)."""
        query_map = {
            'financial_analysis': 'financial analysis ratios liquidity solvency profitability',
            'qca': 'qualitative credit assessment QCA business operations management',
            'credit_scoring': 'credit scoring quantitative assessment risk rating',
            'covenants': 'covenants triggers monitoring requirements',
            'financial_projections': 'financial projections forecasting scenarios base case downside',
            'industry_analysis': 'industry analysis sector trends market conditions',
            'collateral': 'collateral security guarantees risk mitigation',
            'cash_flow': 'cash flow operating investing financing activities'
        }
        
        query = query_map.get(category.lower(), category)
        return await self.retrieve_relevant_context(query, n_results=10)
    
    async def search_specific_topic(self, topic: str, document_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for specific topics in the guidelines."""
        filters = None
        if document_filter:
            filters = {"title": {"$eq": document_filter}}
        
        return await self.retrieve_relevant_context(topic, n_results=8, filters=filters)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        try:
            count = self.collection.count()
            return {
                'total_chunks': count,
                'collection_name': self.collection_name,
                'embedding_model': settings.embeddings_model
            }
        except Exception as e:
            self.logger.error("Failed to get collection stats", error=str(e))
            return {'error': str(e)} 