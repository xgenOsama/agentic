from google.adk import Agent
from .tools import ingest_new_data_to_index_from_gcs
import os

model_name = os.getenv("MODEL", "gemini-2.0-flash")


INSTRUCTION = """
You are responsible for detecting if the user input contains a Google Cloud Storage URL (starts with 'gs://').
If it does, call the ingestion tool to process the file.
If not, respond with a message indicating that no GCS URL was found.
"""

GCS_INGEST_AGENT = Agent(
    name="GCSIngestAgent",
    model=model_name,
    description="Checks user input for GCS bucket URLs and ingests the data if found.",
    instruction=INSTRUCTION,
    tools=[ingest_new_data_to_index_from_gcs]
)
