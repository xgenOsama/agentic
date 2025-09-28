from dotenv import load_dotenv
import os
from google.adk import Agent
from ...tools import (
    ingest_incident_data, 
    get_incident_statistics, 
    ingest_excel_data, 
    ingest_sample_data, 
    create_table_if_not_exists,
    check_table_exists
)
from ...prompts import return_instruction_ingest

load_dotenv()
model_name = os.getenv("MODEL", "gemini-2.0-flash")

INGEST_AGENT = Agent(
    name="IncidentIngestionAgent",
    model=model_name,
    description="Agent specialized in ingesting and validating network incident data into BigQuery, including Excel file processing and table management.",
    instruction=return_instruction_ingest(),
    tools=[
        ingest_incident_data,
        get_incident_statistics,
        ingest_excel_data,
        ingest_sample_data,
        create_table_if_not_exists,
        check_table_exists
    ]
)