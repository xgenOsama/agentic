import pandas as pd
from google.cloud import storage
from langchain.schema import Document
import io

from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
import pandas as pd
from langchain.docstore.document import Document

# Constants
PROJECT_ID = 'vodaf-aida25lcpm-206'
LOCATION = 'europe-west1'
INDEX_ENDPOINT_ID = 'projects/100938974863/locations/europe-west1/indexEndpoints/7257260528437821440'
DEPLOYED_INDEX_ID = 'Test_INDEX_ENDPOINT_20250910101151'
EMBEDDINGS_FILE = 'embeddings_text.json'
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

# Function to read file from GCS and ingest into index
def ingest_new_data_to_index_from_gcs(gcs_url: str):
    """
    Reads a file from GCS, ingests new text data into the Matching Engine index.

    Args:
        gcs_url (str): GCS URL to the file (e.g., 'gs://your-bucket-name/path/to/file.json')
    """

    # Parse GCS URL
    if not gcs_url.startswith("gs://"):
        raise ValueError("Invalid GCS URL format. Must start with 'gs://'")

    bucket_name, blob_path = gcs_url[5:].split("/", 1)

    # Initialize GCS client and download file
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    # Download file content  
    file_bytes = blob.download_as_bytes()
    # Read Excel file into DataFrame
    new_data = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')    
    print(new_data)

    # Load existing embeddings
    df = pd.read_json(EMBEDDINGS_FILE, orient='records', lines=True)

    # Prepare documents
    documents = [
        Document(page_content=row.to_string(), metadata={"row_index": i})
        for i, row in new_data.iterrows()
    ]

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
    items = [
        {
            "datapoint_id": str(row['id']),
            "feature_vector": row['embedding'],
        }
        for _, row in additional_df.iterrows()
    ]

    # Upsert to index
    print(index.upsert_datapoints(datapoints=items))

    # Update embeddings file
    updated_df = pd.concat([df, additional_df], ignore_index=True).drop_duplicates(subset='id')
    updated_df.to_json(EMBEDDINGS_FILE, orient='records', lines=True)
