"""Advanced document intelligence using computer vision and NLP."""
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import torch
from transformers import pipeline, AutoTokenizer, AutoModel
from PIL import Image
import pandas as pd
import re
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class DocumentInsight:
    """Document analysis result."""
    document_type: str
    confidence: float
    key_entities: Dict[str, Any]
    financial_data: Dict[str, float]
    anomalies: List[str]
    risk_flags: List[str]
    completeness_score: float


class AdvancedDocumentAI:
    """Advanced document intelligence system."""
    
    def __init__(self):
        self.financial_ner = pipeline(
            "ner", 
            model="ProsusAI/finbert", 
            tokenizer="ProsusAI/finbert",
            aggregation_strategy="simple"
        )
        
        self.document_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        
        self.table_detector = self._initialize_table_detection()
        self.fraud_detector = self._initialize_fraud_detection()
        
    def analyze_financial_document(
        self, 
        document_path: str,
        document_type: str = "auto"
    ) -> DocumentInsight:
        """Comprehensive financial document analysis."""
        
        # Extract text and images
        text_content = self._extract_text_advanced(document_path)
        tables = self._extract_tables_advanced(document_path)
        images = self._extract_images(document_path)
        
        # Document classification
        if document_type == "auto":
            document_type = self._classify_document_type(text_content)
        
        # Multi-modal analysis
        financial_data = self._extract_financial_data(text_content, tables)
        entities = self._extract_entities(text_content)
        anomalies = self._detect_anomalies(text_content, financial_data, images)
        risk_flags = self._identify_risk_flags(text_content, financial_data)
        completeness = self._assess_completeness(text_content, document_type)
        
        return DocumentInsight(
            document_type=document_type,
            confidence=self._calculate_confidence(text_content, financial_data),
            key_entities=entities,
            financial_data=financial_data,
            anomalies=anomalies,
            risk_flags=risk_flags,
            completeness_score=completeness
        )
    
    def _extract_text_advanced(self, document_path: str) -> str:
        """Advanced text extraction with layout understanding."""
        # In production, use advanced OCR like AWS Textract, Google Document AI
        # For now, simulate enhanced text extraction
        
        # Simulate document regions
        text_regions = {
            'header': "FINANCIAL STATEMENT\nFor the Year Ended December 31, 2023",
            'body': """
            Revenue: $2,500,000
            Cost of Goods Sold: $1,200,000
            Gross Profit: $1,300,000
            Operating Expenses: $800,000
            Net Income: $500,000
            
            Assets:
            Current Assets: $1,800,000
            Fixed Assets: $2,200,000
            Total Assets: $4,000,000
            
            Liabilities:
            Current Liabilities: $600,000
            Long-term Debt: $1,400,000
            Total Liabilities: $2,000,000
            
            Equity: $2,000,000
            """,
            'footer': "Prepared by: John Smith, CPA\nDate: January 15, 2024"
        }
        
        return "\n".join(text_regions.values())
    
    def _extract_tables_advanced(self, document_path: str) -> List[pd.DataFrame]:
        """Advanced table extraction with structure understanding."""
        
        # Simulate extracted financial tables
        income_statement = pd.DataFrame({
            'Item': ['Revenue', 'COGS', 'Gross Profit', 'Operating Expenses', 'Net Income'],
            '2023': [2500000, 1200000, 1300000, 800000, 500000],
            '2022': [2200000, 1100000, 1100000, 750000, 350000],
            '2021': [2000000, 1000000, 1000000, 700000, 300000]
        })
        
        balance_sheet = pd.DataFrame({
            'Item': ['Current Assets', 'Fixed Assets', 'Total Assets', 
                    'Current Liabilities', 'Long-term Debt', 'Total Liabilities', 'Equity'],
            '2023': [1800000, 2200000, 4000000, 600000, 1400000, 2000000, 2000000],
            '2022': [1600000, 2000000, 3600000, 550000, 1300000, 1850000, 1750000],
            '2021': [1400000, 1800000, 3200000, 500000, 1200000, 1700000, 1500000]
        })
        
        return [income_statement, balance_sheet]
    
    def _extract_images(self, document_path: str) -> List[Dict[str, Any]]:
        """Extract and analyze images/charts from documents."""
        
        # Simulate chart analysis
        charts = [
            {
                'type': 'bar_chart',
                'title': 'Revenue Growth',
                'data_points': [2000000, 2200000, 2500000],
                'trend': 'increasing',
                'anomalies': []
            },
            {
                'type': 'pie_chart',
                'title': 'Expense Breakdown',
                'data_points': {'COGS': 0.48, 'OpEx': 0.32, 'Other': 0.20},
                'anomalies': ['Unusually high COGS percentage']
            }
        ]
        
        return charts
    
    def _classify_document_type(self, text: str) -> str:
        """Classify document type using NLP."""
        
        candidate_labels = [
            "income statement", "balance sheet", "cash flow statement",
            "tax return", "bank statement", "loan application",
            "financial projection", "audit report"
        ]
        
        result = self.document_classifier(text[:512], candidate_labels)
        return result['labels'][0] if result['scores'][0] > 0.3 else "unknown"
    
    def _extract_financial_data(
        self, 
        text: str, 
        tables: List[pd.DataFrame]
    ) -> Dict[str, float]:
        """Extract structured financial data using NLP and table analysis."""
        
        financial_data = {}
        
        # Extract from text using regex patterns
        patterns = {
            'revenue': r'(?:revenue|sales|income).*?[\$]?([0-9,]+)',
            'net_income': r'(?:net income|profit).*?[\$]?([0-9,]+)',
            'total_assets': r'(?:total assets).*?[\$]?([0-9,]+)',
            'total_liabilities': r'(?:total liabilities).*?[\$]?([0-9,]+)',
            'cash': r'(?:cash|cash equivalents).*?[\$]?([0-9,]+)'
        }
        
        for metric, pattern in patterns.items():
            matches = re.findall(pattern, text.lower(), re.IGNORECASE)
            if matches:
                try:
                    value = float(matches[0].replace(',', ''))
                    financial_data[metric] = value
                except ValueError:
                    continue
        
        # Extract from tables
        for table in tables:
            if 'Item' in table.columns:
                for idx, row in table.iterrows():
                    item = row['Item'].lower()
                    if 'revenue' in item and '2023' in table.columns:
                        financial_data['revenue'] = float(row['2023'])
                    elif 'net income' in item and '2023' in table.columns:
                        financial_data['net_income'] = float(row['2023'])
                    elif 'total assets' in item and '2023' in table.columns:
                        financial_data['total_assets'] = float(row['2023'])
        
        return financial_data
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities and financial terms."""
        
        # Use financial NER model
        entities = self.financial_ner(text[:512])  # Limit text length
        
        # Organize entities by type
        entity_dict = {}
        for entity in entities:
            entity_type = entity['entity_group']
            if entity_type not in entity_dict:
                entity_dict[entity_type] = []
            entity_dict[entity_type].append({
                'text': entity['word'],
                'confidence': entity['score'],
                'start': entity['start'],
                'end': entity['end']
            })
        
        # Extract additional business entities
        business_entities = self._extract_business_entities(text)
        entity_dict.update(business_entities)
        
        return entity_dict
    
    def _extract_business_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract business-specific entities."""
        
        patterns = {
            'company_names': r'(?:Inc\.|LLC|Corp\.|Corporation|Company|Ltd\.)',
            'currencies': r'\$[0-9,]+(?:\.[0-9]{2})?',
            'percentages': r'[0-9]+(?:\.[0-9]+)?%',
            'dates': r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+[0-9]{1,2},?\s+[0-9]{4}',
            'phone_numbers': r'\([0-9]{3}\)\s*[0-9]{3}-[0-9]{4}',
            'tax_ids': r'[0-9]{2}-[0-9]{7}'
        }
        
        entities = {}
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities[entity_type] = list(set(matches))
        
        return entities
    
    def _detect_anomalies(
        self, 
        text: str, 
        financial_data: Dict[str, float], 
        images: List[Dict[str, Any]]
    ) -> List[str]:
        """Detect anomalies in document content."""
        
        anomalies = []
        
        # Financial ratio anomalies
        if 'revenue' in financial_data and 'net_income' in financial_data:
            margin = financial_data['net_income'] / financial_data['revenue']
            if margin < 0:
                anomalies.append("Negative profit margin detected")
            elif margin > 0.5:
                anomalies.append("Unusually high profit margin (>50%)")
        
        # Text inconsistencies
        if 'loss' in text.lower() and 'profit' in text.lower():
            anomalies.append("Document contains both profit and loss statements")
        
        # Image anomalies
        for image in images:
            if image.get('anomalies'):
                anomalies.extend(image['anomalies'])
        
        # Date inconsistencies
        dates = re.findall(r'[0-9]{4}', text)
        if dates:
            years = [int(d) for d in dates if d.isdigit()]
            if len(set(years)) > 3:
                anomalies.append("Multiple years referenced - verify data consistency")
        
        return anomalies
    
    def _identify_risk_flags(
        self, 
        text: str, 
        financial_data: Dict[str, float]
    ) -> List[str]:
        """Identify risk indicators in document."""
        
        risk_flags = []
        
        # High-risk keywords
        risk_keywords = [
            'bankruptcy', 'default', 'restructuring', 'lawsuit',
            'investigation', 'fraud', 'material weakness',
            'going concern', 'covenant violation'
        ]
        
        text_lower = text.lower()
        for keyword in risk_keywords:
            if keyword in text_lower:
                risk_flags.append(f"High-risk keyword detected: {keyword}")
        
        # Financial risk indicators
        if 'revenue' in financial_data and financial_data['revenue'] < 100000:
            risk_flags.append("Very low revenue (<$100K)")
        
        if 'total_assets' in financial_data and 'total_liabilities' in financial_data:
            if financial_data['total_liabilities'] > financial_data['total_assets']:
                risk_flags.append("Liabilities exceed assets")
        
        # Completeness risks
        required_fields = ['revenue', 'net_income', 'total_assets']
        missing_fields = [field for field in required_fields if field not in financial_data]
        if missing_fields:
            risk_flags.append(f"Missing critical financial data: {', '.join(missing_fields)}")
        
        return risk_flags
    
    def _assess_completeness(self, text: str, document_type: str) -> float:
        """Assess document completeness."""
        
        # Define required sections by document type
        required_sections = {
            'income statement': ['revenue', 'expenses', 'net income'],
            'balance sheet': ['assets', 'liabilities', 'equity'],
            'cash flow statement': ['operating', 'investing', 'financing'],
            'loan application': ['company info', 'financial data', 'purpose']
        }
        
        sections = required_sections.get(document_type, [])
        if not sections:
            return 0.5  # Unknown document type
        
        # Check for presence of required sections
        text_lower = text.lower()
        present_sections = 0
        
        for section in sections:
            if section in text_lower:
                present_sections += 1
        
        completeness = present_sections / len(sections)
        
        # Bonus for signatures, dates, and official formatting
        if 'signature' in text_lower or 'signed' in text_lower:
            completeness += 0.1
        if re.search(r'[0-9]{4}', text):  # Contains year
            completeness += 0.05
        
        return min(completeness, 1.0)
    
    def _calculate_confidence(
        self, 
        text: str, 
        financial_data: Dict[str, float]
    ) -> float:
        """Calculate overall confidence in document analysis."""
        
        confidence_factors = []
        
        # Text quality
        if len(text) > 500:
            confidence_factors.append(0.8)
        elif len(text) > 200:
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.3)
        
        # Financial data completeness
        if len(financial_data) >= 5:
            confidence_factors.append(0.9)
        elif len(financial_data) >= 3:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)
        
        # Structured content indicators
        if any(keyword in text.lower() for keyword in ['statement', 'report', 'financial']):
            confidence_factors.append(0.8)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def _initialize_table_detection(self):
        """Initialize table detection model."""
        # In production, use specialized table detection models
        # like Microsoft Table Transformer or similar
        return None
    
    def _initialize_fraud_detection(self):
        """Initialize fraud detection model."""
        # In production, use trained fraud detection models
        # trained on financial document fraud patterns
        return None


