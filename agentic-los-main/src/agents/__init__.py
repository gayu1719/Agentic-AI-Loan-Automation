"""Agents package for the Agentic LOS system."""

from .base_agent import BaseAgent
from .data_ingestion import ApplicationDataAgent, DocumentIngestionAgent
from .financial_analysis import HistoricalFinancialAnalysisAgent, FinancialProjectionAgent

# Note: Additional agent modules (credit_assessment, decisioning, monitoring) 
# are not yet implemented in this base version

__all__ = [
    "BaseAgent",
    "ApplicationDataAgent",
    "DocumentIngestionAgent", 
    "HistoricalFinancialAnalysisAgent",
    "FinancialProjectionAgent"
] 