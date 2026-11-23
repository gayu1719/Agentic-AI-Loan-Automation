"""
Augmented Underwriter Agent - AI that enhances human underwriter capabilities

This agent empowers human underwriters with intelligent insights, automated data synthesis,
and risk identification while preserving human judgment for nuanced decisions.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import structlog

from ..utils.rag_system import RAGSystem
from .base_agent import BaseAgent

logger = structlog.get_logger()


class RiskLevel(Enum):
    """Risk level classifications"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionRecommendation(Enum):
    """Decision recommendations"""
    APPROVE = "approve"
    DECLINE = "decline"
    REFER_FOR_REVIEW = "refer_for_review" 
    APPROVE_WITH_CONDITIONS = "approve_with_conditions"


@dataclass
class RiskFlag:
    """Individual risk flag identified by the agent"""
    id: str
    category: str
    severity: RiskLevel
    title: str
    description: str
    data_source: str
    confidence: float
    policy_reference: Optional[str] = None
    raw_data: Optional[Dict] = None
    

@dataclass
class PolicyCheck:
    """Policy compliance check result"""
    policy_id: str
    policy_name: str
    status: str  # "compliant", "non_compliant", "warning"
    details: str
    data_points: List[str]


@dataclass
class DecisionJustification:
    """Complete justification for a decision recommendation"""
    recommendation: DecisionRecommendation
    confidence: float
    primary_factors: List[str]
    supporting_evidence: List[str]
    risk_mitigation: List[str]
    policy_alignment: List[PolicyCheck]
    data_sources: List[str]


@dataclass
class UnderwriterInsight:
    """Comprehensive insight package for underwriters"""
    application_id: str
    timestamp: datetime
    applicant_summary: Dict[str, Any]
    risk_flags: List[RiskFlag]
    risk_score: float
    decision_recommendation: DecisionJustification
    suggested_conditions: List[str]
    next_actions: List[str]
    audit_trail: List[Dict[str, Any]]


