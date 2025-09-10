from typing import Dict, List, Any
import json
import os
from datetime import datetime

def simple_validate_incident(incident_data: Dict[str, Any]) -> str:
    """
    Simple validation for incident data.
    
    Args:
        incident_data: Dictionary containing incident information
        
    Returns:
        "VALID" if valid, otherwise error message
    """
    required_fields = [
        'incident_id', 'timestamp', 'severity', 'service_impact',
        'incident_description', 'resolution_steps', 'root_cause'
    ]
    
    errors = []
    
    # Check required fields
    for field in required_fields:
        if field not in incident_data or not incident_data[field]:
            errors.append(f"Missing: {field}")
    
    # Validate severity
    if 'severity' in incident_data:
        valid_severities = ['Low', 'Medium', 'High', 'Critical']
        if incident_data['severity'] not in valid_severities:
            errors.append(f"Invalid severity: {incident_data['severity']}")
    
    # Validate incident_id format
    if 'incident_id' in incident_data:
        if not str(incident_data['incident_id']).startswith('INC-'):
            errors.append("Incident ID must start with 'INC-'")
    
    return "VALID" if not errors else "; ".join(errors)

def simple_ingest_incident(incident_data: Dict[str, Any]) -> str:
    """
    Simple ingestion that stores data locally.
    
    Args:
        incident_data: Dictionary containing incident information
        
    Returns:
        Status message
    """
    try:
        # Validate first
        validation = simple_validate_incident(incident_data)
        if validation != "VALID":
            return f"❌ Validation failed: {validation}"
        
        # Prepare record
        record = {
            'id': str(incident_data['incident_id']),
            'text': f"Incident {incident_data['incident_id']}: {incident_data['service_impact']} - {incident_data['incident_description']} - Resolution: {incident_data['resolution_steps']} - Root Cause: {incident_data['root_cause']}",
            'metadata': {
                'severity': incident_data['severity'],
                'service_impact': incident_data['service_impact'],
                'timestamp': incident_data['timestamp'],
                'ingestion_time': datetime.now().isoformat()
            }
        }
        
        # Store locally
        filename = "simple_incidents.jsonl"
        with open(filename, 'a') as f:
            f.write(json.dumps(record) + '\n')
        
        return f"✅ Successfully stored incident {incident_data['incident_id']} in {filename}"
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

def test_simple_ingestion():
    """Test the simplified ingestion"""
    
    print("🔧 TESTING SIMPLIFIED INGESTION")
    print("=" * 40)
    
    test_incident = {
        "incident_id": "INC-SIMPLE001",
        "timestamp": "2025-09-10T14:30:00Z",
        "severity": "High",
        "service_impact": "4G Network Outage Manchester",
        "incident_description": "Complete 4G service outage affecting Manchester region. Users unable to connect.",
        "resolution_steps": "1. Identified BGP session failure 2. Restarted BGP processes 3. Verified service restoration",
        "root_cause": "BGP session timeout due to fiber maintenance work"
    }
    
    print("📋 Test incident:")
    for key, value in test_incident.items():
        print(f"  {key}: {value}")
    
    print("\n🔍 Testing validation...")
    validation_result = simple_validate_incident(test_incident)
    print(f"Validation: {validation_result}")
    
    if validation_result == "VALID":
        print("\n💾 Testing ingestion...")
        ingestion_result = simple_ingest_incident(test_incident)
        print(f"Ingestion: {ingestion_result}")
        
        # Verify file was created
        if os.path.exists("simple_incidents.jsonl"):
            with open("simple_incidents.jsonl", 'r') as f:
                lines = f.readlines()
            print(f"✅ File created with {len(lines)} records")
        
    else:
        print(f"❌ Validation failed: {validation_result}")

if __name__ == "__main__":
    test_simple_ingestion()
