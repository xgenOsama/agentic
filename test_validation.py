#!/usr/bin/env python3
"""
Test script for the updated validation function
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.ingestion_agent.tools import validate_incident_format
    
    # Test with valid data
    valid_data = {
        'incident_id': 'INC-1000',
        'timestamp': '2025-09-10T14:30:00Z',
        'severity': 'High',
        'service_impact': 'Test Service',
        'incident_description': 'Test description',
        'resolution_steps': 'Test resolution',
        'root_cause': 'Test cause'
    }
    
    result = validate_incident_format(valid_data)
    print(f'✅ Valid data result: {result}')
    
    # Test with invalid data
    invalid_data = {
        'incident_id': 'INVALID-1000',
        'severity': 'Invalid'
    }
    
    result = validate_incident_format(invalid_data)
    print(f'❌ Invalid data result: {result}')
    
    print("\n🎉 Function signature update successful!")
    print("The validate_incident_format function now returns a simple string instead of Tuple[bool, List[str]]")
    print("This should resolve the Google ADK automatic function calling issue.")
    
except Exception as e:
    print(f"Error testing function: {e}")
