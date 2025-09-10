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
INDEX_ENDPOINT_ID = os.getenv("INDEX_ENDPOINT_ID","projects/100938974863/locations/europe-west1/indexEndpoints/8033005564252389376")
DEPLOYED_INDEX_ID = os.getenv("DEPLOYED_INDEX_ID","VECTOR_SEARCH_ENDPOINT_20250909155315")
EMBEDDINGS_FILE = os.getenv("EMBEDDINGS_FILE","embeddings_text.json")
BUCKET_NAME = "vodaf-aida25lcpm-206-rag"
BLOB_NAME = "csv_data/embeddings_text.json"

# Initialize AI Platform with explicit project
try:
    aiplatform.init(project=PROJECT_ID, location=LOCATION)
except Exception as e:
    print(f"Warning: Failed to initialize AI Platform: {e}")

INDEX_NAME = "projects/100938974863/locations/europe-west1/indexes/462806434363473920"
# Initialize AI Platform
aiplatform.init(project=PROJECT_ID, location=LOCATION)

# Load index endpoint
index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
    INDEX_ENDPOINT_ID,
    project=PROJECT_ID,
    location=LOCATION,
)

# Retrieve the index
index = aiplatform.MatchingEngineIndex(
    index_name = INDEX_NAME
)

# Load embedding model
embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")

def ingest_new_data_to_index(new_data: pd.DataFrame):
    """
    Ingests new text data into the Matching Engine index.

    Args:
        new_data (pd.DataFrame): DataFrame with 'id' and 'text' columns.
    """

    # Load existing embeddings
    df = pd.read_json(EMBEDDINGS_FILE, orient='records', lines=True)

    # Prepare documents
    documents = []
    for i, row in new_data.iterrows():
        content = row.to_string()
        documents.append(Document(page_content=content, metadata={"row_index": i}))

    # Generate embeddings
    embeddings = [embedding_model.get_embeddings([doc.page_content])[0].values for doc in documents]
    text_chunks = [doc.page_content for doc in documents]

    # Create new DataFrame
    additional_df = pd.DataFrame({
        "id": range(1, len(text_chunks) + 1),
        "text": text_chunks,
        "embedding": embeddings
    })
    
    
    # Assign new IDs
    last_id = df['id'].max() if not df.empty else 0
    additional_df['id'] = range(last_id + 1, last_id + 1 + len(additional_df))

    # Format for upload
    items = []
    for i, row in additional_df.iterrows():
        items.append({
            "datapoint_id": str(row['id']),
            "feature_vector": row['embedding'],
        })
        

    # Upsert to index
    print(index.upsert_datapoints(datapoints=items))
    print(items)
    # Update embeddings file
    updated_df = pd.concat([df, additional_df], ignore_index=True).drop_duplicates(subset='id')
    updated_df.to_json(EMBEDDINGS_FILE, orient='records', lines=True)
    

# def get_embedding_model():
#     """Get the embedding model, initializing it if necessary."""
#     global embedding_model
#     if embedding_model is None:
#         try:
#             # Initialize AI Platform first
#             if not hasattr(aiplatform, '_initialized') or not aiplatform._initialized:
#                 aiplatform.init(project=PROJECT_ID, location=LOCATION)
            
#             embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
#             print(f"✅ Embedding model initialized successfully")
#         except Exception as e:
#             print(f"❌ Error initializing embedding model: {e}")
#             # Return a mock model for testing
#             class MockEmbeddingModel:
#                 def get_embeddings(self, texts):
#                     # Return mock embeddings for testing
#                     class MockEmbedding:
#                         def __init__(self):
#                             self.values = [0.1] * 768  # Standard embedding dimension
#                     return [MockEmbedding()]
            
#             print("⚠️  Using mock embedding model for testing")
#             embedding_model = MockEmbeddingModel()
#     return embedding_model

# def validate_incident_format(incident_data: Dict[str, Any]) -> str:
#     """
#     Validate incident data format and return validation status with error messages.
    
#     Args:
#         incident_data: Dictionary containing incident information
        
#     Returns:
#         String containing validation result - either "VALID" or error messages separated by semicolons
#     """
#     errors = []
#     required_fields = [
#         'incident_id', 'timestamp', 'severity', 'service_impact',
#         'incident_description', 'resolution_steps', 'root_cause'
#     ]
    
#     # Check required fields
#     for field in required_fields:
#         if field not in incident_data or not incident_data[field]:
#             errors.append(f"Missing or empty required field: {field}")
    
