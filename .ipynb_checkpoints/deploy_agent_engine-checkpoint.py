
import datetime
import logging
import os
import vertexai
from absl import app, flags
from dotenv import load_dotenv
from google.adk.sessions import VertexAiSessionService
from google.api_core import exceptions as google_exceptions
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

from backend.agent import root_agent

wheel_file = "network_agent-0.1.0-py3-none-any.whl"
use_case_name = "Network Agent"

use_case_description = "Agent for resolving network issues"

BUCKET = "gs://vodaf-aida25lcpm-206-rag"
PROJECT_ID = 'vodaf-aida25lcpm-206'
LOCATION = 'europe-west1'

# Initialize Vertex AI
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=BUCKET,
)


def create():
    adk_app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )
    today = datetime.datetime.now()
    today = datetime.datetime.strftime(today, "%Y%m%d%H%M")

    kwargs = {
        "agent_engine": adk_app,
        "requirements": [wheel_file],
        "extra_packages": [wheel_file],
        "env_vars": {},
        "display_name": use_case_name,
        "gcs_dir_name": f"{use_case_name}-{today}",
        "description": use_case_description,
    }

    remote_app = agent_engines.create(**kwargs)
    
    print(f"Deployment finished!")
    print(f"Resource Name: {remote_app.resource_name}")
    
    
create()