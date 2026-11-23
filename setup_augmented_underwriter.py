#!/usr/bin/env python3
"""
Setup script for the Augmented Underwriter Agent

This script helps you quickly set up and test the Augmented Underwriter Agent
in your Agentic LOS system.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_success(message):
    print(f"✅ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def check_dependencies():
    """Check if required dependencies are installed"""
    print_header("CHECKING DEPENDENCIES")
    
    required_packages = [
        'fastapi',
        'uvicorn', 
        'structlog',
        'langchain',
        'openai',
        'chromadb'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"{package} is installed")
        except ImportError:
            missing_packages.append(package)
            print_warning(f"{package} is missing")
    
    if missing_packages:
        print_info("Installing missing packages...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print_success("All dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please install manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

def verify_file_structure():
    """Verify all required files are in place"""
    print_header("VERIFYING FILE STRUCTURE")
    
    required_files = [
        "src/agents/augmented_underwriter.py",
        "templates/augmented_underwriter_dashboard.html", 
        "demo_augmented_underwriter.py",
        "main.py",
        "config.py"
    ]
    
    all_present = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"{file_path}")
        else:
            print_warning(f"{file_path} - MISSING")
            all_present = False
    
    return all_present

def create_sample_config():
    """Create sample configuration if needed"""
    print_header("CONFIGURATION SETUP")
    
    config_path = "config.py"
    if os.path.exists(config_path):
        print_success("Configuration file exists")
        return True
    
    print_info("Creating sample configuration...")
    
    sample_config = '''"""Configuration settings for Agentic LOS"""
import os
from pathlib import Path

class Settings:
    app_name = "Agentic LOS"
    app_version = "1.0.0"
    debug = True
    log_level = "INFO"
    
    # OpenAI Configuration
    openai_api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    
    # Database Configuration
    database_url = "sqlite:///./agentic_los.db"
    
    # RAG System Configuration
    vector_store_path = "./vector_store"
    rules_path = "./rules"
    
    # Security
    secret_key = "your-secret-key-here"

settings = Settings()
'''
    
    try:
        with open(config_path, 'w') as f:
            f.write(sample_config)
        print_success("Sample configuration created")
        print_info("Please update config.py with your actual API keys")
        return True
    except Exception as e:
        print(f"❌ Failed to create config: {e}")
        return False

def test_augmented_underwriter():
    """Test the Augmented Underwriter Agent"""
    print_header("TESTING AUGMENTED UNDERWRITER")
    
    try:
        # Import and test the agent
        from src.agents.augmented_underwriter import AugmentedUnderwriterAgent
        
        agent = AugmentedUnderwriterAgent()
        print_success("Agent initialized successfully")
        
        # Test with sample data
        sample_data = {
            "application_id": "TEST-001",
            "applicant_name": "Test Applicant",
            "credit_score": 720,
            "annual_income": 75000,
            "monthly_debt_payments": 2000,
            "requested_loan_amount": 300000,
            "property_value": 350000,
            "employment_status": "full_time",
            "years_employed": 3
        }
        
        print_info("Running test analysis...")
        import asyncio
        
        async def run_test():
            insight = await agent.analyze_application(sample_data)
            return insight
        
        insight = asyncio.run(run_test())
        print_success(f"Analysis completed - Risk Score: {insight.risk_score:.1f}")
        print_success(f"Recommendation: {insight.decision_recommendation.recommendation.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def show_quick_start():
    """Show quick start instructions"""
    print_header("🚀 QUICK START GUIDE")
    
    print("""
1. START THE SERVER:
   python main.py

2. OPEN THE DASHBOARD:
   http://localhost:8000/underwriter/dashboard

3. RUN THE DEMO:
   python demo_augmented_underwriter.py

4. API ENDPOINTS:
   POST /underwriter/analyze/{application_id}  - Analyze application
   GET  /underwriter/insights/{application_id} - Get stored insights  
   POST /underwriter/override/{application_id} - Submit human override
   GET  /underwriter/portfolio/summary         - Portfolio analytics

5. SAMPLE API CALL:
   curl -X POST "http://localhost:8000/underwriter/analyze/TEST-001" \\
        -H "Content-Type: application/json" \\
        -d '{"applicant_name": "John Doe", "credit_score": 720}'

6. DOCUMENTATION:
   See AUGMENTED_UNDERWRITER_GUIDE.md for complete documentation
    """)

def main():
    """Main setup function"""
    print_header("🤖 AUGMENTED UNDERWRITER SETUP")
    print("""
Welcome to the Augmented Underwriter Agent setup!

This AI agent enhances human underwriter capabilities with:
✅ Automated data synthesis and risk analysis
✅ Policy compliance checking with full transparency
✅ Clear recommendations while preserving human judgment  
✅ Complete audit trails for regulatory compliance
✅ Human override capabilities maintaining final authority

Let's get you set up!
    """)
    
    # Run setup steps
    steps = [
        ("Checking Dependencies", check_dependencies),
        ("Verifying File Structure", verify_file_structure), 
        ("Setting Up Configuration", create_sample_config),
        ("Testing Agent", test_augmented_underwriter)
    ]
    
    success_count = 0
    
    for step_name, step_func in steps:
        print_info(f"Running: {step_name}")
        if step_func():
            success_count += 1
        else:
            print_warning(f"Step failed: {step_name}")
    
    print_header("SETUP SUMMARY")
    
    if success_count == len(steps):
        print_success("🎉 Setup completed successfully!")
        print_success("Your Augmented Underwriter Agent is ready to use!")
        show_quick_start()
    else:
        print_warning(f"Setup completed with {len(steps) - success_count} issues")
        print_info("Please resolve the issues above before proceeding")
    
    print_header("NEXT STEPS")
    print("""
1. Review and update your configuration in config.py
2. Set your OpenAI API key in environment variables or config.py
3. Start the server: python main.py
4. Open the dashboard: http://localhost:8000/underwriter/dashboard
5. Run the demo: python demo_augmented_underwriter.py

For detailed documentation, see: AUGMENTED_UNDERWRITER_GUIDE.md
    """)

if __name__ == "__main__":
    main() 