"""Main LangGraph workflow for loan underwriting process."""
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
import structlog

from ..agents.base_agent import AgentInput, AgentOutput
from ..agents.data_ingestion import ApplicationDataAgent, DocumentIngestionAgent
from ..agents.financial_analysis import HistoricalFinancialAnalysisAgent, FinancialProjectionAgent
from ..models.loan_application import LoanApplication
from ..models.decisions import LoanDecision, DecisionStatus
from ..utils.rag_system import RAGSystem

logger = structlog.get_logger()


class WorkflowState(BaseModel):
    """State model for the loan underwriting workflow."""
    
    # Input data
    application_data: Dict[str, Any] = {}
    document_paths: List[str] = []
    
    # Agent outputs
    parsed_application: Dict[str, Any] = {}
    processed_documents: Dict[str, Any] = {}
    historical_analysis: Dict[str, Any] = {}
    financial_projections: Dict[str, Any] = {}
    qca_assessment: Dict[str, Any] = {}
    quantitative_assessment: Dict[str, Any] = {}
    credit_decision: Dict[str, Any] = {}
    
    # Workflow metadata
    workflow_id: str = ""
    current_step: str = ""
    errors: List[str] = []
    warnings: List[str] = []
    
    # Final outputs
    loan_decision: Optional[LoanDecision] = None
    processing_complete: bool = False


