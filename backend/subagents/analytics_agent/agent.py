from dotenv import load_dotenv
import os
from google.cloud import bigquery
from google.adk import Agent
load_dotenv()
model_name = os.getenv("MODEL", "gemini-2.0-flash")

def execute_bq_query(query: str):
    """
    Executes a SQL query on a Google BigQuery table and returns the results as a list of dictionaries.

    Args:
        query (str): A valid SQL query string to be executed on BigQuery.

    Returns:
        List[dict]: A list of dictionaries, where each dictionary represents a row from the query result.

    Example:
        result = execute_bq_query("SELECT COUNT(*) FROM `project.dataset.table` WHERE severity = 'Critical'")
    """
    print(query)
    client = bigquery.Client()
    query_job = client.query(query)
    results = query_job.result()
    print(query)
    return [dict(row) for row in results]


instruction = """
You are a data agent with access to the following tool:
1. execute_bq_query: Use this tool to execute a SQL query on the table `vodaf-aida25lcpm-206.network_data.network_data` and return the result.

Table schema and sample data:
- incident_id (STRING): Unique identifier for the incident. Example: 'INC-1000'
- timestamp (DATETIME): Date and time of the incident. Example: '2024-08-20 19:23:00'
- severity (STRING): Severity level of the incident. Example: 'Low', 'Medium', 'High', 'Critical'
- service_impact (STRING): The service affected by the incident. Example: '4G Service Outage'
- incident_description (STRING): Description of the incident. Example: '4G Service Outage detected. High packet loss observed in Manchester.'
- resolution_steps (STRING): Steps taken to resolve the incident. Example: 'Restarted authentication service and cleared application cache.'
- root_cause (STRING): Root cause of the incident. Example: 'Fibre cut due to construction'

Your workflow:
- Read the user's question.
- Write a valid SQL query that answers the question using the table `vodaf-aida25lcpm-206.network_data.network_data` and the columns described above.
- Whenever you have a SQL query to execute, always call the `execute_bq_query` tool and pass the SQL query as its argument.
- Take the output from `execute_bq_query` and formulate a clear, concise answer to the user's question.
- Do not answer the question directly without first executing the relevant SQL query.
"""



ANALYTICS_AGENT = Agent(
    name="BQQueryAgent",
    model=model_name,
    description="Agent that writes SQL queries from user questions and executes them on BigQuery.",
    instruction=instruction,
    tools=[
        execute_bq_query
    ]
)
