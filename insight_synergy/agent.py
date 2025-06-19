# Copyright 2025 Google LLC
# Licensed under the Apache License, Version 2.0

"""InsightSynergy Council: Multi-Agent Debate-Driven Data Analysis

Main orchestrator agent with multi-model support for different debate agents.
"""

import os
from datetime import date
from google.genai import types
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import load_artifacts

from .sub_agents import db_agent
from .prompts import return_instructions_root
from .tools import (
    call_ds_agent,
    call_db_agent,
    call_optimist_agent,
    call_pessimist_agent,
    call_ethical_auditor_agent,
    call_synthesis_moderator_agent,
    initiate_council_debate,
)
from .sub_agents.bigquery.tools import (
    get_database_settings as get_bq_database_settings,
)

date_today = date.today()

def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the root agent with database and debate settings."""
    
    # setting up database settings in session.state
    if "database_settings" not in callback_context.state:
        db_settings = dict()
        db_settings["use_database"] = "BigQuery"
        callback_context.state["all_db_settings"] = db_settings
    
    if "debate_settings" not in callback_context.state:
        callback_context.state["debate_settings"] = {
            "max_rounds": int(os.getenv("MAX_DEBATE_ROUNDS", "3")),
            "conflict_threshold": int(os.getenv("CONFLICT_ALERT_LEVEL", "7")),
            "fairness_threshold": float(os.getenv("FAIRNESS_THRESHOLD", "0.85")),
            # Use the configured models from environment
            "models": {
                "orchestrator": os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-001"),
                "data_detective": os.getenv("BIGQUERY_AGENT_MODEL", "gemini-2.0-flash-001"),
                "data_science": os.getenv("ANALYTICS_AGENT_MODEL", "gemini-2.0-flash-001"),
                "optimist": os.getenv("OPTIMIST_MODEL", "claude-3-5-sonnet-20240620"),
                "pessimist": os.getenv("PESSIMIST_MODEL", "grok-1"), 
                "ethical": os.getenv("ETHICAL_AUDITOR_MODEL", "gpt-4"),
                "synthesis": os.getenv("SYNTHESIS_MODEL", "gemini-1.5-pro")
            },
            "cost_optimization": os.getenv("USE_COST_OPTIMIZATION", "true").lower() == "true",
            "fallback_model": os.getenv("FALLBACK_MODEL", "gemini-pro")
        }
    
    # Log the model configuration
    models = callback_context.state["debate_settings"]["models"]
    print(f"=== InsightSynergy Council Model Configuration ===")
    print(f"Orchestrator: {models['orchestrator']}")
    print(f"Data Detective: {models['data_detective']}")
    print(f"Data Science: {models['data_science']}")
    print(f"Optimist: {models['optimist']}")
    print(f"Pessimist: {models['pessimist']}")
    print(f"Ethical Auditor: {models['ethical']}")
    print(f"Synthesis: {models['synthesis']}")
    print(f"===============================================")
    
    # setting up schema in instruction
    if callback_context.state["all_db_settings"]["use_database"] == "BigQuery":
        callback_context.state["database_settings"] = get_bq_database_settings()
        schema = callback_context.state["database_settings"]["bq_ddl_schema"]

        callback_context._invocation_context.agent.instruction = (
            return_instructions_root()
            + f"""

    --------- The BigQuery schema of the relevant data with a few sample rows. ---------
    {schema}

    """
        )

# Use environment variable for main orchestrator agent
root_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-001"),
    name="insight_synergy_orchestrator",
    instruction=return_instructions_root(),
    global_instruction=f"""
    You are the InsightSynergy Council Orchestrator.
    Today's date: {date_today}
    
    Your role is to coordinate multi-agent debates that expose hidden biases 
    and generate consensus-driven insights through adversarial reasoning.
    
    This system uses multiple AI models for specialized perspectives:
    - Optimist: {os.getenv("OPTIMIST_MODEL", "claude-3-5-sonnet-20240620")} (identifies opportunities)
    - Pessimist: {os.getenv("PESSIMIST_MODEL", "grok-1")} (identifies risks)
    - Ethical Auditor: {os.getenv("ETHICAL_AUDITOR_MODEL", "gpt-4")} (checks for bias)
    - Synthesis: {os.getenv("SYNTHESIS_MODEL", "gemini-1.5-pro")} (creates consensus)
    """,
    sub_agents=[db_agent],
    tools=[
        call_db_agent,
        call_ds_agent,
        call_optimist_agent,
        call_pessimist_agent,
        call_ethical_auditor_agent,
        call_synthesis_moderator_agent,
        initiate_council_debate,
        load_artifacts
    ],
    before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.01)
)