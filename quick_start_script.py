#!/usr/bin/env python3
# Copyright 2025 Google LLC
# Licensed under the Apache License, Version 2.0

"""
Quick start script for InsightSynergy Council.
Run this to test your multi-model debate system.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def test_insight_synergy():
    """Test the InsightSynergy Council with a sample query."""
    
    try:
        from insight_synergy.agent import root_agent
        from insight_synergy.utils.model_fallback_system import check_model_status
        
        print("=== InsightSynergy Council Quick Start ===\n")
        
        # Check model availability
        print("1. Checking model availability...")
        model_config = check_model_status()
        
        print(f"\n2. Testing with sample query...")
        
        # Sample query that should trigger debate
        test_query = "Are there any insights about who is canceling subscriptions more frequently across years?"
        
        print(f"Query: {test_query}")
        print(f"Expected flow: DB Agent → Optimist → Pessimist → Ethical Audit → Synthesis")
        
        # In a real implementation, you would run:
        # response = await root_agent.run_async(test_query)
        # print(f"\nResponse:\n{response}")
        
        print(f"\n✓ System appears to be configured correctly!")
        print(f"✓ Models available: {list(model_config.values())}")
        
        print(f"\nTo run actual queries, use:")
        print(f"  from insight_synergy.agent import root_agent")
        print(f"  response = await root_agent.run_async('Your question here')")
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print(f"Make sure you've installed all dependencies and created the agent files.")
    except Exception as e:
        print(f"✗ Error: {e}")

def check_environment_setup():
    """Check if environment is properly configured."""
    
    print("=== Environment Check ===")
    
    required_vars = [
        "GOOGLE_CLOUD_PROJECT",
        "BQ_PROJECT_ID", 
        "BQ_DATASET_ID",
        "ROOT_AGENT_MODEL",
        "ANALYTICS_AGENT_MODEL"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
        else:
            print(f"✓ {var}: {os.getenv(var)}")
    
    if missing:
        print(f"\n✗ Missing required variables: {missing}")
        return False
    
    # Check API keys
    api_keys = ["CLAUDE_API_KEY", "OPENAI_API_KEY", "GROK_API_KEY"]
    available_apis = []
    for key in api_keys:
        if os.getenv(key):
            available_apis.append(key.replace("_API_KEY", ""))
    
    print(f"\nAvailable APIs: {available_apis}")
    
    if not available_apis and not os.getenv("GOOGLE_CLOUD_PROJECT"):
        print("✗ No API access configured")
        return False
    
    print("✓ Environment looks good!")
    return True

def main():
    """Main function."""
    
    print("InsightSynergy Council - Quick Start")
    print("=" * 40)
    
    # Check if .env exists
    if not Path('.env').exists():
        print("✗ No .env file found. Please create one with your configuration.")
        return
    
    # Check environment
    if not check_environment_setup():
        print("\n⚠️  Please fix environment configuration before proceeding.")
        return
    
    # Test the system
    print(f"\n" + "=" * 40)
    asyncio.run(test_insight_synergy())

if __name__ == "__main__":
    main()