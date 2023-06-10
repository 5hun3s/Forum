import openai
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from chromadb.config import Settings
import os

#embeddingを行う
#os.environ["OPENAI_API_KEY"] = "[YOUR_API_KEY_HERE]"
openai.api_key = os.getenv("OPENAI_API_KEY")

EMBEDDING_MODEL = "text-embedding-ada-002"  # OpenAI's best embeddings as of Apr 2023
BATCH_SIZE = 1000  # you can submit up to 2048 embedding inputs per request

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

#chromaに質問を問い合わせる
def query_collection(
    query: str,
    collection: chromadb.api.models.Collection.Collection, 
    max_results: int = 100)-> tuple[list[str], list[float]]:
    results = collection.query(query_texts=query, n_results=max_results, include=['documents', 'distances'])
    strings = results['documents'][0]
    relatednesses = [1 - x for x in results['distances'][0]]
    return strings, relatednesses

strings, relatednesses = query_collection(
    collection=stevie_collection,
    query="スティービーは日本武道館で何回公演している？",
    max_results=3,
)

for string, relatedness in zip(strings, relatednesses):
    print(f"{relatedness=:.3f}")
    display(string)

#Q＆Aに答える実装
def query_message(
    query: str,
    collection: chromadb.api.models.Collection.Collection,
    model: str,
    token_budget: int
) -> str:
    strings, relatednesses = query_collection(query, collection, max_results=3)
    introduction = '以下の記事を使って質問に答えてください。もし答えが見つからない場合、「データベースには答えがありませんでした。」 と返答してください。\n\n# 記事'
    question = f"\n\n# 質問\n {query}"
    message = introduction
    for string in strings:
        next_article = f'\n{string}\n"""'
        if (
            num_tokens(message + next_article + question, model=model)
            > token_budget
        ):
            break
        else:
            message += next_article
    return message + question

def ask(
    query: str,
    collection = stevie_collection,
    model: str = GPT_MODEL,
    token_budget: int = 4096 - 500,
    print_message: bool = False,
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    message = query_message(query, collection, model=model, token_budget=token_budget)
    if print_message:
        print(message)
    messages = [
        {"role": "system", "content": "スティービー・ワンダーに関する質問に答えます。"},
        {"role": "user", "content": message},
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0
    )
    response_message = response["choices"][0]["message"]["content"]
    return response_message

#Q&A実行
ask("スティービーの武道館公演の回数を教えてください。")