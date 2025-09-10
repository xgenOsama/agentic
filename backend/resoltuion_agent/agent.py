from dotenv import load_dotenv
from google.adk import Agent
import os
from .prompts import return_instruction_resolution
from .tools import retrieve_context_from_query, analyze_incident_patterns, suggest_resolution_steps

load_dotenv()

model_name = os.getenv("MODEL", "gemini-2.0-flash-001")

# ---------- Resolution Agent ----------
resolution_agent = Agent(
    name="IncidentResolutionAgent",
    model=model_name,
    description="Specialized agent for analyzing network incidents and providing intelligent resolution guidance based on historical data.",
    instruction=return_instruction_resolution(),
    tools=[
        retrieve_context_from_query,
        analyze_incident_patterns,
        suggest_resolution_steps
    ],
)
