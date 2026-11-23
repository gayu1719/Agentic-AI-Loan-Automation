"""Document processing utilities for the Agentic LOS system."""
import os
import tempfile
from typing import Dict, List, Optional, Any
from pathlib import Path
import PyPDF2
from PIL import Image
import pytesseract
from docx import Document
import structlog
from config import settings

logger = structlog.get_logger()


class DocumentProcessor:
    """Document processing and OCR utilities."""
    
    def __init__(self):
        self.supported_formats = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.docx', '.doc'}
        self.logger = logger.bind(component="document_processor")
    
    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a document and extract text and metadata."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if file_path.suffix.lower() not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            # Extract text based on file type
            if file_path.suffix.lower() == '.pdf':
                result = await self._process_pdf(file_path)
            elif file_path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.tiff'}:
                result = await self._process_image(file_path)
            elif file_path.suffix.lower() in {'.docx', '.doc'}:
                result = await self._process_word_doc(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            self.logger.info(
                "Document processed successfully",
                file_path=str(file_path),
                pages=result.get('pages', 0),
                text_length=len(result.get('text', ''))
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "Document processing failed",
                file_path=str(file_path),
                error=str(e)
            )
            raise
    
    async def _process_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Process PDF file and extract text."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                text_content = []
                page_contents = []
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        text_content.append(page_text)
                        page_contents.append({
                            'page_number': page_num + 1,
                            'text': page_text,
                            'word_count': len(page_text.split())
                        })
                    except Exception as e:
                        self.logger.warning(
                            "Failed to extract text from page",
                            page_number=page_num + 1,
                            error=str(e)
                        )
                        page_contents.append({
                            'page_number': page_num + 1,
                            'text': '',
                            'word_count': 0,
                            'error': str(e)
                        })
                
                full_text = '\n'.join(text_content)
                
                return {
                    'text': full_text,
                    'pages': len(pdf_reader.pages),
                    'page_contents': page_contents,
                    'file_type': 'pdf',
                    'file_size': file_path.stat().st_size,
                    'metadata': {
                        'title': pdf_reader.metadata.get('/Title', '') if pdf_reader.metadata else '',
                        'author': pdf_reader.metadata.get('/Author', '') if pdf_reader.metadata else '',
                        'creation_date': str(pdf_reader.metadata.get('/CreationDate', '')) if pdf_reader.metadata else ''
                    }
                }
                
        except Exception as e:
            self.logger.error("PDF processing failed", error=str(e))
            raise
    
    async def _process_image(self, file_path: Path) -> Dict[str, Any]:
        """Process image file using OCR."""
        try:
            image = Image.open(file_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(
                image, 
                lang=settings.ocr_language,
                config='--psm 6'  # Assume uniform block of text
            )
            
            return {
                'text': text,
                'pages': 1,
                'page_contents': [{
                    'page_number': 1,
                    'text': text,
                    'word_count': len(text.split())
                }],
                'file_type': 'image',
                'file_size': file_path.stat().st_size,
                'metadata': {
                    'image_size': image.size,
                    'image_mode': image.mode,
                    'image_format': image.format
                }
            }
            
        except Exception as e:
            self.logger.error("Image OCR processing failed", error=str(e))
            raise
    
    async def _process_word_doc(self, file_path: Path) -> Dict[str, Any]:
        """Process Word document."""
        try:
            doc = Document(file_path)
            
            paragraphs = []
            full_text = []
            
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)
                    full_text.append(para.text)
            
            text_content = '\n'.join(full_text)
            
            return {
                'text': text_content,
                'pages': 1,  # Word docs don't have a direct page concept
                'page_contents': [{
                    'page_number': 1,
                    'text': text_content,
                    'word_count': len(text_content.split())
                }],
                'file_type': 'word',
                'file_size': file_path.stat().st_size,
                'metadata': {
                    'paragraphs_count': len(paragraphs),
                    'core_properties': {
                        'title': doc.core_properties.title or '',
                        'author': doc.core_properties.author or '',
                        'created': str(doc.core_properties.created) if doc.core_properties.created else ''
                    }
                }
            }
            
        except Exception as e:
            self.logger.error("Word document processing failed", error=str(e))
            raise
    
    def extract_financial_tables(self, text: str) -> List[Dict[str, Any]]:
        """Extract financial tables from processed text."""
        # This is a simplified implementation
        # In a production system, you'd use more sophisticated table detection
        tables = []
        lines = text.split('\n')
        
        current_table = []
        in_table = False
        
        for line in lines:
            # Simple heuristic: lines with multiple numbers separated by spaces might be table rows
            numbers = [word for word in line.split() if self._is_number(word)]
            
            if len(numbers) >= 3:  # Likely a table row
                if not in_table:
                    in_table = True
                    current_table = []
                current_table.append(line.strip())
            else:
                if in_table and current_table:
                    tables.append({
                        'rows': current_table,
                        'row_count': len(current_table)
                    })
                    current_table = []
                in_table = False
        
        # Add the last table if it exists
        if current_table:
            tables.append({
                'rows': current_table,
                'row_count': len(current_table)
            })
        
        return tables
    
    def _is_number(self, text: str) -> bool:
        """Check if text represents a number."""
        try:
            # Remove common currency symbols and commas
            cleaned = text.replace('$', '').replace(',', '').replace('(', '').replace(')', '')
            float(cleaned)
            return True
        except ValueError:
            return False 