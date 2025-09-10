from dotenv import load_dotenv
from google.adk import Agent
import os
from .prompts import return_instraction_root
from .ingestion_agent.agent import ingestion_agent
from .resoltuion_agent.agent import resolution_agent

model_name = os.getenv("MODEL", "gemini-2.0-flash-001")
load_dotenv()



# ---------- Root Coordinator Agent ----------
root_agent = Agent(
    name="NetworkIncidentCoordinatorAgent",
    model=model_name,
    description="Main coordinator for network incident management that intelligently routes requests between ingestion and resolution sub-agents.",
    instruction=return_instraction_root(),
    sub_agents=[ingestion_agent,resolution_agent]
)