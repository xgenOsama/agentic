# NetGuardian AI - Multi-Agent Network Incident Management System

NetGuardian AI is a sophisticated multi-agent system designed for comprehensive network incident management, combining specialized data ingestion capabilities with intelligent resolution guidance through vector search and pattern analysis.

## 🏗️ Architecture Overview

The system consists of three main agents working in coordination:

### 1. 🤖 NetworkIncidentCoordinatorAgent (Root Agent)
- **Role**: Main orchestrator and intelligent request router
- **Responsibilities**: 
  - Routes requests to appropriate sub-agents
  - Coordinates complex workflows spanning both data management and resolution
  - Maintains context across multi-step operations
  - Provides unified responses combining insights from both specialized agents

### 2. 📥 IncidentIngestionAgent (Data Management Specialist)
- **Role**: Handles all data ingestion, validation, and storage operations
- **Capabilities**:
  - Validates incident data format and quality
  - Processes single incidents or batch imports
  - Generates embeddings for vector database storage
  - Maintains data integrity and standardization
  - Provides quality metrics and improvement recommendations

### 3. 🔧 IncidentResolutionAgent (Analysis & Resolution Specialist)
- **Role**: Analyzes incidents and provides intelligent resolution guidance
- **Capabilities**:
  - Searches vector database for similar historical incidents
  - Identifies patterns and root cause correlations
  - Generates step-by-step resolution plans
  - Provides data-driven recommendations based on historical success rates

## 📊 Data Structure

The system processes incident records with the following structure:

```json
{
  "incident_id": "INC-1000",
  "timestamp": "2025-09-10T14:30:00Z",
  "severity": "High",
  "service_impact": "4G Service Outage Manchester",
  "incident_description": "Complete 4G service outage affecting Manchester region...",
  "resolution_steps": "1. Identified core router BGP session failure...",
  "root_cause": "BGP session timeout due to fiber cut during construction work"
}
```

## 🛠️ Core Tools and Capabilities

### Ingestion Agent Tools:
- **`validate_incident_format()`**: Validates data structure and quality
- **`ingest_incident_data()`**: Processes individual incident records
- **`batch_ingest_incidents()`**: Handles bulk data imports

### Resolution Agent Tools:
- **`retrieve_context_from_query()`**: Searches for similar historical incidents
- **`analyze_incident_patterns()`**: Identifies patterns and correlations
- **`suggest_resolution_steps()`**: Generates actionable resolution plans

## 🚀 Getting Started

### Prerequisites
```bash
pip install -r backend/requirements.txt
```

### Environment Setup
Create a `.env` file in the backend directory:
```env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=your-region
GOOGLE_CLOUD_QUOTA_PROJECT_ID=your-project-id
MODEL=gemini-2.0-flash-001
INDEX_ENDPOINT_ID=your-vector-search-endpoint
DEPLOYED_INDEX_ID=your-deployed-index-id
EMBEDDINGS_FILE=embeddings_text.json
```

### Basic Usage

#### 1. Data Ingestion Example
```python
from backend.ingestion_agent import ingest_incident_data, validate_incident_format

# Validate incident data
incident_data = {
    "incident_id": "INC-2025001",
    "timestamp": "2025-09-10T14:30:00Z",
    "severity": "High",
    "service_impact": "4G Service Outage",
    "incident_description": "Service outage in Manchester region",
    "resolution_steps": "Restarted BGP processes, verified routing",
    "root_cause": "BGP session failure due to fiber cut"
}

validation_result = validate_incident_format(incident_data)
if validation_result == "VALID":
    result = ingest_incident_data(incident_data)
    print(result)
else:
    print(f"Validation failed: {validation_result}")
```

#### 2. Incident Resolution Example
```python
from backend.resoltuion_agent import retrieve_context_from_query, suggest_resolution_steps

# Search for similar incidents
query = "4G service outage packet loss Manchester"
similar_incidents = retrieve_context_from_query(query, num_neighbors=10)

# Get resolution recommendations
resolution_plan = suggest_resolution_steps(similar_incidents, {
    "service_impact": "4G Service Performance Issues",
    "description": "Intermittent packet loss in Glasgow area"
})
```

