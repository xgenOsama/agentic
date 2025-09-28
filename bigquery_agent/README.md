# BigQuery Network Incident Agent

A sophisticated AI agent system for network incident management using Google BigQuery as the data backend. This agent provides intelligent incident resolution, data ingestion, and analytics capabilities.

## Architecture

```
bigquery_agent/
├── agent.py                 # Main coordinator agent
├── tools.py                 # BigQuery interaction tools
├── prompts.py              # Agent instructions and prompts
├── test.py                 # Test and demonstration script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── subagents/
    ├── ingest_agent/       # Data ingestion specialist
    │   └── agent.py
    └── resolution_agent/   # Incident resolution specialist
        └── agent.py
```

## Features

### 🔍 **Intelligent Incident Search**
- Semantic search through historical incidents in BigQuery
- Multi-dimensional filtering (severity, service type, location)
- Pattern recognition for similar incidents

### 📊 **Data Ingestion**
- Structured incident data validation and ingestion
- Automatic data quality checks
- Standardized format enforcement

### 🛠️ **Resolution Analysis**
- Historical pattern matching for proven solutions
- Root cause analysis based on past incidents
- Step-by-step resolution recommendations

### 📈 **Analytics & Reporting**
- Real-time incident statistics
- Trend analysis and insights
- Custom BigQuery analytics

## Configuration

### Environment Variables (.env)
```bash
GOOGLE_CLOUD_PROJECT=vf-pf1-ca-nonlive
GOOGLE_CLOUD_LOCATION=europe-west1
BIGQUERY_DATASET=hackathon_team6_data
BIGQUERY_TABLE=network_incidents
MODEL=gemini-2.0-flash
```

### BigQuery Table Schema
The agent expects a table with the following structure:
```sql
CREATE TABLE `vf-pf1-ca-nonlive.hackathon_team6_data.network_incidents` (
    incident_id STRING,
    timestamp DATETIME,
    severity STRING,
    service_impact STRING,
    incident_description STRING,
    resolution_steps STRING,
    root_cause STRING
);
```

## Usage

### Basic Setup
```python
from bigquery_agent.agent import bigquery_root_agent

# The agent automatically routes queries to appropriate sub-agents
response = bigquery_root_agent.query("I'm experiencing 4G service issues in Manchester")
```

### Direct Tool Usage
```python
from bigquery_agent.tools import (
    search_incidents_by_similarity,
    ingest_incident_data,
    get_incident_statistics
)

# Search for similar incidents
results = search_incidents_by_similarity("packet loss", limit=5)

# Ingest new incident
incident_data = {
    "incident_id": "INC-2024-001",
    "timestamp": "2024-01-15 14:30:00",
    "severity": "High",
    "service_impact": "4G Service Outage",
    "incident_description": "Widespread packet loss affecting Manchester region",
    "resolution_steps": "Restarted core router, cleared BGP sessions",
    "root_cause": "Router configuration error after maintenance"
}
ingest_incident_data(incident_data)
```

## Agent Capabilities

### 🤖 **Main Coordinator Agent**
- Intelligent query routing to sub-agents
- Context-aware incident classification
- Multi-faceted search strategies
- Historical pattern analysis

### 📥 **Ingest Agent**
- Data validation and quality assurance
- Structured incident data processing
- Duplicate detection and prevention
- Format standardization

### 🔧 **Resolution Agent**
- Historical incident matching
- Root cause pattern recognition
- Resolution strategy development
- Preventive recommendations

## Example Queries

The agent can handle various types of requests:

**Incident Resolution:**
- "I have packet loss in Birmingham, find similar incidents and solutions"
- "4G service is down in Manchester, what are the common causes?"
- "Authentication service failures - show me resolution patterns"

**Data Analysis:**
- "Show me critical incidents from last month"
- "What are the most common root causes for DNS issues?"
- "Analyze incident trends by service type"

**Data Ingestion:**
- "Insert new incident: Service outage in London affecting billing portal"
- "Add incident data with ID INC-2024-100"

## Installation

1. Clone the repository and navigate to the bigquery_agent directory
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your Google Cloud credentials:
```bash
gcloud auth application-default login
```

4. Set up environment variables in `.env` file

5. Run the test script to verify setup:
```bash
python test.py
```

## Dependencies

- `google-cloud-bigquery`: BigQuery client library
- `google-adk`: Google Agent Development Kit
- `python-dotenv`: Environment variable management
- `pandas`: Data manipulation and analysis

## Key Differences from Vector Database Backend

| Feature | Vector Database | BigQuery Backend |
|---------|----------------|------------------|
| Search Method | Semantic similarity vectors | SQL-based text matching |
| Scalability | Limited by vector index size | Highly scalable |
| Query Flexibility | Fixed similarity search | Custom SQL analytics |
| Real-time Updates | Complex index updates | Simple INSERT operations |
| Analytics | Basic similarity metrics | Advanced SQL analytics |
| Cost Model | Fixed infrastructure | Pay-per-query |

## Contributing

When extending the agent:

1. **Add new tools**: Create functions in `tools.py` for BigQuery operations
2. **Extend prompts**: Update agent instructions in `prompts.py`
3. **Create sub-agents**: Add specialized agents in the `subagents/` directory
4. **Update tests**: Add test cases in `test.py`

## Security Considerations

- Uses Google Cloud IAM for authentication
- BigQuery row-level security can be implemented
- Environment variables for sensitive configuration
- No hardcoded credentials in source code

## Performance Tips

- Use appropriate `LIMIT` clauses for large datasets
- Index frequently queried columns in BigQuery
- Consider partitioning tables by timestamp for better performance
- Cache frequently used statistics and patterns