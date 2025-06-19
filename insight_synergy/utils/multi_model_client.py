# Copyright 2025 Google LLC
# Licensed under the Apache License, Version 2.0

"""Multi-Model Client Manager for handling different API providers."""

import os
from typing import Any, Dict, Optional
from google.genai import Client as GeminiClient

class MultiModelClientManager:
    """Manages connections to different model providers."""
    
    def __init__(self):
        self.clients = {}
        self._setup_clients()
    
    def _setup_clients(self):
        """Initialize clients for available model providers."""
        
        # Google Gemini Client (Vertex AI)
        if os.getenv("GOOGLE_CLOUD_PROJECT"):
            try:
                self.clients["gemini"] = GeminiClient(
                    vertexai=True,
                    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
                    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
                )
                print("✓ Google Gemini client initialized")
            except Exception as e:
                print(f"✗ Failed to initialize Gemini client: {e}")
        
        # Claude Client (Anthropic)
        if os.getenv("CLAUDE_API_KEY"):
            try:
                import anthropic
                self.clients["claude"] = anthropic.Anthropic(
                    api_key=os.getenv("CLAUDE_API_KEY")
                )
                print("✓ Claude client initialized")
            except ImportError:
                print("✗ Anthropic package not installed. Run: pip install anthropic")
            except Exception as e:
                print(f"✗ Failed to initialize Claude client: {e}")
        
        # OpenAI Client (GPT-4)
        if os.getenv("OPENAI_API_KEY"):
            try:
                import openai
                self.clients["openai"] = openai.OpenAI(
                    api_key=os.getenv("OPENAI_API_KEY")
                )
                print("✓ OpenAI client initialized")
            except ImportError:
                print("✗ OpenAI package not installed. Run: pip install openai")
            except Exception as e:
                print(f"✗ Failed to initialize OpenAI client: {e}")
        
        # Grok Client (if available)
        if os.getenv("GROK_API_KEY"):
            try:
                # Note: Replace with actual Grok client when available
                print("✓ Grok API key found (client implementation needed)")
            except Exception as e:
                print(f"✗ Failed to initialize Grok client: {e}")
    
    def get_client(self, model_name: str) -> Optional[Any]:
        """Get the appropriate client for a given model."""
        
        model_provider_map = {
            # Gemini models
            "gemini-2.0-flash-001": "gemini",
            "gemini-1.5-pro": "gemini", 
            "gemini-1.5-flash": "gemini",
            "gemini-pro": "gemini",
            
            # Claude models
            "claude-3-5-sonnet-20240620": "claude",
            "claude-3-opus-20240229": "claude",
            "claude-3-haiku-20240307": "claude",
            
            # OpenAI models
            "gpt-4": "openai",
            "gpt-4-turbo": "openai",
            "gpt-3.5-turbo": "openai",
            
            # Grok models
            "grok-1": "grok"
        }
        
        provider = model_provider_map.get(model_name)
        if provider and provider in self.clients:
            return self.clients[provider]
        
        # Fallback to Gemini if available
        return self.clients.get("gemini")
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a model is available."""
        return self.get_client(model_name) is not None
    
    def get_available_models(self) -> Dict[str, list]:
        """Get list of available models by provider."""
        available = {}
        
        if "gemini" in self.clients:
            available["gemini"] = [
                "gemini-2.0-flash-001",
                "gemini-1.5-pro", 
                "gemini-1.5-flash",
                "gemini-pro"
            ]
        
        if "claude" in self.clients:
            available["claude"] = [
                "claude-3-5-sonnet-20240620",
                "claude-3-opus-20240229",
                "claude-3-haiku-20240307"
            ]
        
        if "openai" in self.clients:
            available["openai"] = [
                "gpt-4",
                "gpt-4-turbo", 
                "gpt-3.5-turbo"
            ]
        
        if "grok" in self.clients:
            available["grok"] = ["grok-1"]
        
        return available

# Global instance
model_manager = MultiModelClientManager()

def get_model_client(model_name: str):
    """Get client for a specific model."""
    return model_manager.get_client(model_name)

def check_model_availability():
    """Check which models are available in the current environment."""
    available = model_manager.get_available_models()
    
    print("\n=== Available Models ===")
    for provider, models in available.items():
        print(f"{provider.upper()}:")
        for model in models:
            print(f"  ✓ {model}")
    
    print(f"\nEnvironment Variables Set:")
    print(f"  GOOGLE_CLOUD_PROJECT: {'✓' if os.getenv('GOOGLE_CLOUD_PROJECT') else '✗'}")
    print(f"  CLAUDE_API_KEY: {'✓' if os.getenv('CLAUDE_API_KEY') else '✗'}")
    print(f"  OPENAI_API_KEY: {'✓' if os.getenv('OPENAI_API_KEY') else '✗'}")
    print(f"  GROK_API_KEY: {'✓' if os.getenv('GROK_API_KEY') else '✗'}")
    
    return available

if __name__ == "__main__":
    check_model_availability()