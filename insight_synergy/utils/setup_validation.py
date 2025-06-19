#!/usr/bin/env python3
# Copyright 2025 Google LLC
# Licensed under the Apache License, Version 2.0

"""
Setup validation script for InsightSynergy Council multi-model configuration.
Run this to check if your environment is properly configured.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file."""
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded environment from {env_path}")
    else:
        print(f"✗ No .env file found at {env_path}")
        return False
    return True

def check_google_cloud_config():
    """Check Google Cloud configuration."""
    print("\n=== Google Cloud Configuration ===")
    
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")
    
    print(f"Project: {project}")
    print(f"Location: {location}")
    print(f"Use Vertex AI: {use_vertex}")
    
    if not project:
        print("✗ GOOGLE_CLOUD_PROJECT not set")
        return False
    
    print("✓ Google Cloud configuration looks good")
    return True

def check_bigquery_config():
    """Check BigQuery configuration."""
    print("\n=== BigQuery Configuration ===")
    
    bq_project = os.getenv("BQ_PROJECT_ID")
    bq_dataset = os.getenv("BQ_DATASET_ID")
    
    print(f"Project: {bq_project}")
    print(f"Dataset: {bq_dataset}")
    
    if not bq_project or not bq_dataset:
        print("✗ BigQuery configuration incomplete")
        return False
    
    print("✓ BigQuery configuration looks good")
    return True

def check_api_keys():
    """Check API key configuration."""
    print("\n=== API Keys Configuration ===")
    
    api_keys = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "CLAUDE_API_KEY": os.getenv("CLAUDE_API_KEY"), 
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GROK_API_KEY": os.getenv("GROK_API_KEY")
    }
    
    for key_name, key_value in api_keys.items():
        if key_value:
            masked_key = key_value[:8] + "..." + key_value[-4:] if len(key_value) > 12 else "***"
            print(f"✓ {key_name}: {masked_key}")
        else:
            print(f"✗ {key_name}: Not set")
    
    # Check if at least Google Cloud is configured
    if not api_keys["GEMINI_API_KEY"] and not os.getenv("GOOGLE_CLOUD_PROJECT"):
        print("✗ No Google AI access configured (need either GEMINI_API_KEY or Google Cloud)")
        return False
    
    return True

def check_model_assignments():
    """Check model assignments for each agent."""
    print("\n=== Model Assignments ===")
    
    models = {
        "ROOT_AGENT_MODEL": os.getenv("ROOT_AGENT_MODEL"),
        "ANALYTICS_AGENT_MODEL": os.getenv("ANALYTICS_AGENT_MODEL"),
        "OPTIMIST_MODEL": os.getenv("OPTIMIST_MODEL"),
        "PESSIMIST_MODEL": os.getenv("PESSIMIST_MODEL"),
        "ETHICAL_AUDITOR_MODEL": os.getenv("ETHICAL_AUDITOR_MODEL"),
        "SYNTHESIS_MODEL": os.getenv("SYNTHESIS_MODEL"),
        "BIGQUERY_AGENT_MODEL": os.getenv("BIGQUERY_AGENT_MODEL"),
        "BASELINE_NL2SQL_MODEL": os.getenv("BASELINE_NL2SQL_MODEL")
    }
    
    for model_var, model_value in models.items():
        print(f"{model_var}: {model_value or 'Not set'}")
    
    # Check if critical models are set
    critical_models = ["ROOT_AGENT_MODEL", "ANALYTICS_AGENT_MODEL", "BIGQUERY_AGENT_MODEL"]
    missing_critical = [m for m in critical_models if not models[m]]
    
    if missing_critical:
        print(f"✗ Critical models not set: {missing_critical}")
        return False
    
    print("✓ Model assignments look good")
    return True

def check_optional_config():
    """Check optional configuration."""
    print("\n=== Optional Configuration ===")
    
    optional_vars = {
        "NL2SQL_METHOD": os.getenv("NL2SQL_METHOD"),
        "FAIRNESS_THRESHOLD": os.getenv("FAIRNESS_THRESHOLD"),
        "CONFLICT_ALERT_LEVEL": os.getenv("CONFLICT_ALERT_LEVEL"),
        "MAX_DEBATE_ROUNDS": os.getenv("MAX_DEBATE_ROUNDS"),
        "USE_COST_OPTIMIZATION": os.getenv("USE_COST_OPTIMIZATION"),
        "FALLBACK_MODEL": os.getenv("FALLBACK_MODEL")
    }
    
    for var_name, var_value in optional_vars.items():
        print(f"{var_name}: {var_value or 'Using default'}")
    
    return True

def check_dependencies():
    """Check if required packages are installed."""
    print("\n=== Dependencies Check ===")
    
    required_packages = [
        ("google-cloud-aiplatform", "Google Cloud AI Platform"),
        ("google-cloud-bigquery", "BigQuery"),
        ("google-genai", "Google GenAI"),
    ]
    
    optional_packages = [
        ("anthropic", "Claude API"),
        ("openai", "OpenAI API"),
        ("python-dotenv", "Environment management")
    ]
    
    all_good = True
    
    print("Required packages:")
    for package, description in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} ({description})")
        except ImportError:
            print(f"✗ {package} ({description}) - Run: pip install {package}")
            all_good = False
    
    print("\nOptional packages:")
    for package, description in optional_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} ({description})")
        except ImportError:
            print(f"⚠ {package} ({description}) - Install if needed: pip install {package}")
    
    return all_good

def main():
    """Main validation function."""
    print("=== InsightSynergy Council Setup Validation ===")
    
    checks = [
        ("Environment Loading", load_environment),
        ("Google Cloud Config", check_google_cloud_config),
        ("BigQuery Config", check_bigquery_config),
        ("API Keys", check_api_keys),
        ("Model Assignments", check_model_assignments),
        ("Optional Config", check_optional_config),
        ("Dependencies", check_dependencies)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"✗ Error in {check_name}: {e}")
            results.append((check_name, False))
    
    print("\n=== Summary ===")
    all_passed = True
    for check_name, passed in results:
        status = "✓" if passed else "✗"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! Your InsightSynergy Council is ready to use.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())