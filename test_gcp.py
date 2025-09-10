#!/usr/bin/env python3
"""
Test Google Cloud authentication and access
"""

def test_gcp_access():
    """Test basic Google Cloud Platform access"""
    
    print("☁️  TESTING GOOGLE CLOUD ACCESS")
    print("=" * 40)
    
    # Test environment variables
    import os
    print("🔧 Environment Variables:")
    gcp_vars = [
        'GOOGLE_CLOUD_PROJECT',
        'GOOGLE_CLOUD_LOCATION', 
        'GOOGLE_CLOUD_QUOTA_PROJECT_ID',
        'INDEX_ENDPOINT_ID',
        'DEPLOYED_INDEX_ID'
    ]
    
    for var in gcp_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: Not set")
    
    # Test 1: Basic Google Cloud imports
    print("\n📦 Testing Google Cloud imports...")
    try:
        from google.cloud import storage
        print("  ✅ google.cloud.storage imported successfully")
    except Exception as e:
        print(f"  ❌ google.cloud.storage import failed: {e}")
        return
    
    try:
        from google.cloud import aiplatform
        print("  ✅ google.cloud.aiplatform imported successfully")
    except Exception as e:
        print(f"  ❌ google.cloud.aiplatform import failed: {e}")
        return
    
    try:
        from vertexai.language_models import TextEmbeddingModel
        print("  ✅ vertexai.language_models imported successfully")
    except Exception as e:
        print(f"  ❌ vertexai.language_models import failed: {e}")
        return
    
    # Test 2: Authentication check
    print("\n🔑 Testing authentication...")
    try:
        # Try to create a storage client
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'vodaf-aida25lcpm-206')
        client = storage.Client(project=project_id)
        print(f"  ✅ Storage client created for project: {project_id}")
    except Exception as e:
        print(f"  ❌ Storage client creation failed: {e}")
        print("  💡 This might indicate authentication issues")
        return
    
    # Test 3: AI Platform initialization
    print("\n🤖 Testing AI Platform...")
    try:
        location = os.getenv('GOOGLE_CLOUD_LOCATION', 'europe-west1')
        aiplatform.init(project=project_id, location=location)
        print(f"  ✅ AI Platform initialized for {project_id} in {location}")
    except Exception as e:
        print(f"  ❌ AI Platform initialization failed: {e}")
        return
    
    # Test 4: Embedding model access
    print("\n🧠 Testing embedding model...")
    try:
        model = TextEmbeddingModel.from_pretrained("text-embedding-004")
        print("  ✅ Embedding model loaded successfully")
        
        # Test embedding generation
        test_text = "This is a test for network incident analysis"
        embeddings = model.get_embeddings([test_text])
        embedding_vector = embeddings[0].values
        print(f"  ✅ Generated embedding with {len(embedding_vector)} dimensions")
        
    except Exception as e:
        print(f"  ❌ Embedding model test failed: {e}")
        return
    
    print("\n🎉 Google Cloud access test completed successfully!")
    print("All required GCP services are accessible and working.")

if __name__ == "__main__":
    test_gcp_access()
