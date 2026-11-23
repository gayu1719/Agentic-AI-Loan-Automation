"""Real-time data integration for enhanced decision accuracy."""
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from dataclasses import dataclass


@dataclass
class MarketData:
    """Market data structure."""
    timestamp: datetime
    industry_index: float
    credit_spread: float
    interest_rate: float
    volatility: float
    economic_indicators: Dict[str, float]


class RealTimeDataIntegrator:
    """Integrate real-time market and economic data."""
    
    def __init__(self):
        self.data_sources = {
            'market_data': 'https://api.marketdata.com/v1',
            'credit_ratings': 'https://api.sp.com/ratings',
            'economic_data': 'https://api.fred.stlouisfed.org/series',
            'industry_trends': 'https://api.industry-analytics.com/v2'
        }
        
    async def get_real_time_market_context(
        self, 
        industry: str, 
        company_size: str = "medium"
    ) -> Dict[str, Any]:
        """Fetch real-time market context for better decision making."""
        
        # Parallel API calls for efficiency
        tasks = [
            self._fetch_industry_trends(industry),
            self._fetch_credit_market_conditions(),
            self._fetch_economic_indicators(),
            self._fetch_peer_performance(industry, company_size)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            'industry_trends': results[0] if not isinstance(results[0], Exception) else {},
            'credit_market': results[1] if not isinstance(results[1], Exception) else {},
            'economic_indicators': results[2] if not isinstance(results[2], Exception) else {},
            'peer_performance': results[3] if not isinstance(results[3], Exception) else {},
            'context_timestamp': datetime.now().isoformat(),
            'market_sentiment': self._analyze_market_sentiment(results)
        }
    
    async def _fetch_industry_trends(self, industry: str) -> Dict[str, Any]:
        """Fetch industry-specific trends and outlook."""
        # Simulated API call - replace with actual API integration
        await asyncio.sleep(0.1)  # Simulate API latency
        
        # Industry trend simulation
        industry_data = {
            'technology': {
                'growth_forecast': 0.15,
                'risk_level': 'medium',
                'funding_availability': 'high',
                'market_saturation': 0.6,
                'disruption_risk': 0.3
            },
            'manufacturing': {
                'growth_forecast': 0.05,
                'risk_level': 'high',
                'funding_availability': 'medium',
                'market_saturation': 0.8,
                'disruption_risk': 0.2
            },
            'healthcare': {
                'growth_forecast': 0.12,
                'risk_level': 'low',
                'funding_availability': 'high',
                'market_saturation': 0.4,
                'disruption_risk': 0.1
            }
        }
        
        return industry_data.get(industry.lower(), industry_data['manufacturing'])
    
    async def _fetch_credit_market_conditions(self) -> Dict[str, Any]:
        """Fetch current credit market conditions."""
        await asyncio.sleep(0.1)
        
        return {
            'credit_spread_10y': 1.85,  # 10-year credit spread
            'high_yield_spread': 4.2,
            'investment_grade_spread': 1.1,
            'credit_availability': 'tight',
            'default_rate_trend': 'increasing',
            'lender_sentiment': 'cautious'
        }
    
    async def _fetch_economic_indicators(self) -> Dict[str, Any]:
        """Fetch key economic indicators."""
        await asyncio.sleep(0.1)
        
        return {
            'gdp_growth': 2.1,
            'unemployment_rate': 3.8,
            'inflation_rate': 3.2,
            'fed_funds_rate': 5.25,
            'consumer_confidence': 102.3,
            'business_investment': 1.8,
            'economic_cycle_stage': 'late_expansion'
        }
    
    async def _fetch_peer_performance(
        self, 
        industry: str, 
        company_size: str
    ) -> Dict[str, Any]:
        """Fetch peer company performance data."""
        await asyncio.sleep(0.1)
        
        return {
            'peer_default_rate': 0.025,  # 2.5%
            'peer_avg_revenue_growth': 0.08,
            'peer_avg_margin': 0.12,
            'peer_avg_debt_ratio': 0.45,
            'peer_funding_success_rate': 0.78,
            'industry_consolidation_trend': 'increasing'
        }
    
    def _analyze_market_sentiment(self, api_results: List[Any]) -> str:
        """Analyze overall market sentiment from API results."""
        
        # Simple sentiment analysis based on fetched data
        positive_signals = 0
        negative_signals = 0
        
        for result in api_results:
            if isinstance(result, dict):
                # Check for positive indicators
                if result.get('growth_forecast', 0) > 0.1:
                    positive_signals += 1
                if result.get('funding_availability') == 'high':
                    positive_signals += 1
                if result.get('gdp_growth', 0) > 2.0:
                    positive_signals += 1
                
                # Check for negative indicators
                if result.get('risk_level') == 'high':
                    negative_signals += 1
                if result.get('default_rate_trend') == 'increasing':
                    negative_signals += 1
                if result.get('credit_availability') == 'tight':
                    negative_signals += 1
        
        if positive_signals > negative_signals:
            return 'bullish'
        elif negative_signals > positive_signals:
            return 'bearish'
        else:
            return 'neutral'


