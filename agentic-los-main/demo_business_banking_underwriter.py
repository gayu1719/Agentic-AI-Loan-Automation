#!/usr/bin/env python3
"""
Business Banking Augmented Underwriter Demo

Comprehensive demo showcasing commercial lending AI capabilities.
This script demonstrates the AI system that enhances business banking underwriters
with sophisticated commercial loan analysis, industry risk assessment, and 
relationship banking insights.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
import requests
import httpx
import structlog

from src.agents.business_banking_underwriter import BusinessBankingAugmentedUnderwriter
from src.agents.base_agent import AgentInput

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# API Configuration
BASE_URL = "http://localhost:8000"
BUSINESS_API = f"{BASE_URL}/business-banking"


def print_section_header(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n--- {title} ---")

def get_industry_icon(industry: str) -> str:
    """Get emoji icon for industry type"""
    icons = {
        "manufacturing": "🏭",
        "technology": "💻",
        "construction": "🏗️",
        "retail": "🏪",
        "professional_services": "🏢",
        "healthcare": "🏥",
        "restaurant": "🍽️"
    }
    return icons.get(industry.lower(), "🏢")

def get_risk_level_color(score: float) -> str:
    """Get color indicator for risk level"""
    if score < 25:
        return "🟢 LOW RISK"
    elif score < 50:
        return "🟡 MEDIUM RISK"  
    elif score < 75:
        return "🟠 HIGH RISK"
    else:
        return "🔴 CRITICAL RISK"

def get_recommendation_icon(decision: str) -> str:
    """Get icon for recommendation decision"""
    icons = {
        "approve": "✅",
        "conditional_approve": "⚠️",
        "counter_proposal": "🔄",
        "decline": "❌"
    }
    return icons.get(decision.lower(), "❓")

def check_server_status():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

class BusinessBankingDemo:
    """Business Banking Demo Runner"""
    
    def __init__(self):
        self.underwriter = BusinessBankingAugmentedUnderwriter()
        self.demo_applications = self._create_demo_applications()

    def _create_demo_applications(self) -> List[Dict[str, Any]]:
        """Create realistic business banking applications"""
        
        return [
            # Manufacturing Company - Strong Profile
            {
                "application_id": "BIZ-MFG-001",
                "company_name": "Precision Metal Works Inc.",
                "industry_type": "manufacturing",
                "years_in_business": 15,
                "number_of_employees": 85,
                "annual_revenue": 12000000,
                "requested_loan_amount": 2500000,
                "loan_purpose": "Equipment upgrade and facility expansion",
                "loan_type": "term_loan",
                "monthly_cash_flow": 180000,
                "business_description": "Custom metal fabrication for aerospace and automotive"
            },
            
            # Technology Startup - Moderate Risk
            {
                "application_id": "BIZ-TECH-002", 
                "company_name": "CloudFlow Solutions LLC",
                "industry_type": "technology",
                "years_in_business": 4,
                "number_of_employees": 32,
                "annual_revenue": 4500000,
                "requested_loan_amount": 1000000,
                "loan_purpose": "Working capital and talent acquisition",
                "loan_type": "line_of_credit",
                "monthly_cash_flow": 95000,
                "business_description": "SaaS platform for supply chain optimization"
            },
            
            # Construction Company - Higher Risk
            {
                "application_id": "BIZ-CONST-003",
                "company_name": "Summit Construction Group",
                "industry_type": "construction", 
                "years_in_business": 8,
                "number_of_employees": 45,
                "annual_revenue": 6500000,
                "requested_loan_amount": 1800000,
                "loan_purpose": "Heavy equipment purchase and bonding capacity",
                "loan_type": "equipment_financing",
                "monthly_cash_flow": 85000,
                "business_description": "Commercial construction and infrastructure projects"
            }
        ]

    async def run_comprehensive_demo(self):
        """Run complete business banking underwriter demo"""
        
        print_section_header("🏦 BUSINESS BANKING AUGMENTED UNDERWRITER DEMO")
        print("""
This demo showcases an AI system that ENHANCES business banking underwriters
with sophisticated commercial lending capabilities:

