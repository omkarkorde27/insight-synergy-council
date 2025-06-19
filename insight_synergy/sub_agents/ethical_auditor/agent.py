import os
from google.adk.agents import Agent
from google.genai import types
from .prompts import return_instructions_ethical_auditor

ethical_auditor_agent = Agent(
    model=os.getenv("ETHICAL_AUDITOR_MODEL", "gemini-1.5-pro"),
    name="ethical_auditor_agent",
    instruction=return_instructions_ethical_auditor(),
    generate_content_config=types.GenerateContentConfig(temperature=0.1)
)