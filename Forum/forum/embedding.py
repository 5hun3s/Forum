#投稿メッセージのembeddingを行い、データベースに保存するプログラム
import openai
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from chromadb.config import Settings
import os

#os.environ["OPENAI_API_KEY"] = "[YOUR_API_KEY_HERE]"
openai.api_key = os.getenv("OPENAI_API_KEY")

EMBEDDING_MODEL = "text-embedding-ada-002"  # OpenAI's best embeddings as of Apr 2023
BATCH_SIZE = 1000  # you can submit up to 2048 embedding inputs per request

def MyEmbedding(message):
    
    return 


def create_embeddings(items):
    embeddings = []
    for batch_start in range(0, len(items), BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        batch = items[batch_start:batch_end]
        print(f"Batch {batch_start} to {batch_end-1}")
        response = openai.Embedding.create(model=EMBEDDING_MODEL, input=batch)
        for i, be in enumerate(response["data"]):
            assert i == be["index"]  # double check embeddings are in same order as input
        batch_embeddings = [e["embedding"] for e in response["data"]]
        embeddings.extend(batch_embeddings)

    df = pd.DataFrame({"text": items, "embedding": embeddings})
    return df

items = df["content"].to_list()
df_embedding = create_embeddings(items)

#embeddingを保存
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from chromadb.config import Settings

def create_chroma_client():
  persist_directory = 'chroma_persistence'
  chroma_client = chromadb.Client(
      Settings(
          persist_directory=persist_directory,
          chroma_db_impl="duckdb+parquet",
      )
  )
  return chroma_client

def create_chroma_collection(chroma_client):
  embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name=EMBEDDING_MODEL)
  collection = chroma_client.create_collection(name='stevie_collection', embedding_function=embedding_function)
  return collection

chroma_client = create_chroma_client()
stevie_collection = create_chroma_collection(chroma_client)
stevie_collection.add(
     ids = df_embedding.index.astype(str).tolist(),
     documents = df_embedding['text'].tolist(),
     embeddings = df_embedding['embedding'].tolist(),
)
chroma_client.persist() 