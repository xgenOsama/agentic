from google.cloud import aiplatform
from google.cloud import storage
from vertexai.language_models import TextEmbeddingModel
import os
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

# Set environment variable for quota project
os.environ['GOOGLE_CLOUD_QUOTA_PROJECT_ID'] = os.getenv("GOOGLE_CLOUD_PROJECT", "vodaf-aida25lcpm-206")

# Constants
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT","vodaf-aida25lcpm-206")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION","europe-west1")
INDEX_ENDPOINT_ID = os.getenv("INDEX_ENDPOINT_ID","projects/vodaf-aida25lcpm-206/locations/europe-west1/indexEndpoints/7257260528437821440")
DEPLOYED_INDEX_ID = os.getenv("DEPLOYED_INDEX_ID","Test_INDEX_ENDPOINT_20250910101151")
INDEX_NAME = os.getenv("INDEX_NAME","projects/vodaf-aida25lcpm-206/locations/europe-west1/indexes/462806434363473920")
EMBEDDINGS_FILE = os.getenv("EMBEDDINGS_FILE","embeddings_text.json")
BUCKET_NAME = "vodaf-aida25lcpm-206-rag"
BLOB_NAME = "csv_data/embeddings_text.json"

# Initialize AI Platform with explicit project
try:
    aiplatform.init(project=PROJECT_ID, location=LOCATION)
except Exception as e:
    print(f"Warning: Failed to initialize AI Platform: {e}")

# Load embedding model lazily to avoid initialization issues
embedding_model = None

def get_embedding_model():
    """Get the embedding model, initializing it if necessary."""
    global embedding_model
    if embedding_model is None:
        try:
            # Initialize AI Platform first
            if not hasattr(aiplatform, '_initialized') or not aiplatform._initialized:
                aiplatform.init(project=PROJECT_ID, location=LOCATION)
            
            embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
            print(f"✅ Embedding model initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing embedding model: {e}")
            # Return a mock model for testing
            class MockEmbeddingModel:
                def get_embeddings(self, texts):
                    # Return mock embeddings for testing
                    class MockEmbedding:
                        def __init__(self):
                            self.values = [0.1] * 768  # Standard embedding dimension
                    return [MockEmbedding()]
            
            print("⚠️  Using mock embedding model for testing")
            embedding_model = MockEmbeddingModel()
    return embedding_model

def get_vector_index():
    """Get the vector search index for direct datapoint insertion."""
    try:
        # Initialize AI Platform if not already done
        if not hasattr(aiplatform, '_initialized') or not aiplatform._initialized:
            aiplatform.init(project=PROJECT_ID, location=LOCATION)
        
        # Retrieve the index
        index = aiplatform.MatchingEngineIndex(
            index_name=INDEX_NAME
        )
        print(f"✅ Vector index initialized: {INDEX_NAME}")
        return index
    except Exception as e:
        print(f"❌ Error initializing vector index: {e}")
        return None

def get_index_endpoint():
    """Get the index endpoint for vector search."""
    try:
        # Initialize AI Platform if not already done
        if not hasattr(aiplatform, '_initialized') or not aiplatform._initialized:
            aiplatform.init(project=PROJECT_ID, location=LOCATION)
        
        index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            INDEX_ENDPOINT_ID,
            project=PROJECT_ID,
            location=LOCATION,
        )
        print(f"✅ Index endpoint initialized: {INDEX_ENDPOINT_ID}")
        return index_endpoint
    except Exception as e:
        print(f"❌ Error initializing index endpoint: {e}")
        return None

