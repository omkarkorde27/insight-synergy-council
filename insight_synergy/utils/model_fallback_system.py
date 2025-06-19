# Copyright 2025 Google LLC
# Licensed under the Apache License, Version 2.0

"""Model fallback system for handling unavailable models."""

import os
from typing import Dict, List

class ModelFallbackManager:
    """Manages model fallbacks when preferred models are unavailable."""
    
    def __init__(self):
        self.fallback_chains = {
            # Optimist agent fallbacks (positive, growth-focused)
            "optimist": [
                "claude-3-5-sonnet-20240620",  # Primary: Great at nuanced analysis
                "gemini-1.5-pro",              # Fallback 1: Strong reasoning
                "gpt-4",                       # Fallback 2: Reliable performance
                "gemini-2.0-flash-001"         # Final fallback: Always available
            ],
            
            # Pessimist agent fallbacks (critical, risk-focused)
            "pessimist": [
                "grok-1",                      # Primary: Direct, unfiltered analysis
                "claude-3-5-sonnet-20240620",  # Fallback 1: Good at critical thinking
                "gpt-4",                       # Fallback 2: Thorough analysis
                "gemini-2.0-flash-001"         # Final fallback: Always available
            ],
            
            # Ethical auditor fallbacks (bias detection, fairness)
            "ethical": [
                "gpt-4",                       # Primary: Strong ethical reasoning
                "claude-3-5-sonnet-20240620",  # Fallback 1: Good at nuanced ethics
                "gemini-1.5-pro",              # Fallback 2: Reliable analysis
                "gemini-2.0-flash-001"         # Final fallback: Always available
            ],
            
            # Synthesis moderator fallbacks (integration, consensus)
            "synthesis": [
                "gemini-1.5-pro",              # Primary: Excellent at synthesis
                "claude-3-5-sonnet-20240620",  # Fallback 1: Good at integration
                "gpt-4",                       # Fallback 2: Reliable consensus
                "gemini-2.0-flash-001"         # Final fallback: Always available
            ]
        }
        
        self.available_models = self._check_available_models()
    
    def _check_available_models(self) -> List[str]:
        """Check which models are actually available."""
        available = []
        
        # Google models (always available if Google Cloud is configured)
        if os.getenv("GOOGLE_CLOUD_PROJECT"):
            available.extend([
                "gemini-2.0-flash-001",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-pro"
            ])
        
        # Claude models
        if os.getenv("CLAUDE_API_KEY"):
            available.extend([
                "claude-3-5-sonnet-20240620",
                "claude-3-opus-20240229",
                "claude-3-haiku-20240307"
            ])
        
        # OpenAI models
        if os.getenv("OPENAI_API_KEY"):
            available.extend([
                "gpt-4",
                "gpt-4-turbo",
                "gpt-3.5-turbo"
            ])
        
        # Grok models (check if API is available)
        if os.getenv("GROK_API_KEY"):
            # Note: Grok might not be publicly available yet
            try:
                # Add actual availability check here when Grok API is released
                available.append("grok-1")
            except:
                pass
        
        return available
    
    def get_best_available_model(self, agent_type: str, preferred_model: str = None) -> str:
        """Get the best available model for an agent type."""
        
        # If a specific model is preferred and available, use it
        if preferred_model and preferred_model in self.available_models:
            return preferred_model
        
        # Use fallback chain for the agent type
        fallback_chain = self.fallback_chains.get(agent_type, ["gemini-2.0-flash-001"])
        
        for model in fallback_chain:
            if model in self.available_models:
                if model != preferred_model:
                    print(f"⚠️  Using fallback model {model} for {agent_type} agent (preferred: {preferred_model})")
                return model
        
        # Ultimate fallback
        print(f"⚠️  Using ultimate fallback gemini-2.0-flash-001 for {agent_type} agent")
        return "gemini-2.0-flash-001"
    
    def get_agent_model_config(self) -> Dict[str, str]:
        """Get the optimal model configuration for all agents."""
        
        config = {
            "optimist": self.get_best_available_model("optimist", os.getenv("OPTIMIST_MODEL")),
            "pessimist": self.get_best_available_model("pessimist", os.getenv("PESSIMIST_MODEL")),
            "ethical": self.get_best_available_model("ethical", os.getenv("ETHICAL_AUDITOR_MODEL")),
            "synthesis": self.get_best_available_model("synthesis", os.getenv("SYNTHESIS_MODEL"))
        }
        
        return config
    
    def print_model_status(self):
        """Print current model availability and assignments."""
        print("\n=== Model Availability Status ===")
        print(f"Available models: {len(self.available_models)}")
        for model in self.available_models:
            print(f"  ✓ {model}")
        
        print(f"\nUnavailable models:")
        all_models = set()
        for chain in self.fallback_chains.values():
            all_models.update(chain)
        
        unavailable = all_models - set(self.available_models)
        for model in unavailable:
            print(f"  ✗ {model}")
        
        print(f"\n=== Final Agent Assignments ===")
        config = self.get_agent_model_config()
        for agent, model in config.items():
            preferred = os.getenv(f"{agent.upper()}_MODEL")
            status = "✓" if model == preferred else "⚠️ (fallback)"
            print(f"  {agent.capitalize()}: {model} {status}")

# Global instance
fallback_manager = ModelFallbackManager()

def get_optimal_model_for_agent(agent_type: str) -> str:
    """Get the optimal available model for a specific agent type."""
    return fallback_manager.get_best_available_model(agent_type)

def check_model_status():
    """Check and print model availability status."""
    fallback_manager.print_model_status()
    return fallback_manager.get_agent_model_config()

if __name__ == "__main__":
    check_model_status()