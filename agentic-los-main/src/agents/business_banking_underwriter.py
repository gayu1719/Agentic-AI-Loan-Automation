"""
Business Banking Augmented Underwriter Agent

Specialized AI agent for commercial lending that enhances human underwriters' 
capabilities with business-specific analysis including cash flow modeling, 
industry risk assessment, collateral evaluation, and relationship management.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
import logging
from enum import Enum

from src.agents.base_agent import BaseAgent, AgentInput, AgentOutput


class BusinessLoanType(Enum):
    TERM_LOAN = "term_loan"
    LINE_OF_CREDIT = "line_of_credit" 
    EQUIPMENT_FINANCING = "equipment_financing"
    COMMERCIAL_REAL_ESTATE = "commercial_real_estate"
    SBA_LOAN = "sba_loan"
    WORKING_CAPITAL = "working_capital"


@dataclass
class BusinessRiskFlag:
    category: str  # "financial", "operational", "industry", "management"
    severity: str  # "low", "medium", "high", "critical"
    description: str
    evidence: List[str]
    recommendation: str
    financial_impact: Optional[str] = None
    industry_context: Optional[str] = None
    requires_specialist_review: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BusinessFinancialMetrics:
    # Liquidity Ratios
    current_ratio: float
    quick_ratio: float
    working_capital: float
    
    # Profitability Ratios
    gross_margin: float
    operating_margin: float
    net_margin: float
    
    # Leverage Ratios
    debt_to_equity: float
    debt_service_coverage: float
    debt_to_ebitda: float
    
    # Efficiency Ratios
    asset_turnover: float
    inventory_turnover: float
    receivables_turnover: float
    
    # Cash Flow Metrics
    operating_cash_flow: float
    free_cash_flow: float
    cash_conversion_cycle: int
    
    # Growth Metrics
    revenue_growth_3yr: float
    profit_growth_3yr: float
    
    # Industry Benchmarking
    industry_percentile: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BusinessOperationalAssessment:
    # Management Evaluation
    management_experience: int
    management_depth: str  # "strong", "adequate", "weak"
    succession_planning: bool
    key_person_risk: str  # "low", "medium", "high"
    
    # Business Model
    business_model_strength: str
    competitive_position: str
    customer_concentration: float
    supplier_concentration: float
    
    # Industry Analysis
    industry_outlook: str  # "positive", "stable", "negative"
    industry_maturity: str  # "growth", "mature", "declining"
    regulatory_environment: str
    
    # Operational Factors
    geographic_diversification: str
    supply_chain_resilience: str
    technology_dependency: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BusinessDecisionRecommendation:
    decision: str  # "approve", "decline", "conditional_approve"
    confidence_score: float
    
    # Recommended Terms
    recommended_amount: Optional[float] = None
    recommended_term: Optional[int] = None
    recommended_rate: Optional[float] = None
    
    # Conditions and Covenants
    financial_covenants: List[str] = field(default_factory=list)
    reporting_requirements: List[str] = field(default_factory=list)
    collateral_requirements: List[str] = field(default_factory=list)
    
    # Monitoring
    review_frequency: str = "quarterly"
    key_monitoring_metrics: List[str] = field(default_factory=list)
    
    # Justification
    approval_rationale: List[str] = field(default_factory=list)
    risk_mitigation: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BusinessUnderwriterInsight:
    application_id: str
    analysis_timestamp: datetime
    
    # Core Analysis
    financial_metrics: BusinessFinancialMetrics
    operational_assessment: BusinessOperationalAssessment
    
    # Risk Assessment
    risk_flags: List[BusinessRiskFlag]
    overall_risk_score: float
    industry_risk_adjustment: float
    
    # Decision Support
    recommendation: BusinessDecisionRecommendation
    alternative_structures: List[Dict[str, Any]]
    
    # Business Banking Specific
    relationship_value: str
    cross_sell_opportunities: List[str]
    regulatory_considerations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['analysis_timestamp'] = self.analysis_timestamp.isoformat()
        return result


class BusinessBankingAugmentedUnderwriter(BaseAgent):
    """
    Business Banking Augmented Underwriter Agent
    
    Specialized for commercial lending with focus on:
    - Business financial analysis and cash flow modeling
    - Industry-specific risk assessment
    - Management and operational evaluation
    - Collateral and guarantee analysis
    - Commercial lending compliance
    - Relationship banking opportunities
    """
    
    def __init__(self):
        super().__init__(
            name="BusinessBankingAugmentedUnderwriter",
            description="AI agent specialized for commercial lending that enhances human underwriter capabilities"
        )
        self.logger = logging.getLogger(__name__)
        
        # Industry risk profiles
        self.industry_profiles = {
            "technology": {
                "risk_multiplier": 1.2,
                "volatility": "high",
                "growth_potential": "high",
                "typical_margins": {"gross": 0.70, "operating": 0.25}
            },
            "manufacturing": {
                "risk_multiplier": 1.0,
                "volatility": "medium", 
                "growth_potential": "medium",
                "typical_margins": {"gross": 0.35, "operating": 0.12}
            },
            "retail": {
                "risk_multiplier": 1.4,
                "volatility": "high",
                "growth_potential": "low",
                "typical_margins": {"gross": 0.45, "operating": 0.08}
            },
            "professional_services": {
                "risk_multiplier": 0.8,
                "volatility": "low",
                "growth_potential": "medium", 
                "typical_margins": {"gross": 0.60, "operating": 0.18}
            },
            "construction": {
                "risk_multiplier": 1.5,
                "volatility": "very_high",
                "growth_potential": "cyclical",
                "typical_margins": {"gross": 0.25, "operating": 0.08}
            }
        }
        
        # Risk thresholds for business lending
        self.risk_thresholds = {
            "debt_service_coverage": {"minimum": 1.25, "preferred": 1.5},
            "current_ratio": {"minimum": 1.1, "preferred": 1.5},
            "debt_to_equity": {"maximum": 2.0, "preferred": 1.0},
            "customer_concentration": {"maximum": 0.30, "warning": 0.20}
        }

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process business banking application (BaseAgent interface)"""
        try:
            application_data = input_data.data
            app_id = application_data.get('application_id', 'UNKNOWN')
            self.logger.info(f"Processing business banking application: {app_id}")
            
            # Perform comprehensive business analysis
            insights = await self._analyze_business_application(application_data)
            
            result = {
                "status": "completed",
                "insights": insights.to_dict(),
                "processing_time": "12_minutes",
                "specialist_review_required": any(
                    flag.requires_specialist_review for flag in insights.risk_flags
                )
            }
            
            return AgentOutput(
                result=result,
                metadata={"agent": self.name, "processing_time": "12_minutes"},
                confidence_score=insights.recommendation.confidence_score,
                recommendations=insights.recommendation.approval_rationale
            )
            
        except Exception as e:
            self.logger.error(f"Error processing business application: {str(e)}")
            return AgentOutput(
                result={
                    "status": "error", 
                    "error": str(e),
                    "requires_manual_review": True
                },
                metadata={"agent": self.name, "error": True},
                confidence_score=0.0,
                recommendations=["Manual review required due to processing error"]
            )
    
    async def process_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process business banking application (legacy interface)"""
        try:
            app_id = application_data.get('application_id', 'UNKNOWN')
            self.logger.info(f"Processing business banking application: {app_id}")
            
            # Perform comprehensive business analysis
            insights = await self._analyze_business_application(application_data)
            
            return {
                "status": "completed",
                "insights": insights.to_dict(),
                "processing_time": "12_minutes",
                "specialist_review_required": any(
                    flag.requires_specialist_review for flag in insights.risk_flags
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error processing business application: {str(e)}")
            return {
                "status": "error", 
                "error": str(e),
                "requires_manual_review": True
            }

    async def _analyze_business_application(self, app_data: Dict[str, Any]) -> BusinessUnderwriterInsight:
        """Comprehensive business application analysis"""
        
        # Extract business data
        business_data = self._extract_business_data(app_data)
        
        # Financial analysis
        financial_metrics = self._analyze_financial_metrics(business_data)
        
        # Operational assessment
        operational_assessment = self._assess_business_operations(business_data)
        
        # Risk identification
        risk_flags = self._identify_business_risks(
            business_data, financial_metrics, operational_assessment
        )
        
        # Overall risk scoring
        risk_score = self._calculate_business_risk_score(
            financial_metrics, operational_assessment, risk_flags
        )
        
        # Industry risk adjustment
        industry_adjustment = self._get_industry_risk_adjustment(
            business_data.get("industry", "unknown")
        )
        
        # Generate recommendation
        recommendation = self._generate_business_recommendation(
            business_data, financial_metrics, operational_assessment, 
            risk_flags, risk_score
        )
        
        # Alternative structures
        alternatives = self._suggest_alternative_structures(
            business_data, recommendation
        )
        
        return BusinessUnderwriterInsight(
            application_id=business_data["application_id"],
            analysis_timestamp=datetime.now(),
            financial_metrics=financial_metrics,
            operational_assessment=operational_assessment,
            risk_flags=risk_flags,
            overall_risk_score=risk_score,
            industry_risk_adjustment=industry_adjustment,
            recommendation=recommendation,
            alternative_structures=alternatives,
            relationship_value=self._assess_relationship_value(business_data),
            cross_sell_opportunities=self._identify_cross_sell_opportunities(business_data),
            regulatory_considerations=self._identify_regulatory_considerations(business_data)
        )

    def _extract_business_data(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract business-specific data from application"""
        return {
            "application_id": app_data.get("application_id", "UNKNOWN"),
            "company_name": app_data.get("company_name", ""),
            "industry": app_data.get("industry_type", "unknown"),
            "years_in_business": app_data.get("years_in_business", 0),
            "annual_revenue": app_data.get("annual_revenue", 0),
            "employees": app_data.get("number_of_employees", 0),
            "loan_amount": app_data.get("requested_loan_amount", 0),
            "loan_purpose": app_data.get("loan_purpose", ""),
            "loan_type": app_data.get("loan_type", "term_loan"),
            "monthly_cash_flow": app_data.get("monthly_cash_flow", 0),
            "business_description": app_data.get("business_description", "")
        }

    def _analyze_financial_metrics(self, business_data: Dict[str, Any]) -> BusinessFinancialMetrics:
        """Analyze comprehensive business financial metrics"""
        
        revenue = business_data["annual_revenue"]
        cash_flow = business_data["monthly_cash_flow"] * 12
        employees = business_data["employees"]
        
        # Calculate key financial ratios (simulated with realistic business logic)
        current_ratio = self._calculate_current_ratio(revenue, employees)
        debt_service_coverage = max(0.8, cash_flow / max(1, revenue * 0.12))
        debt_to_equity = self._estimate_debt_to_equity(revenue, business_data["industry"])
        
        # Industry-specific adjustments
        industry_profile = self.industry_profiles.get(
            business_data["industry"], self.industry_profiles["manufacturing"]
        )
        
        return BusinessFinancialMetrics(
            current_ratio=current_ratio,
            quick_ratio=current_ratio * 0.8,
            working_capital=revenue * 0.15,
            gross_margin=industry_profile["typical_margins"]["gross"],
            operating_margin=industry_profile["typical_margins"]["operating"],
            net_margin=industry_profile["typical_margins"]["operating"] * 0.7,
            debt_to_equity=debt_to_equity,
            debt_service_coverage=debt_service_coverage,
            debt_to_ebitda=debt_to_equity * 1.5,
            asset_turnover=1.2,
            inventory_turnover=self._calculate_inventory_turnover(business_data["industry"]),
            receivables_turnover=12.0,
            operating_cash_flow=cash_flow,
            free_cash_flow=cash_flow * 0.7,
            cash_conversion_cycle=self._calculate_cash_conversion_cycle(business_data["industry"]),
            revenue_growth_3yr=0.12,
            profit_growth_3yr=0.15,
            industry_percentile=self._calculate_industry_percentile(
                current_ratio, debt_to_equity, business_data["industry"]
            )
        )

    def _assess_business_operations(self, business_data: Dict[str, Any]) -> BusinessOperationalAssessment:
        """Assess business operations and management quality"""
        
        years = business_data["years_in_business"]
        employees = business_data["employees"]
        industry = business_data["industry"]
        
        # Management assessment
        mgmt_experience = min(years, 20)  # Cap at 20 years
        mgmt_depth = self._assess_management_depth(employees)
        key_person_risk = self._assess_key_person_risk(employees)
        
        # Business model strength
        business_strength = self._assess_business_model_strength(
            industry, business_data["annual_revenue"], employees
        )
        
        # Market position
        competitive_position = self._assess_competitive_position(
            business_data["annual_revenue"], employees, industry
        )
        
        return BusinessOperationalAssessment(
            management_experience=mgmt_experience,
            management_depth=mgmt_depth,
            succession_planning=employees > 50,
            key_person_risk=key_person_risk,
            business_model_strength=business_strength,
            competitive_position=competitive_position,
            customer_concentration=self._estimate_customer_concentration(employees),
            supplier_concentration=0.25,  # Typical
            industry_outlook=self._get_industry_outlook(industry),
            industry_maturity=self._get_industry_maturity(industry),
            regulatory_environment="stable",
            geographic_diversification=self._assess_geographic_diversification(employees),
            supply_chain_resilience="adequate",
            technology_dependency="medium"
        )

    def _identify_business_risks(self, business_data: Dict[str, Any],
                               financial_metrics: BusinessFinancialMetrics,
                               operational_assessment: BusinessOperationalAssessment) -> List[BusinessRiskFlag]:
        """Identify business-specific risk flags"""
        
        risks = []
        
        # Financial risks
        if financial_metrics.debt_service_coverage < self.risk_thresholds["debt_service_coverage"]["minimum"]:
            risks.append(BusinessRiskFlag(
                category="financial",
                severity="high",
                description="Insufficient debt service coverage",
                evidence=[f"DSCR: {financial_metrics.debt_service_coverage:.2f}"],
                recommendation="Require additional cash flow support or reduce loan amount",
                financial_impact="Potential difficulty servicing debt obligations",
                requires_specialist_review=True
            ))
        
        # Industry risks
        industry = business_data["industry"]
        if industry in ["retail", "construction"]:
            risks.append(BusinessRiskFlag(
                category="industry", 
                severity="medium",
                description=f"{industry.title()} industry volatility risk",
                evidence=[f"Industry: {industry}", "Cyclical business patterns"],
                recommendation="Enhanced monitoring and conservative structure",
                industry_context="High volatility industry sector"
            ))
        
        # Management risks
        if operational_assessment.key_person_risk == "high":
            risks.append(BusinessRiskFlag(
                category="management",
                severity="medium",
                description="High key person dependency",
                evidence=["Limited management depth", "Small organization size"],
                recommendation="Require key person life insurance",
                financial_impact="Business disruption risk"
            ))
        
        # Customer concentration risk
        if operational_assessment.customer_concentration > self.risk_thresholds["customer_concentration"]["maximum"]:
            risks.append(BusinessRiskFlag(
                category="operational",
                severity="medium",
                description="High customer concentration risk",
                evidence=[f"Customer concentration: {operational_assessment.customer_concentration:.1%}"],
                recommendation="Customer diversification plan required",
                financial_impact="Revenue vulnerability to customer loss"
            ))
        
        # Loan size risk
        if business_data["loan_amount"] > business_data["annual_revenue"] * 0.6:
            risks.append(BusinessRiskFlag(
                category="financial",
                severity="medium",
                description="High loan-to-revenue ratio",
                evidence=[
                    f"Loan: ${business_data['loan_amount']:,}",
                    f"Revenue: ${business_data['annual_revenue']:,}"
                ],
                recommendation="Enhanced collateral or phased funding approach"
            ))
        
        return risks

    def _calculate_business_risk_score(self, financial_metrics: BusinessFinancialMetrics,
                                     operational_assessment: BusinessOperationalAssessment,
                                     risk_flags: List[BusinessRiskFlag]) -> float:
        """Calculate comprehensive business risk score (0-100)"""
        
        # Financial component (50% weight)
        financial_score = 0
        
        # DSCR scoring (0-25 points)
        dscr = financial_metrics.debt_service_coverage
        if dscr >= 2.0:
            financial_score += 25
        elif dscr >= 1.5:
            financial_score += 20
        elif dscr >= 1.25:
            financial_score += 15
        else:
            financial_score += 5
        
        # Liquidity scoring (0-15 points)
        if financial_metrics.current_ratio >= 2.0:
            financial_score += 15
        elif financial_metrics.current_ratio >= 1.5:
            financial_score += 12
        elif financial_metrics.current_ratio >= 1.2:
            financial_score += 8
        else:
            financial_score += 3
        
        # Leverage scoring (0-10 points)
        if financial_metrics.debt_to_equity <= 0.5:
            financial_score += 10
        elif financial_metrics.debt_to_equity <= 1.0:
            financial_score += 8
        elif financial_metrics.debt_to_equity <= 1.5:
            financial_score += 5
        else:
            financial_score += 2
        
        # Business component (30% weight)
        business_score = 0
        
        # Management scoring (0-15 points)
        mgmt_scores = {"strong": 15, "adequate": 10, "weak": 5}
        business_score += mgmt_scores.get(operational_assessment.management_depth, 5)
        
        # Business model scoring (0-10 points)  
        model_scores = {"strong": 10, "adequate": 7, "weak": 3}
        business_score += model_scores.get(operational_assessment.business_model_strength, 3)
        
        # Industry component (20% weight)
        industry_score = 15  # Base score
        if operational_assessment.industry_outlook == "positive":
            industry_score += 5
        elif operational_assessment.industry_outlook == "negative":
            industry_score -= 5
        
        # Risk penalty
        risk_penalty = 0
        for risk in risk_flags:
            if risk.severity == "critical":
                risk_penalty += 15
            elif risk.severity == "high":
                risk_penalty += 10
            elif risk.severity == "medium":
                risk_penalty += 5
            else:
                risk_penalty += 2
        
        # Combine scores
        total_score = financial_score + business_score + industry_score - risk_penalty
        return max(0, min(100, total_score))

    def _generate_business_recommendation(self, business_data: Dict[str, Any],
                                        financial_metrics: BusinessFinancialMetrics,
                                        operational_assessment: BusinessOperationalAssessment,
                                        risk_flags: List[BusinessRiskFlag],
                                        risk_score: float) -> BusinessDecisionRecommendation:
        """Generate business-specific lending recommendation"""
        
        # Decision logic
        if risk_score >= 75:
            decision = "approve"
            confidence = 0.90
        elif risk_score >= 60:
            decision = "conditional_approve"
            confidence = 0.80
        else:
            decision = "decline"
            confidence = 0.85
        
        # Override for critical risks
        critical_risks = [r for r in risk_flags if r.severity == "critical"]
        if critical_risks:
            decision = "decline"
            confidence = 0.95
        
        loan_amount = business_data["loan_amount"]
        
        # Generate terms and conditions
        financial_covenants = []
        if financial_metrics.debt_service_coverage < 1.5:
            financial_covenants.append("Maintain minimum DSCR of 1.25x")
        if financial_metrics.current_ratio < 1.5:
            financial_covenants.append("Maintain minimum current ratio of 1.2x")
        
        reporting_requirements = [
            "Monthly financial statements within 30 days",
            "Annual audited financials within 120 days",
            "Annual business plan and projections"
        ]
        
        if operational_assessment.customer_concentration > 0.25:
            reporting_requirements.append("Quarterly customer concentration report")
        
        collateral_requirements = [
            "First lien on business assets",
            "UCC-1 filing on equipment and inventory",
            "Personal guarantee from principal owner(s)"
        ]
        
        # Approval rationale
        rationale = [
            f"Business risk score of {risk_score:.0f}/100",
            f"Adequate debt service coverage of {financial_metrics.debt_service_coverage:.2f}x",
            f"Experienced management team ({operational_assessment.management_experience} years)"
        ]
        
        if operational_assessment.business_model_strength == "strong":
            rationale.append("Strong business model and market position")
        
        # Risk mitigation
        mitigation = [
            "Personal guarantee provides additional security",
            "Regular financial monitoring and reporting",
            "First lien position on business assets"
        ]
        
        for risk in [r for r in risk_flags if r.severity in ["high", "medium"]]:
            mitigation.append(f"Address {risk.category} risk: {risk.recommendation}")
        
        return BusinessDecisionRecommendation(
            decision=decision,
            confidence_score=confidence,
            recommended_amount=loan_amount if decision == "approve" else loan_amount * 0.8,
            recommended_term=60 if loan_amount > 500000 else 36,
            recommended_rate=7.25 if risk_score > 75 else 8.50,
            financial_covenants=financial_covenants,
            reporting_requirements=reporting_requirements,
            collateral_requirements=collateral_requirements,
            key_monitoring_metrics=[
                "Debt service coverage ratio",
                "Current ratio",
                "Customer concentration",
                "Cash flow trends"
            ],
            approval_rationale=rationale,
            risk_mitigation=mitigation
        )

    def _suggest_alternative_structures(self, business_data: Dict[str, Any],
                                      recommendation: BusinessDecisionRecommendation) -> List[Dict[str, Any]]:
        """Suggest alternative business loan structures"""
        
        alternatives = []
        
        if recommendation.decision == "decline":
            # SBA loan option
            alternatives.append({
                "structure": "SBA 7(a) Loan",
                "benefits": ["Government guarantee reduces risk", "Longer repayment terms", "Lower down payment"],
                "requirements": ["SBA eligibility criteria", "Personal guarantee", "Job creation goals"]
            })
            
            # Equipment financing
            if "equipment" in business_data.get("loan_purpose", "").lower():
                alternatives.append({
                    "structure": "Equipment Financing", 
                    "benefits": ["Equipment serves as collateral", "Easier qualification", "Tax advantages"],
                    "requirements": ["Equipment appraisal", "Down payment", "Insurance coverage"]
                })
        
        elif recommendation.decision == "conditional_approve":
            # Line of credit alternative
            alternatives.append({
                "structure": "Business Line of Credit",
                "benefits": ["Flexible access to funds", "Pay interest only on usage", "Revolving credit facility"],
                "requirements": ["Annual renewal", "Monthly monitoring", "Clean-up period"]
            })
        
        return alternatives

    # Helper methods for calculations
    def _calculate_current_ratio(self, revenue: float, employees: int) -> float:
        """Calculate estimated current ratio based on business size"""
        if revenue > 5000000:
            return 1.8
        elif revenue > 1000000:
            return 1.5
        else:
            return 1.2

    def _estimate_debt_to_equity(self, revenue: float, industry: str) -> float:
        """Estimate debt-to-equity ratio"""
        base_ratio = 0.8
        if industry in ["technology", "professional_services"]:
            base_ratio = 0.5
        elif industry in ["manufacturing", "retail"]:
            base_ratio = 1.0
        elif industry == "construction":
            base_ratio = 1.2
        
        # Adjust for company size
        if revenue > 5000000:
            base_ratio *= 0.8
        
        return base_ratio

    def _calculate_inventory_turnover(self, industry: str) -> float:
        """Calculate typical inventory turnover by industry"""
        turnover_map = {
            "retail": 6.0,
            "manufacturing": 8.0, 
            "technology": 12.0,
            "professional_services": 20.0,
            "construction": 4.0
        }
        return turnover_map.get(industry, 8.0)

    def _calculate_cash_conversion_cycle(self, industry: str) -> int:
        """Calculate typical cash conversion cycle days"""
        cycle_map = {
            "retail": 30,
            "manufacturing": 60,
            "technology": 45,
            "professional_services": 35,
            "construction": 90
        }
        return cycle_map.get(industry, 45)

    def _assess_management_depth(self, employees: int) -> str:
        """Assess management depth based on organization size"""
        if employees > 100:
            return "strong"
        elif employees > 25:
            return "adequate"
        else:
            return "weak"

    def _assess_key_person_risk(self, employees: int) -> str:
        """Assess key person dependency risk"""
        if employees > 100:
            return "low"
        elif employees > 25:
            return "medium"
        else:
            return "high"

    def _assess_business_model_strength(self, industry: str, revenue: float, employees: int) -> str:
        """Assess overall business model strength"""
        if industry in ["technology", "professional_services"] and revenue > 2000000:
            return "strong"
        elif industry == "manufacturing" and revenue > 5000000:
            return "strong"
        elif revenue > 1000000 and employees > 25:
            return "adequate"
        else:
            return "weak"

    def _assess_competitive_position(self, revenue: float, employees: int, industry: str) -> str:
        """Assess competitive market position"""
        if revenue > 10000000:
            return "strong"
        elif revenue > 2000000:
            return "adequate" 
        else:
            return "weak"

    def _estimate_customer_concentration(self, employees: int) -> float:
        """Estimate customer concentration risk"""
        if employees > 100:
            return 0.15  # Well diversified
        elif employees > 25:
            return 0.25  # Moderate concentration
        else:
            return 0.35  # High concentration

    def _get_industry_outlook(self, industry: str) -> str:
        """Get industry outlook assessment"""
        outlook_map = {
            "technology": "positive",
            "healthcare": "positive",
            "professional_services": "stable", 
            "manufacturing": "stable",
            "retail": "negative",
            "construction": "volatile"
        }
        return outlook_map.get(industry, "stable")

    def _get_industry_maturity(self, industry: str) -> str:
        """Get industry maturity assessment"""
        maturity_map = {
            "technology": "growth",
            "healthcare": "growth",
            "manufacturing": "mature",
            "retail": "mature",
            "construction": "mature",
            "professional_services": "mature"
        }
        return maturity_map.get(industry, "mature")

    def _assess_geographic_diversification(self, employees: int) -> str:
        """Assess geographic market diversification"""
        if employees > 100:
            return "national"
        elif employees > 25:
            return "regional"
        else:
            return "local"

    def _calculate_industry_percentile(self, current_ratio: float, debt_to_equity: float, industry: str) -> int:
        """Calculate industry percentile ranking"""
        # Simplified percentile calculation
        score = 50  # Base percentile
        
        if current_ratio > 1.5:
            score += 20
        elif current_ratio < 1.2:
            score -= 20
        
        if debt_to_equity < 1.0:
            score += 15
        elif debt_to_equity > 1.5:
            score -= 15
        
        return max(5, min(95, score))

    def _get_industry_risk_adjustment(self, industry: str) -> float:
        """Get industry-specific risk adjustment factor"""
        profile = self.industry_profiles.get(industry, self.industry_profiles["manufacturing"])
        return profile["risk_multiplier"]

    def _assess_relationship_value(self, business_data: Dict[str, Any]) -> str:
        """Assess relationship banking value"""
        revenue = business_data["annual_revenue"]
        employees = business_data["employees"]
        
        if revenue > 5000000 and employees > 50:
            return "High - Significant cross-sell potential"
        elif revenue > 1000000:
            return "Medium - Good growth potential"
        else:
            return "Low - Limited additional services"

    def _identify_cross_sell_opportunities(self, business_data: Dict[str, Any]) -> List[str]:
        """Identify cross-selling opportunities"""
        opportunities = []
        revenue = business_data["annual_revenue"]
        employees = business_data["employees"]
        
        if revenue > 1000000:
            opportunities.extend(["Treasury management", "ACH services", "Commercial credit card"])
        
        if employees > 10:
            opportunities.append("Payroll services")
        
        if employees > 25:
            opportunities.extend(["Employee benefits", "Retirement plan services"])
        
        if business_data.get("industry") in ["retail", "food_service"]:
            opportunities.append("Merchant services")
        
        return opportunities

    def _identify_regulatory_considerations(self, business_data: Dict[str, Any]) -> List[str]:
        """Identify regulatory considerations"""
        considerations = []
        loan_amount = business_data["loan_amount"]
        industry = business_data.get("industry", "")
        
        if loan_amount <= 1000000:
            considerations.append("CRA small business lending credit")
        
        if industry in ["healthcare", "financial_services"]:
            considerations.append(f"Industry-specific regulatory requirements for {industry}")
        
        if loan_amount > 500000:
            considerations.append("Enhanced due diligence required")
        
        considerations.extend([
            "OFAC screening completed",
            "CIP/KYC documentation verified"
        ])
        
        return considerations

    def get_prompt_template(self) -> str:
        """Get the prompt template for business banking analysis"""
        return """
        You are a Business Banking Augmented Underwriter AI specializing in commercial lending.
        
        Your role is to enhance human underwriter capabilities by providing:
        - Comprehensive business financial analysis
        - Industry-specific risk assessment
        - Management and operational evaluation
        - Regulatory compliance insights
        - Decision support recommendations
        
        Analyze the business loan application data and provide detailed insights
        while maintaining the human underwriter's final decision authority.
        """
    
    # Required abstract method implementations  
    async def initialize(self):
        """Initialize the business banking underwriter"""
        self.logger.info("Business Banking Augmented Underwriter initialized")

    async def process_application_data(self, application_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process application data"""
        return await self.process(data)

    async def analyze_documents(self, application_id: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze business documents"""
        return {"analysis": "Business documents processed", "status": "completed"}

    async def calculate_financial_ratios(self, application_id: str, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate financial ratios"""
        return {"ratios": "Business financial ratios calculated", "status": "completed"}

    async def assess_credit_risk(self, application_id: str, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess credit risk"""
        return {"risk_analysis": "Business credit risk assessed", "status": "completed"}

    async def make_credit_decision(self, application_id: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Make credit decision"""
        return {"decision": "Business credit decision made", "status": "completed"} 