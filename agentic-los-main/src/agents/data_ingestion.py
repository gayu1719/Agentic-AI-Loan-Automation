"""Data ingestion agents for loan applications and documents."""
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from .base_agent import BaseAgent, AgentInput, AgentOutput
from ..models.loan_application import LoanApplication
from ..utils.document_processor import DocumentProcessor
from ..utils.rag_system import RAGSystem
import structlog

logger = structlog.get_logger()


class ApplicationDataAgent(BaseAgent):
    """Agent for processing and validating loan application data."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="Application Data Agent",
            description="Processes and validates initial loan application data",
            **kwargs
        )
        self.rag_system = RAGSystem()
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process loan application data."""
        try:
            # Validate input
            if not self.validate_input(input_data):
                raise ValueError("Invalid input data")
            
            application_data = input_data.data
            
            # Parse and validate application
            loan_application = self._parse_application_data(application_data)
            
            # Perform data quality checks
            quality_score, quality_issues = self._assess_data_quality(loan_application)
            
            # Extract key risk indicators
            risk_indicators = self._extract_risk_indicators(loan_application)
            
            # Get relevant guidelines
            guidelines = await self.rag_system.get_guidelines_for_category("application_requirements")
            
            # Generate recommendations
            recommendations = self._generate_recommendations(loan_application, quality_issues)
            
            result = {
                "loan_application": loan_application.dict(),
                "data_quality_score": quality_score,
                "quality_issues": quality_issues,
                "risk_indicators": risk_indicators,
                "guidelines_context": guidelines[:3] if guidelines else [],
                "validation_status": "passed" if quality_score >= 0.7 else "requires_attention"
            }
            
            output = AgentOutput(
                result=result,
                metadata={
                    "processing_time": datetime.now().isoformat(),
                    "data_completeness": quality_score,
                    "issues_count": len(quality_issues)
                },
                confidence_score=quality_score,
                recommendations=recommendations
            )
            
            await self._log_execution(input_data, output)
            return output
            
        except Exception as e:
            self.logger.error("Application data processing failed", error=str(e))
            return AgentOutput(
                result={"error": str(e)},
                metadata={"error": True},
                confidence_score=0.0,
                recommendations=["Fix application data processing error"]
            )
    
    def _parse_application_data(self, data: Dict[str, Any]) -> LoanApplication:
        """Parse raw application data into structured format."""
        try:
            # This would typically handle various input formats
            # For now, assume the data is already structured
            return LoanApplication(**data)
        except Exception as e:
            self.logger.error("Failed to parse application data", error=str(e))
            raise ValueError(f"Invalid application data format: {str(e)}")
    
    def _assess_data_quality(self, application: LoanApplication) -> tuple[float, List[str]]:
        """Assess the quality and completeness of application data."""
        issues = []
        score_components = []
        
        # Check company details completeness
        company_score = 0
        total_company_fields = 9
        
        if application.company_details.company_name:
            company_score += 1
        else:
            issues.append("Missing company name")
            
        if application.company_details.years_in_business > 0:
            company_score += 1
        else:
            issues.append("Years in business not specified")
            
        if application.company_details.annual_revenue > 0:
            company_score += 1
        else:
            issues.append("Annual revenue not provided")
            
        if application.company_details.industry_type:
            company_score += 1
        else:
            issues.append("Industry type not specified")
            
        if application.company_details.number_of_employees > 0:
            company_score += 1
        else:
            issues.append("Number of employees not provided")
            
        if application.company_details.business_address:
            company_score += 1
        else:
            issues.append("Business address missing")
            
        if application.company_details.business_description:
            company_score += 1
        else:
            issues.append("Business description missing")
            
        if application.company_details.key_management:
            company_score += 1
        else:
            issues.append("Key management information missing")
            
        if application.company_details.business_registration_number:
            company_score += 1
        else:
            issues.append("Business registration number missing")
        
        score_components.append(company_score / total_company_fields)
        
        # Check financial data completeness
        financial_score = 0
        total_financial_fields = 6
        
        if application.financial_data.requested_loan_amount > 0:
            financial_score += 1
        else:
            issues.append("Loan amount not specified")
            
        if application.financial_data.loan_purpose:
            financial_score += 1
        else:
            issues.append("Loan purpose not provided")
            
        if application.financial_data.preferred_term_months > 0:
            financial_score += 1
        else:
            issues.append("Loan term not specified")
            
        if application.financial_data.monthly_cash_flow is not None:
            financial_score += 1
        else:
            issues.append("Monthly cash flow not provided")
            
        if application.financial_data.existing_debt is not None:
            financial_score += 1
        else:
            issues.append("Existing debt information missing")
            
        if application.financial_data.collateral_offered:
            financial_score += 1
        else:
            issues.append("Collateral information not provided")
        
        score_components.append(financial_score / total_financial_fields)
        
        # Check supporting documents
        if application.supporting_documents:
            score_components.append(1.0)
        else:
            issues.append("No supporting documents provided")
            score_components.append(0.0)
        
        # Calculate overall score
        overall_score = sum(score_components) / len(score_components)
        
        return overall_score, issues
    
    def _extract_risk_indicators(self, application: LoanApplication) -> List[str]:
        """Extract key risk indicators from application data."""
        risk_indicators = []
        
        # Business age risk
        if application.company_details.years_in_business < 2:
            risk_indicators.append("New business - less than 2 years in operation")
        
        # Revenue to loan ratio
        loan_to_revenue_ratio = application.financial_data.requested_loan_amount / application.company_details.annual_revenue
        if loan_to_revenue_ratio > 0.5:
            risk_indicators.append(f"High loan-to-revenue ratio: {loan_to_revenue_ratio:.2f}")
        
        # Cash flow concerns
        if application.financial_data.monthly_cash_flow and application.financial_data.monthly_cash_flow < 0:
            risk_indicators.append("Negative monthly cash flow reported")
        
        # High existing debt
        if application.financial_data.existing_debt:
            debt_to_revenue = application.financial_data.existing_debt / application.company_details.annual_revenue
            if debt_to_revenue > 0.3:
                risk_indicators.append(f"High existing debt-to-revenue ratio: {debt_to_revenue:.2f}")
        
        # Industry risk (simplified)
        high_risk_industries = ["hospitality", "retail", "construction"]
        if application.company_details.industry_type.value in high_risk_industries:
            risk_indicators.append(f"High-risk industry: {application.company_details.industry_type.value}")
        
        return risk_indicators
    
    def _generate_recommendations(self, application: LoanApplication, quality_issues: List[str]) -> List[str]:
        """Generate recommendations based on application analysis."""
        recommendations = []
        
        if quality_issues:
            recommendations.append("Address data quality issues before proceeding")
        
        if application.company_details.years_in_business < 3:
            recommendations.append("Request additional business documentation for newer businesses")
        
        if not application.financial_data.collateral_offered:
            recommendations.append("Consider requiring collateral for this loan size")
        
        if application.financial_data.requested_loan_amount > 500000:
            recommendations.append("Loan amount requires enhanced due diligence")
        
        return recommendations
    
    def get_prompt_template(self) -> str:
        """Get the prompt template for this agent."""
        return """
        You are a loan application data processing agent. Your role is to:
        1. Validate and structure incoming loan application data
        2. Assess data quality and completeness
        3. Identify potential risk indicators
        4. Recommend next steps in the loan process
        
        Focus on data accuracy, completeness, and early risk identification.
        """