#     # Validate specific field formats
#     if 'severity' in incident_data:
#         valid_severities = ['Low', 'Medium', 'High', 'Critical']
#         if incident_data['severity'] not in valid_severities:
#             errors.append(f"Invalid severity level. Must be one of: {valid_severities}")
    
#     if 'timestamp' in incident_data:
#         try:
#             # Try to parse timestamp
#             datetime.fromisoformat(incident_data['timestamp'].replace('Z', '+00:00'))
#         except (ValueError, AttributeError):
#             errors.append("Invalid timestamp format. Use ISO 8601 format (e.g., 2024-01-01T10:00:00Z)")
    
#     if 'incident_id' in incident_data:
#         incident_id = str(incident_data['incident_id'])
#         if not incident_id.startswith('INC-'):
#             errors.append("Incident ID should follow format: INC-XXXX")
    
#     # Return validation result as string
#     if len(errors) == 0:
#         return "VALID"
#     else:
#         return "; ".join(errors)

# def prepare_incident_text(incident_data: Dict[str, Any]) -> str:
#     """
#     Prepare comprehensive searchable text from incident data.
    
#     Args:
#         incident_data: Validated incident dictionary
        
#     Returns:
#         Formatted text string for embedding generation
#     """
#     text_parts = []
    
#     # Add structured information
#     text_parts.append(f"Incident ID: {incident_data['incident_id']}")
#     text_parts.append(f"Severity: {incident_data['severity']}")
#     text_parts.append(f"Service Impact: {incident_data['service_impact']}")
#     text_parts.append(f"Description: {incident_data['incident_description']}")
#     text_parts.append(f"Resolution Steps: {incident_data['resolution_steps']}")
#     text_parts.append(f"Root Cause: {incident_data['root_cause']}")
#     text_parts.append(f"Timestamp: {incident_data['timestamp']}")
    
#     # Combine into searchable text
#     return " | ".join(text_parts)

# def ingest_incident_data(incident_data: Dict[str, Any]) -> str:
#     """
#     Ingest a single incident record into the vector database.
    
#     Args:
#         incident_data: Dictionary containing incident information
        
#     Returns:
#         Status message indicating success or failure
#     """
#     try:
#         print(f"🔍 Starting ingestion for incident: {incident_data.get('incident_id', 'Unknown')}")
        
#         # Step 1: Validate incident format
#         validation_result = validate_incident_format(incident_data)
#         if validation_result != "VALID":
#             return f"❌ Validation failed: {validation_result}"
        
#         print("✅ Validation passed")
        
#         # Step 2: Prepare text for embedding
#         incident_text = prepare_incident_text(incident_data)
#         print(f"📝 Prepared text for embedding (length: {len(incident_text)} chars)")
        
#         # Step 3: Generate embedding
#         try:
#             model = get_embedding_model()
#             embeddings_response = model.get_embeddings([incident_text])
#             embedding = embeddings_response[0].values
#             print(f"🧠 Generated embedding (dimension: {len(embedding)})")
#         except Exception as e:
#             return f"❌ Error generating embedding: {str(e)}"
        
#         # Step 4: Create record for storage
#         record = {
#             'id': str(incident_data['incident_id']),
#             'text': incident_text,
#             'metadata': {
#                 'severity': incident_data['severity'],
#                 'service_impact': incident_data['service_impact'],
#                 'timestamp': incident_data['timestamp'],
#                 'ingestion_time': datetime.now().isoformat()
#             }
#         }
        
#         # For vector database, we need to store embedding separately
#         vector_record = {
#             'id': str(incident_data['incident_id']),
#             'embedding': embedding
#         }
        
#         print("📋 Created records for storage")
        
#         # Step 5: Store in local file for backup/reference
#         try:
#             # Create embeddings file if it doesn't exist
#             if not os.path.exists(EMBEDDINGS_FILE):
#                 print(f"📁 Creating new embeddings file: {EMBEDDINGS_FILE}")
#                 with open(EMBEDDINGS_FILE, 'w') as f:
#                     f.write("")  # Create empty file
            
#             # Append to local embeddings file (include embedding for backup)
#             record_with_embedding = record.copy()
#             record_with_embedding['embedding'] = embedding
            
#             with open(EMBEDDINGS_FILE, 'a') as f:
#                 f.write(json.dumps(record_with_embedding) + '\n')
            
#             print(f"💾 Stored record in local file: {EMBEDDINGS_FILE}")
            
#         except Exception as e:
#             print(f"⚠️  Warning: Failed to write to local file: {str(e)}")
        
