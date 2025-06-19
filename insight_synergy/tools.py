# Copyright 2025 Google LLC
# Licensed under the Apache License, Version 2.0

"""Tools for orchestrating the InsightSynergy Council debate process."""

import json
from typing import Dict, Any, List
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

from .sub_agents import (
    db_agent, 
    ds_agent, 
    optimist_analyst_agent,
    pessimist_critic_agent,
    ethical_auditor_agent,
    synthesis_moderator_agent
)

async def call_db_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call database (nl2sql) agent."""
    print(
        "\n call_db_agent.use_database:"
        f' {tool_context.state["all_db_settings"]["use_database"]}'
    )

    agent_tool = AgentTool(agent=db_agent)

    db_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["db_agent_output"] = db_agent_output
    return db_agent_output

async def call_ds_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call data science (nl2py) agent."""

    if question == "N/A":
        return tool_context.state["db_agent_output"]

    input_data = tool_context.state["query_result"]

    question_with_data = f"""
  Question to answer: {question}

  Actual data to analyze previous question is already in the following:
  {input_data}

  """

    agent_tool = AgentTool(agent=ds_agent)

    ds_agent_output = await agent_tool.run_async(
        args={"request": question_with_data}, tool_context=tool_context
    )
    tool_context.state["ds_agent_output"] = ds_agent_output
    return ds_agent_output

async def call_optimist_agent(
    analysis_context: str,
    tool_context: ToolContext,
):
    """Tool to call optimist analyst agent."""
    
    # Get the data from previous analysis
    input_data = tool_context.state.get("query_result", "")
    ds_output = tool_context.state.get("ds_agent_output", "")
    
    # Prepare context for the optimist agent
    optimist_input = f"""
    Analysis Context: {analysis_context}
    
    Dataset Results: {json.dumps(input_data, default=str) if input_data else "No database results available"}
    
    Data Science Analysis: {ds_output if ds_output else "No data science analysis available"}
    
    Please identify growth opportunities, positive trends, and improvement indicators from this data.
    """
    
    agent_tool = AgentTool(agent=optimist_analyst_agent)
    
    optimist_output = await agent_tool.run_async(
        args={"request": optimist_input}, tool_context=tool_context
    )
    tool_context.state["optimist_agent_output"] = optimist_output
    return optimist_output

async def call_pessimist_agent(
    analysis_context: str,
    tool_context: ToolContext,
):
    """Tool to call pessimist critic agent."""
    
    # Get the data from previous analysis
    input_data = tool_context.state.get("query_result", "")
    ds_output = tool_context.state.get("ds_agent_output", "")
    
    # Prepare context for the pessimist agent
    pessimist_input = f"""
    Analysis Context: {analysis_context}
    
    Dataset Results: {json.dumps(input_data, default=str) if input_data else "No database results available"}
    
    Data Science Analysis: {ds_output if ds_output else "No data science analysis available"}
    
    Please identify risks, anomalies, declining trends, and potential problem areas from this data.
    """
    
    agent_tool = AgentTool(agent=pessimist_critic_agent)
    
    pessimist_output = await agent_tool.run_async(
        args={"request": pessimist_input}, tool_context=tool_context
    )
    tool_context.state["pessimist_agent_output"] = pessimist_output
    return pessimist_output

async def call_ethical_auditor_agent(
    analysis_context: str,
    tool_context: ToolContext,
):
    """Tool to call ethical auditor agent."""
    
    # Get the data from previous analysis
    input_data = tool_context.state.get("query_result", "")
    ds_output = tool_context.state.get("ds_agent_output", "")
    
    # Prepare context for the ethical auditor agent
    ethical_input = f"""
    Analysis Context: {analysis_context}
    
    Dataset Results: {json.dumps(input_data, default=str) if input_data else "No database results available"}
    
    Data Science Analysis: {ds_output if ds_output else "No data science analysis available"}
    
    Please conduct a fairness audit to identify any bias, demographic disparities, or ethical concerns in this data.
    """
    
    agent_tool = AgentTool(agent=ethical_auditor_agent)
    
    ethical_output = await agent_tool.run_async(
        args={"request": ethical_input}, tool_context=tool_context
    )
    tool_context.state["ethical_agent_output"] = ethical_output
    return ethical_output

async def call_synthesis_moderator_agent(
    analysis_context: str,
    tool_context: ToolContext,
):
    """Tool to call synthesis moderator agent."""
    
    # Get outputs from all perspective agents
    optimist_output = tool_context.state.get("optimist_agent_output", "")
    pessimist_output = tool_context.state.get("pessimist_agent_output", "")
    ethical_output = tool_context.state.get("ethical_agent_output", "")
    
    # Prepare synthesis input
    synthesis_input = f"""
    Analysis Context: {analysis_context}
    
    Agent Perspectives to Synthesize:
    
    OPTIMIST PERSPECTIVE:
    {optimist_output}
    
    PESSIMIST PERSPECTIVE:
    {pessimist_output}
    
    ETHICAL AUDITOR PERSPECTIVE:
    {ethical_output}
    
    Please synthesize these perspectives into a unified consensus with conflict scoring and recommendations.
    """
    
    agent_tool = AgentTool(agent=synthesis_moderator_agent)
    
    synthesis_output = await agent_tool.run_async(
        args={"request": synthesis_input}, tool_context=tool_context
    )
    tool_context.state["synthesis_agent_output"] = synthesis_output
    return synthesis_output

def check_for_demographic_columns(data: List[Dict[str, Any]]) -> bool:
    """Check if dataset contains demographic attributes."""
    if not data or not isinstance(data, list) or not data[0]:
        return False
    
    # Common demographic column names to look for
    demographic_indicators = [
        'gender', 'sex', 'age', 'age_group', 'age_range', 'birth_date',
        'region', 'state', 'country', 'location', 'zip_code', 'postal_code',
        'race', 'ethnicity', 'nationality', 'culture', 'language',
        'income', 'education', 'occupation', 'employment'
    ]
    
    # Get column names from first row
    if isinstance(data[0], dict):
        column_names = [col.lower() for col in data[0].keys()]
    else:
        return False
    
    # Check if any demographic indicators are present
    return any(indicator in ' '.join(column_names) for indicator in demographic_indicators)

async def initiate_council_debate(
    question: str,
    tool_context: ToolContext,
):
    """Orchestrate the full debate process across all perspective agents."""
    
    # Ensure we have data from previous analysis
    if "query_result" not in tool_context.state:
        return "Error: No data available for debate analysis. Please run database query first."
    
    input_data = tool_context.state["query_result"]
    
    # Check if demographic data is present for ethical auditor
    has_demographics = check_for_demographic_columns(input_data)
    
    # Call perspective agents
    await call_optimist_agent(question, tool_context)
    await call_pessimist_agent(question, tool_context)
    
    # Only call ethical auditor if demographic data is present
    if has_demographics:
        await call_ethical_auditor_agent(question, tool_context)
    else:
        tool_context.state["ethical_agent_output"] = "**Ethical Auditor Perspective**\n\nFairness audit was not applicable as the dataset lacked demographic attributes required for bias detection analysis."
    
    # Synthesize all perspectives
    synthesis_result = await call_synthesis_moderator_agent(question, tool_context)
    
    return synthesis_result