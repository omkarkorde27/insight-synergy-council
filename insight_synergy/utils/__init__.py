# Copyright 2025 Google LLC
# Licensed under the Apache License, Version 2.0

"""Utilities for InsightSynergy Council."""

try:
    from .multi_model_client import MultiModelClientManager, check_model_availability, get_model_client
except ImportError:
    print("Multi-model client not available. Install required dependencies: pip install anthropic openai")
    MultiModelClientManager = None
    check_model_availability = None
    get_model_client = None

try:
    from .model_fallback_system import ModelFallbackManager, get_optimal_model_for_agent, check_model_status
except ImportError:
    print("Model fallback system not available.")
    ModelFallbackManager = None
    get_optimal_model_for_agent = None
    check_model_status = None

# Import existing utilities if they exist
try:
    from .utils import get_env_var
except ImportError:
    # Create a simple get_env_var function if utils.py doesn't exist
    import os
    def get_env_var(var_name: str, default=None):
        """Get environment variable with optional default."""
        value = os.getenv(var_name, default)
        if value is None:
            raise ValueError(f"Environment variable {var_name} is required but not set")
        return value

__all__ = [
    "MultiModelClientManager",
    "check_model_availability", 
    "get_model_client",
    "ModelFallbackManager",
    "get_optimal_model_for_agent",
    "check_model_status",
    "get_env_var"
]