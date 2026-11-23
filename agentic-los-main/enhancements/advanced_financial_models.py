"""Advanced financial modeling capabilities for enhanced accuracy."""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from scipy import stats
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class AdvancedFinancialModels:
    """Advanced financial modeling and analysis."""
    
    def __init__(self):
        self.monte_carlo_iterations = 10000
        self.confidence_levels = [0.05, 0.25, 0.50, 0.75, 0.95]
        
    def monte_carlo_cash_flow_simulation(
        self, 
        base_projections: Dict[str, List[float]],
        volatility_params: Dict[str, float],
        correlation_matrix: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """Perform Monte Carlo simulation for cash flow projections."""
        
        revenues = np.array(base_projections['revenue'])
        n_periods = len(revenues)
        
        # Define uncertainty parameters
        revenue_vol = volatility_params.get('revenue_volatility', 0.15)
        margin_vol = volatility_params.get('margin_volatility', 0.10)
        expense_vol = volatility_params.get('expense_volatility', 0.08)
        
        results = {
            'revenue_scenarios': [],
            'cash_flow_scenarios': [],
            'probability_of_default': 0,
            'value_at_risk': {},
            'stress_test_results': {}
        }
        
        for iteration in range(self.monte_carlo_iterations):
            # Generate correlated random shocks
            shocks = np.random.multivariate_normal(
                mean=[0, 0, 0],
                cov=correlation_matrix or np.eye(3),
                size=n_periods
            )
            
            # Apply shocks to revenue, margins, and expenses
            revenue_scenario = revenues * (1 + shocks[:, 0] * revenue_vol)
            margin_multiplier = 1 + shocks[:, 1] * margin_vol
            expense_multiplier = 1 + shocks[:, 2] * expense_vol
            
            # Calculate cash flows
            base_margins = np.array(base_projections.get('margins', [0.15] * n_periods))
            margins = base_margins * margin_multiplier
            
            cash_flows = revenue_scenario * margins
            results['revenue_scenarios'].append(revenue_scenario)
            results['cash_flow_scenarios'].append(cash_flows)
        
        # Calculate statistics
        cf_array = np.array(results['cash_flow_scenarios'])
        results['percentiles'] = {
            f'p{int(p*100)}': np.percentile(cf_array, p*100, axis=0)
            for p in self.confidence_levels
        }
        
        # Calculate probability of negative cash flow
        negative_cf_prob = np.mean(cf_array < 0, axis=0)
        results['probability_of_default'] = np.max(negative_cf_prob)
        
        # Value at Risk calculations
        for confidence in [0.95, 0.99]:
            var_threshold = np.percentile(cf_array.sum(axis=1), (1-confidence)*100)
            results['value_at_risk'][f'VaR_{confidence}'] = var_threshold
        
        return results
    
    def industry_benchmarking_analysis(
        self, 
        company_ratios: Dict[str, float],
        industry: str,
        company_size: str = "medium"
    ) -> Dict[str, Any]:
        """Advanced industry benchmarking with peer analysis."""
        
        # Industry benchmark data (in production, this would come from external sources)
        industry_benchmarks = {
            'technology': {
                'current_ratio': {'p25': 1.8, 'p50': 2.4, 'p75': 3.2},
                'debt_to_equity': {'p25': 0.1, 'p50': 0.3, 'p75': 0.6},
                'roa': {'p25': 0.08, 'p50': 0.15, 'p75': 0.25},
                'revenue_growth': {'p25': 0.10, 'p50': 0.20, 'p75': 0.35}
            },
            'manufacturing': {
                'current_ratio': {'p25': 1.2, 'p50': 1.6, 'p75': 2.1},
                'debt_to_equity': {'p25': 0.4, 'p50': 0.8, 'p75': 1.2},
                'roa': {'p25': 0.04, 'p50': 0.08, 'p75': 0.15},
                'revenue_growth': {'p25': 0.03, 'p50': 0.08, 'p75': 0.15}
            }
        }
        
        benchmarks = industry_benchmarks.get(industry.lower(), industry_benchmarks['manufacturing'])
        
        analysis = {
            'industry': industry,
            'company_size': company_size,
            'ratio_rankings': {},
            'competitive_position': {},
            'outlier_flags': []
        }
        
        for ratio_name, company_value in company_ratios.items():
            if ratio_name in benchmarks:
                benchmark = benchmarks[ratio_name]
                
                # Calculate percentile ranking
                if company_value <= benchmark['p25']:
                    percentile = 25
                    position = "Bottom Quartile"
                elif company_value <= benchmark['p50']:
                    percentile = 50
                    position = "Below Median"
                elif company_value <= benchmark['p75']:
                    percentile = 75
                    position = "Above Median"
                else:
                    percentile = 90
                    position = "Top Quartile"
                
                analysis['ratio_rankings'][ratio_name] = {
                    'company_value': company_value,
                    'industry_median': benchmark['p50'],
                    'percentile_rank': percentile,
                    'competitive_position': position
                }
                
                # Flag outliers
                if (company_value > benchmark['p75'] * 2 or 
                    company_value < benchmark['p25'] * 0.5):
                    analysis['outlier_flags'].append(f"{ratio_name}: {position.lower()}")
        
        return analysis
    
    def advanced_credit_scoring_model(
        self, 
        financial_data: Dict[str, Any],
        qualitative_data: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """ML-based credit scoring with multiple data sources."""
        
        # Feature engineering
        features = self._engineer_credit_features(financial_data, qualitative_data, market_data)
        
        # Multiple model ensemble
        models = {
            'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
        }
        
        # In production, these would be pre-trained models
        # For demo, we'll simulate model predictions
        predictions = {}
        feature_importance = {}
        
        for model_name, model in models.items():
            # Simulate model prediction
            base_score = 650  # Base credit score
            
            # Adjust based on key features
            score_adjustments = 0
            
            if features.get('debt_to_equity', 0) > 1.0:
                score_adjustments -= 50
            if features.get('current_ratio', 0) > 1.5:
                score_adjustments += 30
            if features.get('revenue_growth', 0) > 0.15:
                score_adjustments += 40
            if features.get('years_in_business', 0) > 5:
                score_adjustments += 25
            
            final_score = max(300, min(850, base_score + score_adjustments))
            predictions[model_name] = final_score
            
            # Simulate feature importance
            feature_importance[model_name] = {
                'debt_to_equity': 0.25,
                'current_ratio': 0.20,
                'revenue_growth': 0.18,
                'years_in_business': 0.15,
                'industry_risk': 0.12,
                'management_quality': 0.10
            }
        
        # Ensemble prediction (weighted average)
        ensemble_score = float(np.mean(list(predictions.values())))
        
        # Calculate prediction confidence
        score_variance = np.var(list(predictions.values()))
        confidence = max(0.5, 1 - (score_variance / 10000))  # Normalize variance
        
        return {
            'ensemble_credit_score': ensemble_score,
            'individual_model_scores': predictions,
            'confidence_level': confidence,
            'feature_importance': feature_importance,
            'risk_grade': self._score_to_risk_grade(ensemble_score),
            'probability_of_default': self._score_to_pd(ensemble_score)
        }
    
    def stress_testing_framework(
        self, 
        base_financials: Dict[str, Any],
        stress_scenarios: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """Comprehensive stress testing framework."""
        
        default_scenarios = {
            'mild_recession': {
                'revenue_shock': -0.15,
                'margin_compression': -0.10,
                'credit_tightening': 0.02,  # Interest rate increase
                'ar_deterioration': 0.20    # Accounts receivable issues
            },
            'severe_recession': {
                'revenue_shock': -0.35,
                'margin_compression': -0.25,
                'credit_tightening': 0.05,
                'ar_deterioration': 0.40
            },
            'industry_disruption': {
                'revenue_shock': -0.50,
                'margin_compression': -0.30,
                'credit_tightening': 0.03,
                'ar_deterioration': 0.60
            }
        }
        
        # Use provided scenarios or defaults
        scenarios = stress_scenarios or default_scenarios
        
        stress_results = {}
        
        for scenario_name, shocks in scenarios.items():
            stressed_financials = base_financials.copy()
            
            # Apply revenue shock
            base_revenue = stressed_financials.get('revenue', 1000000)
            stressed_revenue = base_revenue * (1 + shocks['revenue_shock'])
            
            # Apply margin compression
            base_margin = stressed_financials.get('net_margin', 0.10)
            stressed_margin = base_margin * (1 + shocks['margin_compression'])
            
            # Calculate stressed cash flow
            stressed_cash_flow = stressed_revenue * stressed_margin
            
            # Apply working capital impacts
            base_current_ratio = stressed_financials.get('current_ratio', 1.5)
            ar_impact = shocks.get('ar_deterioration', 0)
            stressed_current_ratio = base_current_ratio * (1 - ar_impact * 0.3)
            
            stress_results[scenario_name] = {
                'stressed_revenue': stressed_revenue,
                'stressed_margin': stressed_margin,
                'stressed_cash_flow': stressed_cash_flow,
                'stressed_current_ratio': stressed_current_ratio,
                'cash_flow_decline_pct': (stressed_cash_flow - base_revenue * base_margin) / (base_revenue * base_margin) * 100,
                'survival_probability': self._calculate_survival_probability(stressed_cash_flow, stressed_financials),
                'recovery_time_estimate': self._estimate_recovery_time(shocks, base_financials)
            }
        
        return stress_results
    
    def _engineer_credit_features(
        self, 
        financial_data: Dict[str, Any],
        qualitative_data: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Engineer features for credit modeling."""
        
        features = {}
        
        # Financial ratios
        features['debt_to_equity'] = financial_data.get('debt_to_equity', 0)
        features['current_ratio'] = financial_data.get('current_ratio', 1)
        features['roa'] = financial_data.get('return_on_assets', 0)
        features['revenue_growth'] = financial_data.get('revenue_growth', 0)
        
        # Qualitative factors (convert to numeric)
        features['years_in_business'] = qualitative_data.get('years_in_business', 0)
        features['management_quality'] = qualitative_data.get('management_score', 50) / 100
        
        # Industry/market factors
        features['industry_risk'] = market_data.get('industry_risk_score', 50) / 100
        features['economic_cycle'] = market_data.get('economic_indicator', 0)
        
        return features
    
    def _score_to_risk_grade(self, score: float) -> str:
        """Convert credit score to risk grade."""
        if score >= 750:
            return "AAA"
        elif score >= 700:
            return "AA"
        elif score >= 650:
            return "A"
        elif score >= 600:
            return "BBB"
        elif score >= 550:
            return "BB"
        elif score >= 500:
            return "B"
        else:
            return "CCC"
    
    def _score_to_pd(self, score: float) -> float:
        """Convert credit score to probability of default."""
        # Simplified mapping (in practice, use historical data)
        if score >= 750:
            return 0.005   # 0.5%
        elif score >= 700:
            return 0.01    # 1%
        elif score >= 650:
            return 0.025   # 2.5%
        elif score >= 600:
            return 0.05    # 5%
        elif score >= 550:
            return 0.10    # 10%
        elif score >= 500:
            return 0.20    # 20%
        else:
            return 0.40    # 40%
    
    def _calculate_survival_probability(
        self, 
        stressed_cash_flow: float, 
        financials: Dict[str, Any]
    ) -> float:
        """Calculate probability of business survival under stress."""
        
        cash_reserves = financials.get('cash', 0)
        fixed_costs = financials.get('fixed_costs', stressed_cash_flow * 0.6)
        
        if stressed_cash_flow > 0:
            return min(0.95, 0.5 + (stressed_cash_flow / (fixed_costs * 2)))
        else:
            months_of_survival = cash_reserves / abs(fixed_costs) if fixed_costs > 0 else 0
            return max(0.05, months_of_survival / 24)  # 24 months = high survival
    
    def _estimate_recovery_time(
        self, 
        shocks: Dict[str, float], 
        base_financials: Dict[str, Any]
    ) -> int:
        """Estimate recovery time in months."""
        
        severity = abs(shocks.get('revenue_shock', 0))
        
        if severity < 0.10:
            return 6    # 6 months
        elif severity < 0.25:
            return 12   # 1 year
        elif severity < 0.40:
            return 24   # 2 years
        else:
            return 36   # 3+ years 