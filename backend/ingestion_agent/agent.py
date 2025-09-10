from dotenv import load_dotenv
from google.adk import Agent
import os
from .prompts import return_instruction_ingestion
from .tools import ingest_incident_data, validate_incident_format, batch_ingest_incidents

load_dotenv()

model_name = os.getenv("MODEL", "gemini-2.0-flash-001")

# ---------- Ingestion Agent ----------
ingestion_agent = Agent(
    name="IncidentIngestionAgent",
    model=model_name,
    description="Specialized agent for ingesting and processing network incident data into the vector database.",
    instruction=return_instruction_ingestion(),
    tools=[
        ingest_incident_data,
        validate_incident_format,
        batch_ingest_incidents
    ],
)