class LiveRiskMonitoring:
    """Real-time risk monitoring system."""
    
    def __init__(self):
        self.risk_thresholds = {
            'credit_spread_increase': 0.5,  # 50 bps
            'industry_default_rate': 0.05,  # 5%
            'economic_downturn_indicator': -1.0,
            'peer_performance_decline': -0.2  # 20%
        }
        
    async def monitor_portfolio_risks(
        self, 
        loan_portfolio: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Monitor real-time risks across loan portfolio."""
        
        risk_alerts = []
        portfolio_health = {}
        
        # Aggregate portfolio exposure
        industry_exposure = self._calculate_industry_exposure(loan_portfolio)
        size_exposure = self._calculate_size_exposure(loan_portfolio)
        
        # Monitor each risk dimension
        market_risks = await self._monitor_market_risks(industry_exposure)
        credit_risks = await self._monitor_credit_risks(loan_portfolio)
        concentration_risks = self._monitor_concentration_risks(industry_exposure, size_exposure)
        
        # Generate alerts
        all_risks = [market_risks, credit_risks, concentration_risks]
        for risk_category in all_risks:
            risk_alerts.extend(risk_category.get('alerts', []))
        
        portfolio_health = {
            'overall_risk_score': self._calculate_portfolio_risk_score(all_risks),
            'risk_distribution': {
                'market_risk': market_risks.get('score', 0),
                'credit_risk': credit_risks.get('score', 0),
                'concentration_risk': concentration_risks.get('score', 0)
            },
            'alerts': risk_alerts,
            'recommendations': self._generate_risk_recommendations(all_risks)
        }
        
        return portfolio_health
    
    def _calculate_industry_exposure(
        self, 
        portfolio: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate industry exposure percentages."""
        
        total_exposure = sum(loan.get('amount', 0) for loan in portfolio)
        industry_exposure = {}
        
        for loan in portfolio:
            industry = loan.get('industry', 'unknown')
            amount = loan.get('amount', 0)
            
            if industry not in industry_exposure:
                industry_exposure[industry] = 0
            industry_exposure[industry] += amount
        
        # Convert to percentages
        for industry in industry_exposure:
            industry_exposure[industry] = industry_exposure[industry] / total_exposure
        
        return industry_exposure
    
    def _calculate_size_exposure(
        self, 
        portfolio: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate exposure by company size."""
        
        total_exposure = sum(loan.get('amount', 0) for loan in portfolio)
        size_buckets = {'small': 0.0, 'medium': 0.0, 'large': 0.0}
        
        for loan in portfolio:
            size = loan.get('company_size', 'medium')
            amount = loan.get('amount', 0)
            
            if size in size_buckets:
                size_buckets[size] += amount
        
        # Convert to percentages
        for size in size_buckets:
            size_buckets[size] = size_buckets[size] / total_exposure if total_exposure > 0 else 0.0
        
        return size_buckets
    
    async def _monitor_market_risks(
        self, 
        industry_exposure: Dict[str, float]
    ) -> Dict[str, Any]:
        """Monitor market-level risks."""
        
        integrator = RealTimeDataIntegrator()
        alerts = []
        risk_score = 0
        
        for industry, exposure in industry_exposure.items():
            if exposure > 0.1:  # Monitor industries with >10% exposure
                market_data = await integrator.get_real_time_market_context(industry)
                
                # Check for risk triggers
                industry_trends = market_data.get('industry_trends', {})
                if industry_trends.get('growth_forecast', 0) < -0.05:  # -5% growth
                    alerts.append({
                        'type': 'market_risk',
                        'severity': 'high',
                        'message': f"{industry} industry showing negative growth forecast",
                        'exposure': exposure
                    })
                    risk_score += exposure * 10  # Weight by exposure
        
        return {
            'score': min(risk_score, 10),  # Cap at 10
            'alerts': alerts,
            'market_conditions': 'deteriorating' if risk_score > 5 else 'stable'
        }
    
    async def _monitor_credit_risks(
        self, 
        portfolio: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Monitor credit-level risks."""
        
        alerts = []
        risk_score = 0
        
        high_risk_loans = [
            loan for loan in portfolio 
            if loan.get('credit_score', 700) < 600
        ]
        
        if len(high_risk_loans) / len(portfolio) > 0.2:  # >20% high-risk
            alerts.append({
                'type': 'credit_risk',
                'severity': 'medium',
                'message': f"{len(high_risk_loans)} loans have credit scores below 600",
                'percentage': len(high_risk_loans) / len(portfolio)
            })
            risk_score += 5
        
        return {
            'score': risk_score,
            'alerts': alerts,
            'high_risk_count': len(high_risk_loans)
        }
    
    def _monitor_concentration_risks(
        self, 
        industry_exposure: Dict[str, float],
        size_exposure: Dict[str, float]
    ) -> Dict[str, Any]:
        """Monitor concentration risks."""
        
        alerts = []
        risk_score = 0
        
        # Industry concentration
        max_industry_exposure = max(industry_exposure.values()) if industry_exposure else 0
        if max_industry_exposure > 0.4:  # >40% in single industry
            alerts.append({
                'type': 'concentration_risk',
                'severity': 'high',
                'message': f"High concentration in single industry: {max_industry_exposure:.1%}",
                'exposure': max_industry_exposure
            })
            risk_score += 7
        
        # Size concentration
        if size_exposure.get('small', 0) > 0.6:  # >60% small companies
            alerts.append({
                'type': 'concentration_risk',
                'severity': 'medium',
                'message': f"High concentration in small companies: {size_exposure['small']:.1%}",
                'exposure': size_exposure['small']
            })
            risk_score += 4
        
        return {
            'score': risk_score,
            'alerts': alerts,
            'max_industry_exposure': max_industry_exposure
        }
    
    def _calculate_portfolio_risk_score(self, risk_categories: List[Dict[str, Any]]) -> float:
        """Calculate overall portfolio risk score."""
        
        total_score = sum(category.get('score', 0) for category in risk_categories)
        return min(total_score, 10)  # Cap at 10
    
    def _generate_risk_recommendations(
        self, 
        risk_categories: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate risk mitigation recommendations."""
        
        recommendations = []
        
        for category in risk_categories:
            alerts = category.get('alerts', [])
            for alert in alerts:
                if alert['type'] == 'concentration_risk':
                    recommendations.append("Consider diversifying portfolio across industries and company sizes")
                elif alert['type'] == 'market_risk':
                    recommendations.append(f"Monitor {alert.get('message', 'market conditions')} closely")
                elif alert['type'] == 'credit_risk':
                    recommendations.append("Review credit policies and consider tightening underwriting standards")
        
        return list(set(recommendations))  # Remove duplicates 