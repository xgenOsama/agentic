from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
import pandas as pd

# Constants
PROJECT_ID = 'vodaf-aida25lcpm-206'
LOCATION = 'europe-west1'
INDEX_ENDPOINT_ID = 'projects/100938974863/locations/europe-west1/indexEndpoints/8033005564252389376'
DEPLOYED_INDEX_ID = 'VECTOR_SEARCH_ENDPOINT_20250909155315'
EMBEDDINGS_FILE = 'embeddings_text.json'

# Initialize AI Platform
aiplatform.init(project=PROJECT_ID, location=LOCATION)

# Load index endpoint
index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
    INDEX_ENDPOINT_ID,
    project=PROJECT_ID,
    location=LOCATION,
)

# Load embeddings text data
df = pd.read_json(EMBEDDINGS_FILE, orient='records', lines=True)

# Load embedding model
embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")

def retrieve_context_from_query(query: str, num_neighbors: int = 10) -> str:
    """
    Given a query string, returns the context text from the nearest neighbors in the index.
    """
    # Step 1: Create embedding
    embedding = embedding_model.get_embeddings([query])[0].values

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
            print(match)
            if not match.empty:
                context += match['text'].values[0] + "\n\n\n"

    return context

retrieve_context_from_query("DNS Resolution Failure")