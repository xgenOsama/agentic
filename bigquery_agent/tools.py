from dotenv import load_dotenv
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import os
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

load_dotenv()

# Set environment variable for quota project
os.environ['GOOGLE_CLOUD_QUOTA_PROJECT_ID'] = os.getenv("GOOGLE_CLOUD_PROJECT", "vf-pf1-ca-nonlive")

# Constants
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "vf-pf1-ca-nonlive")
DATASET_ID = os.getenv("BIGQUERY_DATASET", "hackathon_team6_data")
TABLE_ID = os.getenv("BIGQUERY_TABLE", "network_incidents")
FULL_TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# Initialize BigQuery client
bq_client = None

def get_bigquery_client():
    """Get BigQuery client, initializing it if necessary."""
    global bq_client
    if bq_client is None:
        try:
            bq_client = bigquery.Client(project=PROJECT_ID)
        except Exception as e:
            print(f"Error initializing BigQuery client: {e}")
            raise
    return bq_client

def execute_bigquery_query(query: str) -> List[Dict[str, Any]]:
    """
    Execute a SQL query on BigQuery and return results as list of dictionaries.
    
    Args:
        query (str): SQL query to execute
        
    Returns:
        List[Dict[str, Any]]: Query results as list of dictionaries
    """
    try:
        client = get_bigquery_client()
        query_job = client.query(query)
        results = query_job.result()
        return [dict(row) for row in results]
    except Exception as e:
        print(f"Error executing BigQuery query: {e}")
        raise

def search_incidents_by_similarity(query: str, limit: int = 10) -> str:
    """
    Search for similar incidents in BigQuery based on text similarity.
    
    Args:
        query (str): Search query describing the incident
        limit (int): Number of results to return
        
    Returns:
        str: Formatted string with incident details
    """
    try:
        sql_query = f"""
        SELECT 
            incident_id,
            timestamp,
            severity,
            service_impact,
            incident_description,
            resolution_steps,
            root_cause
        FROM `{FULL_TABLE_ID}`
        WHERE 
            LOWER(incident_description) LIKE LOWER('%{query}%')
            OR LOWER(service_impact) LIKE LOWER('%{query}%')
            OR LOWER(root_cause) LIKE LOWER('%{query}%')
        ORDER BY timestamp DESC
        LIMIT {limit}
        """
        
        results = execute_bigquery_query(sql_query)
        
        if not results:
            return f"No incidents found matching query: {query}"
        
        context = ""
        for incident in results:
            context += f"""
Incident ID: {incident.get('incident_id', 'N/A')}
Timestamp: {incident.get('timestamp', 'N/A')}
Severity: {incident.get('severity', 'N/A')}
Service Impact: {incident.get('service_impact', 'N/A')}
Description: {incident.get('incident_description', 'N/A')}
Resolution Steps: {incident.get('resolution_steps', 'N/A')}
Root Cause: {incident.get('root_cause', 'N/A')}

---

"""
        
        return context
        
    except Exception as e:
        return f"Error searching incidents: {str(e)}"

