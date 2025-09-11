from dotenv import load_dotenv
from google.adk import Agent
import os
from .prompts import return_instraction_root
from .tools import retrieve_context_from_query
model_name = os.getenv("MODEL", "gemini-2.0-flash")
load_dotenv()

from .subagents.analytics_agent import ANALYTICS_AGENT
from .subagents.ingest_agent import GCS_INGEST_AGENT

from google.adk.tools.agent_tool import AgentTool

ANALYTICS_AGENT_TOOL = AgentTool(agent=ANALYTICS_AGENT)
GCS_INGEST_AGENT_TOOL = AgentTool(agent=GCS_INGEST_AGENT)

# ---------- Root agent ----------
root_agent = Agent(
    name="NetworkIncidentResolutionAgent",
    model=model_name,
    description="Main coordinator for network incident management that intelligently routes requests to specialized sub-agents.",
    instruction=return_instraction_root(),
    tools=[
        retrieve_context_from_query,
        ANALYTICS_AGENT_TOOL,
        GCS_INGEST_AGENT_TOOL
    ],
    
)