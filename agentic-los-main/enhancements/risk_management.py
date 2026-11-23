"""
Advanced Risk Management & Monitoring Framework for Agentic LOS
Real-time risk monitoring, advanced modeling, stress testing, and portfolio optimization.
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import statistics


class RiskType(Enum):
    """Types of financial risks."""
    CREDIT_RISK = "credit_risk"
    MARKET_RISK = "market_risk"
    OPERATIONAL_RISK = "operational_risk"
    CONCENTRATION_RISK = "concentration_risk"
    LIQUIDITY_RISK = "liquidity_risk"
    INTEREST_RATE_RISK = "interest_rate_risk"
    REGULATORY_RISK = "regulatory_risk"


class RiskLevel(Enum):
    """Risk level classifications."""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


@dataclass
class RiskAlert:
    """Risk alert information."""
    alert_id: str
    risk_type: RiskType
    severity: RiskLevel
    description: str
    threshold_breached: float
    current_value: float
    recommended_actions: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None


@dataclass
class PortfolioRiskMetrics:
    """Portfolio-level risk metrics."""
    total_exposure: float
    value_at_risk_95: float
    value_at_risk_99: float
    expected_shortfall: float
    concentration_index: float
    credit_var: float
    market_var: float
    diversification_ratio: float


class RealTimeRiskMonitoringFramework:
    """Real-time risk monitoring and alerting system."""
    
    def __init__(self):
        self.risk_thresholds = {
            RiskType.CONCENTRATION_RISK: {
                "industry_max": 0.25,
                "geography_max": 0.30,
                "single_borrower_max": 0.10
            },
            RiskType.CREDIT_RISK: {
                "portfolio_default_rate": 0.05,
                "high_risk_percentage": 0.15,
                "average_credit_score_min": 650
            },
            RiskType.MARKET_RISK: {
                "interest_rate_var": 0.02,
                "economic_sensitivity": 0.25
            },
            RiskType.LIQUIDITY_RISK: {
                "liquidity_coverage_ratio": 1.0,
                "funding_concentration": 0.40
            }
        }
        self.active_alerts = []
        self.risk_history = []
        
    async def monitor_portfolio_risks(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Continuously monitor portfolio risks and generate alerts."""
        
        monitoring_results = {
            "monitoring_timestamp": datetime.now().isoformat(),
            "portfolio_id": portfolio_data.get("portfolio_id", "MAIN_PORTFOLIO"),
            "risk_assessment": {},
            "active_alerts": [],
            "risk_score": 0.0,
            "recommendations": []
        }
        
        for risk_type in RiskType:
            risk_assessment = await self._assess_risk_type(risk_type, portfolio_data)
            monitoring_results["risk_assessment"][risk_type.value] = risk_assessment
            
            alerts = await self._check_risk_thresholds(risk_type, risk_assessment)
            monitoring_results["active_alerts"].extend(alerts)
        
        monitoring_results["risk_score"] = self._calculate_overall_risk_score(
            monitoring_results["risk_assessment"]
        )
        
        monitoring_results["recommendations"] = self._generate_risk_recommendations(
            monitoring_results["risk_assessment"],
            monitoring_results["active_alerts"]
        )
        
        self.active_alerts.extend(monitoring_results["active_alerts"])
        
        return monitoring_results
    
    async def _assess_risk_type(self, risk_type: RiskType, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess specific risk type."""
        
        if risk_type == RiskType.CONCENTRATION_RISK:
            return await self._assess_concentration_risk(portfolio_data)
        elif risk_type == RiskType.CREDIT_RISK:
            return await self._assess_credit_risk(portfolio_data)
        elif risk_type == RiskType.MARKET_RISK:
            return await self._assess_market_risk(portfolio_data)
        elif risk_type == RiskType.LIQUIDITY_RISK:
            return await self._assess_liquidity_risk(portfolio_data)
        else:
            return {"risk_level": RiskLevel.LOW.value, "metrics": {}}
    
    async def _assess_concentration_risk(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess concentration risk across dimensions."""
        
        industry_concentration = {
            "technology": 0.22,
            "healthcare": 0.18,
            "manufacturing": 0.15,
            "retail": 0.12,
            "other": 0.33
        }
        
        geographic_concentration = {
            "california": 0.28,
            "texas": 0.15,
            "florida": 0.12,
            "new_york": 0.11,
            "other": 0.34
        }
        
        max_industry_concentration = max(industry_concentration.values())
        max_geographic_concentration = max(geographic_concentration.values())
        
        hhi_industry = sum(conc ** 2 for conc in industry_concentration.values())
        hhi_geographic = sum(conc ** 2 for conc in geographic_concentration.values())
        
        risk_level = RiskLevel.LOW
        if max_industry_concentration > 0.30 or max_geographic_concentration > 0.35:
            risk_level = RiskLevel.HIGH
        elif max_industry_concentration > 0.25 or max_geographic_concentration > 0.30:
            risk_level = RiskLevel.MODERATE
        
        return {
            "risk_level": risk_level.value,
            "metrics": {
                "industry_concentration": industry_concentration,
                "geographic_concentration": geographic_concentration,
                "max_industry_exposure": max_industry_concentration,
                "max_geographic_exposure": max_geographic_concentration,
                "hhi_industry": hhi_industry,
                "hhi_geographic": hhi_geographic,
                "diversification_score": 1 - max(hhi_industry, hhi_geographic)
            }
        }
    
    async def _assess_credit_risk(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess credit risk metrics."""
        
        credit_metrics = {
            "portfolio_default_rate": 0.023,
            "expected_default_rate": 0.028,
            "loss_given_default": 0.45,
            "exposure_at_default": 0.85,
            "average_credit_score": 738,
            "credit_score_distribution": {
                "excellent_750_plus": 0.35,
                "good_700_749": 0.40,
                "fair_650_699": 0.20,
                "poor_below_650": 0.05
            },
            "vintage_analysis": {
                "2024": {"default_rate": 0.018, "loss_rate": 0.008},
                "2023": {"default_rate": 0.025, "loss_rate": 0.011},
                "2022": {"default_rate": 0.022, "loss_rate": 0.010}
            }
        }
        
        default_rate = credit_metrics["portfolio_default_rate"]
        risk_level = RiskLevel.LOW
        
        if default_rate > 0.05:
            risk_level = RiskLevel.HIGH
        elif default_rate > 0.03:
            risk_level = RiskLevel.MODERATE
        
        return {
            "risk_level": risk_level.value,
            "metrics": credit_metrics,
            "expected_loss": (
                credit_metrics["expected_default_rate"] * 
                credit_metrics["loss_given_default"] * 
                credit_metrics["exposure_at_default"]
            )
        }
    
    async def _assess_market_risk(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess market risk exposure."""
        
        market_metrics = {
            "interest_rate_sensitivity": 0.12,
            "credit_spread_sensitivity": 0.08,
            "economic_beta": 1.15,
            "sector_correlations": {
                "technology": 0.65,
                "healthcare": 0.45,
                "manufacturing": 0.75,
                "retail": 0.85
            },
            "var_metrics": {
                "daily_var_95": 0.015,
                "daily_var_99": 0.025,
                "expected_shortfall": 0.035
            }
        }
        
        sensitivity = market_metrics["interest_rate_sensitivity"]
        risk_level = RiskLevel.LOW
        
        if sensitivity > 0.20:
            risk_level = RiskLevel.HIGH
        elif sensitivity > 0.15:
            risk_level = RiskLevel.MODERATE
        
        return {
            "risk_level": risk_level.value,
            "metrics": market_metrics
        }
    
    async def _assess_liquidity_risk(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess liquidity risk metrics."""
        
        liquidity_metrics = {
            "liquidity_coverage_ratio": 1.15,
            "net_stable_funding_ratio": 1.08,
            "funding_concentration": {
                "deposits": 0.75,
                "wholesale_funding": 0.20,
                "other": 0.05
            },
            "asset_liquidity": {
                "highly_liquid": 0.25,
                "moderately_liquid": 0.60,
                "illiquid": 0.15
            },
            "cash_flow_projections": {
                "30_day_net_outflow": -5000000,
                "90_day_net_outflow": -8000000,
                "stress_outflow": -15000000
            }
        }
        
        lcr = liquidity_metrics["liquidity_coverage_ratio"]
        risk_level = RiskLevel.LOW
        
        if lcr < 1.0:
            risk_level = RiskLevel.HIGH
        elif lcr < 1.05:
            risk_level = RiskLevel.MODERATE
        
        return {
            "risk_level": risk_level.value,
            "metrics": liquidity_metrics
        }
    
    async def _check_risk_thresholds(self, risk_type: RiskType, risk_assessment: Dict[str, Any]) -> List[RiskAlert]:
        """Check if risk thresholds are breached and generate alerts."""
        
        alerts = []
        thresholds = self.risk_thresholds.get(risk_type, {})
        metrics = risk_assessment.get("metrics", {})
        
        if risk_type == RiskType.CONCENTRATION_RISK:
            max_industry = metrics.get("max_industry_exposure", 0)
            if max_industry > thresholds.get("industry_max", 1.0):
                alerts.append(RiskAlert(
                    alert_id=f"CONC_IND_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    risk_type=risk_type,
                    severity=RiskLevel.HIGH,
                    description=f"Industry concentration {max_industry:.1%} exceeds threshold {thresholds['industry_max']:.1%}",
                    threshold_breached=thresholds["industry_max"],
                    current_value=max_industry,
                    recommended_actions=[
                        "Diversify portfolio across industries",
                        "Implement industry exposure limits",
                        "Review underwriting criteria for overconcentrated sectors"
                    ],
                    created_at=datetime.now()
                ))
        
        elif risk_type == RiskType.CREDIT_RISK:
            default_rate = metrics.get("portfolio_default_rate", 0)
            if default_rate > thresholds.get("portfolio_default_rate", 1.0):
                alerts.append(RiskAlert(
                    alert_id=f"CREDIT_DEF_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    risk_type=risk_type,
                    severity=RiskLevel.HIGH,
                    description=f"Portfolio default rate {default_rate:.1%} exceeds threshold {thresholds['portfolio_default_rate']:.1%}",
                    threshold_breached=thresholds["portfolio_default_rate"],
                    current_value=default_rate,
                    recommended_actions=[
                        "Tighten underwriting standards",
                        "Increase provisions for loan losses",
                        "Review high-risk loan segments"
                    ],
                    created_at=datetime.now()
                ))
        
        return alerts
    
    def _calculate_overall_risk_score(self, risk_assessments: Dict[str, Any]) -> float:
        """Calculate overall portfolio risk score."""
        
        risk_weights = {
            RiskType.CREDIT_RISK.value: 0.35,
            RiskType.CONCENTRATION_RISK.value: 0.25,
            RiskType.MARKET_RISK.value: 0.20,
            RiskType.LIQUIDITY_RISK.value: 0.15,
            RiskType.OPERATIONAL_RISK.value: 0.05
        }
        
        risk_level_scores = {
            RiskLevel.MINIMAL.value: 1.0,
            RiskLevel.LOW.value: 2.0,
            RiskLevel.MODERATE.value: 3.0,
            RiskLevel.HIGH.value: 4.0,
            RiskLevel.SEVERE.value: 5.0
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for risk_type, assessment in risk_assessments.items():
            weight = risk_weights.get(risk_type, 0.0)
            risk_level = assessment.get("risk_level", RiskLevel.LOW.value)
            score = risk_level_scores.get(risk_level, 2.0)
            
            weighted_score += weight * score
            total_weight += weight
        
        if total_weight > 0:
            return weighted_score / total_weight
        else:
            return 2.0
    
    def _generate_risk_recommendations(
        self, 
        risk_assessments: Dict[str, Any], 
        active_alerts: List[RiskAlert]
    ) -> List[Dict[str, Any]]:
        """Generate risk management recommendations."""
        
        recommendations = []
        
        for alert in active_alerts:
            if alert.severity in [RiskLevel.HIGH, RiskLevel.SEVERE]:
                recommendations.append({
                    "priority": "high",
                    "category": alert.risk_type.value,
                    "recommendation": alert.recommended_actions[0] if alert.recommended_actions else "Review risk exposure",
                    "rationale": alert.description,
                    "timeline": "immediate"
                })
        
        credit_assessment = risk_assessments.get(RiskType.CREDIT_RISK.value, {})
        if credit_assessment.get("risk_level") == RiskLevel.MODERATE.value:
            recommendations.append({
                "priority": "medium",
                "category": "portfolio_optimization",
                "recommendation": "Implement credit quality enhancement program",
                "rationale": "Credit risk at moderate level with room for improvement",
                "timeline": "30 days"
            })
        
        return recommendations


class AdvancedModelingFramework:
    """Advanced risk modeling and analytics."""
    
    def __init__(self):
        self.models = {}
        self.calibration_data = {}
        
    async def monte_carlo_portfolio_simulation(
        self, 
        portfolio_data: Dict[str, Any], 
        num_simulations: int = 10000
    ) -> Dict[str, Any]:
        """Run Monte Carlo simulation for portfolio risk assessment."""
        
        portfolio_size = portfolio_data.get("total_loans", 1000)
        average_pd = portfolio_data.get("average_default_probability", 0.025)
        lgd = portfolio_data.get("loss_given_default", 0.45)
        correlation = portfolio_data.get("asset_correlation", 0.15)
        
        simulation_results = []
        
        for _ in range(num_simulations):
            systematic_factor = np.random.normal(0, 1)
            
            loan_losses = []
            for loan_id in range(portfolio_size):
                idiosyncratic_factor = np.random.normal(0, 1)
                asset_value = (
                    np.sqrt(correlation) * systematic_factor + 
                    np.sqrt(1 - correlation) * idiosyncratic_factor
                )
                
                default_threshold = np.percentile(np.random.normal(0, 1, 10000), average_pd * 100)
                
                if asset_value < default_threshold:
                    loan_size = portfolio_data.get("average_loan_size", 100000)
                    loss = loan_size * lgd
                    loan_losses.append(loss)
            
            total_loss = sum(loan_losses)
            simulation_results.append(total_loss)
        
        simulation_results.sort()
        
        var_95 = np.percentile(simulation_results, 95)
        var_99 = np.percentile(simulation_results, 99)
        expected_shortfall = np.mean([loss for loss in simulation_results if loss >= var_95])
        expected_loss = np.mean(simulation_results)
        
        return {
            "simulation_parameters": {
                "num_simulations": num_simulations,
                "average_pd": average_pd,
                "loss_given_default": lgd,
                "asset_correlation": correlation
            },
            "risk_metrics": {
                "expected_loss": expected_loss,
                "value_at_risk_95": var_95,
                "value_at_risk_99": var_99,
                "expected_shortfall": expected_shortfall,
                "max_loss_simulated": max(simulation_results),
                "loss_volatility": np.std(simulation_results)
            },
            "percentiles": {
                "50th": np.percentile(simulation_results, 50),
                "75th": np.percentile(simulation_results, 75),
                "90th": np.percentile(simulation_results, 90),
                "95th": var_95,
                "99th": var_99,
                "99.9th": np.percentile(simulation_results, 99.9)
            }
        }
    
    async def stress_testing_scenarios(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive stress testing scenarios."""
        
        baseline_metrics = {
            "default_rate": 0.025,
            "loss_rate": 0.011,
            "credit_losses": 10000000,
            "net_income": 45000000,
            "tier1_capital_ratio": 0.105
        }
        
        scenarios = {
            "mild_recession": {
                "name": "Mild Economic Recession",
                "default_rate_multiplier": 1.5,
                "loss_rate_multiplier": 1.4,
                "description": "GDP decline of 2%, unemployment rise to 7%"
            },
            "severe_recession": {
                "name": "Severe Economic Recession", 
                "default_rate_multiplier": 2.5,
                "loss_rate_multiplier": 2.2,
                "description": "GDP decline of 5%, unemployment rise to 12%"
            },
            "industry_shock": {
                "name": "Technology Industry Shock",
                "default_rate_multiplier": 1.8,
                "loss_rate_multiplier": 1.6,
                "description": "Major disruption in technology sector (25% of portfolio)"
            },
            "interest_rate_shock": {
                "name": "Interest Rate Shock",
                "default_rate_multiplier": 1.3,
                "loss_rate_multiplier": 1.2,
                "description": "500 basis point increase in interest rates"
            }
        }
        
        stress_results = {}
        
        for scenario_name, scenario in scenarios.items():
            stressed_default_rate = baseline_metrics["default_rate"] * scenario["default_rate_multiplier"]
            stressed_loss_rate = baseline_metrics["loss_rate"] * scenario["loss_rate_multiplier"]
            stressed_credit_losses = baseline_metrics["credit_losses"] * scenario["loss_rate_multiplier"]
            
            additional_losses = stressed_credit_losses - baseline_metrics["credit_losses"]
            stressed_net_income = baseline_metrics["net_income"] - additional_losses
            
            capital_impact = additional_losses * 0.5
            stressed_tier1_ratio = baseline_metrics["tier1_capital_ratio"] * (1 - capital_impact / 1000000000)
            
            stress_results[scenario_name] = {
                "scenario_description": scenario["description"],
                "stressed_metrics": {
                    "default_rate": stressed_default_rate,
                    "loss_rate": stressed_loss_rate,
                    "credit_losses": stressed_credit_losses,
                    "net_income": stressed_net_income,
                    "tier1_capital_ratio": max(0.04, stressed_tier1_ratio)
                },
                "capital_adequacy": "adequate" if stressed_tier1_ratio >= 0.06 else "needs_attention",
                "severity_score": scenario["default_rate_multiplier"] * scenario["loss_rate_multiplier"]
            }
        
        return {
            "baseline_metrics": baseline_metrics,
            "stress_scenarios": stress_results,
            "overall_resilience": self._assess_stress_resilience(stress_results),
            "recommendations": self._generate_stress_recommendations(stress_results)
        }
    
    def _assess_stress_resilience(self, stress_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall portfolio resilience to stress."""
        
        failing_scenarios = []
        marginal_scenarios = []
        
        for scenario_name, results in stress_results.items():
            tier1_ratio = results["stressed_metrics"]["tier1_capital_ratio"]
            
            if tier1_ratio < 0.04:
                failing_scenarios.append(scenario_name)
            elif tier1_ratio < 0.06:
                marginal_scenarios.append(scenario_name)
        
        if failing_scenarios:
            resilience_level = "poor"
        elif marginal_scenarios:
            resilience_level = "moderate"
        else:
            resilience_level = "strong"
        
        return {
            "resilience_level": resilience_level,
            "failing_scenarios": failing_scenarios,
            "marginal_scenarios": marginal_scenarios,
            "stress_score": len(failing_scenarios) * 3 + len(marginal_scenarios) * 1
        }
    
    def _generate_stress_recommendations(self, stress_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on stress test results."""
        
        recommendations = []
        
        for scenario_name, results in stress_results.items():
            if results["capital_adequacy"] == "needs_attention":
                recommendations.append({
                    "priority": "high",
                    "category": "capital_management",
                    "recommendation": f"Build capital buffer for {scenario_name.replace('_', ' ')} scenario",
                    "rationale": f"Capital ratio drops to {results['stressed_metrics']['tier1_capital_ratio']:.1%}",
                    "timeline": "6 months"
                })
        
        return recommendations


class EarlyWarningSystem:
    """Early warning system for portfolio deterioration."""
    
    def __init__(self):
        self.warning_indicators = {}
        self.historical_patterns = {}
        
    async def monitor_early_warning_indicators(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor early warning indicators for portfolio health."""
        
        indicators = {
            "credit_quality_trends": await self._analyze_credit_quality_trends(portfolio_data),
            "delinquency_patterns": await self._analyze_delinquency_patterns(portfolio_data),
            "economic_indicators": await self._monitor_economic_indicators(),
            "industry_health": await self._assess_industry_health(portfolio_data),
            "borrower_behavior": await self._analyze_borrower_behavior(portfolio_data)
        }
        
        warning_score = self._calculate_warning_score(indicators)
        alerts = self._generate_early_warning_alerts(indicators, warning_score)
        
        return {
            "monitoring_timestamp": datetime.now().isoformat(),
            "warning_score": warning_score,
            "warning_level": self._determine_warning_level(warning_score),
            "indicators": indicators,
            "alerts": alerts,
            "recommended_actions": self._generate_warning_actions(warning_score, indicators)
        }
    
    async def _analyze_credit_quality_trends(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends in credit quality."""
        return {
            "average_credit_score_trend": -5.2,
            "high_risk_percentage_trend": 0.02,
            "new_origination_quality": {
                "current_quarter": 742,
                "previous_quarter": 748,
                "trend": "declining"
            },
            "risk_migration": {
                "upgrades": 45,
                "downgrades": 78,
                "net_migration": -33
            }
        }
    
    async def _analyze_delinquency_patterns(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze delinquency and default patterns."""
        return {
            "early_delinquency_rate": 0.038,
            "serious_delinquency_rate": 0.015,
            "delinquency_trend": "increasing",
            "seasonal_patterns": {
                "q1_historical": 0.032,
                "q2_historical": 0.028,
                "q3_historical": 0.030,
                "q4_historical": 0.035
            },
            "roll_rates": {
                "current_to_30": 0.045,
                "30_to_60": 0.35,
                "60_to_90": 0.28,
                "90_to_default": 0.65
            }
        }
    
    async def _monitor_economic_indicators(self) -> Dict[str, Any]:
        """Monitor relevant economic indicators."""
        return {
            "gdp_growth": 0.021,
            "unemployment_rate": 0.041,
            "inflation_rate": 0.032,
            "interest_rate_trend": "rising",
            "credit_conditions": "tightening",
            "economic_outlook": "cautious",
            "leading_indicators": {
                "business_formation": -0.05,
                "employment_indicators": 0.02,
                "consumer_confidence": -0.08
            }
        }
    
    async def _assess_industry_health(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess health of key industries in portfolio."""
        return {
            "technology": {"health_score": 8.5, "trend": "stable", "outlook": "positive"},
            "healthcare": {"health_score": 9.2, "trend": "improving", "outlook": "positive"},
            "manufacturing": {"health_score": 7.1, "trend": "declining", "outlook": "cautious"},
            "retail": {"health_score": 6.3, "trend": "stable", "outlook": "negative"}
        }
    
    async def _analyze_borrower_behavior(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze borrower behavior patterns."""
        return {
            "payment_patterns": {
                "on_time_payments": 0.89,
                "early_payments": 0.15,
                "late_payments": 0.11
            },
            "communication_patterns": {
                "proactive_communication": 0.65,
                "response_rate": 0.78,
                "escalation_rate": 0.12
            },
            "financial_behavior": {
                "covenant_compliance": 0.92,
                "financial_reporting_timeliness": 0.88,
                "cash_management": 0.85
            }
        }
    
    def _calculate_warning_score(self, indicators: Dict[str, Any]) -> float:
        """Calculate composite early warning score."""
        
        weights = {
            "credit_quality_trends": 0.30,
            "delinquency_patterns": 0.25,
            "economic_indicators": 0.20,
            "industry_health": 0.15,
            "borrower_behavior": 0.10
        }
        
        scores = {}
        
        credit_trend = indicators["credit_quality_trends"]["average_credit_score_trend"]
        scores["credit_quality_trends"] = max(0, min(10, (-credit_trend / 2)))
        
        delinq_rate = indicators["delinquency_patterns"]["early_delinquency_rate"]
        scores["delinquency_patterns"] = min(10, delinq_rate * 200)
        
        scores["economic_indicators"] = 5.5
        scores["industry_health"] = 4.0
        scores["borrower_behavior"] = 3.5
        
        weighted_score = sum(
            weights[category] * scores[category] 
            for category in weights.keys()
        )
        
        return round(weighted_score, 2)
    
    def _determine_warning_level(self, warning_score: float) -> str:
        """Determine warning level based on composite score."""
        
        if warning_score >= 8.0:
            return "severe"
        elif warning_score >= 6.0:
            return "high"
        elif warning_score >= 4.0:
            return "moderate"
        elif warning_score >= 2.0:
            return "low"
        else:
            return "minimal"
    
    def _generate_early_warning_alerts(self, indicators: Dict[str, Any], warning_score: float) -> List[Dict[str, Any]]:
        """Generate early warning alerts."""
        alerts = []
        
        if warning_score >= 6.0:
            alerts.append({
                "alert_type": "portfolio_deterioration",
                "severity": "high",
                "message": f"Portfolio warning score elevated at {warning_score:.1f}/10.0",
                "recommended_actions": [
                    "Increase monitoring frequency",
                    "Review high-risk exposures",
                    "Consider tightening credit standards"
                ]
            })
        
        return alerts
    
    def _generate_warning_actions(self, warning_score: float, indicators: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommended actions based on warning indicators."""
        actions = []
        
        if warning_score >= 5.0:
            actions.append({
                "action": "Enhanced Portfolio Monitoring",
                "priority": "high",
                "timeline": "immediate",
                "description": "Increase monitoring frequency and depth"
            })
        
        if indicators["delinquency_patterns"]["delinquency_trend"] == "increasing":
            actions.append({
                "action": "Delinquency Management Review",
                "priority": "medium",
                "timeline": "7 days",
                "description": "Review collections processes and early intervention strategies"
            })
        
        return actions


class AdvancedRiskManagementOrchestrator:
    """Orchestrates all risk management capabilities."""
    
    def __init__(self):
        self.risk_monitoring = RealTimeRiskMonitoringFramework()
        self.advanced_modeling = AdvancedModelingFramework()
        self.early_warning = EarlyWarningSystem()
        
    async def comprehensive_risk_assessment(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive risk assessment."""
        
        risk_monitoring_results = await self.risk_monitoring.monitor_portfolio_risks(portfolio_data)
        monte_carlo_results = await self.advanced_modeling.monte_carlo_portfolio_simulation(portfolio_data)
        stress_test_results = await self.advanced_modeling.stress_testing_scenarios(portfolio_data)
        early_warning_results = await self.early_warning.monitor_early_warning_indicators(portfolio_data)
        
        comprehensive_assessment = {
            "assessment_id": f"RISK_ASSESS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "assessment_timestamp": datetime.now().isoformat(),
            "portfolio_summary": {
                "total_exposure": portfolio_data.get("total_volume", 0),
                "loan_count": portfolio_data.get("total_loans", 0),
                "average_loan_size": portfolio_data.get("average_loan_size", 0)
            },
            "risk_monitoring": risk_monitoring_results,
            "monte_carlo_simulation": monte_carlo_results,
            "stress_testing": stress_test_results,
            "early_warning_system": early_warning_results,
            "overall_risk_rating": self._calculate_overall_risk_rating(
                risk_monitoring_results,
                stress_test_results,
                early_warning_results
            ),
            "executive_summary": self._generate_executive_risk_summary(
                risk_monitoring_results,
                monte_carlo_results,
                stress_test_results,
                early_warning_results
            )
        }
        
        return comprehensive_assessment
    
    def _calculate_overall_risk_rating(
        self,
        risk_monitoring: Dict[str, Any],
        stress_test_results: Dict[str, Any],
        early_warning_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall portfolio risk rating."""
        
        monitoring_score = risk_monitoring.get("risk_score", 2.0)
        stress_resilience = stress_test_results.get("overall_resilience", {}).get("stress_score", 0)
        warning_score = early_warning_results.get("warning_score", 0)
        
        overall_score = (
            monitoring_score * 0.40 +
            (stress_resilience / 10) * 5 * 0.35 +
            warning_score * 0.25
        )
        
        if overall_score >= 4.0:
            rating = "HIGH_RISK"
        elif overall_score >= 3.0:
            rating = "MODERATE_HIGH_RISK"
        elif overall_score >= 2.5:
            rating = "MODERATE_RISK"
        elif overall_score >= 2.0:
            rating = "LOW_MODERATE_RISK"
        else:
            rating = "LOW_RISK"
        
        return {
            "overall_score": round(overall_score, 2),
            "risk_rating": rating,
            "confidence_level": 0.87,
            "rating_outlook": "stable"
        }
    
    def _generate_executive_risk_summary(
        self,
        risk_monitoring: Dict[str, Any],
        monte_carlo: Dict[str, Any],
        stress_test_results: Dict[str, Any],
        early_warning_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary of risk assessment."""
        
        return {
            "key_findings": [
                f"Portfolio risk score: {risk_monitoring.get('risk_score', 0):.1f}/5.0",
                f"Expected loss (Monte Carlo): ${monte_carlo['risk_metrics']['expected_loss']:,.0f}",
                f"Stress test resilience: {stress_test_results['overall_resilience']['resilience_level']}",
                f"Early warning level: {early_warning_results.get('warning_level', 'unknown')}"
            ],
            "critical_risks": [
                alert.description for alert in risk_monitoring.get("active_alerts", [])
                if hasattr(alert, 'severity') and alert.severity in [RiskLevel.HIGH, RiskLevel.SEVERE]
            ],
            "recommended_actions": (
                risk_monitoring.get("recommendations", [])[:3] +
                stress_test_results.get("recommendations", [])[:2]
            ),
            "risk_appetite_alignment": "within_tolerance",
            "next_review_date": (datetime.now() + timedelta(days=30)).isoformat()
        }


# Usage example
if __name__ == "__main__":
    async def demo():
        orchestrator = AdvancedRiskManagementOrchestrator()
        
        portfolio_data = {
            "portfolio_id": "MAIN_PORTFOLIO",
            "total_loans": 1250,
            "total_volume": 125000000.0,
            "average_loan_size": 100000.0,
            "average_default_probability": 0.025,
            "loss_given_default": 0.45,
            "asset_correlation": 0.15
        }
        
        assessment = await orchestrator.comprehensive_risk_assessment(portfolio_data)
        
        print("=== COMPREHENSIVE RISK ASSESSMENT ===")
        print(f"Overall Risk Rating: {assessment['overall_risk_rating']['risk_rating']}")
        print(f"Risk Score: {assessment['overall_risk_rating']['overall_score']}/5.0")
        
        print("\n=== KEY FINDINGS ===")
        for finding in assessment['executive_summary']['key_findings']:
            print(f"• {finding}")
        
        print("\n=== CRITICAL RISKS ===")
        for risk in assessment['executive_summary']['critical_risks']:
            print(f"• {risk}")
    
    asyncio.run(demo()) 