import os
from google.adk.agents import Agent
from google.genai import types
from .prompts import return_instructions_pessimist

pessimist_critic_agent = Agent(
    model=os.getenv("PESSIMIST_MODEL", "gemini-2.0-flash-001"),
    name="pessimist_critic_agent", 
    instruction=return_instructions_pessimist(),
    generate_content_config=types.GenerateContentConfig(temperature=0.3)
)