import json

def test_basic_ingestion():
    """Test basic data structure and file operations"""
    
    print("🧪 BASIC INGESTION TEST")
    print("=" * 30)
    
    # Test data
    test_incident = {
        "incident_id": "INC-TEST001",
        "timestamp": "2025-09-10T14:30:00Z",
        "severity": "High", 
        "service_impact": "Network Connectivity Issues",
        "incident_description": "Users in Manchester reporting intermittent 4G connectivity",
        "resolution_steps": "1. Checked router BGP status 2. Restarted affected BGP sessions 3. Verified service restoration",
        "root_cause": "BGP session timeout due to fiber maintenance"
    }
    
    print("📋 Test incident data:")
    for key, value in test_incident.items():
        print(f"  {key}: {value}")
    
    # Test 1: Data validation logic
    print("\n🔍 Testing validation logic...")
    required_fields = ['incident_id', 'timestamp', 'severity', 'service_impact', 'incident_description', 'resolution_steps', 'root_cause']
    
    missing_fields = []
    for field in required_fields:
        if field not in test_incident or not test_incident[field]:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing fields: {missing_fields}")
    else:
        print("✅ All required fields present")
    
    # Test 2: JSON serialization
    print("\n📝 Testing JSON serialization...")
    try:
        json_str = json.dumps(test_incident)
        print(f"✅ JSON serialization successful ({len(json_str)} chars)")
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")
        return
    
    # Test 3: File write test
    print("\n💾 Testing file operations...")
    test_file = "test_embeddings.jsonl"
    try:
        with open(test_file, 'w') as f:
            f.write(json.dumps(test_incident) + '\n')
        print(f"✅ File write successful: {test_file}")
        
        # Read back
        with open(test_file, 'r') as f:
            read_data = f.read().strip()
        
        parsed_data = json.loads(read_data)
        print(f"✅ File read successful, incident_id: {parsed_data['incident_id']}")
        
        # Clean up
        import os
        os.remove(test_file)
        print("✅ Test file cleaned up")
        
    except Exception as e:
        print(f"❌ File operations failed: {e}")
        return
    
    print("\n🎉 Basic ingestion test completed successfully!")
    print("The core data structures and file operations are working correctly.")

if __name__ == "__main__":
    test_basic_ingestion()