✅ Industry-specific risk assessment and modeling
✅ Comprehensive financial ratio analysis with benchmarking  
✅ Management team and operational strength evaluation
✅ Cross-selling opportunity identification and relationship insights
✅ Alternative loan structure recommendations
✅ Portfolio-level analytics and trend analysis
✅ Human oversight maintaining final commercial lending decisions

Let's explore commercial lending excellence in action!
        """)
        
        # Check server status
        if not check_server_status():
            print("⚠️  Note: API server not running - demo will use mock data")
        
        # Initialize the underwriter
        await self.underwriter.initialize()
        print("✅ Business Banking Augmented Underwriter initialized")
        print()
        
        # Process each application with interactive flow
        portfolio_insights = []
        
        for i, application in enumerate(self.demo_applications, 1):
            await self._process_business_application_demo(
                i, application, portfolio_insights
            )
            
            # Interactive pause between applications
            if i < len(self.demo_applications):
                print("\n" + "-"*60)
                input("Press Enter to continue to next business application...")
        
        # Portfolio-level analytics
        if portfolio_insights:
            await self._display_portfolio_analytics(portfolio_insights)
        
        # Demonstrate cross-selling insights
        await self._demo_cross_selling_insights(portfolio_insights)
        
        # Show human override capabilities
        await self._demo_business_override(self.demo_applications[1])
        
        print_section_header("🎉 BUSINESS BANKING DEMO COMPLETED")
        print("""
✅ Demo applications have been processed and stored in the system!

The Business Banking Augmented Underwriter successfully demonstrated:

✅ Sophisticated commercial loan analysis beyond traditional metrics
✅ Industry-specific risk modeling and market intelligence
✅ Management assessment and operational due diligence
✅ Relationship banking insights and cross-selling opportunities
✅ Alternative financing structure recommendations
✅ Portfolio analytics and risk concentration management
✅ Human oversight capabilities for complex commercial decisions

This AI system transforms business banking by making commercial underwriters
faster, more insightful, and more strategic in their lending decisions!

🌐 Business Banking Dashboard: http://localhost:8000/business-banking/dashboard
📊 Portfolio Analytics: http://localhost:8000/business-banking/portfolio/summary