class DocumentValidationEngine:
    """Advanced document validation and verification."""
    
    def __init__(self):
        self.blockchain_verifier = None  # For document authenticity
        self.cross_reference_db = None   # For data cross-referencing
        
    def validate_document_authenticity(
        self, 
        document_path: str,
        document_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate document authenticity using multiple methods."""
        
        validation_results = {
            'is_authentic': True,
            'confidence': 0.85,
            'validation_methods': [],
            'warnings': [],
            'metadata_analysis': {}
        }
        
        # Metadata analysis
        metadata_analysis = self._analyze_metadata(document_metadata)
        validation_results['metadata_analysis'] = metadata_analysis
        
        # Digital signature verification
        signature_valid = self._verify_digital_signature(document_path)
        validation_results['validation_methods'].append({
            'method': 'digital_signature',
            'result': signature_valid,
            'confidence': 0.9 if signature_valid else 0.1
        })
        
        # Forensic analysis
        forensic_analysis = self._forensic_document_analysis(document_path)
        validation_results['validation_methods'].append({
            'method': 'forensic_analysis',
            'result': forensic_analysis,
            'confidence': 0.8
        })
        
        # Cross-reference with external sources
        cross_ref_results = self._cross_reference_data(document_metadata)
        validation_results['validation_methods'].append({
            'method': 'cross_reference',
            'result': cross_ref_results,
            'confidence': 0.7
        })
        
        # Calculate overall confidence
        method_confidences = [m['confidence'] for m in validation_results['validation_methods']]
        validation_results['confidence'] = sum(method_confidences) / len(method_confidences)
        
        return validation_results
    
    def _analyze_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document metadata for authenticity indicators."""
        
        analysis = {
            'creation_date': metadata.get('creation_date'),
            'modification_date': metadata.get('modification_date'),
            'author': metadata.get('author'),
            'software': metadata.get('software'),
            'flags': []
        }
        
        # Check for suspicious patterns
        if metadata.get('creation_date') and metadata.get('modification_date'):
            creation = datetime.fromisoformat(metadata['creation_date'].replace('Z', '+00:00'))
            modification = datetime.fromisoformat(metadata['modification_date'].replace('Z', '+00:00'))
            
            if (modification - creation).total_seconds() < 60:
                analysis['flags'].append("Very short time between creation and modification")
        
        # Check for suspicious software
        suspicious_software = ['pdf_forge', 'fake_pdf', 'doc_generator']
        if any(sw in metadata.get('software', '').lower() for sw in suspicious_software):
            analysis['flags'].append("Document created with suspicious software")
        
        return analysis
    
    def _verify_digital_signature(self, document_path: str) -> bool:
        """Verify digital signature if present."""
        # In production, implement actual digital signature verification
        # using libraries like cryptography or PyPDF2
        return True  # Simulated result
    
    def _forensic_document_analysis(self, document_path: str) -> Dict[str, Any]:
        """Perform forensic analysis of document."""
        
        # In production, implement:
        # - Font consistency analysis
        # - Image compression analysis
        # - Text alignment patterns
        # - Color profile analysis
        
        return {
            'font_consistency': True,
            'image_integrity': True,
            'text_alignment': True,
            'suspicious_patterns': []
        }
    
    def _cross_reference_data(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-reference data with external sources."""
        
        # In production, cross-reference with:
        # - Company databases
        # - Financial data providers
        # - Regulatory filings
        # - News and events
        
        return {
            'company_exists': True,
            'financial_data_consistent': True,
            'regulatory_filings_match': True,
            'discrepancies': []
        } 