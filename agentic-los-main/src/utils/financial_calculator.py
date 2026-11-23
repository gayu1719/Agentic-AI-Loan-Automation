"""Financial calculator utilities for loan analysis."""
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from datetime import datetime
import structlog

logger = structlog.get_logger()


class FinancialCalculator:
    """Financial calculations and ratio analysis utilities."""
    
    def __init__(self):
        self.logger = logger.bind(component="financial_calculator")
    
    def calculate_liquidity_ratios(self, balance_sheet: Dict[str, float]) -> Dict[str, float]:
        """Calculate liquidity ratios."""
        try:
            ratios = {}
            
            # Current Ratio
            current_assets = balance_sheet.get('current_assets', 0)
            current_liabilities = balance_sheet.get('current_liabilities', 0)
            if current_liabilities > 0:
                ratios['current_ratio'] = current_assets / current_liabilities
            else:
                ratios['current_ratio'] = float('inf')
            
            # Quick Ratio (Acid Test)
            cash = balance_sheet.get('cash_and_equivalents', 0)
            accounts_receivable = balance_sheet.get('accounts_receivable', 0)
            inventory = balance_sheet.get('inventory', 0)
            
            quick_assets = current_assets - inventory
            if current_liabilities > 0:
                ratios['quick_ratio'] = quick_assets / current_liabilities
            else:
                ratios['quick_ratio'] = float('inf')
            
            # Cash Ratio
            if current_liabilities > 0:
                ratios['cash_ratio'] = cash / current_liabilities
            else:
                ratios['cash_ratio'] = float('inf')
            
            return ratios
            
        except Exception as e:
            self.logger.error("Failed to calculate liquidity ratios", error=str(e))
            return {}
    
    def calculate_leverage_ratios(self, balance_sheet: Dict[str, float]) -> Dict[str, float]:
        """Calculate leverage/solvency ratios."""
        try:
            ratios = {}
            
            total_assets = balance_sheet.get('total_assets', 0)
            total_liabilities = balance_sheet.get('total_liabilities', 0)
            total_equity = balance_sheet.get('total_equity', 0)
            long_term_debt = balance_sheet.get('long_term_debt', 0)
            short_term_debt = balance_sheet.get('short_term_debt', 0)
            total_debt = long_term_debt + short_term_debt
            
            # Debt-to-Equity Ratio
            if total_equity > 0:
                ratios['debt_to_equity'] = total_debt / total_equity
            else:
                ratios['debt_to_equity'] = float('inf')
            
            # Debt-to-Assets Ratio
            if total_assets > 0:
                ratios['debt_to_assets'] = total_debt / total_assets
            else:
                ratios['debt_to_assets'] = 0
            
            # Equity Multiplier
            if total_equity > 0:
                ratios['equity_multiplier'] = total_assets / total_equity
            else:
                ratios['equity_multiplier'] = float('inf')
            
            return ratios
            
        except Exception as e:
            self.logger.error("Failed to calculate leverage ratios", error=str(e))
            return {}
    
    def calculate_profitability_ratios(
        self, 
        income_statement: Dict[str, float], 
        balance_sheet: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate profitability ratios."""
        try:
            ratios = {}
            
            revenue = income_statement.get('revenue', 0)
            gross_profit = income_statement.get('gross_profit', 0)
            operating_income = income_statement.get('operating_income', 0)
            net_income = income_statement.get('net_income', 0)
            total_assets = balance_sheet.get('total_assets', 0)
            total_equity = balance_sheet.get('total_equity', 0)
            
            # Gross Profit Margin
            if revenue > 0:
                ratios['gross_margin'] = gross_profit / revenue
            else:
                ratios['gross_margin'] = 0
            
            # Operating Margin
            if revenue > 0:
                ratios['operating_margin'] = operating_income / revenue
            else:
                ratios['operating_margin'] = 0
            
            # Net Profit Margin
            if revenue > 0:
                ratios['net_margin'] = net_income / revenue
            else:
                ratios['net_margin'] = 0
            
            # Return on Assets (ROA)
            if total_assets > 0:
                ratios['return_on_assets'] = net_income / total_assets
            else:
                ratios['return_on_assets'] = 0
            
            # Return on Equity (ROE)
            if total_equity > 0:
                ratios['return_on_equity'] = net_income / total_equity
            else:
                ratios['return_on_equity'] = 0
            
            return ratios
            
        except Exception as e:
            self.logger.error("Failed to calculate profitability ratios", error=str(e))
            return {}
    
    def calculate_efficiency_ratios(
        self, 
        income_statement: Dict[str, float], 
        balance_sheet: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate efficiency/activity ratios."""
        try:
            ratios = {}
            
            revenue = income_statement.get('revenue', 0)
            cost_of_goods_sold = income_statement.get('cost_of_goods_sold', 0)
            total_assets = balance_sheet.get('total_assets', 0)
            accounts_receivable = balance_sheet.get('accounts_receivable', 0)
            inventory = balance_sheet.get('inventory', 0)
            
            # Asset Turnover
            if total_assets > 0:
                ratios['asset_turnover'] = revenue / total_assets
            else:
                ratios['asset_turnover'] = 0
            
            # Inventory Turnover
            if inventory > 0:
                ratios['inventory_turnover'] = cost_of_goods_sold / inventory
            else:
                ratios['inventory_turnover'] = 0
            
            # Receivables Turnover
            if accounts_receivable > 0:
                ratios['receivables_turnover'] = revenue / accounts_receivable
            else:
                ratios['receivables_turnover'] = 0
            
            # Days Sales Outstanding (DSO)
            if ratios['receivables_turnover'] > 0:
                ratios['days_sales_outstanding'] = 365 / ratios['receivables_turnover']
            else:
                ratios['days_sales_outstanding'] = 0
            
            # Days Inventory Outstanding (DIO)
            if ratios['inventory_turnover'] > 0:
                ratios['days_inventory_outstanding'] = 365 / ratios['inventory_turnover']
            else:
                ratios['days_inventory_outstanding'] = 0
            
            return ratios
            
        except Exception as e:
            self.logger.error("Failed to calculate efficiency ratios", error=str(e))
            return {}
    
    def calculate_cash_flow_ratios(
        self, 
        cash_flow_statement: Dict[str, float], 
        balance_sheet: Dict[str, float],
        income_statement: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate cash flow ratios."""
        try:
            ratios = {}
            
            operating_cash_flow = cash_flow_statement.get('operating_cash_flow', 0)
            net_income = income_statement.get('net_income', 0)
            current_liabilities = balance_sheet.get('current_liabilities', 0)
            total_debt = balance_sheet.get('long_term_debt', 0) + balance_sheet.get('short_term_debt', 0)
            
            # Operating Cash Flow to Net Income
            if abs(net_income) > 0.01:  # Avoid division by very small numbers
                ratios['ocf_to_net_income'] = operating_cash_flow / net_income
            else:
                ratios['ocf_to_net_income'] = 0
            
            # Operating Cash Flow to Current Liabilities
            if current_liabilities > 0:
                ratios['ocf_to_current_liabilities'] = operating_cash_flow / current_liabilities
            else:
                ratios['ocf_to_current_liabilities'] = 0
            
            # Cash Flow Coverage Ratio
            if total_debt > 0:
                ratios['cash_flow_coverage'] = operating_cash_flow / total_debt
            else:
                ratios['cash_flow_coverage'] = 0
            
            return ratios
            
        except Exception as e:
            self.logger.error("Failed to calculate cash flow ratios", error=str(e))
            return {}
    
    def calculate_debt_service_coverage(
        self, 
        cash_flow_statement: Dict[str, float],
        debt_schedule: Optional[Dict[str, float]] = None
    ) -> float:
        """Calculate debt service coverage ratio."""
        try:
            operating_cash_flow = cash_flow_statement.get('operating_cash_flow', 0)
            
            if debt_schedule:
                annual_debt_service = debt_schedule.get('annual_principal', 0) + debt_schedule.get('annual_interest', 0)
            else:
                # Estimate from cash flow statement
                debt_payments = cash_flow_statement.get('debt_payments', 0)
                annual_debt_service = debt_payments
            
            if annual_debt_service > 0:
                return operating_cash_flow / annual_debt_service
            else:
                return float('inf')
                
        except Exception as e:
            self.logger.error("Failed to calculate DSCR", error=str(e))
            return 0
    
    def analyze_trend(self, historical_data: List[Dict[str, float]], metric: str) -> Dict[str, Any]:
        """Analyze trend for a specific metric over time."""
        try:
            if len(historical_data) < 2:
                return {"trend": "insufficient_data", "change": 0, "volatility": 0}
            
            values = [data.get(metric, 0) for data in historical_data]
            
            # Calculate trend
            if len(values) >= 2:
                latest_value = values[-1]
                previous_value = values[-2]
                
                if previous_value != 0:
                    change_percent = (latest_value - previous_value) / abs(previous_value)
                else:
                    change_percent = 0
                
                # Determine trend direction
                if change_percent > 0.05:  # 5% improvement
                    trend = "improving"
                elif change_percent < -0.05:  # 5% decline
                    trend = "declining"
                else:
                    trend = "stable"
                
                # Calculate volatility (coefficient of variation)
                if np.mean(values) != 0:
                    volatility = np.std(values) / abs(np.mean(values))
                else:
                    volatility = 0
                
                return {
                    "trend": trend,
                    "change": change_percent,
                    "volatility": volatility,
                    "latest_value": latest_value,
                    "historical_values": values
                }
            
            return {"trend": "insufficient_data", "change": 0, "volatility": 0}
            
        except Exception as e:
            self.logger.error("Failed to analyze trend", metric=metric, error=str(e))
            return {"trend": "error", "change": 0, "volatility": 0}
    
    def calculate_loan_affordability(
        self, 
        cash_flow_statement: Dict[str, float],
        loan_amount: float,
        interest_rate: float,
        term_months: int,
        minimum_dscr: float = 1.25
    ) -> Dict[str, Any]:
        """Calculate loan affordability metrics."""
        try:
            operating_cash_flow = cash_flow_statement.get('operating_cash_flow', 0)
            
            # Calculate monthly payment
            monthly_rate = interest_rate / 12
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**term_months) / ((1 + monthly_rate)**term_months - 1)
            annual_payment = monthly_payment * 12
            
            # Calculate DSCR
            if annual_payment > 0:
                projected_dscr = operating_cash_flow / annual_payment
            else:
                projected_dscr = float('inf')
            
            # Calculate maximum affordable loan
            max_annual_payment = operating_cash_flow / minimum_dscr
            max_loan_amount = max_annual_payment / ((monthly_rate * (1 + monthly_rate)**term_months) / ((1 + monthly_rate)**term_months - 1)) / 12
            
            return {
                'monthly_payment': monthly_payment,
                'annual_payment': annual_payment,
                'projected_dscr': projected_dscr,
                'meets_minimum_dscr': projected_dscr >= minimum_dscr,
                'max_affordable_loan': max_loan_amount,
                'loan_to_cashflow_ratio': loan_amount / operating_cash_flow if operating_cash_flow > 0 else float('inf')
            }
            
        except Exception as e:
            self.logger.error("Failed to calculate loan affordability", error=str(e))
            return {} 