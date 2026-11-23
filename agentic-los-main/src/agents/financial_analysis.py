"""Financial analysis agents for historical analysis and projections."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .base_agent import BaseAgent, AgentInput, AgentOutput
from ..models.financial_statements import FinancialStatements, IncomeStatement, BalanceSheet, CashFlowStatement
from ..models.credit_assessment import FinancialRatios
from ..utils.financial_calculator import FinancialCalculator
from ..utils.rag_system import RAGSystem
import structlog

logger = structlog.get_logger()


class HistoricalFinancialAnalysisAgent(BaseAgent):
    """Agent for analyzing historical financial performance."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="Historical Financial Analysis Agent",
            description="Analyzes historical financial performance and calculates key ratios",
            **kwargs
        )
        self.calculator = FinancialCalculator()
        self.rag_system = RAGSystem()
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Analyze historical financial data."""
        try:
            financial_data = input_data.data.get("financial_statements", {})
            company_info = input_data.data.get("company_info", {})
            
            if not financial_data:
                raise ValueError("No financial statements provided")
            
            # Parse financial statements
            statements = self._parse_financial_statements(financial_data)
            
            # Calculate ratios for each period
            ratio_analysis = self._calculate_all_ratios(statements)
            
            # Perform trend analysis
            trend_analysis = self._analyze_trends(ratio_analysis)
            
            # Assess asset management
            asset_analysis = self._analyze_asset_management(statements)
            
            # Analyze profitability
            profitability_analysis = self._analyze_profitability(statements)
            
            # Cash flow analysis
            cash_flow_analysis = self._analyze_cash_flows(statements)
            
            # Get relevant guidelines
            guidelines = await self.rag_system.get_guidelines_for_category("financial_analysis")
            
            # Generate insights and recommendations
            insights = self._generate_financial_insights(
                ratio_analysis, trend_analysis, asset_analysis, 
                profitability_analysis, cash_flow_analysis
            )
            
            # Assess overall financial health
            health_score = self._assess_financial_health(ratio_analysis, trend_analysis)
            
            result = {
                "company_info": company_info,
                "analysis_period": self._get_analysis_period(statements),
                "ratio_analysis": ratio_analysis,
                "trend_analysis": trend_analysis,
                "asset_management": asset_analysis,
                "profitability_analysis": profitability_analysis,
                "cash_flow_analysis": cash_flow_analysis,
                "financial_health_score": health_score,
                "key_insights": insights,
                "guidelines_context": guidelines[:3] if guidelines else []
            }
            
            recommendations = self._generate_recommendations(
                ratio_analysis, trend_analysis, health_score
            )
            
            output = AgentOutput(
                result=result,
                metadata={
                    "analysis_date": datetime.now().isoformat(),
                    "periods_analyzed": len(statements.income_statements),
                    "analysis_type": "historical_financial"
                },
                confidence_score=min(health_score / 100.0, 1.0),
                recommendations=recommendations
            )
            
            await self._log_execution(input_data, output)
            return output
            
        except Exception as e:
            self.logger.error("Historical financial analysis failed", error=str(e))
            return AgentOutput(
                result={"error": str(e)},
                metadata={"error": True},
                confidence_score=0.0,
                recommendations=["Fix financial analysis error"]
            )
    
    def _parse_financial_statements(self, data: Dict[str, Any]) -> FinancialStatements:
        """Parse financial statements data."""
        try:
            return FinancialStatements(**data)
        except Exception as e:
            self.logger.error("Failed to parse financial statements", error=str(e))
            raise ValueError(f"Invalid financial statements format: {str(e)}")
    
    def _calculate_all_ratios(self, statements: FinancialStatements) -> List[Dict[str, Any]]:
        """Calculate financial ratios for all periods."""
        ratio_analysis = []
        
        for i, income_stmt in enumerate(statements.income_statements):
            try:
                balance_sheet = statements.balance_sheets[i] if i < len(statements.balance_sheets) else None
                cash_flow = statements.cash_flow_statements[i] if i < len(statements.cash_flow_statements) else None
                
                if not balance_sheet:
                    continue
                
                # Convert to dictionaries for calculator
                income_dict = income_stmt.dict()
                balance_dict = balance_sheet.dict()
                cash_flow_dict = cash_flow.dict() if cash_flow else {}
                
                # Calculate ratios
                liquidity = self.calculator.calculate_liquidity_ratios(balance_dict)
                leverage = self.calculator.calculate_leverage_ratios(balance_dict)
                profitability = self.calculator.calculate_profitability_ratios(income_dict, balance_dict)
                efficiency = self.calculator.calculate_efficiency_ratios(income_dict, balance_dict)
                cash_flow_ratios = self.calculator.calculate_cash_flow_ratios(
                    cash_flow_dict, balance_dict, income_dict
                ) if cash_flow else {}
                
                period_analysis = {
                    "period_end_date": income_stmt.period_end_date.isoformat(),
                    "year": income_stmt.period_end_date.year,
                    "liquidity_ratios": liquidity,
                    "leverage_ratios": leverage,
                    "profitability_ratios": profitability,
                    "efficiency_ratios": efficiency,
                    "cash_flow_ratios": cash_flow_ratios,
                    "raw_data": {
                        "revenue": income_stmt.revenue,
                        "net_income": income_stmt.net_income,
                        "total_assets": balance_sheet.total_assets,
                        "total_equity": balance_sheet.total_equity,
                        "operating_cash_flow": cash_flow.operating_cash_flow if cash_flow else 0
                    }
                }
                
                ratio_analysis.append(period_analysis)
                
            except Exception as e:
                self.logger.warning(f"Failed to calculate ratios for period {i}", error=str(e))
                continue
        
        return ratio_analysis
    
    def _analyze_trends(self, ratio_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in financial ratios."""
        if len(ratio_analysis) < 2:
            return {"status": "insufficient_data", "trends": {}}
        
        trends = {}
        
        # Key metrics to analyze trends for
        key_metrics = [
            ("raw_data", "revenue"),
            ("raw_data", "net_income"),
            ("profitability_ratios", "net_margin"),
            ("liquidity_ratios", "current_ratio"),
            ("leverage_ratios", "debt_to_equity"),
            ("efficiency_ratios", "asset_turnover")
        ]
        
        for category, metric in key_metrics:
            try:
                values = []
                for period in ratio_analysis:
                    if category in period and metric in period[category]:
                        values.append({
                            "year": period["year"],
                            "value": period[category][metric]
                        })
                
                if len(values) >= 2:
                    # Calculate trend
                    latest = values[-1]["value"]
                    previous = values[-2]["value"]
                    
                    if previous != 0:
                        change_percent = (latest - previous) / abs(previous)
                        
                        if change_percent > 0.1:
                            trend_direction = "improving"
                        elif change_percent < -0.1:
                            trend_direction = "declining"
                        else:
                            trend_direction = "stable"
                    else:
                        change_percent = 0
                        trend_direction = "stable"
                    
                    # Calculate volatility
                    value_list = [v["value"] for v in values]
                    avg_value = sum(value_list) / len(value_list)
                    if avg_value != 0:
                        volatility = (max(value_list) - min(value_list)) / abs(avg_value)
                    else:
                        volatility = 0
                    
                    trends[f"{category}_{metric}"] = {
                        "direction": trend_direction,
                        "change_percent": change_percent,
                        "volatility": volatility,
                        "values": values,
                        "latest_value": latest
                    }
                    
            except Exception as e:
                self.logger.warning(f"Failed to analyze trend for {metric}", error=str(e))
                continue
        
        return {"status": "completed", "trends": trends}
    
    def _analyze_asset_management(self, statements: FinancialStatements) -> Dict[str, Any]:
        """Analyze asset management efficiency."""
        analysis = {
            "operating_cycle_analysis": {},
            "asset_quality_assessment": {},
            "working_capital_analysis": {}
        }
        
        try:
            latest_balance_sheet = statements.balance_sheets[-1] if statements.balance_sheets else None
            latest_income = statements.income_statements[-1] if statements.income_statements else None
            
            if latest_balance_sheet and latest_income:
                # Working capital analysis
                working_capital = latest_balance_sheet.current_assets - latest_balance_sheet.current_liabilities
                analysis["working_capital_analysis"] = {
                    "working_capital": working_capital,
                    "working_capital_ratio": working_capital / latest_income.revenue if latest_income.revenue > 0 else 0,
                    "current_ratio": latest_balance_sheet.current_assets / latest_balance_sheet.current_liabilities if latest_balance_sheet.current_liabilities > 0 else float('inf')
                }
                
                # Asset composition
                if latest_balance_sheet.total_assets > 0:
                    analysis["asset_quality_assessment"] = {
                        "current_assets_pct": latest_balance_sheet.current_assets / latest_balance_sheet.total_assets,
                        "fixed_assets_pct": latest_balance_sheet.fixed_assets / latest_balance_sheet.total_assets,
                        "intangible_assets_pct": latest_balance_sheet.intangible_assets / latest_balance_sheet.total_assets,
                        "cash_pct": latest_balance_sheet.cash_and_equivalents / latest_balance_sheet.total_assets
                    }
                
                # Operating cycle metrics
                if latest_income.revenue > 0:
                    receivables_days = (latest_balance_sheet.accounts_receivable * 365) / latest_income.revenue
                    inventory_days = (latest_balance_sheet.inventory * 365) / latest_income.cost_of_goods_sold if latest_income.cost_of_goods_sold > 0 else 0
                    
                    analysis["operating_cycle_analysis"] = {
                        "receivables_days": receivables_days,
                        "inventory_days": inventory_days,
                        "operating_cycle_days": receivables_days + inventory_days
                    }
        
        except Exception as e:
            self.logger.error("Asset management analysis failed", error=str(e))
            analysis["error"] = str(e)
        
        return analysis
    
    def _analyze_profitability(self, statements: FinancialStatements) -> Dict[str, Any]:
        """Analyze profitability trends and drivers."""
        analysis = {
            "margin_analysis": {},
            "profitability_trends": {},
            "earnings_quality": {}
        }
        
        try:
            if not statements.income_statements:
                return analysis
            
            # Latest period margins
            latest_income = statements.income_statements[-1]
            if latest_income.revenue > 0:
                analysis["margin_analysis"] = {
                    "gross_margin": latest_income.gross_profit / latest_income.revenue,
                    "operating_margin": latest_income.operating_income / latest_income.revenue,
                    "net_margin": latest_income.net_income / latest_income.revenue,
                    "revenue": latest_income.revenue,
                    "net_income": latest_income.net_income
                }
            
            # Multi-period analysis if available
            if len(statements.income_statements) >= 2:
                revenue_growth = []
                margin_trends = []
                
                for i in range(1, len(statements.income_statements)):
                    current = statements.income_statements[i]
                    previous = statements.income_statements[i-1]
                    
                    if previous.revenue > 0:
                        rev_growth = (current.revenue - previous.revenue) / previous.revenue
                        revenue_growth.append(rev_growth)
                    
                    if current.revenue > 0:
                        margin_trends.append(current.net_income / current.revenue)
                
                analysis["profitability_trends"] = {
                    "average_revenue_growth": sum(revenue_growth) / len(revenue_growth) if revenue_growth else 0,
                    "margin_stability": self._calculate_stability(margin_trends) if margin_trends else 0
                }
        
        except Exception as e:
            self.logger.error("Profitability analysis failed", error=str(e))
            analysis["error"] = str(e)
        
        return analysis
    
    def _analyze_cash_flows(self, statements: FinancialStatements) -> Dict[str, Any]:
        """Analyze cash flow patterns and sustainability."""
        analysis = {
            "cash_flow_summary": {},
            "cash_conversion": {},
            "sustainability_metrics": {}
        }
        
        try:
            if not statements.cash_flow_statements:
                return analysis
            
            latest_cf = statements.cash_flow_statements[-1]
            latest_income = statements.income_statements[-1] if statements.income_statements else None
            
            # Cash flow summary
            analysis["cash_flow_summary"] = {
                "operating_cash_flow": latest_cf.operating_cash_flow,
                "investing_cash_flow": latest_cf.investing_cash_flow,
                "financing_cash_flow": latest_cf.financing_cash_flow,
                "net_cash_flow": latest_cf.net_cash_flow,
                "ending_cash": latest_cf.ending_cash
            }
            
            # Cash conversion analysis
            if latest_income:
                analysis["cash_conversion"] = {
                    "operating_cf_to_net_income": latest_cf.operating_cash_flow / latest_income.net_income if latest_income.net_income != 0 else 0,
                    "cash_earnings_quality": "high" if latest_cf.operating_cash_flow > latest_income.net_income else "low"
                }
            
            # Multi-period sustainability
            if len(statements.cash_flow_statements) >= 2:
                operating_cfs = [cf.operating_cash_flow for cf in statements.cash_flow_statements]
                analysis["sustainability_metrics"] = {
                    "operating_cf_consistency": self._calculate_stability(operating_cfs),
                    "average_operating_cf": sum(operating_cfs) / len(operating_cfs),
                    "cf_trend": "positive" if operating_cfs[-1] > operating_cfs[0] else "negative"
                }
        
        except Exception as e:
            self.logger.error("Cash flow analysis failed", error=str(e))
            analysis["error"] = str(e)
        
        return analysis
    
    def _calculate_stability(self, values: List[float]) -> float:
        """Calculate stability score (0-1, higher is more stable)."""
        if len(values) < 2:
            return 1.0
        
        try:
            import numpy as np
            coefficient_of_variation = np.std(values) / abs(np.mean(values)) if np.mean(values) != 0 else float('inf')
            # Convert to stability score (lower CV = higher stability)
            return max(0, 1 - min(coefficient_of_variation, 1))
        except:
            return 0.5  # Default moderate stability
    
    def _assess_financial_health(self, ratio_analysis: List[Dict[str, Any]], trend_analysis: Dict[str, Any]) -> float:
        """Assess overall financial health score (0-100)."""
        if not ratio_analysis:
            return 0
        
        latest_ratios = ratio_analysis[-1]
        health_components = []
        
        try:
            # Liquidity health (0-25 points)
            current_ratio = latest_ratios.get("liquidity_ratios", {}).get("current_ratio", 0)
            if current_ratio >= 1.5:
                liquidity_score = 25
            elif current_ratio >= 1.0:
                liquidity_score = 15
            else:
                liquidity_score = 5
            health_components.append(liquidity_score)
            
            # Profitability health (0-25 points)
            net_margin = latest_ratios.get("profitability_ratios", {}).get("net_margin", 0)
            if net_margin >= 0.1:  # 10%+ margin
                profitability_score = 25
            elif net_margin >= 0.05:  # 5%+ margin
                profitability_score = 15
            elif net_margin > 0:
                profitability_score = 10
            else:
                profitability_score = 0
            health_components.append(profitability_score)
            
            # Leverage health (0-25 points)
            debt_to_equity = latest_ratios.get("leverage_ratios", {}).get("debt_to_equity", float('inf'))
            if debt_to_equity <= 0.5:
                leverage_score = 25
            elif debt_to_equity <= 1.0:
                leverage_score = 15
            elif debt_to_equity <= 2.0:
                leverage_score = 10
            else:
                leverage_score = 0
            health_components.append(leverage_score)
            
            # Growth/trend health (0-25 points)
            trends = trend_analysis.get("trends", {})
            positive_trends = sum(1 for trend in trends.values() if trend.get("direction") == "improving")
            total_trends = len(trends)
            
            if total_trends > 0:
                trend_score = (positive_trends / total_trends) * 25
            else:
                trend_score = 12.5  # Neutral if no trend data
            health_components.append(trend_score)
            
            return sum(health_components)
            
        except Exception as e:
            self.logger.error("Financial health assessment failed", error=str(e))
            return 50  # Default moderate health score
    
    def _generate_financial_insights(self, ratio_analysis, trend_analysis, asset_analysis, profitability_analysis, cash_flow_analysis) -> List[str]:
        """Generate key financial insights."""
        insights = []
        
        if not ratio_analysis:
            return ["Insufficient data for financial insights"]
        
        latest_ratios = ratio_analysis[-1]
        
        # Liquidity insights
        current_ratio = latest_ratios.get("liquidity_ratios", {}).get("current_ratio", 0)
        if current_ratio < 1.0:
            insights.append("Liquidity concern: Current ratio below 1.0 indicates potential short-term liquidity issues")
        elif current_ratio > 3.0:
            insights.append("High liquidity: Current ratio above 3.0 may indicate inefficient use of working capital")
        
        # Profitability insights
        net_margin = latest_ratios.get("profitability_ratios", {}).get("net_margin", 0)
        if net_margin < 0:
            insights.append("Profitability concern: Negative net margin indicates the company is losing money")
        elif net_margin > 0.15:
            insights.append("Strong profitability: Net margin above 15% indicates excellent profit generation")
        
        # Leverage insights
        debt_to_equity = latest_ratios.get("leverage_ratios", {}).get("debt_to_equity", 0)
        if debt_to_equity > 2.0:
            insights.append("High leverage: Debt-to-equity ratio above 2.0 indicates high financial risk")
        
        # Trend insights
        trends = trend_analysis.get("trends", {})
        declining_trends = [k for k, v in trends.items() if v.get("direction") == "declining"]
        if declining_trends:
            insights.append(f"Declining trends identified in: {', '.join(declining_trends)}")
        
        # Cash flow insights
        cf_summary = cash_flow_analysis.get("cash_flow_summary", {})
        operating_cf = cf_summary.get("operating_cash_flow", 0)
        if operating_cf < 0:
            insights.append("Cash flow concern: Negative operating cash flow indicates operational challenges")
        
        return insights[:5]  # Return top 5 insights
    
    def _generate_recommendations(self, ratio_analysis, trend_analysis, health_score) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if health_score < 50:
            recommendations.append("Overall financial health is concerning - enhanced monitoring required")
        
        if ratio_analysis:
            latest_ratios = ratio_analysis[-1]
            
            # Liquidity recommendations
            current_ratio = latest_ratios.get("liquidity_ratios", {}).get("current_ratio", 0)
            if current_ratio < 1.2:
                recommendations.append("Consider requiring additional liquidity support or guarantees")
            
            # Leverage recommendations
            debt_to_equity = latest_ratios.get("leverage_ratios", {}).get("debt_to_equity", 0)
            if debt_to_equity > 1.5:
                recommendations.append("High leverage warrants careful debt service coverage analysis")
        
        # Trend-based recommendations
        trends = trend_analysis.get("trends", {})
        revenue_trend = trends.get("raw_data_revenue", {})
        if revenue_trend.get("direction") == "declining":
            recommendations.append("Declining revenue trend requires business plan review and stress testing")
        
        return recommendations
    
    def _get_analysis_period(self, statements: FinancialStatements) -> Dict[str, str]:
        """Get the analysis period details."""
        if statements.income_statements:
            dates = [stmt.period_end_date for stmt in statements.income_statements]
            return {
                "start_date": min(dates).isoformat(),
                "end_date": max(dates).isoformat(),
                "periods": len(dates)
            }
        return {}
    
    def get_prompt_template(self) -> str:
        """Get the prompt template for this agent."""
        return """
        You are a financial analysis expert specializing in business loan underwriting. Your role is to:
        1. Analyze historical financial statements comprehensively
        2. Calculate and interpret key financial ratios
        3. Identify trends and patterns in financial performance
        4. Assess overall financial health and creditworthiness
        5. Provide actionable insights for lending decisions
        
        Focus on liquidity, profitability, leverage, and operational efficiency.
        """


