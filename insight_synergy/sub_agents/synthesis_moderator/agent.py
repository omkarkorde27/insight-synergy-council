import os
from google.adk.agents import Agent
from google.genai import types
from .prompts import return_instructions_synthesis_moderator

synthesis_moderator_agent = Agent(
    model=os.getenv("SYNTHESIS_MODEL", "gemini-1.5-pro"),
    name="synthesis_moderator_agent",
    instruction=return_instructions_synthesis_moderator(),
    generate_content_config=types.GenerateContentConfig(temperature=0.2)
)
