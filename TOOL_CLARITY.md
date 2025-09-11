# 🛠️ Agent Tool Clarity Documentation

## Root Agent Tool Configuration

The NetworkIncidentResolutionAgent now has **clear, distinct tools** to eliminate confusion between ingestion and retrieval:

### 🔍 **retrieve_context_from_query**
**Purpose**: SEARCH and RETRIEVE existing incident data
- **When to use**: Finding similar historical incidents for resolution guidance
- **Example**: "Find incidents similar to packet loss in Manchester"
- **Returns**: Similar incidents with resolution steps and root causes

### 📥 **INCIDENT_INGESTION_AGENT_TOOL** 
**Purpose**: INGEST structured incident data into the vector database
- **When to use**: Adding new incident records in JSON format
- **Example**: Processing incident with fields like incident_id, severity, description
- **Function**: Validates, generates embeddings, stores in vector DB

### 📁 **GCS_INGEST_AGENT_TOOL**
**Purpose**: INGEST data files from Google Cloud Storage
- **When to use**: Processing Excel/CSV files from GCS buckets
- **Example**: "Process gs://bucket-name/incidents.xlsx"
- **Function**: Downloads file, extracts data, converts to searchable format

### 📊 **ANALYTICS_AGENT_TOOL**
**Purpose**: ANALYZE data for patterns, trends, and insights
- **When to use**: Asking analytical questions about incident data
- **Example**: "What are the most common root causes this month?"
- **Function**: Queries BigQuery, provides statistical analysis

## Clear Workflow Examples

### 🔄 **Incident Resolution Workflow**
```
User: "We have packet loss in Glasgow, help me resolve it"
↓
Agent uses: retrieve_context_from_query
↓
Returns: Similar incidents with proven resolution steps
```

### 📝 **Incident Ingestion Workflow** 
```
User: "Ingest this incident: {incident_id: 'INC-001', severity: 'High', ...}"
↓
Agent uses: INCIDENT_INGESTION_AGENT_TOOL
↓
Returns: Validation results, embedding generation, storage confirmation
```

### 📈 **Analytics Workflow**
```
User: "What trends do we see in network incidents?"
↓
Agent uses: ANALYTICS_AGENT_TOOL
↓
Returns: Statistical analysis, pattern identification, trend reports
```

## Tool Selection Logic

The root agent now clearly distinguishes:

1. **Information Seeking** → `retrieve_context_from_query`
2. **Data Addition (Structured)** → `INCIDENT_INGESTION_AGENT_TOOL`
3. **Data Addition (Files)** → `GCS_INGEST_AGENT_TOOL`
4. **Data Analysis** → `ANALYTICS_AGENT_TOOL`

This eliminates the previous confusion between ingestion and retrieval operations! 🎯