#         # Step 6: Upload to vector database via index endpoint
#         try:
#             # Initialize AI Platform if not already done
#             if not hasattr(aiplatform, '_initialized') or not aiplatform._initialized:
#                 aiplatform.init(project=PROJECT_ID, location=LOCATION)
            
#             # Try to add to vector search index
#             index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
#                 INDEX_ENDPOINT_ID,
#                 project=PROJECT_ID,
#                 location=LOCATION,
#             )
            
#             # Note: Direct insertion to vector index requires specific API calls
#             # For now, we'll update the GCS file which feeds the index
#             print("🔄 Updating vector database via GCS...")
            
#         except Exception as e:
#             print(f"⚠️  Warning: Vector database update issue: {str(e)}")
        
#         # Step 7: Upload to GCS bucket (this feeds the vector database)
#         gcs_success = False
#         try:
#             storage_client = storage.Client(project=PROJECT_ID)
#             bucket = storage_client.bucket(BUCKET_NAME)
#             blob = bucket.blob(BLOB_NAME)
            
#             # Get existing content
#             try:
#                 existing_content = blob.download_as_text()
#                 print(f"📥 Downloaded existing GCS content ({len(existing_content)} chars)")
#             except Exception:
#                 existing_content = ""
#                 print("📁 No existing GCS content found, creating new file")
            
#             # Append new record
#             new_record_line = json.dumps(record_with_embedding) + '\n'
#             updated_content = existing_content + new_record_line
            
#             # Upload updated content
#             blob.upload_from_string(updated_content)
#             print(f"☁️  Successfully uploaded to GCS: gs://{BUCKET_NAME}/{BLOB_NAME}")
#             gcs_success = True
            
#         except Exception as e:
#             print(f"⚠️  Warning: Failed to upload to GCS: {str(e)}")
#             print("📝 Data is still stored locally for manual upload later")
        
#         # Determine success message based on what worked
#         if gcs_success:
#             success_message = f"""✅ Successfully ingested incident {incident_data['incident_id']}:
# - ✅ Validation passed
# - ✅ Embedding generated ({len(embedding)} dimensions)
# - ✅ Stored locally in {EMBEDDINGS_FILE}
# - ✅ Uploaded to GCS bucket
# - 📊 Ready for vector search queries"""
#         else:
#             success_message = f"""⚠️  Partially ingested incident {incident_data['incident_id']}:
# - ✅ Validation passed
# - ✅ Embedding generated ({len(embedding)} dimensions)
# - ✅ Stored locally in {EMBEDDINGS_FILE}
# - ⚠️  GCS upload failed (stored locally for manual upload)
# - 📊 Local data ready, GCS sync needed for full vector search"""
        
#         print(success_message)
#         return success_message
        
#     except Exception as e:
#         error_message = f"❌ Error ingesting incident data: {str(e)}"
#         print(error_message)
#         import traceback
#         print(f"📍 Full traceback: {traceback.format_exc()}")
#         return error_message

# def batch_ingest_incidents(incidents_list: List[Dict[str, Any]]) -> str:
#     """
#     Ingest multiple incident records in batch.
    
#     Args:
#         incidents_list: List of incident dictionaries
        
#     Returns:
#         Summary of batch ingestion results as formatted string
#     """
#     results = {
#         'total': len(incidents_list),
#         'successful': 0,
#         'failed': 0,
#         'errors': []
#     }
    
#     processed_records = []
    
#     for i, incident in enumerate(incidents_list):
#         try:
#             # Validate incident
#             validation_result = validate_incident_format(incident)
#             if validation_result != "VALID":
#                 results['failed'] += 1
#                 results['errors'].append(f"Record {i+1}: {validation_result}")
#                 continue
            
#             # Prepare and process incident
#             incident_text = prepare_incident_text(incident)
#             model = get_embedding_model()
#             embedding = model.get_embeddings([incident_text])[0].values
            
#             record = {
#                 'id': incident['incident_id'],
#                 'text': incident_text,
#                 'embedding': embedding,
#                 'metadata': {
#                     'severity': incident['severity'],
#                     'service_impact': incident['service_impact'],
#                     'timestamp': incident['timestamp'],
#                     'ingestion_time': datetime.now().isoformat()
#                 }
#             }
            
#             processed_records.append(record)
#             results['successful'] += 1
            
#         except Exception as e:
#             results['failed'] += 1
#             results['errors'].append(f"Record {i+1}: Processing error - {str(e)}")
    
#     # Batch write to file
#     if processed_records:
#         try:
#             with open(EMBEDDINGS_FILE, 'a') as f:
#                 for record in processed_records:
#                     f.write(json.dumps(record) + '\n')
            
