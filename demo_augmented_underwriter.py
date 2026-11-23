#!/usr/bin/env python3
"""
Demo script for the Augmented Underwriter Agent

This script demonstrates the capabilities of the AI-powered underwriter that enhances
human decision-making with automated insights, risk analysis, and decision support.
"""

import asyncio
import json
from datetime import datetime
import requests
from typing import Dict, Any
import structlog

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
UNDERWRITER_API = f"{BASE_URL}/underwriter"

def print_section_header(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n--- {title} ---")

async def demo_augmented_underwriter():
    """Main demo function showcasing the Augmented Underwriter Agent"""
    
    print_section_header("🤖 AUGMENTED UNDERWRITER AGENT DEMO")
    print("""
This demo showcases an AI agent that ENHANCES human underwriter capabilities
rather than replacing them. The agent provides:

✅ Automated data synthesis and risk identification
✅ Policy compliance checking with full transparency  
✅ Clear, justified recommendations with audit trails
✅ Human override capabilities maintaining final authority
✅ Complete explainability for regulatory compliance

Let's see it in action!
    """)
    
    # Sample application scenarios
    applications = [
        {
            "application_id": "APP-2024-001",
            "scenario": "Excellent Credit Application",
            "data": {
                "application_id": "APP-2024-001",
                "applicant_name": "Sarah Chen",
                "credit_score": 780,
                "annual_income": 125000,
                "monthly_debt_payments": 2800,
                "requested_loan_amount": 400000,
                "property_value": 520000,
                "employment_status": "full_time",
                "years_employed": 5,
                "loan_purpose": "home_purchase",
                "total_assets": 180000,
                "total_liabilities": 55000,
                "bankruptcy_history": False,
                "foreclosure_history": False,
                "late_payments": 0,
                "income_verification_provided": True,
                "employment_verification_provided": True,
                "asset_verification_provided": True,
                "identity_verification_provided": True
            }
        },
        {
            "application_id": "APP-2024-002", 
            "scenario": "Moderate Risk Application",
            "data": {
                "application_id": "APP-2024-002",
                "applicant_name": "Michael Rodriguez",
                "credit_score": 680,
                "annual_income": 72000,
                "monthly_debt_payments": 2400,
                "requested_loan_amount": 350000,
                "property_value": 380000,
                "employment_status": "full_time",
                "years_employed": 1.5,
                "loan_purpose": "home_purchase",
                "total_assets": 85000,
                "total_liabilities": 95000,
                "bankruptcy_history": False,
                "foreclosure_history": False,
                "late_payments": 2,
                "income_verification_provided": True,
                "employment_verification_provided": True,
                "asset_verification_provided": False,
                "identity_verification_provided": True
            }
        },
        {
            "application_id": "APP-2024-003",
            "scenario": "High Risk Application", 
            "data": {
                "application_id": "APP-2024-003",
                "applicant_name": "Jennifer Adams",
                "credit_score": 590,
                "annual_income": 48000,
                "monthly_debt_payments": 2100,
                "requested_loan_amount": 280000,
                "property_value": 300000,
                "employment_status": "part_time",
                "years_employed": 0.8,
                "loan_purpose": "home_purchase",
                "total_assets": 25000,
                "total_liabilities": 78000,
                "bankruptcy_history": True,
                "foreclosure_history": False,
                "late_payments": 5,
                "income_verification_provided": False,
                "employment_verification_provided": False,
                "asset_verification_provided": False,
                "identity_verification_provided": True
            }
        }
    ]
    
    # Process each application
    for app_info in applications:
        await process_application_demo(app_info["application_id"], app_info["scenario"], app_info["data"])
        
        # Add a pause between applications
        print("\n" + "-"*60)
        input("Press Enter to continue to next application...")
    
    # Show portfolio summary
    await demo_portfolio_summary()
    
    # Show human override capabilities
    await demo_human_override(applications[1]["application_id"]) # Use moderate risk app
    
    print_section_header("🎉 DEMO COMPLETED")
    print("""
The Augmented Underwriter Agent successfully demonstrated:

✅ Comprehensive risk analysis with transparent reasoning
✅ Policy compliance verification with detailed explanations  
✅ Clear recommendations while preserving human judgment
✅ Complete audit trails for regulatory compliance
✅ Human override capabilities maintaining final authority

This AI system truly augments human underwriters rather than replacing them,
making them faster, more accurate, and more confident in their decisions!

Dashboard URL: http://localhost:8000/underwriter/dashboard
    """)

async def process_application_demo(app_id: str, scenario: str, app_data: Dict[str, Any]):
    """Process a single application and display results"""
    
    print_section_header(f"📋 PROCESSING: {scenario}")
    print(f"Application ID: {app_id}")
    print(f"Applicant: {app_data['applicant_name']}")
    print(f"Credit Score: {app_data['credit_score']}")
    print(f"Requested Amount: ${app_data['requested_loan_amount']:,}")
    print(f"DTI Ratio: {(app_data['monthly_debt_payments'] * 12 / app_data['annual_income']):.1%}")
    
    try:
        # Make API call to analyze the application
        print("\n🤖 AI Agent is analyzing application...")
        
        # Simulate the API call (since we're in demo mode)
        from src.agents.augmented_underwriter import AugmentedUnderwriterAgent
        agent = AugmentedUnderwriterAgent() 
        insight = await agent.analyze_application(app_data)
        
        # Display results
        print_subsection("📊 RISK ANALYSIS RESULTS")
        print(f"Overall Risk Score: {insight.risk_score:.1f}/100")
        print(f"Risk Level: {get_risk_level(insight.risk_score)}")
        print(f"AI Recommendation: {insight.decision_recommendation.recommendation.value.replace('_', ' ').title()}")
        print(f"Confidence Level: {insight.decision_recommendation.confidence:.1%}")
        
        # Show risk flags
        if insight.risk_flags:
            print_subsection("⚠️  RISK FLAGS IDENTIFIED")
            for i, flag in enumerate(insight.risk_flags, 1):
                severity_icon = get_severity_icon(flag.severity.value)
                print(f"{i}. {severity_icon} {flag.title}")
                print(f"   Category: {flag.category}")
                print(f"   Description: {flag.description}")
                print(f"   Confidence: {flag.confidence:.1%}")
                print(f"   Data Source: {flag.data_source}")
                if flag.policy_reference:
                    print(f"   Policy Reference: {flag.policy_reference}")
                print()
        else:
            print("✅ No significant risk flags identified")
        
        # Show decision rationale
        print_subsection("💡 DECISION RATIONALE")
        print("Primary Factors:")
        for factor in insight.decision_recommendation.primary_factors:
            print(f"  • {factor}")
        
        if insight.decision_recommendation.supporting_evidence:
            print("\nSupporting Evidence:")
            for evidence in insight.decision_recommendation.supporting_evidence:
                print(f"  • {evidence}")
        
        # Show policy compliance
        print_subsection("📋 POLICY COMPLIANCE CHECK")
        for check in insight.decision_recommendation.policy_alignment:
            status_icon = "✅" if check.status == "compliant" else "❌"
            print(f"{status_icon} {check.policy_name}: {check.status.upper()}")
            print(f"   Details: {check.details}")
        
        # Show suggested conditions
        if insight.suggested_conditions:
            print_subsection("📝 SUGGESTED CONDITIONS")
            for i, condition in enumerate(insight.suggested_conditions, 1):
                print(f"{i}. {condition}")
        
        # Show next actions
        print_subsection("🎯 RECOMMENDED NEXT ACTIONS")
        for i, action in enumerate(insight.next_actions, 1):
            print(f"{i}. {action}")
        
        # Show audit trail
        print_subsection("📜 AUDIT TRAIL")
        for event in insight.audit_trail:
            timestamp = datetime.fromisoformat(event['timestamp']).strftime("%H:%M:%S")
            print(f"[{timestamp}] {event['phase']}: {event['details']}")
        
        print(f"\n⏱️  Total Processing Time: {(datetime.now() - insight.timestamp).total_seconds():.2f} seconds")
        
    except Exception as e:
        print(f"❌ Error processing application: {str(e)}")

async def demo_portfolio_summary():
    """Demonstrate portfolio-level insights"""
    
    print_section_header("📊 PORTFOLIO INSIGHTS & ANALYTICS")
    print("""
The Augmented Underwriter Agent also provides portfolio-level insights
to help manage risk concentration and monitor performance trends.
    """)
    
    # Mock portfolio data for demo
    portfolio_data = {
        "total_applications": 3,
        "average_risk_score": 45.7,
        "recommendations_breakdown": {
            "approve": 1,
            "approve_with_conditions": 1, 
            "decline": 1
        },
        "risk_flag_categories": {
            "credit_risk": 2,
            "financial_risk": 2,
            "employment_risk": 1,
            "fraud_risk": 0
        },
        "ai_efficiency_metrics": {
            "avg_processing_time": "2.1 seconds",
            "automation_rate": "87%",
            "human_override_rate": "8%"
        }
    }
    
    print(f"📈 Total Applications Processed: {portfolio_data['total_applications']}")
    print(f"📊 Average Risk Score: {portfolio_data['average_risk_score']}")
    
    print("\n🎯 Recommendation Breakdown:")
    for rec, count in portfolio_data['recommendations_breakdown'].items():
        percentage = (count / portfolio_data['total_applications']) * 100
        print(f"  • {rec.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
    
    print("\n⚠️  Risk Flag Categories:")
    for category, count in portfolio_data['risk_flag_categories'].items():
        print(f"  • {category.replace('_', ' ').title()}: {count}")
    
    print("\n🚀 AI Efficiency Metrics:")
    for metric, value in portfolio_data['ai_efficiency_metrics'].items():
        print(f"  • {metric.replace('_', ' ').title()}: {value}")

async def demo_human_override(app_id: str):
    """Demonstrate human override capabilities"""
    
    print_section_header("👤 HUMAN OVERRIDE DEMONSTRATION")
    print(f"""
A key principle of the Augmented Underwriter Agent is that humans always
maintain final authority. Let's demonstrate the override capabilities
for application {app_id}.
    """)
    
    print("🤖 AI Recommendation: Approve with Conditions")
    print("📝 AI Reasoning: Moderate DTI ratio requires additional verification")
    
    print("\n👤 Human Underwriter Decision Options:")
    print("1. Accept AI Recommendation") 
    print("2. Override to Full Approval")
    print("3. Override to Decline")
    print("4. Escalate to Senior Underwriter")
    print("5. Request Additional Information")
    
    # Simulate human override
    print("\n✅ Human Underwriter Selection: Override to Full Approval")
    print("📝 Justification: 'Customer has strong banking history with us and")
    print("    recent promotion provides income stability not captured in DTI calculation.'")
    
    # Create override audit entry
    override_info = {
        "timestamp": datetime.now().isoformat(),
        "underwriter_id": "UW_SARAH_JOHNSON",
        "original_recommendation": "approve_with_conditions",
        "override_decision": "approve",
        "justification": "Customer has strong banking history and recent promotion provides income stability",
        "confidence_level": "high"
    }
    
    print("\n📜 Override Audit Trail:")
    print(f"  Timestamp: {override_info['timestamp']}")
    print(f"  Underwriter: {override_info['underwriter_id']}")
    print(f"  Original AI Recommendation: {override_info['original_recommendation']}")
    print(f"  Human Override Decision: {override_info['override_decision']}")
    print(f"  Justification: {override_info['justification']}")
    
    print("\n✅ Human override successfully recorded with full audit trail!")
    print("   This maintains regulatory compliance while preserving human judgment.")

def get_risk_level(score: float) -> str:
    """Get risk level description from score"""
    if score < 25:
        return "🟢 Low Risk"
    elif score < 50:
        return "🟡 Medium Risk"
    elif score < 75:
        return "🟠 High Risk"
    else:
        return "🔴 Critical Risk"

def get_severity_icon(severity: str) -> str:
    """Get icon for risk flag severity"""
    icons = {
        "low": "🟢",
        "medium": "🟡", 
        "high": "🟠",
        "critical": "🔴"
    }
    return icons.get(severity, "⚪")

def check_server_status():
    """Check if the main server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🚀 Starting Augmented Underwriter Demo...")
    
    # Check if server is running
    if check_server_status():
        print("✅ Server is running")
        print("🌐 Dashboard available at: http://localhost:8000/underwriter/dashboard")
    else:
        print("⚠️  Server not detected - running in standalone mode")
        print("   To access full web interface, start the server with: python main.py")
    
    # Run the demo
    asyncio.run(demo_augmented_underwriter()) 