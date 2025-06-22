# Enhanced Tools Module - Building on Original Structure

import json
import hashlib
import datetime
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

# Enhanced utility functions
def generate_query_fingerprint(question: str) -> str:
    """Generate a simple fingerprint for query caching."""
    return hashlib.md5(question.lower().strip().encode()).hexdigest()[:8]

def assess_data_scope(data: List[Dict[str, Any]], question: str) -> Dict[str, Any]:
    """Enhanced data scope assessment for better handoffs."""
    if not data or not isinstance(data, list):
        return {'valid': False, 'issues': ['No data available'], 'row_count': 0}
    
    assessment = {
        'valid': True,
        'issues': [],
        'row_count': len(data),
        'columns': list(data[0].keys()) if data else [],
        'completeness': 1.0
    }
    
    # Enhanced scope validation
    if len(data) < 50:
        assessment['issues'].append(f'Small dataset ({len(data)} rows) - verify scope completeness')
    
    # Check for demographic columns
    demographic_indicators = ['gender', 'age', 'region', 'country', 'ethnicity', 'income']
    has_demographics = any(indicator in str(assessment['columns']).lower() 
                          for indicator in demographic_indicators)
    assessment['has_demographics'] = has_demographics
    
    # Date range detection
    date_columns = [col for col in assessment['columns'] 
                   if any(keyword in col.lower() for keyword in ['date', 'time', 'created'])]
    if date_columns and data:
        try:
            dates = [row.get(date_columns[0]) for row in data if row.get(date_columns[0])]
            if dates:
                assessment['date_range'] = {'start': min(dates), 'end': max(dates)}
        except:
            pass
    
    return assessment

async def call_db_agent(
    question: str,
    tool_context: ToolContext,
):
    """Enhanced tool to call database agent with improved context and caching."""
    print(
        "\n call_db_agent.use_database:"
        f' {tool_context.state["all_db_settings"]["use_database"]}'
    )

    # Enhanced query caching
    query_fingerprint = generate_query_fingerprint(question)
    cached_fingerprint = tool_context.state.get('last_query_fingerprint')
    
    if (cached_fingerprint == query_fingerprint and 
        'query_result' in tool_context.state and
        'db_agent_output' in tool_context.state):
        print("📋 Reusing cached database results for identical query")
        return tool_context.state["db_agent_output"]

    agent_tool = AgentTool(agent=db_agent)

    # Enhanced query with business context
    enhanced_question = f"""
    {question}
    
    CONTEXT FOR SQL GENERATION:
    - Design query for potential downstream analysis (time-series, cohort, segmentation)
    - Include relevant metadata columns for data science processing
    - Use semantic text matching for keywords like 'urgent', 'premium', 'high-value'
    - Structure for comprehensive data retrieval avoiding partial results
    """

    try:
        db_agent_output = await agent_tool.run_async(
            args={"request": enhanced_question}, tool_context=tool_context
        )
        
        # Enhanced result validation and metadata
        if 'query_result' in tool_context.state:
            data_assessment = assess_data_scope(tool_context.state['query_result'], question)
            
            print(f"✅ Database query completed:")
            print(f"   Rows: {data_assessment['row_count']}")
            print(f"   Columns: {len(data_assessment['columns'])}")
            print(f"   Demographics available: {'Yes' if data_assessment.get('has_demographics') else 'No'}")
            
            if data_assessment['issues']:
                print("⚠️  Data scope considerations:")
                for issue in data_assessment['issues']:
                    print(f"   - {issue}")
            
            # Store enhanced metadata
            tool_context.state['data_assessment'] = data_assessment
            tool_context.state['last_query_fingerprint'] = query_fingerprint
            tool_context.state['data_fetch_timestamp'] = datetime.datetime.now().isoformat()
        
        tool_context.state["db_agent_output"] = db_agent_output
        return db_agent_output
        
    except Exception as e:
        print(f"❌ Database agent error: {str(e)}")
        print("🔄 Attempting simplified fallback query...")
        
        # Fallback strategy
        fallback_question = f"Get basic data for: {question.split('?')[0]}"
        try:
            fallback_output = await agent_tool.run_async(
                args={"request": fallback_question}, tool_context=tool_context
            )
            tool_context.state["db_agent_output"] = fallback_output
            return fallback_output
        except Exception as fallback_e:
            error_msg = f"Database queries failed. Primary: {str(e)}, Fallback: {str(fallback_e)}"
            tool_context.state["db_agent_output"] = error_msg
            return error_msg