class DocumentIngestionAgent(BaseAgent):
    """Agent for processing and digitizing financial documents."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="Document Ingestion Agent",
            description="Processes and digitizes financial statements and supporting documents",
            **kwargs
        )
        self.document_processor = DocumentProcessor()
        self.rag_system = RAGSystem()
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process uploaded documents."""
        try:
            document_paths = input_data.data.get("document_paths", [])
            application_id = input_data.data.get("application_id", "unknown")
            
            if not document_paths:
                raise ValueError("No documents provided for processing")
            
            processed_documents = []
            extraction_results = []
            
            for doc_path in document_paths:
                self.logger.info(f"Processing document: {doc_path}")
                
                # Process document
                doc_result = await self.document_processor.process_document(doc_path)
                
                # Extract financial data
                financial_data = self._extract_financial_data(doc_result)
                
                # Classify document type
                doc_type = self._classify_document_type(doc_result)
                
                processed_doc = {
                    "file_path": doc_path,
                    "document_type": doc_type,
                    "text_content": doc_result["text"],
                    "metadata": doc_result["metadata"],
                    "financial_data": financial_data,
                    "extraction_confidence": self._assess_extraction_confidence(doc_result, financial_data)
                }
                
                processed_documents.append(processed_doc)
                extraction_results.append(financial_data)
            
            # Consolidate financial data
            consolidated_data = self._consolidate_financial_data(extraction_results)
            
            # Get relevant guidelines for document requirements
            guidelines = await self.rag_system.get_guidelines_for_category("document_requirements")
            
            # Generate recommendations
            recommendations = self._generate_document_recommendations(processed_documents)
            
            result = {
                "application_id": application_id,
                "processed_documents": processed_documents,
                "consolidated_financial_data": consolidated_data,
                "document_count": len(processed_documents),
                "guidelines_context": guidelines[:3] if guidelines else [],
                "processing_status": "completed"
            }
            
            # Calculate overall confidence
            confidence_scores = [doc["extraction_confidence"] for doc in processed_documents if doc["extraction_confidence"] > 0]
            overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            output = AgentOutput(
                result=result,
                metadata={
                    "processing_time": datetime.now().isoformat(),
                    "documents_processed": len(processed_documents),
                    "extraction_method": "OCR + NLP"
                },
                confidence_score=overall_confidence,
                recommendations=recommendations
            )
            
            await self._log_execution(input_data, output)
            return output
            
        except Exception as e:
            self.logger.error("Document processing failed", error=str(e))
            return AgentOutput(
                result={"error": str(e)},
                metadata={"error": True},
                confidence_score=0.0,
                recommendations=["Fix document processing error"]
            )
    
    def _extract_financial_data(self, doc_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract financial data from processed document."""
        financial_data = {}
        text = doc_result.get("text", "")
        
        # Extract financial tables
        tables = self.document_processor.extract_financial_tables(text)
        
        # Simple keyword-based extraction (in production, use more sophisticated NLP)
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            
            # Revenue extraction
            if any(keyword in line_lower for keyword in ['revenue', 'sales', 'total income']):
                numbers = self._extract_numbers_from_text(line)
                if numbers:
                    financial_data['revenue'] = max(numbers)  # Take the largest number
            
            # Net income extraction
            if any(keyword in line_lower for keyword in ['net income', 'net profit', 'profit after tax']):
                numbers = self._extract_numbers_from_text(line)
                if numbers:
                    financial_data['net_income'] = max(numbers)
            
            # Total assets extraction
            if 'total assets' in line_lower:
                numbers = self._extract_numbers_from_text(line)
                if numbers:
                    financial_data['total_assets'] = max(numbers)
            
            # Cash extraction
            if any(keyword in line_lower for keyword in ['cash', 'cash and cash equivalents']):
                numbers = self._extract_numbers_from_text(line)
                if numbers:
                    financial_data['cash'] = max(numbers)
        
        financial_data['extracted_tables'] = tables
        return financial_data
    
    def _extract_numbers_from_text(self, text: str) -> List[float]:
        """Extract numeric values from text."""
        import re
        # Pattern to match currency amounts
        pattern = r'[\$]?[\d,]+\.?\d*'
        matches = re.findall(pattern, text)
        
        numbers = []
        for match in matches:
            try:
                # Clean and convert to float
                cleaned = match.replace('$', '').replace(',', '')
                if cleaned:
                    numbers.append(float(cleaned))
            except ValueError:
                continue
        
        return numbers
    
    def _classify_document_type(self, doc_result: Dict[str, Any]) -> str:
        """Classify the type of financial document."""
        text = doc_result.get("text", "").lower()
        
        if any(keyword in text for keyword in ['income statement', 'profit and loss', 'p&l']):
            return 'income_statement'
        elif any(keyword in text for keyword in ['balance sheet', 'statement of financial position']):
            return 'balance_sheet'
        elif any(keyword in text for keyword in ['cash flow', 'statement of cash flows']):
            return 'cash_flow_statement'
        elif any(keyword in text for keyword in ['tax return', '1040', '1120']):
            return 'tax_return'
        elif any(keyword in text for keyword in ['business plan', 'executive summary']):
            return 'business_plan'
        else:
            return 'other'
    
    def _assess_extraction_confidence(self, doc_result: Dict[str, Any], financial_data: Dict[str, Any]) -> float:
        """Assess confidence in data extraction."""
        confidence_factors = []
        
        # Document quality
        if doc_result.get("file_type") == "pdf":
            confidence_factors.append(0.8)  # PDFs generally have better text extraction
        else:
            confidence_factors.append(0.6)  # Images/scanned docs are less reliable
        
        # Amount of extracted data
        if financial_data:
            data_completeness = len(financial_data) / 10  # Assume 10 key fields
            confidence_factors.append(min(data_completeness, 1.0))
        else:
            confidence_factors.append(0.1)
        
        # Text quality indicators
        text = doc_result.get("text", "")
        if len(text) > 1000:  # Sufficient text extracted
            confidence_factors.append(0.8)
        elif len(text) > 100:
            confidence_factors.append(0.5)
        else:
            confidence_factors.append(0.2)
        
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.0
    
    def _consolidate_financial_data(self, extraction_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Consolidate financial data from multiple documents."""
        consolidated = {
            'income_statement': {},
            'balance_sheet': {},
            'cash_flow_statement': {},
            'other_data': {}
        }
        
        for result in extraction_results:
            for key, value in result.items():
                if key != 'extracted_tables':
                    # Simple consolidation - in production, use more sophisticated logic
                    if key not in consolidated['other_data'] or value > consolidated['other_data'].get(key, 0):
                        consolidated['other_data'][key] = value
        
        return consolidated
    
    def _generate_document_recommendations(self, processed_documents: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on document analysis."""
        recommendations = []
        
        doc_types = [doc['document_type'] for doc in processed_documents]
        
        if 'income_statement' not in doc_types:
            recommendations.append("Income statement required for complete financial analysis")
        
        if 'balance_sheet' not in doc_types:
            recommendations.append("Balance sheet required for complete financial analysis")
        
        low_confidence_docs = [doc for doc in processed_documents if doc['extraction_confidence'] < 0.5]
        if low_confidence_docs:
            recommendations.append(f"Manual review needed for {len(low_confidence_docs)} documents with low extraction confidence")
        
        if len(processed_documents) < 3:
            recommendations.append("Additional financial documents recommended for comprehensive analysis")
        
        return recommendations
    
    def get_prompt_template(self) -> str:
        """Get the prompt template for this agent."""
        return """
        You are a document ingestion agent specializing in financial document processing. Your role is to:
        1. Process and digitize various financial documents (PDFs, images, etc.)
        2. Extract key financial data using OCR and NLP techniques
        3. Classify document types and assess extraction quality
        4. Consolidate financial information from multiple sources
        
        Focus on accuracy, completeness, and data quality assessment.
        """ 