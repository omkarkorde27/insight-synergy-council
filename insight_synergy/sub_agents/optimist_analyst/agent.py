import os
from google.adk.agents import Agent
from google.genai import types
from .prompts import return_instructions_optimist

optimist_analyst_agent = Agent(
    model=os.getenv("OPTIMIST_MODEL", "gemini-1.5-pro"),
    name="optimist_analyst_agent",
    instruction=return_instructions_optimist(),
    generate_content_config=types.GenerateContentConfig(temperature=0.3)
)