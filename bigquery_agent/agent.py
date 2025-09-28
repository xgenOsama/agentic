from dotenv import load_dotenv
from google.adk import Agent
import os
from .prompts import return_instruction_root
from .tools import (
    search_incidents_by_similarity, 
    get_incident_statistics,
    search_incidents_advanced,
    search_by_service_and_description,
    search_by_multiple_criteria,
    search_by_severity
)
from .subagents.ingest_agent.agent import INGEST_AGENT
from .subagents.resolution_agent.agent import RESOLUTION_AGENT
from google.adk.tools.agent_tool import AgentTool

model_name = os.getenv("MODEL", "gemini-2.0-flash")
load_dotenv()

# Create agent tools from sub-agents
INGEST_AGENT_TOOL = AgentTool(agent=INGEST_AGENT)
RESOLUTION_AGENT_TOOL = AgentTool(agent=RESOLUTION_AGENT)

# ---------- Root BigQuery Agent ----------
root_agent = Agent(
    name="BigQueryNetworkIncidentAgent",
    model=model_name,
    description="Main coordinator for network incident management using BigQuery with advanced search capabilities.",
    instruction=return_instruction_root(),
    tools=[
        search_incidents_by_similarity,
        get_incident_statistics,
        search_incidents_advanced,
        search_by_service_and_description,
        search_by_multiple_criteria,
        search_by_severity,
        INGEST_AGENT_TOOL,
        RESOLUTION_AGENT_TOOL
    ],
)