class LoanUnderwritingWorkflow:
    """Main workflow orchestrator for loan underwriting."""
    
    def __init__(self):
        self.logger = logger.bind(component="loan_workflow")
        self.rag_system = RAGSystem()
        self.workflow_graph = self._build_workflow_graph()
        
        # Initialize agents
        self.application_agent = ApplicationDataAgent()
        self.document_agent = DocumentIngestionAgent()
        self.historical_analysis_agent = HistoricalFinancialAnalysisAgent()
        self.projection_agent = FinancialProjectionAgent()
    
    def _build_workflow_graph(self):
        """Build the LangGraph workflow."""
        
        # Define the workflow graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes (workflow steps)
        workflow.add_node("initialize", self._initialize_workflow)
        workflow.add_node("process_application", self._process_application_data)
        workflow.add_node("ingest_documents", self._ingest_documents)
        workflow.add_node("analyze_historical_financials", self._analyze_historical_financials)
        workflow.add_node("generate_projections", self._generate_financial_projections)
        workflow.add_node("assess_qualitative_credit", self._assess_qualitative_credit)
        workflow.add_node("assess_quantitative_credit", self._assess_quantitative_credit)
        workflow.add_node("make_credit_decision", self._make_credit_decision)
        workflow.add_node("finalize_workflow", self._finalize_workflow)
        
        # Define the workflow edges (sequence)
        workflow.add_edge("initialize", "process_application")
        workflow.add_edge("process_application", "ingest_documents")
        workflow.add_edge("ingest_documents", "analyze_historical_financials")
        workflow.add_edge("analyze_historical_financials", "generate_projections")
        workflow.add_edge("generate_projections", "assess_qualitative_credit")  
        workflow.add_edge("assess_qualitative_credit", "assess_quantitative_credit")
        workflow.add_edge("assess_quantitative_credit", "make_credit_decision")
        workflow.add_edge("make_credit_decision", "finalize_workflow")
        workflow.add_edge("finalize_workflow", END)
        
        # Set entry point
        workflow.set_entry_point("initialize")
        
        return workflow.compile()
    
    async def process_loan_application(
        self, 
        application_data: Dict[str, Any],
        document_paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Process a complete loan application through the workflow."""
        
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize state
        initial_state = WorkflowState(
            application_data=application_data,
            document_paths=document_paths or [],
            workflow_id=workflow_id,
            current_step="initialize"
        )
        
        try:
            self.logger.info("Starting loan underwriting workflow", workflow_id=workflow_id)
            
            # Execute the workflow
            final_state = await self.workflow_graph.ainvoke(initial_state.dict())
            
            # Convert back to WorkflowState object
            final_workflow_state = WorkflowState(**final_state)
            
            self.logger.info(
                "Loan underwriting workflow completed",
                workflow_id=workflow_id,
                processing_complete=final_workflow_state.processing_complete,
                errors_count=len(final_workflow_state.errors)
            )
            
            return {
                "workflow_id": workflow_id,
                "status": "completed" if final_workflow_state.processing_complete else "failed",
                "loan_decision": final_workflow_state.loan_decision.dict() if final_workflow_state.loan_decision else None,
                "parsed_application": final_workflow_state.parsed_application,
                "document_analysis": final_workflow_state.processed_documents,
                "financial_analysis": final_workflow_state.historical_analysis,
                "projections": final_workflow_state.financial_projections,
                "errors": final_workflow_state.errors,
                "warnings": final_workflow_state.warnings
            }
            
        except Exception as e:
            self.logger.error("Workflow execution failed", workflow_id=workflow_id, error=str(e))
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": str(e),
                "loan_decision": None
            }
    
    async def _initialize_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the workflow and perform basic validation."""
        try:
            workflow_state = WorkflowState(**state)
            workflow_state.current_step = "initialize"
            
            # Validate input data
            if not workflow_state.application_data:
                workflow_state.errors.append("No application data provided")
                return workflow_state.dict()
            
            # Initialize RAG system if not already done
            await self.rag_system.initialize_knowledge_base("./rules")
            
            self.logger.info("Workflow initialized", workflow_id=workflow_state.workflow_id)
            
            return workflow_state.dict()
            
        except Exception as e:
            self.logger.error("Workflow initialization failed", error=str(e))
            state["errors"] = state.get("errors", []) + [f"Initialization error: {str(e)}"]
            return state
    
    async def _process_application_data(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate application data."""
        try:
            workflow_state = WorkflowState(**state)
            workflow_state.current_step = "process_application"
            
            # Create agent input
            agent_input = AgentInput(data=workflow_state.application_data)
            
            # Process with Application Data Agent
            result = await self.application_agent.process(agent_input)
            
            if result.confidence_score < 0.5:
                workflow_state.warnings.append("Low confidence in application data quality")
            
            workflow_state.parsed_application = result.result
            
            self.logger.info(
                "Application data processed",
                workflow_id=workflow_state.workflow_id,
                confidence=result.confidence_score
            )
            
            return workflow_state.dict()
            
        except Exception as e:
            self.logger.error("Application processing failed", error=str(e))
            state["errors"] = state.get("errors", []) + [f"Application processing error: {str(e)}"]
            return state
    
    async def _ingest_documents(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest and process supporting documents."""
        try:
            workflow_state = WorkflowState(**state)
            workflow_state.current_step = "ingest_documents"
            
            if not workflow_state.document_paths:
                workflow_state.warnings.append("No documents provided for processing")
                workflow_state.processed_documents = {"status": "no_documents"}
                return workflow_state.dict()
            
            # Prepare agent input
            agent_input = AgentInput(data={
                "document_paths": workflow_state.document_paths,
                "application_id": workflow_state.workflow_id
            })
            
            # Process with Document Ingestion Agent
            result = await self.document_agent.process(agent_input)
            
            if result.confidence_score < 0.6:
                workflow_state.warnings.append("Low confidence in document extraction")
            
            workflow_state.processed_documents = result.result
            
            self.logger.info(
                "Documents processed",
                workflow_id=workflow_state.workflow_id,
                document_count=len(workflow_state.document_paths),
                confidence=result.confidence_score
            )
            
            return workflow_state.dict()
            
        except Exception as e:
            self.logger.error("Document ingestion failed", error=str(e))
            state["errors"] = state.get("errors", []) + [f"Document processing error: {str(e)}"]
            return state
    
    async def _analyze_historical_financials(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze historical financial performance."""
        try:
            workflow_state = WorkflowState(**state)
            workflow_state.current_step = "analyze_historical_financials"
            
            # Extract financial data from processed documents
            financial_data = workflow_state.processed_documents.get("consolidated_financial_data", {})
            company_info = workflow_state.parsed_application.get("loan_application", {}).get("company_details", {})
            
            if not financial_data:
                workflow_state.warnings.append("Limited financial data available for analysis")
                workflow_state.historical_analysis = {"status": "insufficient_data"}
                return workflow_state.dict()
            
            # Prepare agent input
            agent_input = AgentInput(data={
                "financial_statements": financial_data,
                "company_info": company_info
            })
            
            # Process with Historical Financial Analysis Agent
            result = await self.historical_analysis_agent.process(agent_input)
            
            workflow_state.historical_analysis = result.result
            
            if result.confidence_score < 0.7:
                workflow_state.warnings.append("Financial analysis has moderate confidence due to data limitations")
            
            self.logger.info(
                "Historical financial analysis completed",
                workflow_id=workflow_state.workflow_id,
                health_score=result.result.get("financial_health_score", 0),
                confidence=result.confidence_score
            )
            
            return workflow_state.dict()
            
        except Exception as e:
            self.logger.error("Historical financial analysis failed", error=str(e))
            state["errors"] = state.get("errors", []) + [f"Financial analysis error: {str(e)}"]
            return state
    
    async def _generate_financial_projections(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate financial projections and scenarios."""
        try:
            workflow_state = WorkflowState(**state)
            workflow_state.current_step = "generate_projections"
            
            # Extract required data
            historical_analysis = workflow_state.historical_analysis
            loan_request = workflow_state.parsed_application.get("loan_application", {}).get("financial_data", {})
            
            # For now, use default management inputs and economic assumptions
            # In production, these would come from additional data collection
            management_inputs = {
                "expected_revenue_growth": 0.05,  # 5% growth expectation
                "planned_capex": loan_request.get("requested_loan_amount", 0) * 0.8,
                "market_expansion_plans": "moderate"
            }
            
            economic_assumptions = {
                "gdp_growth_adjustment": 1.0,
                "interest_rate_environment": "stable",
                "downside_revenue_impact": 0.75,  # 25% decline in downside
                "downside_margin_impact": 0.85   # 15% margin compression
            }
            
            # Prepare agent input
            agent_input = AgentInput(data={
                "historical_analysis": historical_analysis,
                "management_inputs": management_inputs,
                "economic_assumptions": economic_assumptions,
                "loan_request": loan_request
            })
            
            # Process with Financial Projection Agent
            result = await self.projection_agent.process(agent_input)
            
            workflow_state.financial_projections = result.result
            
            if result.confidence_score < 0.6:
                workflow_state.warnings.append("Financial projections have lower confidence due to limited inputs")
            
            self.logger.info(
                "Financial projections generated",
                workflow_id=workflow_state.workflow_id,
                projection_confidence=result.confidence_score
            )
            
            return workflow_state.dict()
            
        except Exception as e:
            self.logger.error("Financial projection generation failed", error=str(e))
            state["errors"] = state.get("errors", []) + [f"Projection error: {str(e)}"]
            return state
    
    async def _assess_qualitative_credit(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Assess qualitative credit factors (QCA)."""
        try:
            workflow_state = WorkflowState(**state)
            workflow_state.current_step = "assess_qualitative_credit"
            
            # For now, implement a simplified QCA assessment
            # In production, this would be a full QCA agent with detailed questionnaires
            
            company_details = workflow_state.parsed_application.get("loan_application", {}).get("company_details", {})
            
            qca_score = self._calculate_simplified_qca_score(company_details)
            
            workflow_state.qca_assessment = {
                "overall_qca_score": qca_score,
                "assessment_date": datetime.now().isoformat(),
                "categories": {
                    "management": self._assess_management_quality(company_details),
                    "business_operations": self._assess_business_operations(company_details),
                    "industry_position": self._assess_industry_position(company_details)
                }
            }
            
            self.logger.info(
                "Qualitative credit assessment completed",
                workflow_id=workflow_state.workflow_id,
                qca_score=qca_score
            )
            
            return workflow_state.dict()
            
        except Exception as e:
            self.logger.error("QCA assessment failed", error=str(e))
            state["errors"] = state.get("errors", []) + [f"QCA error: {str(e)}"]
            return state
    
    async def _assess_quantitative_credit(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quantitative credit factors."""
        try:
            workflow_state = WorkflowState(**state)
            workflow_state.current_step = "assess_quantitative_credit"
            
            # Extract relevant data
            historical_analysis = workflow_state.historical_analysis
            company_details = workflow_state.parsed_application.get("loan_application", {}).get("company_details", {})
            
            # Calculate quantitative score based on financial ratios
            quant_score = self._calculate_quantitative_score(historical_analysis)
            
            workflow_state.quantitative_assessment = {
                "quantitative_score": quant_score,
                "assessment_date": datetime.now().isoformat(),
                "key_ratios": historical_analysis.get("ratio_analysis", [])[-1] if historical_analysis.get("ratio_analysis") else {},
                "financial_health_score": historical_analysis.get("financial_health_score", 50),
                "risk_factors": self._identify_quantitative_risk_factors(historical_analysis)
            }
            
            self.logger.info(
                "Quantitative credit assessment completed",
                workflow_id=workflow_state.workflow_id,
                quant_score=quant_score
            )
            
            return workflow_state.dict()
            
        except Exception as e:
            self.logger.error("Quantitative assessment failed", error=str(e))
            state["errors"] = state.get("errors", []) + [f"Quantitative assessment error: {str(e)}"]
            return state
    
    async def _make_credit_decision(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Make the final credit decision."""
        try:
            workflow_state = WorkflowState(**state)
            workflow_state.current_step = "make_credit_decision"
            
            # Extract scores and assessments
            qca_score = workflow_state.qca_assessment.get("overall_qca_score", 50)
            quant_score = workflow_state.quantitative_assessment.get("quantitative_score", 50)
            financial_health = workflow_state.quantitative_assessment.get("financial_health_score", 50)
            
            # Calculate composite score
            composite_score = (qca_score * 0.4) + (quant_score * 0.4) + (financial_health * 0.2)
            
            # Determine decision
            if composite_score >= 80:
                decision_status = DecisionStatus.APPROVED
                decision_color = "GREEN_PASS"
            elif composite_score >= 60:
                decision_status = DecisionStatus.CONDITIONAL_APPROVAL  
                decision_color = "YELLOW_CHECK"
            else:
                decision_status = DecisionStatus.DECLINED
                decision_color = "RED_CHECK"
            
            # Create loan decision
            loan_request = workflow_state.parsed_application.get("loan_application", {})
            
            decision_data = {
                "application_id": workflow_state.workflow_id,
                "decision_id": f"decision_{workflow_state.workflow_id}",
                "decision_status": decision_status,
                "decision_color": decision_color,
                "final_credit_score": composite_score,
                "risk_rating": self._determine_risk_rating(composite_score),
                "decision_rationale": self._generate_decision_rationale(qca_score, quant_score, financial_health),
                "key_factors": self._extract_key_decision_factors(workflow_state),
                "decision_maker": "Agentic LOS System",
                "approval_level": "System"
            }
            
            workflow_state.credit_decision = decision_data
            
            self.logger.info(
                "Credit decision made",
                workflow_id=workflow_state.workflow_id,
                decision=decision_status,
                composite_score=composite_score
            )
            
            return workflow_state.dict()
            
        except Exception as e:
            self.logger.error("Credit decision failed", error=str(e))
            state["errors"] = state.get("errors", []) + [f"Decision error: {str(e)}"]
            return state
    
    async def _finalize_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize the workflow and prepare final output."""
        try:
            workflow_state = WorkflowState(**state)
            workflow_state.current_step = "finalize"
            
            # Create final loan decision object if credit decision was made
            if workflow_state.credit_decision:
                from ..models.decisions import LoanDecision
                workflow_state.loan_decision = LoanDecision(**workflow_state.credit_decision)
            
            # Mark workflow as complete if no critical errors
            if not any("error" in error.lower() for error in workflow_state.errors):
                workflow_state.processing_complete = True
            
            self.logger.info(
                "Workflow finalized",
                workflow_id=workflow_state.workflow_id,
                complete=workflow_state.processing_complete,
                final_decision=workflow_state.loan_decision.decision_status if workflow_state.loan_decision else None
            )
            
            return workflow_state.dict()
            
        except Exception as e:
            self.logger.error("Workflow finalization failed", error=str(e))
            state["errors"] = state.get("errors", []) + [f"Finalization error: {str(e)}"]
            return state
    
    # Helper methods for credit assessment
    
    def _calculate_simplified_qca_score(self, company_details: Dict[str, Any]) -> float:
        """Calculate a simplified QCA score."""
        score = 50  # Base score
        
        # Years in business
        years = company_details.get("years_in_business", 0)
        if years >= 5:
            score += 20
        elif years >= 2:
            score += 10
        
        # Revenue size
        revenue = company_details.get("annual_revenue", 0)
        if revenue >= 5000000:  # $5M+
            score += 15
        elif revenue >= 1000000:  # $1M+
            score += 10
        elif revenue >= 500000:  # $500K+
            score += 5
        
        # Industry risk (simplified)
        industry = company_details.get("industry_type", "")
        low_risk_industries = ["technology", "healthcare", "services"]
        if industry in low_risk_industries:
            score += 10
        
        return min(score, 100)
    
    def _assess_management_quality(self, company_details: Dict[str, Any]) -> Dict[str, Any]:
        """Assess management quality."""
        return {
            "score": 75,  # Simplified
            "factors": ["Experienced team", "Industry knowledge"]
        }
    
    def _assess_business_operations(self, company_details: Dict[str, Any]) -> Dict[str, Any]:
        """Assess business operations."""
        return {
            "score": 70,  # Simplified  
            "factors": ["Established operations", "Market presence"]
        }
    
    def _assess_industry_position(self, company_details: Dict[str, Any]) -> Dict[str, Any]:
        """Assess industry position."""
        return {
            "score": 65,  # Simplified
            "factors": ["Market position", "Competitive advantages"]
        }
    
    def _calculate_quantitative_score(self, historical_analysis: Dict[str, Any]) -> float:
        """Calculate quantitative credit score."""
        if not historical_analysis or not historical_analysis.get("ratio_analysis"):
            return 50  # Default score
        
        latest_ratios = historical_analysis["ratio_analysis"][-1]
        score = 50  # Base score
        
        # Liquidity
        current_ratio = latest_ratios.get("liquidity_ratios", {}).get("current_ratio", 0)
        if current_ratio >= 1.5:
            score += 15
        elif current_ratio >= 1.0:
            score += 10
        
        # Profitability
        net_margin = latest_ratios.get("profitability_ratios", {}).get("net_margin", 0)
        if net_margin >= 0.1:
            score += 20
        elif net_margin >= 0.05:
            score += 10
        elif net_margin > 0:
            score += 5
        
        # Leverage
        debt_to_equity = latest_ratios.get("leverage_ratios", {}).get("debt_to_equity", float('inf'))
        if debt_to_equity <= 0.5:
            score += 15
        elif debt_to_equity <= 1.0:
            score += 10
        elif debt_to_equity <= 2.0:
            score += 5
        
        return min(score, 100)
    
    def _identify_quantitative_risk_factors(self, historical_analysis: Dict[str, Any]) -> List[str]:
        """Identify quantitative risk factors."""
        risk_factors = []
        
        if not historical_analysis or not historical_analysis.get("ratio_analysis"):
            return ["Insufficient financial data"]
        
        latest_ratios = historical_analysis["ratio_analysis"][-1]
        
        # Check various risk factors
        current_ratio = latest_ratios.get("liquidity_ratios", {}).get("current_ratio", 0)
        if current_ratio < 1.0:
            risk_factors.append("Liquidity concern - current ratio below 1.0")
        
        net_margin = latest_ratios.get("profitability_ratios", {}).get("net_margin", 0)
        if net_margin < 0:
            risk_factors.append("Profitability concern - negative net margin")
        
        debt_to_equity = latest_ratios.get("leverage_ratios", {}).get("debt_to_equity", 0)
        if debt_to_equity > 2.0:
            risk_factors.append("High leverage - debt-to-equity ratio above 2.0")
        
        return risk_factors
    
    def _determine_risk_rating(self, composite_score: float) -> str:
        """Determine risk rating based on composite score."""
        if composite_score >= 80:
            return "Low Risk"
        elif composite_score >= 60:
            return "Medium Risk"
        else:
            return "High Risk"
    
    def _generate_decision_rationale(self, qca_score: float, quant_score: float, financial_health: float) -> str:
        """Generate decision rationale text."""
        return f"Decision based on composite analysis: QCA Score: {qca_score:.1f}, Quantitative Score: {quant_score:.1f}, Financial Health: {financial_health:.1f}. Overall assessment considers business strength, financial performance, and risk factors."
    
    def _extract_key_decision_factors(self, workflow_state: WorkflowState) -> List[str]:
        """Extract key factors that influenced the decision."""
        factors = []
        
        # From QCA
        qca_score = workflow_state.qca_assessment.get("overall_qca_score", 0)
        if qca_score >= 70:
            factors.append("Strong qualitative business assessment")
        elif qca_score < 50:
            factors.append("Weak qualitative business factors")
        
        # From quantitative analysis
        quant_score = workflow_state.quantitative_assessment.get("quantitative_score", 0)
        if quant_score >= 70:
            factors.append("Strong financial ratios and performance")
        elif quant_score < 50:
            factors.append("Weak financial performance indicators")
        
        # From financial health
        health_score = workflow_state.quantitative_assessment.get("financial_health_score", 0)
        if health_score >= 70:
            factors.append("Good overall financial health")
        elif health_score < 50:
            factors.append("Poor financial health indicators")
        
        return factors[:5]  # Return top 5 factors 