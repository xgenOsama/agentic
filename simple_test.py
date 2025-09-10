#!/usr/bin/env python3
"""
Simple ingestion test to identify issues
"""

# Test 1: Basic imports
try:
    print("🔄 Testing imports...")
    import sys
    import os
    
    # Add the project root to path
    project_root = os.path.dirname(__file__)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from backend.ingestion_agent.tools import validate_incident_format, ingest_incident_data
    print("✅ Imports successful")
    
    # Test 2: Simple validation
    print("\n🔍 Testing validation...")
    test_data = {
        "incident_id": "INC-TEST001",
        "timestamp": "2025-09-10T14:30:00Z", 
        "severity": "High",
        "service_impact": "Test Service",
        "incident_description": "Test description",
        "resolution_steps": "Test steps",
        "root_cause": "Test cause"
    }
    
    result = validate_incident_format(test_data)
    print(f"Validation result: {result}")
    
    if result == "VALID":
        print("✅ Validation passed")
        
        # Test 3: Try ingestion
        print("\n💾 Testing ingestion...")
        ingest_result = ingest_incident_data(test_data)
        print(f"Ingestion result: {ingest_result}")
    else:
        print(f"❌ Validation failed: {result}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    print(f"Traceback: {traceback.format_exc()}")