async def call_ds_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call data science (nl2py) agent."""

    if question == "N/A":
        return tool_context.state["db_agent_output"]

    input_data = tool_context.state["query_result"]

    # MINIMAL enhancement: Add simple product context
    product_note = ""
    if "prd_1" in question.lower():
        product_note = "Note: This analysis is for product prd_1. "
    elif "prd_2" in question.lower():
        product_note = "Note: This analysis is for product prd_2. "

    question_with_data = f"""
    {product_note}Question to answer: {question}

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
    """Enhanced optimist agent call with rich analytical context."""
    
    # Gather comprehensive context
    input_data = tool_context.state.get("query_result", "")
    ds_output = tool_context.state.get("ds_agent_output", "")
    data_assessment = tool_context.state.get("data_assessment", {})
    analysis_metadata = tool_context.state.get("ds_analysis_metadata", {})
    
    # Enhanced optimist input with business intelligence context
    optimist_input = f"""
    Analysis Context: {analysis_context}
    
    DATA INTELLIGENCE SUMMARY:
    - Dataset scope: {data_assessment.get('row_count', 'Unknown')} records
    - Quality score: {analysis_metadata.get('data_quality_score', 'Unknown')}
    - Analysis timestamp: {analysis_metadata.get('timestamp', 'Unknown')}
    - Date range: {data_assessment.get('date_range', 'Not specified')}
    
    DATASET RESULTS: 
    {json.dumps(input_data, default=str)[:2000] if input_data else "No database results available"}...
    
    DATA SCIENCE ANALYSIS:
    {ds_output if ds_output else "No data science analysis available"}
    
    ENHANCED INSTRUCTIONS:
    Please identify growth opportunities, positive trends, and improvement indicators.
    Focus on quantifiable metrics and evidence-based optimistic insights.
    Consider data quality context when assessing confidence in positive findings.
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
    """Enhanced pessimist agent call with risk analysis focus."""
    
    # Gather context including data quality concerns
    input_data = tool_context.state.get("query_result", "")
    ds_output = tool_context.state.get("ds_agent_output", "")
    data_assessment = tool_context.state.get("data_assessment", {})
    analysis_metadata = tool_context.state.get("ds_analysis_metadata", {})
    
    pessimist_input = f"""
    Analysis Context: {analysis_context}
    
    DATA QUALITY AND RISK FACTORS:
    - Data limitations: {'; '.join(data_assessment.get('issues', ['None identified']))}
    - Scope concerns: {data_assessment.get('row_count', 'Unknown')} records analyzed
    - Quality confidence: {analysis_metadata.get('data_quality_score', 'Unknown')}
    
    DATASET RESULTS:
    {json.dumps(input_data, default=str)[:2000] if input_data else "No database results available"}...
    
    DATA SCIENCE ANALYSIS:
    {ds_output if ds_output else "No data science analysis available"}
    
    ENHANCED INSTRUCTIONS:
    Please identify risks, anomalies, declining trends, and potential problem areas.
    Pay special attention to data quality issues that might mask underlying problems.
    Consider both obvious risks and subtle warning indicators in the patterns.
    Factor in data limitations when assessing severity of concerns.
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
    """Enhanced ethical auditor with comprehensive fairness analysis."""
    
    # Get context and check demographic availability
    input_data = tool_context.state.get("query_result", "")
    ds_output = tool_context.state.get("ds_agent_output", "")
    data_assessment = tool_context.state.get("data_assessment", {})
    
    # Enhanced demographic detection
    has_demographics = data_assessment.get('has_demographics', False)
    
    if not has_demographics:
        # Enhanced check for demographic data
        if input_data and isinstance(input_data, list) and input_data:
            demographic_indicators = ['gender', 'age', 'region', 'country', 'ethnicity', 'race', 'income', 'education']
            columns_text = ' '.join(str(input_data[0].keys())).lower()
            has_demographics = any(indicator in columns_text for indicator in demographic_indicators)
    
    if not has_demographics:
        ethical_output = "**Ethical Auditor Perspective**\n\nFairness audit was not applicable as the dataset lacked demographic attributes required for bias detection analysis."
        tool_context.state["ethical_agent_output"] = ethical_output
        return ethical_output
    
    ethical_input = f"""
    Analysis Context: {analysis_context}
    
    DEMOGRAPHIC DATA ASSESSMENT:
    - Demographics detected: Yes
    - Available columns: {', '.join(data_assessment.get('columns', []))}
    - Sample size: {data_assessment.get('row_count', 'Unknown')} records
    
    DATASET RESULTS:
    {json.dumps(input_data, default=str)[:2000] if input_data else "No database results available"}...
    
    DATA SCIENCE ANALYSIS:
    {ds_output if ds_output else "No data science analysis available"}
    
    ENHANCED FAIRNESS AUDIT INSTRUCTIONS:
    Please conduct a comprehensive fairness analysis focusing on:
    1. Access equity across demographic groups
    2. Treatment consistency and service quality disparities
    3. Outcome fairness in results and opportunities
    4. Systematic bias indicators in policies or processes
    
    Provide specific metrics and quantifiable evidence for any disparities identified.
    Consider data quality limitations when assessing confidence in fairness conclusions.
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
    """Enhanced synthesis with comprehensive context integration."""
    
    # Gather all perspectives and metadata
    optimist_output = tool_context.state.get("optimist_agent_output", "")
    pessimist_output = tool_context.state.get("pessimist_agent_output", "")
    ethical_output = tool_context.state.get("ethical_agent_output", "")
    
    # Include enhanced metadata for synthesis
    data_assessment = tool_context.state.get("data_assessment", {})
    analysis_metadata = tool_context.state.get("ds_analysis_metadata", {})
    
    synthesis_input = f"""
    Analysis Context: {analysis_context}
    
    ANALYSIS QUALITY CONTEXT:
    - Data Quality Score: {analysis_metadata.get('data_quality_score', 'Unknown')}
    - Sample Size: {data_assessment.get('row_count', 'Unknown')} records
    - Data Limitations: {'; '.join(data_assessment.get('issues', ['None identified']))}
    - Analysis Timestamp: {analysis_metadata.get('timestamp', 'Unknown')}
    - Demographics Available: {'Yes' if data_assessment.get('has_demographics') else 'No'}
    
    AGENT PERSPECTIVES TO SYNTHESIZE:
    
    OPTIMIST PERSPECTIVE:
    {optimist_output}
    
    PESSIMIST PERSPECTIVE:
    {pessimist_output}
    
    ETHICAL AUDITOR PERSPECTIVE:
    {ethical_output}
    
    ENHANCED SYNTHESIS INSTRUCTIONS:
    Please synthesize these perspectives into a unified consensus with conflict scoring and recommendations.
    Consider the data quality context when evaluating argument strength and confidence levels.
    Address how data limitations might affect the reliability of different conclusions.
    Provide confidence indicators for key recommendations based on data quality and agreement levels.
    """
    
    agent_tool = AgentTool(agent=synthesis_moderator_agent)
    
    synthesis_output = await agent_tool.run_async(
        args={"request": synthesis_input}, tool_context=tool_context
    )
    tool_context.state["synthesis_agent_output"] = synthesis_output
    return synthesis_output

def check_for_demographic_columns(data: List[Dict[str, Any]]) -> bool:
    """Enhanced demographic detection with broader pattern matching."""
    if not data or not isinstance(data, list) or not data[0]:
        return False
    
    # Comprehensive demographic indicators
    demographic_indicators = [
        'gender', 'sex', 'age', 'age_group', 'age_range', 'birth_date', 'dob',
        'region', 'state', 'country', 'location', 'zip_code', 'postal_code', 'city',
        'race', 'ethnicity', 'nationality', 'culture', 'language', 'locale',
        'income', 'education', 'occupation', 'employment', 'job_title',
        'tier', 'segment', 'category', 'classification'  # Business demographics
    ]
    
    if isinstance(data[0], dict):
        column_names = [col.lower() for col in data[0].keys()]
        column_text = ' '.join(column_names)
        
        # Enhanced pattern matching
        return any(indicator in column_text for indicator in demographic_indicators)
    
    return False

async def initiate_council_debate(
    question: str,
    tool_context: ToolContext,
):
    """Enhanced orchestration of the full debate process with intelligent coordination."""
    
    # Ensure we have data from previous analysis
    if "query_result" not in tool_context.state:
        return "Error: No data available for debate analysis. Please run database query first."
    
    input_data = tool_context.state["query_result"]
    data_assessment = tool_context.state.get("data_assessment", {})
    
    # Enhanced demographic detection and quality assessment
    has_demographics = data_assessment.get('has_demographics', check_for_demographic_columns(input_data))
    
    print(f"🏛️  Initiating Council Debate:")
    print(f"   Question: {question}")
    print(f"   Data scope: {data_assessment.get('row_count', len(input_data))} records")
    print(f"   Demographics: {'Available' if has_demographics else 'Not available'}")
    print(f"   Quality issues: {len(data_assessment.get('issues', []))}")
    
    try:
        # Call perspective agents with enhanced coordination
        print("🎯 Gathering perspectives...")
        
        await call_optimist_agent(question, tool_context)
        print("   ✅ Optimist analysis complete")
        
        await call_pessimist_agent(question, tool_context)
        print("   ✅ Pessimist analysis complete")
        
        # Smart ethical auditor activation
        if has_demographics:
            await call_ethical_auditor_agent(question, tool_context)
            print("   ✅ Ethical audit complete")
        else:
            tool_context.state["ethical_agent_output"] = (
                "**Ethical Auditor Perspective**\n\n"
                "Fairness audit was not applicable as the dataset lacked "
                "demographic attributes required for bias detection analysis."
            )
            print("   ℹ️  Ethical audit skipped (no demographic data)")
        
        # Enhanced synthesis with quality context
        print("🔄 Synthesizing perspectives...")
        synthesis_result = await call_synthesis_moderator_agent(question, tool_context)
        print("   ✅ Synthesis complete")
        
        # Store debate metadata
        debate_metadata = {
            'timestamp': datetime.datetime.now().isoformat(),
            'participants': ['optimist', 'pessimist', 'ethical_auditor' if has_demographics else 'ethical_auditor_skipped'],
            'data_quality_score': tool_context.state.get('ds_analysis_metadata', {}).get('data_quality_score', 'unknown'),
            'demographic_analysis_performed': has_demographics,
            'data_scope': data_assessment.get('row_count', 'unknown')
        }
        tool_context.state['debate_metadata'] = debate_metadata
        
        print("🎉 Council debate completed successfully")
        return synthesis_result
        
    except Exception as e:
        error_msg = f"❌ Error during council debate: {str(e)}"
        print(error_msg)
        # Store partial results for debugging
        tool_context.state['debate_error'] = str(e)
        return error_msg