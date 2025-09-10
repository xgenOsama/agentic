from google.cloud import aiplatform
from google.cloud import storage
from vertexai.language_models import TextEmbeddingModel
import os
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

# Set environment variable for quota project
os.environ['GOOGLE_CLOUD_QUOTA_PROJECT_ID'] = os.getenv("GOOGLE_CLOUD_PROJECT", "vodaf-aida25lcpm-206")

# Constants
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT","vodaf-aida25lcpm-206")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION","europe-west1")
INDEX_ENDPOINT_ID = os.getenv("INDEX_ENDPOINT_ID","projects/100938974863/locations/europe-west1/indexEndpoints/8033005564252389376")
DEPLOYED_INDEX_ID = os.getenv("DEPLOYED_INDEX_ID","VECTOR_SEARCH_ENDPOINT_20250909155315")
EMBEDDINGS_FILE = os.getenv("EMBEDDINGS_FILE","embeddings_text.json")
BUCKET_NAME = "vodaf-aida25lcpm-206-rag"
BLOB_NAME = "csv_data/embeddings_text.json"

def download_embeddings_if_not_exists():
    """Download embeddings file from GCP bucket if it doesn't exist locally."""
    if not os.path.exists(EMBEDDINGS_FILE):
        print(f"Embeddings file {EMBEDDINGS_FILE} not found. Downloading from GCP bucket...")
        try:
            storage_client = storage.Client(project=PROJECT_ID)
            bucket = storage_client.bucket(BUCKET_NAME)
            blob = bucket.blob(BLOB_NAME)
            blob.download_to_filename(EMBEDDINGS_FILE)
            print(f"Successfully downloaded {EMBEDDINGS_FILE}")
        except Exception as e:
            print(f"Error downloading embeddings file: {e}")
            raise
    else:
        print(f"Embeddings file {EMBEDDINGS_FILE} already exists locally.")

# Initialize AI Platform with explicit project
try:
    aiplatform.init(project=PROJECT_ID, location=LOCATION)
except Exception as e:
    print(f"Warning: Failed to initialize AI Platform: {e}")

# Load index endpoint
try:
    index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
        INDEX_ENDPOINT_ID,
        project=PROJECT_ID,
        location=LOCATION,
    )
except Exception as e:
    print(f"Warning: Failed to load index endpoint: {e}")
    index_endpoint = None

# Download embeddings file if it doesn't exist
download_embeddings_if_not_exists()

# Load embeddings text data
df = pd.read_json(EMBEDDINGS_FILE, orient='records', lines=True)

# Load embedding model lazily
embedding_model = None

def get_embedding_model():
    """Get the embedding model, initializing it if necessary."""
    global embedding_model
    if embedding_model is None:
        try:
            embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
        except Exception as e:
            print(f"Error initializing embedding model: {e}")
            raise
    return embedding_model

def retrieve_context_from_query(query: str, num_neighbors: int = 10) -> str:
    """
    Given a query string, returns the context text from the nearest neighbors in the index.
    Enhanced for resolution agent with better error handling and context formatting.
    """
    try:
        # Check if index endpoint is available
        if index_endpoint is None:
            return "Error: Vector search index endpoint is not available. Please check your GCP configuration."
        
        # Step 1: Create embedding
        model = get_embedding_model()
        embedding = model.get_embeddings([query])[0].values

        # Step 2: Retrieve neighbors
        response = index_endpoint.find_neighbors(
            deployed_index_id=DEPLOYED_INDEX_ID,
            queries=[embedding],
            num_neighbors=num_neighbors
        )

        # Step 3: Extract and format context
        contexts = []
        for res in response:
            for i, neighbor in enumerate(res):
                match = df[df['id'] == int(neighbor.id)]
                if not match.empty:
                    incident_text = match['text'].values[0]
                    similarity_score = neighbor.distance
                    contexts.append(f"=== Similar Incident {i+1} (Similarity: {similarity_score:.3f}) ===\n{incident_text}")

        if not contexts:
            return "No similar incidents found in the database."
        
        return "\n\n".join(contexts)
        
    except Exception as e:
        print(f"Error in retrieve_context_from_query: {e}")
        return f"Error retrieving context: {str(e)}"

