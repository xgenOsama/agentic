#!/usr/bin/env python3
"""
Test script for ingestion agent tools
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ingestion_tools():
    """Test the ingestion agent tools"""
    print("🧪 TESTING INGESTION AGENT TOOLS")
    print("=" * 50)
    
    try:
        from backend.ingestion_agent.tools import test_ingestion_setup, validate_incident_format, ingest_incident_data
        
        # Test 1: Setup verification
        print("1️⃣ TESTING SETUP:")
        setup_result = test_ingestion_setup()
        print(setup_result)
        
        # Test 2: Validation function
        print("\n2️⃣ TESTING VALIDATION:")
        test_incident = {
            "incident_id": "INC-TEST001",
            "timestamp": "2025-09-10T14:30:00Z",
            "severity": "High",
            "service_impact": "Test Service Outage",
            "incident_description": "This is a test incident for validation purposes",
            "resolution_steps": "1. Test step 1. 2. Test step 2. 3. Verify resolution.",
            "root_cause": "Testing ingestion functionality"
        }
        
        validation_result = validate_incident_format(test_incident)
        print(f"Validation result: {validation_result}")
        
        if validation_result == "VALID":
            print("✅ Validation passed!")
            
            # Test 3: Ingestion function
            print("\n3️⃣ TESTING INGESTION:")
            ingestion_result = ingest_incident_data(test_incident)
            print(f"\nIngestion result:\n{ingestion_result}")
            
        else:
            print(f"❌ Validation failed: {validation_result}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    test_ingestion_tools()