class AugmentedUnderwriterAgent(BaseAgent):
    """
    AI agent that augments human underwriter capabilities with:
    - Automated data synthesis
    - Risk identification and scoring
    - Policy compliance checking
    - Decision recommendations with full justifications
    - Audit trail maintenance
    """
    
    def __init__(self):
        super().__init__(
            name="augmented_underwriter",
            description="AI agent that enhances human underwriter capabilities with automated data synthesis, risk identification, and decision support"
        )
        self.rag_system = RAGSystem()
        self.risk_models = self._initialize_risk_models()
        self.policy_engine = self._initialize_policy_engine()
        
    def _initialize_risk_models(self) -> Dict[str, Any]:
        """Initialize risk assessment models"""
        return {
            "credit_risk": {
                "model_version": "v2.1",
                "features": ["debt_to_income", "credit_score", "payment_history", "employment_stability"],
                "weights": {"debt_to_income": 0.3, "credit_score": 0.4, "payment_history": 0.2, "employment_stability": 0.1}
            },
            "fraud_detection": {
                "model_version": "v1.8",
                "features": ["identity_verification", "behavioral_patterns", "document_authenticity"],
                "threshold": 0.7
            },
            "portfolio_risk": {
                "model_version": "v1.5",
                "concentration_limits": {"industry": 0.15, "geography": 0.25, "single_borrower": 0.05}
            }
        }
    
    def _initialize_policy_engine(self) -> Dict[str, Any]:
        """Initialize underwriting policy rules"""
        return {
            "eligibility_rules": {
                "min_credit_score": 650,
                "max_debt_to_income": 0.43,
                "min_employment_months": 24,
                "max_loan_to_value": 0.80
            },
            "approval_limits": {
                "auto_approve_threshold": 750,
                "manual_review_threshold": 600,
                "decline_threshold": 550
            },
            "documentation_requirements": {
                "income_verification": True,
                "employment_verification": True,
                "asset_verification": True,
                "identity_verification": True
            }
        }
    
    async def analyze_application(self, application_data: Dict[str, Any]) -> UnderwriterInsight:
        """
        Comprehensive application analysis providing actionable insights to underwriters
        
        Args:
            application_data: Complete application data including financials, documents, etc.
            
        Returns:
            UnderwriterInsight: Comprehensive analysis with recommendations and justifications
        """
        logger.info("Starting augmented underwriting analysis", application_id=application_data.get("application_id"))
        
        start_time = datetime.now()
        audit_events = []
        
        try:
            # Phase 1: Data Aggregation and Synthesis
            logger.info("Phase 1: Data aggregation and synthesis")
            applicant_summary = await self._synthesize_applicant_data(application_data)
            audit_events.append({
                "timestamp": datetime.now().isoformat(),
                "phase": "data_synthesis",
                "status": "completed",
                "details": "Successfully aggregated and normalized application data"
            })
            
            # Phase 2: Risk Identification and Flagging
            logger.info("Phase 2: Risk identification and flagging")
            risk_flags = await self._identify_risk_flags(application_data, applicant_summary)
            risk_score = self._calculate_composite_risk_score(risk_flags, applicant_summary)
            audit_events.append({
                "timestamp": datetime.now().isoformat(),
                "phase": "risk_analysis",
                "status": "completed",
                "details": f"Identified {len(risk_flags)} risk flags, composite score: {risk_score}"
            })
            
            # Phase 3: Policy Compliance Check
            logger.info("Phase 3: Policy compliance verification")
            policy_checks = await self._verify_policy_compliance(application_data, applicant_summary)
            audit_events.append({
                "timestamp": datetime.now().isoformat(),
                "phase": "policy_compliance",
                "status": "completed",
                "details": f"Completed {len(policy_checks)} policy checks"
            })
            
            # Phase 4: Decision Recommendation
            logger.info("Phase 4: Decision recommendation generation")
            decision_justification = await self._generate_decision_recommendation(
                applicant_summary, risk_flags, risk_score, policy_checks
            )
            audit_events.append({
                "timestamp": datetime.now().isoformat(),
                "phase": "decision_recommendation",
                "status": "completed",
                "details": f"Generated recommendation: {decision_justification.recommendation.value}"
            })
            
            # Phase 5: Conditions and Next Actions
            logger.info("Phase 5: Conditions and actions planning")
            suggested_conditions = self._generate_conditions(decision_justification, risk_flags)
            next_actions = self._determine_next_actions(decision_justification, risk_flags)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            insight = UnderwriterInsight(
                application_id=application_data.get("application_id", "unknown"),
                timestamp=datetime.now(),
                applicant_summary=applicant_summary,
                risk_flags=risk_flags,
                risk_score=risk_score,
                decision_recommendation=decision_justification,
                suggested_conditions=suggested_conditions,
                next_actions=next_actions,
                audit_trail=audit_events
            )
            
            logger.info(
                "Augmented underwriting analysis completed",
                application_id=application_data.get("application_id"),
                processing_time=processing_time,
                recommendation=decision_justification.recommendation.value,
                risk_score=risk_score
            )
            
            return insight
            
        except Exception as e:
            logger.error("Augmented underwriting analysis failed", error=str(e))
            audit_events.append({
                "timestamp": datetime.now().isoformat(),
                "phase": "error",
                "status": "failed",
                "details": f"Analysis failed: {str(e)}"
            })
            raise
    
    async def _synthesize_applicant_data(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize and normalize applicant data from multiple sources"""
        
        # Basic applicant information
        applicant_profile = {
            "personal_info": {
                "name": application_data.get("applicant_name", "Unknown"),
                "age": application_data.get("age"),
                "employment_status": application_data.get("employment_status"),
                "years_at_current_job": application_data.get("years_employed"),
                "annual_income": application_data.get("annual_income", 0)
            },
            "financial_profile": {
                "credit_score": application_data.get("credit_score", 0),
                "debt_to_income_ratio": self._calculate_debt_to_income(application_data),
                "monthly_obligations": application_data.get("monthly_debt_payments", 0),
                "liquid_assets": application_data.get("savings_balance", 0),
                "net_worth": self._calculate_net_worth(application_data)
            },
            "loan_details": {
                "requested_amount": application_data.get("requested_loan_amount", 0),
                "loan_purpose": application_data.get("loan_purpose"),
                "loan_to_value": self._calculate_loan_to_value(application_data),
                "term_months": application_data.get("preferred_term_months", 0)
            },
            "risk_indicators": {
                "bankruptcy_history": application_data.get("bankruptcy_history", False),
                "foreclosure_history": application_data.get("foreclosure_history", False),
                "late_payment_history": application_data.get("late_payments", 0),
                "account_delinquencies": application_data.get("delinquent_accounts", 0)
            }
        }
        
        # Enhanced data from external sources (simulated)
        applicant_profile["market_context"] = {
            "industry_outlook": "stable",
            "local_market_conditions": "favorable",
            "economic_indicators": "positive"
        }
        
        return applicant_profile
    
    async def _identify_risk_flags(self, application_data: Dict[str, Any], applicant_summary: Dict[str, Any]) -> List[RiskFlag]:
        """Identify potential risk flags in the application"""
        
        risk_flags = []
        
        # Credit Risk Flags
        credit_score = applicant_summary["financial_profile"]["credit_score"]
        if credit_score < 600:
            risk_flags.append(RiskFlag(
                id="credit_score_low",
                category="credit_risk",
                severity=RiskLevel.HIGH,
                title="Low Credit Score",
                description=f"Credit score of {credit_score} is below recommended threshold",
                data_source="credit_bureau",
                confidence=0.95,
                policy_reference="CR-001"
            ))
        elif credit_score < 650:
            risk_flags.append(RiskFlag(
                id="credit_score_moderate",
                category="credit_risk", 
                severity=RiskLevel.MEDIUM,
                title="Moderate Credit Score",
                description=f"Credit score of {credit_score} requires additional review",
                data_source="credit_bureau",
                confidence=0.85,
                policy_reference="CR-002"
            ))
        
        # Debt-to-Income Risk
        dti_ratio = applicant_summary["financial_profile"]["debt_to_income_ratio"]
        if dti_ratio > 0.43:
            risk_flags.append(RiskFlag(
                id="dti_high",
                category="financial_risk",
                severity=RiskLevel.HIGH,
                title="High Debt-to-Income Ratio",
                description=f"DTI ratio of {dti_ratio:.2%} exceeds policy maximum of 43%",
                data_source="financial_analysis",
                confidence=0.98,
                policy_reference="FR-001"
            ))
        elif dti_ratio > 0.36:
            risk_flags.append(RiskFlag(
                id="dti_elevated",
                category="financial_risk",
                severity=RiskLevel.MEDIUM,
                title="Elevated Debt-to-Income Ratio",
                description=f"DTI ratio of {dti_ratio:.2%} is elevated and warrants monitoring",
                data_source="financial_analysis",
                confidence=0.90,
                policy_reference="FR-002"
            ))
        
        # Employment Stability
        years_employed = applicant_summary["personal_info"]["years_at_current_job"]
        if years_employed and years_employed < 2:
            risk_flags.append(RiskFlag(
                id="employment_stability",
                category="employment_risk",
                severity=RiskLevel.MEDIUM,
                title="Limited Employment History",
                description=f"Only {years_employed} years at current position",
                data_source="employment_verification",
                confidence=0.80,
                policy_reference="ER-001"
            ))
        
        # Loan-to-Value Risk
        ltv_ratio = applicant_summary["loan_details"]["loan_to_value"]
        if ltv_ratio > 0.80:
            risk_flags.append(RiskFlag(
                id="ltv_high",
                category="collateral_risk",
                severity=RiskLevel.HIGH,
                title="High Loan-to-Value Ratio",
                description=f"LTV ratio of {ltv_ratio:.2%} exceeds policy maximum",
                data_source="property_valuation",
                confidence=0.95,
                policy_reference="COL-001"
            ))
        
        # Fraud Indicators
        if self._detect_potential_fraud(application_data):
            risk_flags.append(RiskFlag(
                id="fraud_indicators",
                category="fraud_risk",
                severity=RiskLevel.CRITICAL,
                title="Potential Fraud Indicators",
                description="Multiple fraud indicators detected requiring immediate review",
                data_source="fraud_detection_system",
                confidence=0.75,
                policy_reference="FRD-001"
            ))
            
        return risk_flags
    
    async def _verify_policy_compliance(self, application_data: Dict[str, Any], applicant_summary: Dict[str, Any]) -> List[PolicyCheck]:
        """Verify compliance with underwriting policies"""
        
        policy_checks = []
        
        # Minimum credit score check
        credit_score = applicant_summary["financial_profile"]["credit_score"]
        min_credit = self.policy_engine["eligibility_rules"]["min_credit_score"]
        
        if credit_score >= min_credit:
            policy_checks.append(PolicyCheck(
                policy_id="POL-001",
                policy_name="Minimum Credit Score",
                status="compliant",
                details=f"Credit score {credit_score} meets minimum requirement of {min_credit}",
                data_points=["credit_score"]
            ))
        else:
            policy_checks.append(PolicyCheck(
                policy_id="POL-001", 
                policy_name="Minimum Credit Score",
                status="non_compliant",
                details=f"Credit score {credit_score} below minimum requirement of {min_credit}",
                data_points=["credit_score"]
            ))
        
        # Maximum DTI check
        dti_ratio = applicant_summary["financial_profile"]["debt_to_income_ratio"]
        max_dti = self.policy_engine["eligibility_rules"]["max_debt_to_income"]
        
        if dti_ratio <= max_dti:
            policy_checks.append(PolicyCheck(
                policy_id="POL-002",
                policy_name="Maximum Debt-to-Income",
                status="compliant",
                details=f"DTI ratio {dti_ratio:.2%} within policy limit of {max_dti:.2%}",
                data_points=["debt_to_income_ratio"]
            ))
        else:
            policy_checks.append(PolicyCheck(
                policy_id="POL-002",
                policy_name="Maximum Debt-to-Income",
                status="non_compliant", 
                details=f"DTI ratio {dti_ratio:.2%} exceeds policy limit of {max_dti:.2%}",
                data_points=["debt_to_income_ratio"]
            ))
        
        # Documentation requirements
        required_docs = self.policy_engine["documentation_requirements"]
        missing_docs = []
        
        for doc_type, required in required_docs.items():
            if required and not application_data.get(f"{doc_type}_provided", False):
                missing_docs.append(doc_type)
        
        if not missing_docs:
            policy_checks.append(PolicyCheck(
                policy_id="POL-003",
                policy_name="Documentation Requirements",
                status="compliant",
                details="All required documentation provided",
                data_points=list(required_docs.keys())
            ))
        else:
            policy_checks.append(PolicyCheck(
                policy_id="POL-003",
                policy_name="Documentation Requirements", 
                status="non_compliant",
                details=f"Missing required documentation: {', '.join(missing_docs)}",
                data_points=missing_docs
            ))
            
        return policy_checks
    
    async def _generate_decision_recommendation(
        self, 
        applicant_summary: Dict[str, Any], 
        risk_flags: List[RiskFlag], 
        risk_score: float,
        policy_checks: List[PolicyCheck]
    ) -> DecisionJustification:
        """Generate decision recommendation with full justification"""
        
        # Determine base recommendation from risk score and policy compliance
        critical_flags = [flag for flag in risk_flags if flag.severity == RiskLevel.CRITICAL]
        high_risk_flags = [flag for flag in risk_flags if flag.severity == RiskLevel.HIGH]
        non_compliant_policies = [check for check in policy_checks if check.status == "non_compliant"]
        
        credit_score = applicant_summary["financial_profile"]["credit_score"]
        
        # Decision logic
        if critical_flags or len(non_compliant_policies) > 1:
            recommendation = DecisionRecommendation.DECLINE
            confidence = 0.90
        elif credit_score >= self.policy_engine["approval_limits"]["auto_approve_threshold"] and not high_risk_flags:
            recommendation = DecisionRecommendation.APPROVE
            confidence = 0.85
        elif credit_score <= self.policy_engine["approval_limits"]["decline_threshold"]:
            recommendation = DecisionRecommendation.DECLINE
            confidence = 0.80
        elif high_risk_flags or non_compliant_policies:
            recommendation = DecisionRecommendation.APPROVE_WITH_CONDITIONS
            confidence = 0.75
        else:
            recommendation = DecisionRecommendation.REFER_FOR_REVIEW
            confidence = 0.70
        
        # Build justification
        primary_factors = []
        supporting_evidence = []
        risk_mitigation = []
        
        if credit_score >= 750:
            primary_factors.append("Excellent credit score demonstrates strong creditworthiness")
        elif credit_score >= 650:
            primary_factors.append("Good credit score with acceptable risk profile")
        else:
            primary_factors.append("Credit score below preferred threshold increases risk")
        
        dti_ratio = applicant_summary["financial_profile"]["debt_to_income_ratio"] 
        if dti_ratio <= 0.36:
            supporting_evidence.append("Low debt-to-income ratio indicates strong repayment capacity")
        elif dti_ratio <= 0.43:
            supporting_evidence.append("Moderate debt-to-income ratio within acceptable range")
        else:
            primary_factors.append("High debt-to-income ratio indicates stretched finances")
        
        # Risk mitigation strategies
        if recommendation in [DecisionRecommendation.APPROVE_WITH_CONDITIONS, DecisionRecommendation.REFER_FOR_REVIEW]:
            if any(flag.category == "collateral_risk" for flag in risk_flags):
                risk_mitigation.append("Additional collateral or down payment required")
            if any(flag.category == "employment_risk" for flag in risk_flags):
                risk_mitigation.append("Employment verification and income documentation")
            if any(flag.category == "credit_risk" for flag in risk_flags):
                risk_mitigation.append("Credit enhancement or co-signer consideration")
        
        return DecisionJustification(
            recommendation=recommendation,
            confidence=confidence,
            primary_factors=primary_factors,
            supporting_evidence=supporting_evidence,
            risk_mitigation=risk_mitigation,
            policy_alignment=policy_checks,
            data_sources=["credit_bureau", "financial_analysis", "employment_verification", "property_valuation"]
        )
    
    def _generate_conditions(self, decision: DecisionJustification, risk_flags: List[RiskFlag]) -> List[str]:
        """Generate suggested conditions based on decision and risk factors"""
        
        conditions = []
        
        if decision.recommendation == DecisionRecommendation.APPROVE_WITH_CONDITIONS:
            
            # Collateral conditions
            if any(flag.category == "collateral_risk" for flag in risk_flags):
                conditions.append("Increase down payment to achieve maximum 75% loan-to-value ratio")
                conditions.append("Obtain updated property appraisal from approved appraiser")
            
            # Credit conditions
            credit_flags = [flag for flag in risk_flags if flag.category == "credit_risk"]
            if credit_flags:
                conditions.append("Provide explanation letter for credit score factors")
                if any("late_payment" in flag.id for flag in credit_flags):
                    conditions.append("Demonstrate 12 months of timely payments on all obligations")
            
            # Income/Employment conditions
            if any(flag.category == "employment_risk" for flag in risk_flags):
                conditions.append("Provide additional employment verification documentation")
                conditions.append("Submit most recent pay stubs and tax returns")
            
            # DTI conditions
            if any(flag.category == "financial_risk" for flag in risk_flags):
                conditions.append("Consider debt consolidation to improve debt-to-income ratio")
                conditions.append("Provide proof of additional income sources if applicable")
        
        return conditions
    
    def _determine_next_actions(self, decision: DecisionJustification, risk_flags: List[RiskFlag]) -> List[str]:
        """Determine recommended next actions for the underwriter"""
        
        actions = []
        
        if decision.recommendation == DecisionRecommendation.APPROVE:
            actions.extend([
                "Review automated analysis and approve if in agreement",
                "Generate approval letter with final terms",
                "Submit to loan processing team"
            ])
            
        elif decision.recommendation == DecisionRecommendation.DECLINE:
            actions.extend([
                "Review decline reasons for accuracy",
                "Generate adverse action notice with specific reasons",
                "Consider if applicant qualifies for alternative loan products"
            ])
            
        elif decision.recommendation == DecisionRecommendation.APPROVE_WITH_CONDITIONS:
            actions.extend([
                "Review suggested conditions and modify as needed",
                "Contact applicant to discuss conditional approval",
                "Schedule follow-up to review condition compliance"
            ])
            
        elif decision.recommendation == DecisionRecommendation.REFER_FOR_REVIEW:
            actions.extend([
                "Conduct detailed manual review of flagged items",
                "Consider requesting additional documentation",
                "Escalate to senior underwriter if needed",
                "Schedule applicant interview if warranted"
            ])
        
        # Add specific actions based on risk flags
        critical_flags = [flag for flag in risk_flags if flag.severity == RiskLevel.CRITICAL]
        if critical_flags:
            actions.append("Investigate critical risk flags immediately")
            
        fraud_flags = [flag for flag in risk_flags if flag.category == "fraud_risk"]  
        if fraud_flags:
            actions.append("Escalate to fraud investigation team")
            
        return actions
    
    # Helper methods
    def _calculate_debt_to_income(self, application_data: Dict[str, Any]) -> float:
        """Calculate debt-to-income ratio"""
        monthly_income = application_data.get("annual_income", 0) / 12
        monthly_debt = application_data.get("monthly_debt_payments", 0)
        
        if monthly_income <= 0:
            return 1.0  # Maximum DTI if no income reported
            
        return monthly_debt / monthly_income
    
    def _calculate_net_worth(self, application_data: Dict[str, Any]) -> float:
        """Calculate estimated net worth"""
        assets = application_data.get("total_assets", 0)
        liabilities = application_data.get("total_liabilities", 0)
        return assets - liabilities
    
    def _calculate_loan_to_value(self, application_data: Dict[str, Any]) -> float:
        """Calculate loan-to-value ratio"""
        loan_amount = application_data.get("requested_loan_amount", 0)
        property_value = application_data.get("property_value", 0)
        
        if property_value <= 0:
            return 1.0  # Maximum LTV if no property value
            
        return loan_amount / property_value
    
    def _calculate_composite_risk_score(self, risk_flags: List[RiskFlag], applicant_summary: Dict[str, Any]) -> float:
        """Calculate composite risk score from 0 (lowest risk) to 100 (highest risk)"""
        
        base_score = 50.0  # Neutral starting point
        
        # Adjust based on credit score
        credit_score = applicant_summary["financial_profile"]["credit_score"]
        if credit_score >= 750:
            base_score -= 20
        elif credit_score >= 700:
            base_score -= 10
        elif credit_score >= 650:
            base_score -= 5
        elif credit_score < 600:
            base_score += 25
        elif credit_score < 650:
            base_score += 15
        
        # Adjust based on risk flags
        for flag in risk_flags:
            if flag.severity == RiskLevel.CRITICAL:
                base_score += 25 * flag.confidence
            elif flag.severity == RiskLevel.HIGH:
                base_score += 15 * flag.confidence
            elif flag.severity == RiskLevel.MEDIUM:
                base_score += 8 * flag.confidence
            else:  # LOW
                base_score += 3 * flag.confidence
        
        # Adjust based on DTI
        dti_ratio = applicant_summary["financial_profile"]["debt_to_income_ratio"]
        if dti_ratio > 0.43:
            base_score += 20
        elif dti_ratio > 0.36:
            base_score += 10
        elif dti_ratio < 0.28:
            base_score -= 10
        
        # Ensure score is within bounds
        return max(0, min(100, base_score))
    
    def _detect_potential_fraud(self, application_data: Dict[str, Any]) -> bool:
        """Detect potential fraud indicators (simplified)"""
        
        fraud_indicators = 0
        
        # Check for suspicious patterns (simplified logic)
        if application_data.get("income_verification_method") == "unverified":
            fraud_indicators += 1
            
        if application_data.get("employment_verification") == "unverified":
            fraud_indicators += 1
            
        # Multiple recent credit inquiries
        if application_data.get("recent_credit_inquiries", 0) > 10:
            fraud_indicators += 1
            
        # Inconsistent information
        if self._detect_data_inconsistencies(application_data):
            fraud_indicators += 1
            
        return fraud_indicators >= 2
    
    def _detect_data_inconsistencies(self, application_data: Dict[str, Any]) -> bool:
        """Detect inconsistencies in application data"""
        
        # Example: Income vs employment type consistency
        income = application_data.get("annual_income", 0)
        employment_type = application_data.get("employment_type", "")
        
        if employment_type == "part_time" and income > 80000:
            return True
            
        if employment_type == "unemployed" and income > 0:
            return True
            
        return False

    async def get_human_override_interface(self, insight: UnderwriterInsight) -> Dict[str, Any]:
        """Provide interface for human underwriter to override recommendations"""
        
        return {
            "application_id": insight.application_id,
            "current_recommendation": insight.decision_recommendation.recommendation.value,
            "override_options": [
                {"value": "approve", "label": "Override to Approve", "requires_justification": True},
                {"value": "decline", "label": "Override to Decline", "requires_justification": True},
                {"value": "refer", "label": "Refer to Senior Underwriter", "requires_justification": False},
                {"value": "request_more_info", "label": "Request Additional Information", "requires_justification": False}
            ],
            "risk_flags_override": {
                "flags": [
                    {
                        "flag_id": flag.id,
                        "title": flag.title,
                        "can_override": flag.severity != RiskLevel.CRITICAL,
                        "override_reason_required": True
                    }
                    for flag in insight.risk_flags
                ]
            },
            "conditions_modification": {
                "current_conditions": insight.suggested_conditions,
                "can_add_conditions": True,
                "can_remove_conditions": True,
                "predefined_conditions": [
                    "Increase down payment to 25%",
                    "Require co-signer",
                    "Reduce loan amount by 10%",
                    "Shorter loan term (max 15 years)",
                    "Additional income verification"
                ]
            }
        }
    
    # Required abstract methods from BaseAgent
    async def process(self, input_data):
        """Process application data and return underwriter insights"""
        from .base_agent import AgentInput, AgentOutput
        
        # Handle both direct dict input and AgentInput
        if isinstance(input_data, dict):
            data = input_data
        else:
            data = input_data.data
            
        insight = await self.analyze_application(data)
        
        # Convert to AgentOutput format
        return AgentOutput(
            result={
                "agent_name": self.name,
                "insight": asdict(insight),
                "processing_time": (datetime.now() - insight.timestamp).total_seconds()
            },
            metadata={
                "risk_score": insight.risk_score,
                "recommendation": insight.decision_recommendation.recommendation.value,
                "flags_count": len(insight.risk_flags)
            },
            confidence_score=insight.decision_recommendation.confidence,
            recommendations=insight.next_actions
        )
    
    def get_prompt_template(self) -> str:
        """Get the prompt template for the augmented underwriter agent"""
        return """
        You are an AI-powered Augmented Underwriter Agent designed to enhance human underwriter capabilities.
        
        Your role is to:
        1. Synthesize and analyze application data from multiple sources
        2. Identify potential risk factors and policy compliance issues
        3. Provide clear, justified recommendations while preserving human judgment
        4. Maintain complete audit trails for all decisions
        
        Always provide transparent, explainable insights that empower human underwriters to make informed decisions.
        """ 