#### 3. Coordinated Workflow Example
```python
from backend.agent import root_agent

# The root agent automatically coordinates both sub-agents
# For resolution requests, it uses resolution tools
# For ingestion requests, it uses ingestion tools
# For complex workflows, it orchestrates both
```

## 📋 Workflow Examples

### Standard Resolution Workflow:
1. **Query Phase**: Search vector database for similar incidents
2. **Analysis Phase**: Identify patterns and root cause correlations
3. **Resolution Phase**: Generate step-by-step action plan
4. **Learning Phase**: After resolution, ingest the complete incident record

### Batch Data Import Workflow:
1. **Validation Phase**: Check data quality and format compliance
2. **Processing Phase**: Generate embeddings and store in vector database
3. **Quality Assurance**: Verify searchability and data integrity
4. **Analytics Phase**: Analyze new patterns and update system insights

### Quality Improvement Workflow:
1. **Assessment Phase**: Evaluate existing data quality
2. **Gap Analysis**: Identify areas for data enhancement
3. **Optimization Phase**: Implement improvements for better searchability
4. **Validation Phase**: Test search accuracy and resolution effectiveness

## 🔧 Advanced Features

### Multi-Dimensional Search
The resolution agent uses sophisticated search strategies:
- **Service-based searches**: Target specific service types
- **Symptom-based searches**: Find incidents with similar technical symptoms
- **Component-based searches**: Locate incidents affecting similar infrastructure
- **Root cause searches**: Identify incidents with known underlying causes

### Pattern Recognition
Advanced analytics capabilities include:
- **Severity distribution analysis**: Understanding incident criticality patterns
- **Service impact correlation**: Mapping relationships between services
- **Root cause trending**: Identifying emerging failure patterns
- **Resolution effectiveness tracking**: Measuring success rates of different approaches

### Quality Metrics
Comprehensive monitoring includes:
- **Data completeness scores**: Ensuring all required fields are populated
- **Standardization compliance**: Maintaining consistent categorization
- **Searchability optimization**: Maximizing vector search effectiveness
- **Resolution success tracking**: Measuring outcome effectiveness

## 📁 Project Structure

```
backend/
├── agent.py                    # Root coordinator agent
├── prompts.py                  # Coordinator instructions
├── tools.py                    # Legacy tools (deprecated)
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
├── ingestion_agent/
│   ├── __init__.py
│   ├── agent.py               # Ingestion agent definition
│   ├── prompts.py             # Ingestion-specific instructions
│   └── tools.py               # Data validation and storage tools
└── resoltuion_agent/
    ├── __init__.py
    ├── agent.py               # Resolution agent definition
    ├── prompts.py             # Resolution-specific instructions
    └── tools.py               # Search and analysis tools
```

## 🌟 Key Benefits

### Specialized Expertise
- **Focused Capabilities**: Each agent optimized for specific aspects of incident management
- **Domain Knowledge**: Specialized instructions and tools for data management vs. resolution
- **Quality Assurance**: Dedicated validation processes ensure high-quality data

### Scalable Architecture
- **Modular Design**: Independent agents can be scaled or modified separately
- **Workflow Flexibility**: Support for simple single-agent tasks or complex coordinated operations
- **Future Extensibility**: Easy to add new specialized agents for emerging requirements

### Intelligent Coordination
- **Smart Routing**: Automatic determination of appropriate agent tools based on request type
- **Context Preservation**: Maintain conversation state across multi-agent interactions
- **Error Recovery**: Robust fallback strategies when individual agents encounter issues

### Continuous Learning
- **Feedback Loop**: Resolution outcomes improve ingestion data quality recommendations
- **Pattern Evolution**: System becomes more intelligent as it processes more incidents
- **Quality Improvement**: Ongoing optimization of both data management and resolution processes

## 🤝 Contributing

This multi-agent architecture provides a robust foundation for network incident management. Each agent can be enhanced independently while maintaining seamless coordination through the root agent.

## 📄 License

This project is part of the NetGuardian AI incident management system.