class FinancialProjectionAgent(BaseAgent):
    """Agent for developing financial projections and scenario analysis."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="Financial Projection Agent",
            description="Develops financial projections and scenario analysis",
            **kwargs
        )
        self.calculator = FinancialCalculator()
        self.rag_system = RAGSystem()
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Generate financial projections."""
        try:
            historical_data = input_data.data.get("historical_analysis", {})
            management_inputs = input_data.data.get("management_inputs", {})
            economic_assumptions = input_data.data.get("economic_assumptions", {})
            loan_request = input_data.data.get("loan_request", {})
            
            # Generate base case projections
            base_case = self._generate_base_case_projections(
                historical_data, management_inputs, economic_assumptions
            )
            
            # Generate downside scenario
            downside_case = self._generate_downside_scenario(base_case, economic_assumptions)
            
            # Generate break-even analysis
            break_even_case = self._generate_break_even_scenario(base_case, loan_request)
            
            # Stress test scenarios
            stress_tests = self._perform_stress_testing(base_case, historical_data)
            
            # Assess projection quality
            projection_quality = self._assess_projection_quality(
                base_case, historical_data, management_inputs
            )
            
            # Get relevant guidelines
            guidelines = await self.rag_system.get_guidelines_for_category("financial_projections")
            
            result = {
                "base_case_projections": base_case,
                "downside_scenario": downside_case,
                "break_even_analysis": break_even_case,
                "stress_test_scenarios": stress_tests,
                "projection_quality_assessment": projection_quality,
                "key_assumptions": self._extract_key_assumptions(management_inputs, economic_assumptions),
                "guidelines_context": guidelines[:3] if guidelines else []
            }
            
            recommendations = self._generate_projection_recommendations(
                base_case, downside_case, projection_quality
            )
            
            output = AgentOutput(
                result=result,
                metadata={
                    "projection_date": datetime.now().isoformat(),
                    "projection_horizon_years": 3,
                    "scenarios_generated": 3
                },
                confidence_score=projection_quality.get("overall_confidence", 0.7),
                recommendations=recommendations
            )
            
            await self._log_execution(input_data, output)
            return output
            
        except Exception as e:
            self.logger.error("Financial projection generation failed", error=str(e))
            return AgentOutput(
                result={"error": str(e)},
                metadata={"error": True},
                confidence_score=0.0,
                recommendations=["Fix financial projection error"]
            )
    
    def _generate_base_case_projections(self, historical_data, management_inputs, economic_assumptions) -> Dict[str, Any]:
        """Generate base case financial projections."""
        projections = {
            "income_statements": [],
            "balance_sheets": [],
            "cash_flow_statements": [],
            "assumptions": {}
        }
        
        try:
            # Extract historical trends
            historical_ratios = historical_data.get("ratio_analysis", [])
            if not historical_ratios:
                raise ValueError("Insufficient historical data for projections")
            
            latest_period = historical_ratios[-1]
            
            # Revenue growth assumptions
            revenue_growth_rate = management_inputs.get("expected_revenue_growth", 0.05)  # Default 5%
            economic_growth_factor = economic_assumptions.get("gdp_growth_adjustment", 1.0)
            adjusted_growth = revenue_growth_rate * economic_growth_factor
            
            # Starting values from latest historical data
            base_revenue = latest_period["raw_data"]["revenue"]
            base_margins = latest_period["profitability_ratios"]
            
            # Generate 3-year projections
            for year in range(1, 4):
                # Income Statement Projections
                projected_revenue = base_revenue * ((1 + adjusted_growth) ** year)
                
                # Apply margin assumptions (with slight deterioration over time)
                margin_decay = 0.95 ** year  # 5% annual decay in margins
                gross_margin = base_margins.get("gross_margin", 0.3) * margin_decay
                operating_margin = base_margins.get("operating_margin", 0.1) * margin_decay
                net_margin = base_margins.get("net_margin", 0.05) * margin_decay
                
                income_projection = {
                    "year": datetime.now().year + year,
                    "revenue": projected_revenue,
                    "gross_profit": projected_revenue * gross_margin,
                    "operating_income": projected_revenue * operating_margin,
                    "net_income": projected_revenue * net_margin,
                    "ebitda": projected_revenue * (operating_margin + 0.03)  # Add back D&A estimate
                }
                
                projections["income_statements"].append(income_projection)
                
                # Balance Sheet Projections (simplified)
                asset_turnover = latest_period["efficiency_ratios"].get("asset_turnover", 1.0)
                total_assets = projected_revenue / asset_turnover
                
                # Assume debt-to-equity ratio remains stable
                debt_to_equity = latest_period["leverage_ratios"].get("debt_to_equity", 0.5)
                equity_multiplier = 1 + debt_to_equity
                total_equity = total_assets / equity_multiplier
                total_debt = total_assets - total_equity
                
                balance_projection = {
                    "year": datetime.now().year + year,
                    "total_assets": total_assets,
                    "total_equity": total_equity,
                    "total_debt": total_debt,
                    "cash": total_assets * 0.1,  # Assume 10% cash
                    "current_assets": total_assets * 0.4,  # Assume 40% current assets
                    "current_liabilities": total_debt * 0.3  # Assume 30% of debt is current
                }
                
                projections["balance_sheets"].append(balance_projection)
                
                # Cash Flow Projections
                operating_cf = income_projection["net_income"] * 1.2  # Assume positive working capital effect
                investing_cf = -projected_revenue * 0.03  # 3% of revenue in capex
                financing_cf = 0  # Assume no major financing changes
                
                cash_flow_projection = {
                    "year": datetime.now().year + year,
                    "operating_cash_flow": operating_cf,
                    "investing_cash_flow": investing_cf,
                    "financing_cash_flow": financing_cf,
                    "net_cash_flow": operating_cf + investing_cf + financing_cf
                }
                
                projections["cash_flow_statements"].append(cash_flow_projection)
            
            # Store key assumptions
            projections["assumptions"] = {
                "revenue_growth_rate": adjusted_growth,
                "margin_decay_factor": 0.95,
                "asset_turnover_stable": True,
                "debt_structure_stable": True
            }
            
        except Exception as e:
            self.logger.error("Base case projection generation failed", error=str(e))
            projections["error"] = str(e)
        
        return projections
    
    def _generate_downside_scenario(self, base_case, economic_assumptions) -> Dict[str, Any]:
        """Generate downside scenario projections."""
        downside = {"income_statements": [], "balance_sheets": [], "cash_flow_statements": []}
        
        try:
            # Apply stress factors
            revenue_stress = economic_assumptions.get("downside_revenue_impact", 0.8)  # 20% reduction
            margin_stress = economic_assumptions.get("downside_margin_impact", 0.9)   # 10% margin compression
            
            for i, income_stmt in enumerate(base_case.get("income_statements", [])):
                stressed_income = {
                    "year": income_stmt["year"],
                    "revenue": income_stmt["revenue"] * revenue_stress,
                    "gross_profit": income_stmt["gross_profit"] * revenue_stress * margin_stress,
                    "operating_income": income_stmt["operating_income"] * revenue_stress * margin_stress,
                    "net_income": income_stmt["net_income"] * revenue_stress * margin_stress,
                    "ebitda": income_stmt["ebitda"] * revenue_stress * margin_stress
                }
                downside["income_statements"].append(stressed_income)
                
                # Adjust balance sheet accordingly
                balance_stmt = base_case["balance_sheets"][i]
                stressed_balance = {
                    "year": balance_stmt["year"],
                    "total_assets": balance_stmt["total_assets"] * 0.9,  # Asset values decline
                    "total_equity": balance_stmt["total_equity"] * 0.8,  # Equity takes bigger hit
                    "total_debt": balance_stmt["total_debt"],  # Debt remains same
                    "cash": balance_stmt["cash"] * 0.7,  # Cash burns faster
                    "current_assets": balance_stmt["current_assets"] * 0.85,
                    "current_liabilities": balance_stmt["current_liabilities"] * 1.1  # Liabilities may increase
                }
                downside["balance_sheets"].append(stressed_balance)
                
                # Adjust cash flows
                cash_flow = base_case["cash_flow_statements"][i]
                stressed_cash_flow = {
                    "year": cash_flow["year"],
                    "operating_cash_flow": stressed_income["net_income"] * 1.1,  # Less conversion
                    "investing_cash_flow": cash_flow["investing_cash_flow"] * 0.5,  # Reduce capex
                    "financing_cash_flow": 0,
                    "net_cash_flow": 0  # Will calculate
                }
                stressed_cash_flow["net_cash_flow"] = (
                    stressed_cash_flow["operating_cash_flow"] + 
                    stressed_cash_flow["investing_cash_flow"]
                )
                downside["cash_flow_statements"].append(stressed_cash_flow)
                
        except Exception as e:
            self.logger.error("Downside scenario generation failed", error=str(e))
            downside["error"] = str(e)
        
        return downside
    
    def _generate_break_even_scenario(self, base_case, loan_request) -> Dict[str, Any]:
        """Generate break-even analysis."""
        break_even = {
            "minimum_revenue_required": 0,
            "break_even_metrics": {},
            "debt_service_requirements": {}
        }
        
        try:
            loan_amount = loan_request.get("loan_amount", 0)
            interest_rate = loan_request.get("interest_rate", 0.05)
            term_years = loan_request.get("term_years", 5)
            
            if loan_amount > 0:
                # Calculate annual debt service
                monthly_payment = self.calculator.calculate_loan_affordability(
                    {"operating_cash_flow": 100000},  # Dummy value
                    loan_amount, interest_rate, term_years * 12
                )
                annual_debt_service = monthly_payment.get("annual_payment", 0)
                
                # Assume minimum DSCR of 1.25
                min_operating_cf = annual_debt_service * 1.25
                
                # Work backwards to required revenue
                # Assume operating CF = 15% of revenue (typical)
                min_revenue = min_operating_cf / 0.15
                
                break_even["minimum_revenue_required"] = min_revenue
                break_even["debt_service_requirements"] = {
                    "annual_debt_service": annual_debt_service,
                    "minimum_operating_cf": min_operating_cf,
                    "required_dscr": 1.25
                }
                
                # Compare to base case projections
                if base_case.get("income_statements"):
                    base_revenue = base_case["income_statements"][0]["revenue"]
                    break_even["break_even_metrics"] = {
                        "break_even_coverage": base_revenue / min_revenue if min_revenue > 0 else float('inf'),
                        "revenue_cushion_pct": (base_revenue - min_revenue) / base_revenue if base_revenue > 0 else 0
                    }
                    
        except Exception as e:
            self.logger.error("Break-even analysis failed", error=str(e))
            break_even["error"] = str(e)
        
        return break_even
    
    def _perform_stress_testing(self, base_case, historical_data) -> Dict[str, Any]:
        """Perform various stress tests."""
        stress_tests = {
            "interest_rate_sensitivity": {},
            "recession_scenario": {},
            "industry_downturn": {}
        }
        
        try:
            # Interest rate stress test (rates increase by 200 bps)
            # This would affect financing costs and potentially demand
            
            # Recession scenario (based on historical volatility)
            historical_ratios = historical_data.get("ratio_analysis", [])
            if len(historical_ratios) >= 2:
                revenues = [period["raw_data"]["revenue"] for period in historical_ratios]
                revenue_volatility = self._calculate_volatility(revenues)
                
                # Apply 2-sigma stress (roughly 2.5th percentile outcome)
                stress_factor = 1 - (2 * revenue_volatility)
                
                recession_revenues = []
                for income_stmt in base_case.get("income_statements", []):
                    stressed_revenue = income_stmt["revenue"] * max(stress_factor, 0.5)  # Floor at 50% decline
                    recession_revenues.append({
                        "year": income_stmt["year"],
                        "stressed_revenue": stressed_revenue,
                        "revenue_decline_pct": (income_stmt["revenue"] - stressed_revenue) / income_stmt["revenue"]
                    })
                
                stress_tests["recession_scenario"] = {
                    "stress_factor": stress_factor,
                    "revenue_volatility": revenue_volatility,
                    "stressed_projections": recession_revenues
                }
                
        except Exception as e:
            self.logger.error("Stress testing failed", error=str(e))
            stress_tests["error"] = str(e)
        
        return stress_tests
    
    def _assess_projection_quality(self, projections, historical_data, management_inputs) -> Dict[str, Any]:
        """Assess the quality and reliability of projections."""
        quality_assessment = {
            "overall_confidence": 0.7,  # Default
            "data_quality_factors": [],
            "assumption_reasonableness": {},
            "reliability_score": 0
        }
        
        try:
            factors = []
            
            # Historical data completeness
            historical_ratios = historical_data.get("ratio_analysis", [])
            if len(historical_ratios) >= 3:
                factors.append(("Historical data completeness", 0.9))
            elif len(historical_ratios) >= 2:
                factors.append(("Historical data completeness", 0.7))
            else:
                factors.append(("Historical data completeness", 0.4))
            
            # Management input quality
            mgmt_quality = len(management_inputs) / 10  # Assume 10 key inputs needed
            factors.append(("Management input quality", min(mgmt_quality, 1.0)))
            
            # Projection methodology
            factors.append(("Projection methodology", 0.8))  # Good but not perfect
            
            # Calculate weighted confidence
            if factors:
                quality_assessment["overall_confidence"] = sum(score for _, score in factors) / len(factors)
                quality_assessment["data_quality_factors"] = factors
            
            # Assess assumption reasonableness
            assumptions = projections.get("assumptions", {})
            revenue_growth = assumptions.get("revenue_growth_rate", 0)
            
            if 0 <= revenue_growth <= 0.15:  # 0-15% growth seems reasonable
                quality_assessment["assumption_reasonableness"]["revenue_growth"] = "reasonable"
            elif revenue_growth > 0.25:  # >25% growth is aggressive
                quality_assessment["assumption_reasonableness"]["revenue_growth"] = "aggressive"
            else:
                quality_assessment["assumption_reasonableness"]["revenue_growth"] = "conservative"
            
            quality_assessment["reliability_score"] = quality_assessment["overall_confidence"] * 100
            
        except Exception as e:
            self.logger.error("Projection quality assessment failed", error=str(e))
            quality_assessment["error"] = str(e)
        
        return quality_assessment
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate coefficient of variation."""
        if len(values) < 2:
            return 0
        
        try:
            import numpy as np
            return np.std(values) / abs(np.mean(values)) if np.mean(values) != 0 else 0
        except:
            # Fallback calculation
            mean_val = sum(values) / len(values)
            if mean_val == 0:
                return 0
            variance = sum((x - mean_val) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5
            return std_dev / abs(mean_val)
    
    def _extract_key_assumptions(self, management_inputs, economic_assumptions) -> Dict[str, Any]:
        """Extract and summarize key assumptions."""
        return {
            "management_assumptions": management_inputs,
            "economic_assumptions": economic_assumptions,
            "model_assumptions": {
                "projection_horizon": "3 years",
                "margin_decay_rate": "5% annually",
                "working_capital_stable": True
            }
        }
    
    def _generate_projection_recommendations(self, base_case, downside_case, quality_assessment) -> List[str]:
        """Generate recommendations based on projections."""
        recommendations = []
        
        confidence = quality_assessment.get("overall_confidence", 0)
        if confidence < 0.6:
            recommendations.append("Low projection confidence - require additional management input and stress testing")
        
        # Analyze base vs downside scenarios
        if base_case.get("income_statements") and downside_case.get("income_statements"):
            base_revenue = base_case["income_statements"][0]["revenue"]
            downside_revenue = downside_case["income_statements"][0]["revenue"]
            
            revenue_impact = (base_revenue - downside_revenue) / base_revenue
            if revenue_impact > 0.3:  # >30% revenue decline in downside
                recommendations.append("High downside revenue risk - consider additional covenants and monitoring")
        
        # Growth reasonableness
        assumptions = base_case.get("assumptions", {})
        growth_rate = assumptions.get("revenue_growth_rate", 0)
        if growth_rate > 0.2:  # >20% growth
            recommendations.append("Aggressive growth assumptions - validate with market analysis")
        
        return recommendations
    
    def get_prompt_template(self) -> str:
        """Get the prompt template for this agent."""
        return """
        You are a financial projection specialist for business lending. Your role is to:
        1. Develop realistic financial projections based on historical performance
        2. Create multiple scenarios (base case, downside, break-even)
        3. Perform comprehensive stress testing
        4. Assess projection quality and assumption reasonableness
        5. Provide scenario-based lending recommendations
        
        Focus on conservative assumptions and thorough stress testing.
        """ 