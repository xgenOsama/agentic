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

# Function to ingest new data
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
    print(df['id'])
    print(last_id)
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

 
 
df_insert_data_test = pd.read_excel("data.xlsx")
ingest_new_data_to_index(df_insert_data_test.head(10))