def search_incidents_advanced(
    service_impact_filter: Optional[str] = None,
    incident_description_filter: Optional[str] = None, 
    severity_filter: Optional[str] = None,
    root_cause_filter: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    Advanced search for incidents with multiple filter criteria.
    
    Args:
        service_impact_filter (str): Filter by service impact
        incident_description_filter (str): Filter by incident description
        severity_filter (str): Filter by severity level
        root_cause_filter (str): Filter by root cause
        limit (int): Number of results to return
        
    Returns:
        str: Formatted string with incident details
    """
    try:
        # Build WHERE clause dynamically based on provided filters
        where_conditions = []
        
        if service_impact_filter:
            where_conditions.append(f"LOWER(service_impact) LIKE LOWER('%{service_impact_filter}%')")
        
        if incident_description_filter:
            where_conditions.append(f"LOWER(incident_description) LIKE LOWER('%{incident_description_filter}%')")
        
        if severity_filter:
            where_conditions.append(f"LOWER(severity) = LOWER('{severity_filter}')")
        
        if root_cause_filter:
            where_conditions.append(f"LOWER(root_cause) LIKE LOWER('%{root_cause_filter}%')")
        
        # If no filters provided, return error
        if not where_conditions:
            return "No search criteria provided. Please specify at least one filter."
        
        where_clause = " AND ".join(where_conditions)
        
        sql_query = f"""
        SELECT 
            incident_id,
            timestamp,
            severity,
            service_impact,
            incident_description,
            resolution_steps,
            root_cause
        FROM `{FULL_TABLE_ID}`
        WHERE {where_clause}
        ORDER BY timestamp DESC
        LIMIT {limit}
        """
        
        results = execute_bigquery_query(sql_query)
        
        if not results:
            return f"No incidents found matching the specified criteria."
        
        context = f"Found {len(results)} incidents matching criteria:\n\n"
        for incident in results:
            context += f"""
Incident ID: {incident.get('incident_id', 'N/A')}
Timestamp: {incident.get('timestamp', 'N/A')}
Severity: {incident.get('severity', 'N/A')}
Service Impact: {incident.get('service_impact', 'N/A')}
Description: {incident.get('incident_description', 'N/A')}
Resolution Steps: {incident.get('resolution_steps', 'N/A')}
Root Cause: {incident.get('root_cause', 'N/A')}

---

"""
        
        return context
        
    except Exception as e:
        return f"Error in advanced search: {str(e)}"

def search_by_service_and_description(
    service_impact: str,
    description_keywords: str,
    limit: int = 10
) -> str:
    """
    Search incidents by specific service impact and description keywords.
    
    Args:
        service_impact (str): Service impact to filter by
        description_keywords (str): Keywords to search in description
        limit (int): Number of results to return
        
    Returns:
        str: Formatted string with incident details
    """
    try:
        sql_query = f"""
        SELECT 
            incident_id,
            timestamp,
            severity,
            service_impact,
            incident_description,
            resolution_steps,
            root_cause
        FROM `{FULL_TABLE_ID}`
        WHERE 
            LOWER(service_impact) LIKE LOWER('%{service_impact}%')
            AND LOWER(incident_description) LIKE LOWER('%{description_keywords}%')
        ORDER BY timestamp DESC
        LIMIT {limit}
        """
        
        results = execute_bigquery_query(sql_query)
        
        if not results:
            return f"No incidents found for service '{service_impact}' with description containing '{description_keywords}'"
        
        context = f"Found {len(results)} incidents for '{service_impact}' with '{description_keywords}':\n\n"
        for incident in results:
            context += f"""
Incident ID: {incident.get('incident_id', 'N/A')}
Timestamp: {incident.get('timestamp', 'N/A')}
Severity: {incident.get('severity', 'N/A')}
Service Impact: {incident.get('service_impact', 'N/A')}
Description: {incident.get('incident_description', 'N/A')}
Resolution Steps: {incident.get('resolution_steps', 'N/A')}
Root Cause: {incident.get('root_cause', 'N/A')}

---

"""
        
        return context
        
    except Exception as e:
        return f"Error searching by service and description: {str(e)}"

def search_by_multiple_criteria(criteria_dict: Dict[str, str], limit: int = 10) -> str:
    """
    Search incidents using multiple criteria with exact field matching.
    
    Args:
        criteria_dict (Dict[str, str]): Dictionary with field names as keys and search terms as values
        limit (int): Number of results to return
        
    Example:
        criteria = {
            "service_impact": "4G Service",
            "incident_description": "packet loss",
            "severity": "High"
        }
        
    Returns:
        str: Formatted string with incident details
    """
    try:
        valid_fields = ['incident_id', 'severity', 'service_impact', 'incident_description', 'resolution_steps', 'root_cause']
        where_conditions = []
        
        for field, value in criteria_dict.items():
            if field not in valid_fields:
                return f"Invalid field '{field}'. Valid fields: {valid_fields}"
            
            if field in ['severity']:
                # Exact match for severity
                where_conditions.append(f"LOWER({field}) = LOWER('{value}')")
            else:
                # Partial match for other fields
                where_conditions.append(f"LOWER({field}) LIKE LOWER('%{value}%')")
        
        if not where_conditions:
            return "No search criteria provided."
        
        where_clause = " AND ".join(where_conditions)
        
        sql_query = f"""
        SELECT 
            incident_id,
            timestamp,
            severity,
            service_impact,
            incident_description,
            resolution_steps,
            root_cause
        FROM `{FULL_TABLE_ID}`
        WHERE {where_clause}
        ORDER BY timestamp DESC
        LIMIT {limit}
        """
        
        results = execute_bigquery_query(sql_query)
        
        if not results:
            return f"No incidents found matching criteria: {criteria_dict}"
        
        context = f"Found {len(results)} incidents matching criteria {criteria_dict}:\n\n"
        for incident in results:
            context += f"""
Incident ID: {incident.get('incident_id', 'N/A')}
Timestamp: {incident.get('timestamp', 'N/A')}
Severity: {incident.get('severity', 'N/A')}
Service Impact: {incident.get('service_impact', 'N/A')}
Description: {incident.get('incident_description', 'N/A')}
Resolution Steps: {incident.get('resolution_steps', 'N/A')}
Root Cause: {incident.get('root_cause', 'N/A')}

---

"""
        
        return context
        
    except Exception as e:
        return f"Error in multi-criteria search: {str(e)}"

def ingest_incident_data(incident_data: Dict[str, Any]) -> str:
    """
    Insert new incident data into BigQuery table.
    
    Args:
        incident_data (Dict[str, Any]): Incident data to insert
        
    Returns:
        str: Success or error message
    """
    try:
        client = get_bigquery_client()
        table_ref = client.dataset(DATASET_ID).table(TABLE_ID)
        table = client.get_table(table_ref)
        
        # Insert the row
        errors = client.insert_rows_json(table, [incident_data])
        
        if errors:
            return f"Error inserting incident data: {errors}"
        else:
            return f"Successfully inserted incident: {incident_data.get('incident_id', 'Unknown ID')}"
            
    except Exception as e:
        return f"Error inserting incident data: {str(e)}"

def get_incident_statistics() -> str:
    """
    Get basic statistics about incidents in the database.
    
    Returns:
        str: Formatted statistics
    """
    try:
        sql_query = f"""
        SELECT 
            COUNT(*) as total_incidents,
            COUNT(DISTINCT severity) as severity_levels,
            COUNT(DISTINCT service_impact) as service_types,
            MIN(timestamp) as earliest_incident,
            MAX(timestamp) as latest_incident
        FROM `{FULL_TABLE_ID}`
        """
        
        results = execute_bigquery_query(sql_query)
        
        if results:
            stats = results[0]
            return f"""
Incident Database Statistics:
- Total Incidents: {stats.get('total_incidents', 0)}
- Severity Levels: {stats.get('severity_levels', 0)}
- Service Types: {stats.get('service_types', 0)}
- Date Range: {stats.get('earliest_incident', 'N/A')} to {stats.get('latest_incident', 'N/A')}
"""
        else:
            return "No statistics available"
            
    except Exception as e:
        return f"Error getting statistics: {str(e)}"

def search_by_severity(severity: str, limit: int = 10) -> str:
    """
    Search incidents by severity level.
    
    Args:
        severity (str): Severity level to search for
        limit (int): Number of results to return
        
    Returns:
        str: Formatted incident results
    """
    try:
        sql_query = f"""
        SELECT 
            incident_id,
            timestamp,
            service_impact,
            incident_description,
            resolution_steps,
            root_cause
        FROM `{FULL_TABLE_ID}`
        WHERE LOWER(severity) = LOWER('{severity}')
        ORDER BY timestamp DESC
        LIMIT {limit}
        """
        
        results = execute_bigquery_query(sql_query)
        
        if not results:
            return f"No incidents found with severity: {severity}"
        
        context = ""
        for incident in results:
            context += f"""
Incident ID: {incident.get('incident_id', 'N/A')}
Timestamp: {incident.get('timestamp', 'N/A')}
Service Impact: {incident.get('service_impact', 'N/A')}
Description: {incident.get('incident_description', 'N/A')}
Resolution Steps: {incident.get('resolution_steps', 'N/A')}
Root Cause: {incident.get('root_cause', 'N/A')}

---

"""
        
        return context
        
    except Exception as e:
        return f"Error searching by severity: {str(e)}"

def check_table_exists() -> bool:
    """
    Check if the BigQuery table exists.
    
    Returns:
        bool: True if table exists, False otherwise
    """
    try:
        client = get_bigquery_client()
        client.get_table(FULL_TABLE_ID)
        return True
    except NotFound:
        return False
    except Exception as e:
        print(f"Error checking table existence: {e}")
        return False

def create_table_if_not_exists() -> str:
    """
    Create the BigQuery table if it doesn't exist.
    
    Returns:
        str: Success or error message
    """
    try:
        client = get_bigquery_client()
        
        # Check if table already exists
        if check_table_exists():
            return f"Table {FULL_TABLE_ID} already exists"
        
        # Define table schema
        schema = [
            bigquery.SchemaField("incident_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "DATETIME", mode="REQUIRED"),
            bigquery.SchemaField("severity", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("service_impact", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("incident_description", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("resolution_steps", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("root_cause", "STRING", mode="REQUIRED"),
        ]
        
        # Create table
        table = bigquery.Table(FULL_TABLE_ID, schema=schema)
        table.description = "Network incidents data for TroubleBuster Agent"
        
        table = client.create_table(table)
        return f"Successfully created table {FULL_TABLE_ID}"
        
    except Exception as e:
        return f"Error creating table: {str(e)}"

def ingest_excel_data(excel_file_path: str) -> str:
    """
    Ingest data from Excel file into BigQuery table.
    
    Args:
        excel_file_path (str): Path to the Excel file
        
    Returns:
        str: Success or error message with details
    """
    try:
        # Check/create table first
        table_status = create_table_if_not_exists()
        print(f"Table status: {table_status}")
        
        # Read Excel file
        if not os.path.exists(excel_file_path):
            return f"Excel file not found: {excel_file_path}"
        
        df = pd.read_excel(excel_file_path)
        
        # Validate expected columns
        expected_columns = ['incident_id', 'timestamp', 'severity', 'service_impact', 
                          'incident_description', 'resolution_steps', 'root_cause']
        
        if not all(col in df.columns for col in expected_columns):
            missing_cols = [col for col in expected_columns if col not in df.columns]
            return f"Missing required columns: {missing_cols}. Found columns: {list(df.columns)}"
        
        # Clean and prepare data
        df = df[expected_columns]  # Select only needed columns
        df = df.dropna()  # Remove rows with missing data
        
        # Convert timestamp to proper format and then to string for JSON serialization
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Ensure all string fields are properly converted
        for col in ['incident_id', 'severity', 'service_impact', 'incident_description', 'resolution_steps', 'root_cause']:
            df[col] = df[col].astype(str)
        
        # Convert DataFrame to list of dictionaries
        records = df.to_dict('records')
        
        if not records:
            return "No valid records found to insert after data cleaning"
        
        print(f"Prepared {len(records)} records for insertion")
        
        # Insert data into BigQuery
        client = get_bigquery_client()
        table_ref = client.dataset(DATASET_ID).table(TABLE_ID)
        table = client.get_table(table_ref)
        
        # Insert rows
        errors = client.insert_rows_json(table, records)
        
        if errors:
            return f"Error inserting data: {errors}"
        else:
            return f"Successfully inserted {len(records)} records from {excel_file_path} into {FULL_TABLE_ID}"
            
    except Exception as e:
        return f"Error ingesting Excel data: {str(e)}"

def ingest_sample_data() -> str:
    """
    Ingest sample data directly into BigQuery table for testing.
    
    Returns:
        str: Success or error message
    """
    try:
        # Check/create table first
        table_status = create_table_if_not_exists()
        print(f"Table status: {table_status}")
        
        # Sample data based on the provided format
        sample_data = [
            {
                "incident_id": "INC-1000",
                "timestamp": "2024-08-20 19:23:00",
                "severity": "Low",
                "service_impact": "4G Service Outage",
                "incident_description": "4G Service Outage detected. High packet loss observed in Manchester.",
                "resolution_steps": "Restarted authentication service and cleared application cache.",
                "root_cause": "Fibre cut due to construction"
            },
            {
                "incident_id": "INC-1001",
                "timestamp": "2024-09-25 03:23:00",
                "severity": "Low",
                "service_impact": "DNS Resolution Failure",
                "incident_description": "DNS Resolution Failure detected. Performance degradation noted in London.",
                "resolution_steps": "Restarted core router, cleared BGP sessions, applied patch.",
                "root_cause": "SIP trunk congestion"
            },
            {
                "incident_id": "INC-1002",
                "timestamp": "2024-02-04 02:43:00",
                "severity": "Medium",
                "service_impact": "Billing Portal Access",
                "incident_description": "Billing Portal Access detected. Users experiencing issues in Glasgow.",
                "resolution_steps": "Rolled back recent configuration change and optimized routing.",
                "root_cause": "SSL certificate expired"
            },
            {
                "incident_id": "INC-1003",
                "timestamp": "2024-09-17 16:40:00",
                "severity": "Critical",
                "service_impact": "Billing Portal Access",
                "incident_description": "Billing Portal Access detected. Service unavailable in London.",
                "resolution_steps": "Restarted authentication service and cleared application cache.",
                "root_cause": "Database connection pool exhausted"
            },
            {
                "incident_id": "INC-1004",
                "timestamp": "2024-09-11 04:26:00",
                "severity": "Critical",
                "service_impact": "Email Service Delay",
                "incident_description": "Email Service Delay detected. High packet loss observed in Manchester.",
                "resolution_steps": "Blocked offending IP addresses and enabled DDOS protection.",
                "root_cause": "Fibre cut due to construction"
            },
            {
                "incident_id": "INC-1005",
                "timestamp": "2024-02-07 05:07:00",
                "severity": "Low",
                "service_impact": "SMS Delivery Failure",
                "incident_description": "SMS Delivery Failure detected. Service unavailable in Birmingham.",
                "resolution_steps": "Replaced faulty optical transceiver and tested link stability.",
                "root_cause": "SIP trunk congestion"
            }
        ]
        
        # Insert data into BigQuery
        client = get_bigquery_client()
        table_ref = client.dataset(DATASET_ID).table(TABLE_ID)
        table = client.get_table(table_ref)
        
        # Insert rows
        errors = client.insert_rows_json(table, sample_data)
        
        if errors:
            return f"Error inserting sample data: {errors}"
        else:
            return f"Successfully inserted {len(sample_data)} sample records into {FULL_TABLE_ID}"
            
    except Exception as e:
        return f"Error ingesting sample data: {str(e)}"

def clear_table_data() -> str:
    """
    Clear all data from the BigQuery table.
    
    Returns:
        str: Success or error message
    """
    try:
        client = get_bigquery_client()
        
        # Delete all rows from the table
        sql_query = f"DELETE FROM `{FULL_TABLE_ID}` WHERE TRUE"
        
        query_job = client.query(sql_query)
        query_job.result()  # Wait for the job to complete
        
        return f"Successfully cleared all data from {FULL_TABLE_ID}"
        
    except Exception as e:
        return f"Error clearing table data: {str(e)}"

def recreate_table_with_data(excel_file_path: str = None) -> str:
    """
    Drop existing table and recreate with fresh data.
    
    Args:
        excel_file_path (str): Path to Excel file, if None uses sample data
        
    Returns:
        str: Success or error message
    """
    try:
        client = get_bigquery_client()
        
        # Delete table if exists
        try:
            client.delete_table(FULL_TABLE_ID)
            print(f"Deleted existing table: {FULL_TABLE_ID}")
        except NotFound:
            print("Table doesn't exist, creating new one")
        
        # Create new table
        create_result = create_table_if_not_exists()
        print(f"Table creation: {create_result}")
        
        # Ingest data
        if excel_file_path and os.path.exists(excel_file_path):
            ingest_result = ingest_excel_data(excel_file_path)
        else:
            ingest_result = ingest_sample_data()
            
        return f"Table recreated successfully. {ingest_result}"
        
    except Exception as e:
        return f"Error recreating table: {str(e)}"