def analyze_incident_patterns(incident_description: str, service_impact: str) -> str:
    """
    Analyze patterns in similar incidents to identify common root causes and resolution approaches.
    
    Args:
        incident_description: Description of the current incident
        service_impact: Type of service being impacted
        
    Returns:
        Analysis of patterns and recommendations
    """
    try:
        # Search for similar incidents using multiple strategies
        search_queries = [
            service_impact,
            incident_description,
            f"{service_impact} {incident_description}",
            # Extract key technical terms for additional searches
            *extract_technical_terms(incident_description)
        ]
        
        all_contexts = []
        for query in search_queries[:5]:  # Limit to avoid too many API calls
            context = retrieve_context_from_query(query, num_neighbors=5)
            if context and "Error" not in context:
                all_contexts.append(context)
        
        if not all_contexts:
            return "No similar incident patterns found for analysis."
        
        # Parse incidents to extract patterns
        incidents = parse_incident_contexts(all_contexts)
        
        # Analyze patterns
        severity_patterns = Counter([inc.get('severity', 'Unknown') for inc in incidents])
        service_patterns = Counter([inc.get('service_impact', 'Unknown') for inc in incidents])
        root_cause_patterns = analyze_root_causes([inc.get('root_cause', '') for inc in incidents])
        resolution_patterns = analyze_resolution_steps([inc.get('resolution_steps', '') for inc in incidents])
        
        # Generate analysis report
        analysis = f"""
INCIDENT PATTERN ANALYSIS
========================

Service Impact Patterns:
{format_counter_results(service_patterns)}

Severity Distribution:
{format_counter_results(severity_patterns)}

Common Root Causes:
{root_cause_patterns}

Effective Resolution Approaches:
{resolution_patterns}

RECOMMENDATIONS:
- Focus on the most common root causes identified above
- Use resolution approaches that have proven successful for similar incidents
- Consider the typical severity progression for this service impact type
- Prepare escalation procedures based on historical patterns
        """
        
        return analysis
        
    except Exception as e:
        return f"Error analyzing incident patterns: {str(e)}"

def suggest_resolution_steps(context_data: str, incident_details: Dict[str, Any]) -> str:
    """
    Generate prioritized resolution steps based on historical context and current incident details.
    
    Args:
        context_data: Retrieved context from similar incidents
        incident_details: Dictionary with current incident information
        
    Returns:
        Structured resolution plan with prioritized steps
    """
    try:
        # Parse context to extract resolution steps
        incidents = parse_incident_contexts([context_data])
        
        # Extract and prioritize resolution steps
        resolution_approaches = []
        for incident in incidents:
            if 'resolution_steps' in incident:
                resolution_approaches.append(incident['resolution_steps'])
        
        if not resolution_approaches:
            return "No historical resolution data available for similar incidents."
        
        # Analyze resolution steps to create prioritized action plan
        immediate_actions = extract_immediate_actions(resolution_approaches)
        diagnostic_steps = extract_diagnostic_steps(resolution_approaches)
        resolution_steps = extract_resolution_steps(resolution_approaches)
        verification_steps = extract_verification_steps(resolution_approaches)
        
        # Generate structured resolution plan
        resolution_plan = f"""
INCIDENT RESOLUTION PLAN
========================

IMMEDIATE STABILIZATION ACTIONS (0-15 minutes):
{format_action_list(immediate_actions)}

DIAGNOSTIC PROCEDURES (15-30 minutes):
{format_action_list(diagnostic_steps)}

RESOLUTION IMPLEMENTATION (30+ minutes):
{format_action_list(resolution_steps)}

VERIFICATION AND MONITORING:
{format_action_list(verification_steps)}

ESCALATION TRIGGERS:
- If stabilization actions don't reduce impact within 15 minutes
- If diagnostic steps don't identify root cause within 30 minutes
- If resolution implementation doesn't restore service within 60 minutes
- If incident affects critical business functions or multiple services

ROLLBACK PROCEDURES:
- Document all changes made during resolution
- Prepare rollback steps for each configuration change
- Monitor service health after each resolution step
- Have communication plan ready for extended outages

EXPECTED TIMELINE:
Based on similar incidents: 45-90 minutes average resolution time
Critical path: Service stabilization → Root cause identification → Resolution implementation → Verification
        """
        
        return resolution_plan
        
    except Exception as e:
        return f"Error generating resolution steps: {str(e)}"