Now when you visit the portfolio summary URL, you'll see the analyzed applications!
        """)

    async def _process_business_application_demo(self, app_num: int, application: Dict[str, Any], portfolio_insights: List):
        """Process a single business application with detailed output"""
        
        industry_icon = get_industry_icon(application['industry_type'])
        company_name = application['company_name']
        
        print_section_header(f"{industry_icon} PROCESSING APPLICATION {app_num}/3: {company_name}")
        print(f"Company: {company_name}")
        print(f"Industry: {application['industry_type'].title()}")
        print(f"Years in Business: {application['years_in_business']}")
        print(f"Annual Revenue: ${application['annual_revenue']:,}")
        print(f"Employees: {application['number_of_employees']}")
        print(f"Loan Amount: ${application['requested_loan_amount']:,}")
        print(f"Purpose: {application['loan_purpose']}")
        print(f"Monthly Cash Flow: ${application['monthly_cash_flow']:,}")
        
        print("\n🤖 AI Business Banking Agent analyzing application...")
        print("   • Evaluating financial strength and cash flow patterns")
        print("   • Assessing industry risks and market conditions")
        print("   • Analyzing management team and operational capabilities")  
        print("   • Identifying cross-selling and relationship opportunities")
        print("   • Generating alternative loan structure recommendations")
        
        # Check if server is running to use API or local processing
        if check_server_status():
            try:
                # Use API endpoint to store data in the system
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{BUSINESS_API}/analyze/{application['application_id']}",
                        json=application,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        api_result = response.json()
                        insights = api_result["insights"]
                        portfolio_insights.append(insights)
                        
                        # Display comprehensive analysis
                        self._display_enhanced_business_analysis(application, insights)
                        
                        print("✅ Application data stored in system for portfolio analytics")
                        
                    else:
                        print(f"❌ API Error: {response.status_code}")
                        raise Exception("API call failed")
                        
            except Exception as e:
                print(f"⚠️  API unavailable, using local processing: {str(e)}")
                # Fallback to local processing
                agent_input = AgentInput(data=application)
                result = await self.underwriter.process(agent_input)
                
                if result.result["status"] == "completed":
                    insights = result.result["insights"]
                    portfolio_insights.append(insights)
                    self._display_enhanced_business_analysis(application, insights)
                else:
                    print(f"❌ Error processing application: {result.result.get('error')}")
        else:
            # Local processing when server is not available
            agent_input = AgentInput(data=application)
            result = await self.underwriter.process(agent_input)
            
            if result.result["status"] == "completed":
                insights = result.result["insights"]
                portfolio_insights.append(insights)
                self._display_enhanced_business_analysis(application, insights)
            else:
                print(f"❌ Error processing application: {result.result.get('error')}")
        
        print("─" * 80)

    def _display_business_analysis(self, application: Dict[str, Any], insights: Dict[str, Any]):
        """Display comprehensive business analysis results"""
        
        company_name = application["company_name"]
        recommendation = insights["recommendation"]
        financial_metrics = insights["financial_metrics"]
        operational_assessment = insights["operational_assessment"]
        risk_flags = insights["risk_flags"]
        
        print(f"🏢 BUSINESS ANALYSIS: {company_name}")
        print(f"   Application ID: {insights['application_id']}")
        print()
        
        # Financial Strength Analysis
        print("💰 FINANCIAL STRENGTH ANALYSIS")
        print(f"   • Debt Service Coverage: {financial_metrics['debt_service_coverage']:.2f}x")
        print(f"   • Current Ratio: {financial_metrics['current_ratio']:.2f}")
        print(f"   • Debt-to-Equity: {financial_metrics['debt_to_equity']:.2f}")
        print(f"   • Operating Margin: {financial_metrics['operating_margin']:.1%}")
        print()
        
        # Business Operations Assessment
        print("🏭 BUSINESS OPERATIONS ASSESSMENT")
        print(f"   • Management Depth: {operational_assessment['management_depth'].title()}")
        print(f"   • Management Experience: {operational_assessment['management_experience']} years")
        print(f"   • Business Model Strength: {operational_assessment['business_model_strength'].title()}")
        print(f"   • Customer Concentration: {operational_assessment['customer_concentration']:.1%}")
        print()
        
        # Risk Assessment
        print("⚠️  RISK ASSESSMENT")
        print(f"   • Overall Risk Score: {insights['overall_risk_score']:.0f}/100")
        print(f"   • Risk Flags Identified: {len(risk_flags)}")
        
        if risk_flags:
            print("   • Key Risk Factors:")
            for flag in risk_flags[:3]:  # Show top 3 risks
                print(f"     - {flag['category'].title()}: {flag['description']}")
        print()
        
        # AI Recommendation
        print("🎯 AI RECOMMENDATION")
        decision_color = "🟢" if recommendation['decision'] == 'approve' else "🟡" if recommendation['decision'] == 'conditional_approve' else "🔴"
        print(f"   • Decision: {decision_color} {recommendation['decision'].replace('_', ' ').title()}")
        print(f"   • Confidence: {recommendation['confidence_score']:.1%}")
        
        if recommendation.get('recommended_amount'):
            print(f"   • Recommended Amount: ${recommendation['recommended_amount']:,.0f}")
        if recommendation.get('recommended_rate'):
            print(f"   • Recommended Rate: {recommendation['recommended_rate']:.2f}%")
        print()

    def _display_enhanced_business_analysis(self, application: Dict[str, Any], insights: Dict[str, Any]):
        """Display enhanced business analysis with more detail"""
        
        company_name = application["company_name"]
        recommendation = insights["recommendation"]
        financial_metrics = insights["financial_metrics"]
        operational_assessment = insights["operational_assessment"]
        risk_flags = insights["risk_flags"]
        
        print_subsection(f"🏢 COMPREHENSIVE BUSINESS ANALYSIS: {company_name}")
        print(f"Application ID: {insights['application_id']}")
        
        # Financial Strength Analysis
        print_subsection("💰 FINANCIAL STRENGTH METRICS")
        dscr = financial_metrics['debt_service_coverage']
        dscr_status = "✅ Strong" if dscr >= 1.25 else "⚠️ Adequate" if dscr >= 1.0 else "❌ Weak"
        print(f"   • Debt Service Coverage: {dscr:.2f}x ({dscr_status})")
        
        current_ratio = financial_metrics['current_ratio']
        cr_status = "✅ Strong" if current_ratio >= 1.5 else "⚠️ Adequate" if current_ratio >= 1.0 else "❌ Weak"
        print(f"   • Current Ratio: {current_ratio:.2f} ({cr_status})")
        
        print(f"   • Debt-to-Equity: {financial_metrics['debt_to_equity']:.2f}")
        print(f"   • Operating Margin: {financial_metrics['operating_margin']:.1%}")
        print(f"   • Working Capital: ${financial_metrics.get('working_capital', 0):,}")
        
        # Business Operations Deep Dive
        print_subsection("🏭 BUSINESS OPERATIONS DEEP DIVE")
        print(f"   • Management Depth: {operational_assessment['management_depth'].title()}")
        print(f"   • Management Experience: {operational_assessment['management_experience']} years")
        print(f"   • Business Model Strength: {operational_assessment['business_model_strength'].title()}")
        print(f"   • Customer Concentration: {operational_assessment['customer_concentration']:.1%}")
        print(f"   • Market Position: {operational_assessment.get('market_position', 'Established')}")
        
        # Industry Intelligence
        print_subsection("📊 INDUSTRY INTELLIGENCE")
        industry_data = insights.get('industry_analysis', {})
        print(f"   • Industry Risk Level: {industry_data.get('risk_level', 'Medium')}")
        print(f"   • Market Outlook: {industry_data.get('market_outlook', 'Stable')}")
        print(f"   • Cyclical Sensitivity: {industry_data.get('cyclical_sensitivity', 'Moderate')}")
        
        # Risk Assessment
        print_subsection("⚠️  COMPREHENSIVE RISK ASSESSMENT")
        risk_score = insights['overall_risk_score']
        risk_level = get_risk_level_color(risk_score)
        print(f"   • Overall Risk Score: {risk_score:.0f}/100 ({risk_level})")
        print(f"   • Risk Flags Identified: {len(risk_flags)}")
        
        if risk_flags:
            print("   • Key Commercial Risk Factors:")
            for flag in risk_flags[:4]:  # Show top 4 risks
                severity_icon = "🔴" if flag['severity'] == 'high' else "🟡" if flag['severity'] == 'medium' else "🟢"
                print(f"     {severity_icon} {flag['category'].title()}: {flag['description']}")
        
        # AI Recommendation with Business Context
        print_subsection("🎯 AI COMMERCIAL LENDING RECOMMENDATION")
        decision = recommendation['decision']
        decision_icon = get_recommendation_icon(decision)
        print(f"   • Decision: {decision_icon} {decision.replace('_', ' ').title()}")
        print(f"   • Confidence: {recommendation['confidence_score']:.1%}")
        
        if recommendation.get('recommended_amount'):
            print(f"   • Recommended Amount: ${recommendation['recommended_amount']:,.0f}")
        if recommendation.get('recommended_rate'):
            print(f"   • Recommended Rate: {recommendation['recommended_rate']:.2f}%")
        if recommendation.get('recommended_term'):
            print(f"   • Recommended Term: {recommendation['recommended_term']} months")
        
        # Alternative Structures
        if insights.get('alternative_structures'):
            print_subsection("🔄 ALTERNATIVE FINANCING STRUCTURES")
            for structure in insights['alternative_structures'][:2]:
                print(f"   • {structure['structure']}")
                if 'benefits' in structure:
                    print(f"     Benefits: {', '.join(structure['benefits'][:2])}")
                if 'requirements' in structure:
                    print(f"     Requirements: {', '.join(structure['requirements'][:2])}")

    async def _demo_cross_selling_insights(self, portfolio_insights: List[Dict[str, Any]]):
        """Demonstrate cross-selling opportunity identification"""
        
        print_section_header("💼 RELATIONSHIP BANKING & CROSS-SELLING INSIGHTS")
        
        cross_selling_opportunities = []
        total_relationship_value = 0
        
        for insights in portfolio_insights:
            if insights['recommendation']['decision'] in ['approve', 'conditional_approve']:
                # Generate cross-selling opportunities
                company_data = {
                    'name': insights.get('company_name', 'Business'),
                    'industry': insights.get('industry_type', 'general'),
                    'revenue': insights.get('annual_revenue', 0),
                    'employees': insights.get('number_of_employees', 0)
                }
                
                opportunities = self._generate_cross_selling_opportunities(company_data)
                cross_selling_opportunities.extend(opportunities)
                
                for opp in opportunities:
                    total_relationship_value += opp['annual_revenue_potential']
        
        print(f"Total Cross-Selling Opportunities Identified: {len(cross_selling_opportunities)}")
        print(f"Total Additional Revenue Potential: ${total_relationship_value:,.0f}")
        print()
        
        # Display top opportunities
        print_subsection("🎯 TOP CROSS-SELLING OPPORTUNITIES")
        sorted_opportunities = sorted(cross_selling_opportunities, 
                                    key=lambda x: x['annual_revenue_potential'], reverse=True)
        
        for i, opp in enumerate(sorted_opportunities[:5], 1):
            print(f"{i}. {opp['product_name']}")
            print(f"   Company: {opp['company_name']}")
            print(f"   Reason: {opp['rationale']}")
            print(f"   Revenue Potential: ${opp['annual_revenue_potential']:,}/year")
            print(f"   Probability: {opp['probability']:.0%}")
            print()

    def _generate_cross_selling_opportunities(self, company_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate cross-selling opportunities based on company profile"""
        
        opportunities = []
        
        # Cash Management Services
        if company_data['revenue'] > 1000000:
            opportunities.append({
                'company_name': company_data['name'],
                'product_name': 'Commercial Cash Management',
                'rationale': 'High revenue suggests complex cash flow needs',
                'annual_revenue_potential': 12000 + (company_data['revenue'] * 0.001),
                'probability': 0.75
            })
        
        # Payroll Services
        if company_data['employees'] > 20:
            opportunities.append({
                'company_name': company_data['name'],
                'product_name': 'Payroll Processing Services',
                'rationale': f'Company has {company_data["employees"]} employees',
                'annual_revenue_potential': company_data['employees'] * 180,
                'probability': 0.65
            })
        
        # Trade Finance (for manufacturers)
        if company_data['industry'] == 'manufacturing':
            opportunities.append({
                'company_name': company_data['name'],
                'product_name': 'Trade Finance Solutions',
                'rationale': 'Manufacturing typically involves supplier/vendor financing',
                'annual_revenue_potential': 25000,
                'probability': 0.60
            })
        
        # Equipment Financing
        if company_data['industry'] in ['construction', 'manufacturing']:
            opportunities.append({
                'company_name': company_data['name'],
                'product_name': 'Equipment Financing Line',
                'rationale': 'Industry requires ongoing equipment investment',
                'annual_revenue_potential': 18000,
                'probability': 0.70
            })
        
        return opportunities

    async def _demo_business_override(self, application: Dict[str, Any]):
        """Demonstrate human override capabilities for business banking"""
        
        print_section_header("👨‍💼 HUMAN OVERRIDE DEMONSTRATION")
        print(f"""
Commercial underwriters maintain full authority over final lending decisions.
The AI provides sophisticated analysis and recommendations, but humans make
the final call based on relationship considerations, market conditions,
and strategic priorities.

Example Override Scenario: {application['company_name']}
        """)
        
        print_subsection("🔄 OVERRIDE OPTIONS AVAILABLE")
        print("1. ✅ Approve Despite AI Caution")
        print("   - Relationship value justifies risk")
        print("   - Additional collateral obtained")
        print("   - Management track record override")
        print()
        
        print("2. ⚠️ Modify Terms and Conditions")
        print("   - Adjust loan amount or pricing")
        print("   - Add covenant requirements")
        print("   - Require additional guarantees")
        print()
        
        print("3. 🔄 Counter-Propose Alternative Structure")
        print("   - Suggest equipment financing instead")
        print("   - Recommend SBA loan structure")
        print("   - Propose line of credit alternative")
        print()
        
        print("4. 🤝 Escalate for Relationship Review")
        print("   - Senior underwriter assessment")
        print("   - Relationship manager input")
        print("   - Committee review for large exposures")
        print()
        
        print_subsection("📋 OVERRIDE JUSTIFICATION REQUIRED")
        print("✅ All overrides require detailed business justification")
        print("✅ Complete audit trail maintained for regulators")
        print("✅ Risk committee notification for significant overrides")
        print("✅ Relationship profitability analysis documented")

    async def _display_portfolio_analytics(self, portfolio_insights: List[Dict[str, Any]]):
        """Display portfolio-level analytics"""
        
        print_section_header("📊 BUSINESS BANKING PORTFOLIO ANALYTICS")
        
        # Try to get live portfolio data from API if server is running
        if check_server_status():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{BUSINESS_API}/portfolio/summary", timeout=10.0)
                    
                    if response.status_code == 200:
                        portfolio_data = response.json()
                        portfolio_summary = portfolio_data["portfolio_summary"]
                        
                        print(f"📈 LIVE PORTFOLIO SUMMARY (From API)")
                        print(f"   • Total Applications Processed: {portfolio_summary['total_applications']}")
                        print(f"   • Total Recommended Exposure: ${portfolio_summary['total_exposure']:,.0f}")
                        print(f"   • Average Portfolio Risk Score: {portfolio_summary['average_risk_score']}/100")
                        
                        decision_dist = portfolio_summary["decision_distribution"]
                        print(f"\n✅ DECISION DISTRIBUTION")
                        print(f"   • Approved: {decision_dist['approved']} applications")
                        print(f"   • Conditional: {decision_dist['conditional']} applications") 
                        print(f"   • Declined: {decision_dist['declined']} applications")
                        
                        if "key_insights" in portfolio_data:
                            print(f"\n💡 KEY PORTFOLIO INSIGHTS")
                            for insight in portfolio_data["key_insights"]:
                                print(f"   • {insight}")
                        
                        print(f"\n🌐 Access live portfolio analytics at:")
                        print(f"   {BUSINESS_API}/portfolio/summary")
                        return
                        
            except Exception as e:
                print(f"⚠️  Could not fetch live portfolio data: {str(e)}")
                print("   Showing local demo analytics instead...")
        
        # Fallback to local analytics if API not available
        if not portfolio_insights:
            print("No applications processed in this session.")
            return
        
        # Portfolio composition
        decisions = {"approve": 0, "conditional_approve": 0, "decline": 0}
        risk_scores = []
        total_exposure = 0
        
        for insight in portfolio_insights:
            # Decision distribution
            decision = insight.get('recommendation', {}).get('decision', 'unknown')
            decisions[decision] = decisions.get(decision, 0) + 1
            
            # Risk scoring
            risk_score = insight.get('overall_risk_score', 0)
            risk_scores.append(risk_score)
            
            # Total exposure
            if insight.get('recommendation', {}).get('recommended_amount'):
                total_exposure += insight['recommendation']['recommended_amount']
        
        print(f"📈 PORTFOLIO OVERVIEW (Local Demo Data)")
        print(f"   • Total Applications: {len(portfolio_insights)}")
        print(f"   • Total Recommended Exposure: ${total_exposure:,.0f}")
        if risk_scores:
            print(f"   • Average Risk Score: {sum(risk_scores)/len(risk_scores):.1f}/100")
        print()
        
        print("✅ DECISION DISTRIBUTION")
        for decision, count in decisions.items():
            if count > 0:
                percentage = (count / len(portfolio_insights)) * 100
                print(f"   • {decision.replace('_', ' ').title()}: {count} ({percentage:.0f}%)")
        print()


async def main():
    """Run the business banking underwriter demo"""
    
    demo = BusinessBankingDemo()
    
    try:
        await demo.run_comprehensive_demo()
        
        print("\n" + "="*80)
        print("🏆 BUSINESS BANKING AUGMENTED UNDERWRITER DEMO COMPLETE")
        print()
        print("Key Benefits Demonstrated:")
        print("✅ Industry-specific risk assessment and modeling")
        print("✅ Comprehensive business analysis beyond just financials")
        print("✅ Portfolio-level insights and cross-selling opportunities")
        print("✅ Alternative structure suggestions and optimization")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Demo error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main()) 