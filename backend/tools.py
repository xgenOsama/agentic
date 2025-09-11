from google.cloud import aiplatform
from google.cloud import storage
from vertexai.language_models import TextEmbeddingModel
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Set environment variable for quota project
os.environ['GOOGLE_CLOUD_QUOTA_PROJECT_ID'] = os.getenv("GOOGLE_CLOUD_PROJECT", "vodaf-aida25lcpm-206")

# Constants
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT","vodaf-aida25lcpm-206")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION","europe-west1")
INDEX_ENDPOINT_ID = os.getenv("INDEX_ENDPOINT_ID","projects/100938974863/locations/europe-west1/indexEndpoints/5059503910281019392")
DEPLOYED_INDEX_ID = os.getenv("DEPLOYED_INDEX_ID","VECTOR_SEARCH_ENDPOINT_20250909155315")
EMBEDDINGS_FILE = os.getenv("EMBEDDINGS_FILE","embeddings_text.json")
BUCKET_NAME = "vodaf-aida25lcpm-206-rag"
BLOB_NAME = "csv_data/embeddings_text.json"

def download_embeddings_if_not_exists():
    """Download embeddings file from GCP bucket if it doesn't exist locally."""
    if not os.path.exists(EMBEDDINGS_FILE):
        print(f"Embeddings file {EMBEDDINGS_FILE} not found. Downloading from GCP bucket...")
        try:
            # Initialize storage client
            storage_client = storage.Client(project=PROJECT_ID)
            bucket = storage_client.bucket(BUCKET_NAME)
            blob = bucket.blob(BLOB_NAME)
            
            # Download the file
            blob.download_to_filename(EMBEDDINGS_FILE)
            print(f"Successfully downloaded {EMBEDDINGS_FILE} from gs://{BUCKET_NAME}/{BLOB_NAME}")
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

# Load embedding model lazily to avoid authentication issues at import time
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

        # Step 3: Extract context
        context = ""
        for res in response:
            for neighbor in res:
                match = df[df['id'] == int(neighbor.id)]
                if not match.empty:
                    context += match['text'].values[0] + "\n\n\n"

        return context
    except Exception as e:
        print(f"Error in retrieve_context_from_query: {e}")
        return f"Error retrieving context: {str(e)}"