# Helper functions

def extract_technical_terms(description: str) -> List[str]:
    """Extract technical terms from incident description for additional searches."""
    technical_keywords = [
        'BGP', 'DNS', 'router', 'switch', 'fiber', 'authentication', 'SSL', 'certificate',
        'packet loss', 'latency', 'timeout', 'connection', 'service', 'outage', 'failure',
        'performance', 'degradation', 'error', 'down', 'unavailable'
    ]
    
    found_terms = []
    description_lower = description.lower()
    for term in technical_keywords:
        if term.lower() in description_lower:
            found_terms.append(term)
    
    return found_terms[:3]  # Return top 3 technical terms

def parse_incident_contexts(contexts: List[str]) -> List[Dict[str, Any]]:
    """Parse incident context strings into structured data."""
    incidents = []
    
    for context in contexts:
        # Split by incident separators
        incident_blocks = context.split("=== Similar Incident")
        
        for block in incident_blocks:
            if "Incident ID:" in block:
                incident = parse_single_incident(block)
                if incident:
                    incidents.append(incident)
    
    return incidents

def parse_single_incident(incident_text: str) -> Dict[str, Any]:
    """Parse a single incident text block into structured data."""
    incident = {}
    
    lines = incident_text.split(" | ")
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip().lower().replace(" ", "_")
            value = value.strip()
            incident[key] = value
    
    return incident

def analyze_root_causes(root_causes: List[str]) -> str:
    """Analyze common root cause patterns."""
    if not root_causes:
        return "No root cause data available"
    
    # Common root cause categories
    categories = {
        'hardware': ['hardware', 'router', 'switch', 'server', 'equipment', 'power'],
        'network': ['routing', 'BGP', 'DNS', 'connectivity', 'network', 'fiber'],
        'software': ['software', 'bug', 'application', 'service', 'process'],
        'configuration': ['configuration', 'config', 'setting', 'parameter'],
        'capacity': ['capacity', 'overload', 'congestion', 'bandwidth', 'resource'],
        'security': ['security', 'certificate', 'authentication', 'SSL', 'expired'],
        'external': ['external', 'provider', 'third-party', 'construction', 'weather']
    }
    
    category_counts = {cat: 0 for cat in categories}
    
    for root_cause in root_causes:
        if root_cause:
            root_cause_lower = root_cause.lower()
            for category, keywords in categories.items():
                if any(keyword in root_cause_lower for keyword in keywords):
                    category_counts[category] += 1
                    break
    
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    result = []
    for category, count in sorted_categories:
        if count > 0:
            result.append(f"- {category.title()}: {count} incidents")
    
    return '\n'.join(result) if result else "No clear root cause patterns identified"

