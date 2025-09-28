from dotenv import load_dotenv
import os
from google.adk import Agent
from ...tools import (
    search_incidents_by_similarity, 
    search_by_severity, 
    execute_bigquery_query,
    search_incidents_advanced,
    search_by_service_and_description,
    search_by_multiple_criteria
)
from ...prompts import return_instruction_resolution

load_dotenv()
model_name = os.getenv("MODEL", "gemini-2.0-flash")

RESOLUTION_AGENT = Agent(
    name="ResolutionAnalysisAgent",
    model=model_name,
    description="Agent specialized in analyzing incidents and providing resolution strategies with advanced search capabilities.",
    instruction=return_instruction_resolution(),
    tools=[
        search_incidents_by_similarity,
        search_by_severity,
        execute_bigquery_query,
        search_incidents_advanced,
        search_by_service_and_description,
        search_by_multiple_criteria
    ]
)