#             # Upload to GCS
#             try:
#                 storage_client = storage.Client(project=PROJECT_ID)
#                 bucket = storage_client.bucket(BUCKET_NAME)
#                 blob = bucket.blob(BLOB_NAME)
                
#                 # Append all new records
#                 new_content = '\n'.join([json.dumps(record) for record in processed_records]) + '\n'
#                 try:
#                     existing_content = blob.download_as_text()
#                     updated_content = existing_content + new_content
#                 except:
#                     updated_content = new_content
                
#                 blob.upload_from_string(updated_content)
                
#             except Exception as e:
#                 print(f"Warning: Failed to upload batch to GCS: {e}")
                
#         except Exception as e:
#             results['errors'].append(f"File write error: {str(e)}")
    
#     # Generate summary
#     summary = f"""
#     Batch Ingestion Summary:
#     - Total records processed: {results['total']}
#     - Successfully ingested: {results['successful']}
#     - Failed: {results['failed']}
#     """
    
#     if results['errors']:
#         summary += f"\nErrors encountered:\n" + "\n".join(results['errors'][:10])  # Limit to first 10 errors
#         if len(results['errors']) > 10:
#             summary += f"\n... and {len(results['errors']) - 10} more errors"
    
#     return summary

# def test_ingestion_setup() -> str:
#     """
#     Test the ingestion setup and configuration.
    
#     Returns:
#         Status of ingestion environment setup
#     """
#     try:
#         setup_status = []
        
#         # Test 1: Environment variables
#         setup_status.append("🔧 ENVIRONMENT SETUP:")
#         setup_status.append(f"  - PROJECT_ID: {PROJECT_ID}")
#         setup_status.append(f"  - LOCATION: {LOCATION}")
#         setup_status.append(f"  - INDEX_ENDPOINT_ID: {INDEX_ENDPOINT_ID}")
#         setup_status.append(f"  - DEPLOYED_INDEX_ID: {DEPLOYED_INDEX_ID}")
#         setup_status.append(f"  - EMBEDDINGS_FILE: {EMBEDDINGS_FILE}")
#         setup_status.append(f"  - BUCKET_NAME: {BUCKET_NAME}")
#         setup_status.append(f"  - BLOB_NAME: {BLOB_NAME}")
        
#         # Test 2: AI Platform initialization
#         setup_status.append("\n🤖 AI PLATFORM:")
#         try:
#             aiplatform.init(project=PROJECT_ID, location=LOCATION)
#             setup_status.append("  ✅ AI Platform initialized successfully")
#         except Exception as e:
#             setup_status.append(f"  ❌ AI Platform initialization failed: {str(e)}")
        
#         # Test 3: Embedding model
#         setup_status.append("\n🧠 EMBEDDING MODEL:")
#         try:
#             model = get_embedding_model()
#             test_embedding = model.get_embeddings(["test text"])[0].values
#             setup_status.append(f"  ✅ Embedding model working (dimension: {len(test_embedding)})")
#         except Exception as e:
#             setup_status.append(f"  ❌ Embedding model failed: {str(e)}")
        
#         # Test 4: Local file access
#         setup_status.append("\n📁 LOCAL FILE ACCESS:")
#         try:
#             # Test write access
#             test_file = f"{EMBEDDINGS_FILE}.test"
#             with open(test_file, 'w') as f:
#                 f.write("test")
#             os.remove(test_file)
#             setup_status.append("  ✅ Local file write access working")
#         except Exception as e:
#             setup_status.append(f"  ❌ Local file access failed: {str(e)}")
        
#         # Test 5: GCS access
#         setup_status.append("\n☁️  GCS ACCESS:")
#         try:
#             storage_client = storage.Client(project=PROJECT_ID)
#             bucket = storage_client.bucket(BUCKET_NAME)
#             # Just check if bucket exists
#             bucket.reload()
#             setup_status.append(f"  ✅ GCS bucket '{BUCKET_NAME}' accessible")
#         except Exception as e:
#             setup_status.append(f"  ❌ GCS access failed: {str(e)}")
        
#         # Test 6: Vector search endpoint
#         setup_status.append("\n🔍 VECTOR SEARCH:")
#         try:
#             index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
#                 INDEX_ENDPOINT_ID,
#                 project=PROJECT_ID,
#                 location=LOCATION,
#             )
#             setup_status.append("  ✅ Vector search endpoint accessible")
#         except Exception as e:
#             setup_status.append(f"  ❌ Vector search endpoint failed: {str(e)}")
        
#         return "\n".join(setup_status)
        
#     except Exception as e:
#         return f"❌ Setup test failed: {str(e)}"