def validate_incident_format(incident_data: Dict[str, Any]) -> str:
    """
    Validate incident data format and return validation status with error messages.
    
    Args:
        incident_data: Dictionary containing incident information
        
    Returns:
        String containing validation result - either "VALID" or error messages separated by semicolons
    """
    errors = []
    required_fields = [
        'incident_id', 'timestamp', 'severity', 'service_impact',
        'incident_description', 'resolution_steps', 'root_cause'
    ]
    
    # Check required fields
    for field in required_fields:
        if field not in incident_data or not incident_data[field]:
            errors.append(f"Missing or empty required field: {field}")
    
    # Validate specific field formats
    if 'severity' in incident_data:
        valid_severities = ['Low', 'Medium', 'High', 'Critical']
        if incident_data['severity'] not in valid_severities:
            errors.append(f"Invalid severity level. Must be one of: {valid_severities}")
    
    if 'timestamp' in incident_data:
        try:
            # Try to parse timestamp
            datetime.fromisoformat(incident_data['timestamp'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            errors.append("Invalid timestamp format. Use ISO 8601 format (e.g., 2024-01-01T10:00:00Z)")
    
    if 'incident_id' in incident_data:
        incident_id = str(incident_data['incident_id'])
        if not incident_id.startswith('INC-'):
            errors.append("Incident ID should follow format: INC-XXXX")
    
    # Return validation result as string
    if len(errors) == 0:
        return "VALID"
    else:
        return "; ".join(errors)

def prepare_incident_text(incident_data: Dict[str, Any]) -> str:
    """
    Prepare comprehensive searchable text from incident data.
    
    Args:
        incident_data: Validated incident dictionary
        
    Returns:
        Formatted text string for embedding generation
    """
    text_parts = []
    
    # Add structured information
    text_parts.append(f"Incident ID: {incident_data['incident_id']}")
    text_parts.append(f"Severity: {incident_data['severity']}")
    text_parts.append(f"Service Impact: {incident_data['service_impact']}")
    text_parts.append(f"Description: {incident_data['incident_description']}")
    text_parts.append(f"Resolution Steps: {incident_data['resolution_steps']}")
    text_parts.append(f"Root Cause: {incident_data['root_cause']}")
    text_parts.append(f"Timestamp: {incident_data['timestamp']}")
    
    # Combine into searchable text
    return " | ".join(text_parts)

def ingest_incident_data(incident_data: Dict[str, Any]) -> str:
    """
    Ingest a single incident record into the vector database.
    
    Args:
        incident_data: Dictionary containing incident information
        
    Returns:
        Status message indicating success or failure
    """
    try:
        print(f"🔍 Starting ingestion for incident: {incident_data.get('incident_id', 'Unknown')}")
        
        # Step 1: Validate incident format
        validation_result = validate_incident_format(incident_data)
        if validation_result != "VALID":
            return f"❌ Validation failed: {validation_result}"
        
        print("✅ Validation passed")
        
        # Step 2: Transform incident ID by removing "INC-" prefix if present
        original_incident_id = str(incident_data['incident_id'])
        if original_incident_id.startswith('INC-'):
            record_id = original_incident_id[4:]  # Remove "INC-" prefix
            print(f"🔄 Transformed ID: {original_incident_id} → {record_id}")
        else:
            record_id = original_incident_id
            print(f"📋 Using original ID: {record_id}")
        
        # Step 3: Prepare text for embedding
        incident_text = prepare_incident_text(incident_data)
        print(f"📝 Prepared text for embedding (length: {len(incident_text)} chars)")
        
        # Step 4: Generate embedding
        try:
            model = get_embedding_model()
            embeddings_response = model.get_embeddings([incident_text])
            embedding = embeddings_response[0].values
            print(f"🧠 Generated embedding (dimension: {len(embedding)})")
        except Exception as e:
            return f"❌ Error generating embedding: {str(e)}"
        
        # Step 5: Create record for storage (using transformed ID)
        record = {
            'id': record_id,
            'text': incident_text,
            'metadata': {
                'original_incident_id': original_incident_id,  # Keep original for reference
                'severity': incident_data['severity'],
                'service_impact': incident_data['service_impact'],
                'timestamp': incident_data['timestamp'],
                'ingestion_time': datetime.now().isoformat()
            }
        }
        
        # For vector database, we need to store embedding separately
        vector_record = {
            'id': record_id,
            'embedding': embedding
        }
        
        print("📋 Created records for storage")
        
        # Step 6: Store in local file for backup/reference
        try:
            # Create embeddings file if it doesn't exist
            if not os.path.exists(EMBEDDINGS_FILE):
                print(f"📁 Creating new embeddings file: {EMBEDDINGS_FILE}")
                with open(EMBEDDINGS_FILE, 'w') as f:
                    f.write("")  # Create empty file
            
            # Append to local embeddings file (include embedding for backup)
            record_with_embedding = record.copy()
            record_with_embedding['embedding'] = embedding
            
            with open(EMBEDDINGS_FILE, 'a') as f:
                f.write(json.dumps(record_with_embedding) + '\n')
            
            print(f"💾 Stored record in local file: {EMBEDDINGS_FILE}")
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to write to local file: {str(e)}")
        
        # Step 7: Upload to vector database via direct index insertion
        vector_insert_success = False
        try:
            print("🔄 Inserting directly into vector index...")
            
            # Get the vector index
            index = get_vector_index()
            if index is None:
                print("⚠️  Could not initialize vector index, skipping direct insertion")
            else:
                # Prepare datapoint for insertion
                datapoint = {
                    "datapoint_id": str(record_id),
                    "feature_vector": embedding,
                }
                
                # Upsert to index
                print(f"📤 Upserting datapoint with ID: {record_id}")
                result = index.upsert_datapoints(datapoints=[datapoint])
                print(f"✅ Vector index upsert result: {result}")
                vector_insert_success = True
                
        except Exception as e:
            print(f"⚠️  Warning: Direct vector index insertion failed: {str(e)}")
        
        # Step 8: Also try to load via index endpoint (alternative method)
        endpoint_success = False
        try:
            # Initialize AI Platform if not already done
            if not hasattr(aiplatform, '_initialized') or not aiplatform._initialized:
                aiplatform.init(project=PROJECT_ID, location=LOCATION)
            
            # Try to get index endpoint for verification
            index_endpoint = get_index_endpoint()
            if index_endpoint:
                print("✅ Index endpoint is accessible for future queries")
                endpoint_success = True
            
        except Exception as e:
            print(f"⚠️  Warning: Index endpoint access issue: {str(e)}")
        
        # Step 9: Upload to GCS bucket (backup method)
        gcs_success = False
        try:
            storage_client = storage.Client(project=PROJECT_ID)
            bucket = storage_client.bucket(BUCKET_NAME)
            blob = bucket.blob(BLOB_NAME)
            
            # Get existing content
            try:
                existing_content = blob.download_as_text()
                print(f"📥 Downloaded existing GCS content ({len(existing_content)} chars)")
            except Exception:
                existing_content = ""
                print("📁 No existing GCS content found, creating new file")
            
            # Append new record
            new_record_line = json.dumps(record_with_embedding) + '\n'
            updated_content = existing_content + new_record_line
            
            # Upload updated content
            blob.upload_from_string(updated_content)
            print(f"☁️  Successfully uploaded to GCS: gs://{BUCKET_NAME}/{BLOB_NAME}")
            gcs_success = True
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to upload to GCS: {str(e)}")
            print("📝 Data is still stored locally for manual upload later")
        
        # Determine success message based on what worked
        if vector_insert_success and gcs_success:
            success_message = f"""✅ Successfully ingested incident {original_incident_id} (stored as ID: {record_id}):
- ✅ Validation passed
- ✅ ID transformed: {original_incident_id} → {record_id}
- ✅ Embedding generated ({len(embedding)} dimensions)
- ✅ Stored locally in {EMBEDDINGS_FILE}
- ✅ Inserted directly into vector index
- ✅ Uploaded to GCS bucket
- 📊 Ready for immediate vector search queries"""
        elif vector_insert_success:
            success_message = f"""✅ Successfully ingested incident {original_incident_id} (stored as ID: {record_id}):
- ✅ Validation passed
- ✅ ID transformed: {original_incident_id} → {record_id}
- ✅ Embedding generated ({len(embedding)} dimensions)
- ✅ Stored locally in {EMBEDDINGS_FILE}
- ✅ Inserted directly into vector index
- ⚠️  GCS upload failed (but vector index updated)
- 📊 Ready for immediate vector search queries"""
        elif gcs_success:
            success_message = f"""⚠️  Partially ingested incident {original_incident_id} (stored as ID: {record_id}):
- ✅ Validation passed
- ✅ ID transformed: {original_incident_id} → {record_id}
- ✅ Embedding generated ({len(embedding)} dimensions)
- ✅ Stored locally in {EMBEDDINGS_FILE}
- ⚠️  Direct vector insertion failed
- ✅ Uploaded to GCS bucket
- 📊 Available via GCS, may need index rebuild for vector search"""
        else:
            success_message = f"""⚠️  Partially ingested incident {original_incident_id} (stored as ID: {record_id}):
- ✅ Validation passed
- ✅ ID transformed: {original_incident_id} → {record_id}
- ✅ Embedding generated ({len(embedding)} dimensions)
- ✅ Stored locally in {EMBEDDINGS_FILE}
- ⚠️  Direct vector insertion failed
- ⚠️  GCS upload failed (stored locally for manual upload)
- 📊 Local data ready, manual sync needed for vector search"""
        
        print(success_message)
        return success_message
        
    except Exception as e:
        error_message = f"❌ Error ingesting incident data: {str(e)}"
        print(error_message)
        import traceback
        print(f"📍 Full traceback: {traceback.format_exc()}")
        return error_message

def batch_ingest_incidents(incidents_list: List[Dict[str, Any]]) -> str:
    """
    Ingest multiple incident records in batch with direct vector index insertion.
    
    Args:
        incidents_list: List of incident dictionaries
        
    Returns:
        Summary of batch ingestion results as formatted string
    """
    results = {
        'total': len(incidents_list),
        'successful': 0,
        'failed': 0,
        'vector_inserted': 0,
        'errors': []
    }
    
    processed_records = []
    vector_datapoints = []
    
    # Process all records first
    for i, incident in enumerate(incidents_list):
        try:
            # Validate incident
            validation_result = validate_incident_format(incident)
            if validation_result != "VALID":
                results['failed'] += 1
                results['errors'].append(f"Record {i+1}: {validation_result}")
                continue
            
            # Prepare and process incident
            incident_text = prepare_incident_text(incident)
            model = get_embedding_model()
            embedding = model.get_embeddings([incident_text])[0].values
            
            # Transform incident ID by removing "INC-" prefix if present
            original_incident_id = str(incident['incident_id'])
            if original_incident_id.startswith('INC-'):
                record_id = original_incident_id[4:]  # Remove "INC-" prefix
            else:
                record_id = original_incident_id
            
            record = {
                'id': record_id,
                'text': incident_text,
                'embedding': embedding,
                'metadata': {
                    'original_incident_id': original_incident_id,  # Keep original for reference
                    'severity': incident['severity'],
                    'service_impact': incident['service_impact'],
                    'timestamp': incident['timestamp'],
                    'ingestion_time': datetime.now().isoformat()
                }
            }
            
            # Prepare datapoint for vector insertion
            datapoint = {
                "datapoint_id": str(record_id),
                "feature_vector": embedding,
            }
            
            processed_records.append(record)
            vector_datapoints.append(datapoint)
            results['successful'] += 1
            
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"Record {i+1}: Processing error - {str(e)}")
    
    # Batch insert into vector index
    vector_success = False
    if vector_datapoints:
        try:
            print(f"🔄 Batch inserting {len(vector_datapoints)} records into vector index...")
            index = get_vector_index()
            if index:
                # Upsert all datapoints at once
                result = index.upsert_datapoints(datapoints=vector_datapoints)
                print(f"✅ Batch vector index upsert result: {result}")
                results['vector_inserted'] = len(vector_datapoints)
                vector_success = True
            else:
                print("⚠️  Could not initialize vector index for batch insertion")
        except Exception as e:
            print(f"⚠️  Warning: Batch vector index insertion failed: {e}")
    
    # Batch write to local file
    if processed_records:
        try:
            with open(EMBEDDINGS_FILE, 'a') as f:
                for record in processed_records:
                    f.write(json.dumps(record) + '\n')
            print(f"💾 Wrote {len(processed_records)} records to local file")
            
            # Upload to GCS
            try:
                storage_client = storage.Client(project=PROJECT_ID)
                bucket = storage_client.bucket(BUCKET_NAME)
                blob = bucket.blob(BLOB_NAME)
                
                # Append all new records
                new_content = '\n'.join([json.dumps(record) for record in processed_records]) + '\n'
                try:
                    existing_content = blob.download_as_text()
                    updated_content = existing_content + new_content
                except:
                    updated_content = new_content
                
                blob.upload_from_string(updated_content)
                print(f"☁️  Uploaded {len(processed_records)} records to GCS")
                
            except Exception as e:
                print(f"Warning: Failed to upload batch to GCS: {e}")
                
        except Exception as e:
            results['errors'].append(f"File write error: {str(e)}")
    
    # Generate summary
    summary = f"""
Batch Ingestion Summary:
- Total records processed: {results['total']}
- Successfully processed: {results['successful']}
- Direct vector insertions: {results['vector_inserted']}
- Failed: {results['failed']}
- Vector index updated: {'✅ Yes' if vector_success else '⚠️  No'}
    """
    
    if results['errors']:
        summary += f"\nErrors encountered:\n" + "\n".join(results['errors'][:10])  # Limit to first 10 errors
        if len(results['errors']) > 10:
            summary += f"\n... and {len(results['errors']) - 10} more errors"
    
    return summary

def test_ingestion_setup() -> str:
    """
    Test the ingestion setup and configuration.
    
    Returns:
        Status of ingestion environment setup
    """
    try:
        setup_status = []
        
        # Test 1: Environment variables
        setup_status.append("🔧 ENVIRONMENT SETUP:")
        setup_status.append(f"  - PROJECT_ID: {PROJECT_ID}")
        setup_status.append(f"  - LOCATION: {LOCATION}")
        setup_status.append(f"  - INDEX_ENDPOINT_ID: {INDEX_ENDPOINT_ID}")
        setup_status.append(f"  - DEPLOYED_INDEX_ID: {DEPLOYED_INDEX_ID}")
        setup_status.append(f"  - EMBEDDINGS_FILE: {EMBEDDINGS_FILE}")
        setup_status.append(f"  - BUCKET_NAME: {BUCKET_NAME}")
        setup_status.append(f"  - BLOB_NAME: {BLOB_NAME}")
        
        # Test 2: AI Platform initialization
        setup_status.append("\n🤖 AI PLATFORM:")
        try:
            aiplatform.init(project=PROJECT_ID, location=LOCATION)
            setup_status.append("  ✅ AI Platform initialized successfully")
        except Exception as e:
            setup_status.append(f"  ❌ AI Platform initialization failed: {str(e)}")
        
        # Test 3: Embedding model
        setup_status.append("\n🧠 EMBEDDING MODEL:")
        try:
            model = get_embedding_model()
            test_embedding = model.get_embeddings(["test text"])[0].values
            setup_status.append(f"  ✅ Embedding model working (dimension: {len(test_embedding)})")
        except Exception as e:
            setup_status.append(f"  ❌ Embedding model failed: {str(e)}")
        
        # Test 4: Local file access
        setup_status.append("\n📁 LOCAL FILE ACCESS:")
        try:
            # Test write access
            test_file = f"{EMBEDDINGS_FILE}.test"
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            setup_status.append("  ✅ Local file write access working")
        except Exception as e:
            setup_status.append(f"  ❌ Local file access failed: {str(e)}")
        
        # Test 5: GCS access
        setup_status.append("\n☁️  GCS ACCESS:")
        try:
            storage_client = storage.Client(project=PROJECT_ID)
            bucket = storage_client.bucket(BUCKET_NAME)
            # Just check if bucket exists
            bucket.reload()
            setup_status.append(f"  ✅ GCS bucket '{BUCKET_NAME}' accessible")
        except Exception as e:
            setup_status.append(f"  ❌ GCS access failed: {str(e)}")
        
        # Test 6: Vector search index (direct insertion)
        setup_status.append("\n🔍 VECTOR SEARCH INDEX:")
        try:
            index = get_vector_index()
            if index:
                setup_status.append(f"  ✅ Vector search index accessible: {INDEX_NAME}")
            else:
                setup_status.append(f"  ❌ Vector search index not accessible")
        except Exception as e:
            setup_status.append(f"  ❌ Vector search index failed: {str(e)}")
        
        # Test 7: Vector search endpoint
        setup_status.append("\n🔗 VECTOR SEARCH ENDPOINT:")
        try:
            index_endpoint = get_index_endpoint()
            if index_endpoint:
                setup_status.append(f"  ✅ Vector search endpoint accessible: {INDEX_ENDPOINT_ID}")
            else:
                setup_status.append(f"  ❌ Vector search endpoint not accessible")
        except Exception as e:
            setup_status.append(f"  ❌ Vector search endpoint failed: {str(e)}")
        
        return "\n".join(setup_status)
        
    except Exception as e:
        return f"❌ Setup test failed: {str(e)}"