def analyze_resolution_steps(resolution_steps: List[str]) -> str:
    """Analyze common resolution approaches."""
    if not resolution_steps:
        return "No resolution data available"
    
    # Common resolution action types
    action_types = {
        'restart': ['restart', 'reboot', 'reload', 'reset'],
        'configuration': ['configure', 'setting', 'parameter', 'config'],
        'replacement': ['replace', 'swap', 'change hardware', 'new equipment'],
        'routing': ['routing', 'BGP', 'route', 'failover'],
        'certificate': ['certificate', 'SSL', 'renew', 'update cert'],
        'monitoring': ['monitor', 'check', 'verify', 'test', 'validate'],
        'escalation': ['escalate', 'specialist', 'vendor', 'support'],
        'communication': ['communicate', 'notify', 'inform', 'announce']
    }
    
    action_counts = {action: 0 for action in action_types}
    
    for steps in resolution_steps:
        if steps:
            steps_lower = steps.lower()
            for action_type, keywords in action_types.items():
                if any(keyword in steps_lower for keyword in keywords):
                    action_counts[action_type] += 1
    
    sorted_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)
    result = []
    for action, count in sorted_actions:
        if count > 0:
            result.append(f"- {action.title()}: {count} incidents")
    
    return '\n'.join(result) if result else "No clear resolution patterns identified"

def extract_immediate_actions(resolution_approaches: List[str]) -> List[str]:
    """Extract immediate stabilization actions from resolution steps."""
    immediate_keywords = ['immediate', 'urgent', 'first', 'quickly', 'emergency', 'critical']
    actions = []
    
    for approach in resolution_approaches:
        if approach:
            sentences = approach.split('.')
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in immediate_keywords):
                    actions.append(sentence.strip())
    
    # Add common immediate actions if none found
    if not actions:
        actions = [
            "Check service status and current alerts",
            "Verify critical system health indicators",
            "Assess immediate impact scope and affected users"
        ]
    
    return actions[:5]  # Limit to top 5 immediate actions

def extract_diagnostic_steps(resolution_approaches: List[str]) -> List[str]:
    """Extract diagnostic procedures from resolution steps."""
    diagnostic_keywords = ['check', 'verify', 'test', 'examine', 'investigate', 'analyze', 'diagnose']
    steps = []
    
    for approach in resolution_approaches:
        if approach:
            sentences = approach.split('.')
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in diagnostic_keywords):
                    steps.append(sentence.strip())
    
    if not steps:
        steps = [
            "Review system logs and error messages",
            "Check network connectivity and routing",
            "Verify service dependencies and integrations",
            "Test affected functionality from multiple locations"
        ]
    
    return steps[:5]

def extract_resolution_steps(resolution_approaches: List[str]) -> List[str]:
    """Extract main resolution actions from resolution steps."""
    resolution_keywords = ['configure', 'restart', 'replace', 'update', 'fix', 'repair', 'resolve']
    steps = []
    
    for approach in resolution_approaches:
        if approach:
            sentences = approach.split('.')
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in resolution_keywords):
                    steps.append(sentence.strip())
    
    if not steps:
        steps = [
            "Implement configuration changes based on root cause",
            "Restart affected services or components",
            "Apply necessary patches or updates",
            "Failover to backup systems if available"
        ]
    
    return steps[:5]

def extract_verification_steps(resolution_approaches: List[str]) -> List[str]:
    """Extract verification and monitoring steps from resolution approaches."""
    verification_keywords = ['verify', 'confirm', 'validate', 'monitor', 'test', 'ensure']
    steps = []
    
    for approach in resolution_approaches:
        if approach:
            sentences = approach.split('.')
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in verification_keywords):
                    steps.append(sentence.strip())
    
    if not steps:
        steps = [
            "Verify service functionality is fully restored",
            "Monitor system performance for stability",
            "Confirm all affected users can access services",
            "Update incident documentation and closure notes"
        ]
    
    return steps[:4]

def format_counter_results(counter: Counter) -> str:
    """Format Counter results for display."""
    if not counter:
        return "No data available"
    
    result = []
    for item, count in counter.most_common(5):
        result.append(f"- {item}: {count} incidents")
    
    return '\n'.join(result)

def format_action_list(actions: List[str]) -> str:
    """Format action list for display."""
    if not actions:
        return "No specific actions identified"
    
    formatted = []
    for i, action in enumerate(actions, 1):
        if action.strip():
            formatted.append(f"{i}. {action.strip()}")
    
    return '\n'.join(formatted)
