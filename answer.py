from chromadb import PersistentClient
from ingest import (
    DB_NAME,
    COLLECTION_NAME,
    MODEL,
    MODEL_EMBED,
    RERANK_TOP_K,
    RETRIEVAL_N,
    Result)

from data import KNOWLEDGE_FILE_PATH
from langchain_ollama import ChatOllama, OllamaEmbeddings

llm = ChatOllama(model="llama3.2:latest")

SYSTEM_PROMPT = """
You are an inventory bot of a E Commerce Company
you have entry related to all the products Sold by the company.
You are needed to answer the user queries about the products they wish to buy in our company.

You are chatting with potential customers of the company. You are needed to provide relevant info about their product they wish to purchase You are needed to suggest the product related to it also.

If you don't know the answer, say so.

For context here are the specific extracts from the knowledge bases that might be directly relevant to the user's question {context}

with this context please answer the user's questions be accurate relevant and complete

Your answers will be evaluated for accuracy relevance and completeness so make sure it only answers the question and fully answers it

the conversation you make with user should be more engaging, make the product  more interesting to the user.
"""

def make_rag_messages(question, history, chunks):
    context = "\n\n".join(
        f"Extract from {chunk.metadata["source"]}:\n{chunk.page_content}" for   chunk in chunks
    )
    system_prompt = SYSTEM_PROMPT.format(context=context)

    return (
        [{"role":"system", "content":system_prompt}]
        + history
        + [{"role":"user", "content":question}]
    )


def fetch_context(question):
    embeddings = OllamaEmbeddings(model=MODEL_EMBED)
    query_vector = embeddings.embed_query(question)

    chroma = PersistentClient(path=DB_NAME)
    collection = chroma.get_or_create_collection(COLLECTION_NAME)

    results = collection.query(query_embeddings=[query_vector], n_results=RETRIEVAL_N)

    chunks = [
        Result(page_content=doc, metadata=meta)
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]

    return chunks

def answer_question(question:str, history: list[dict]= []) -> tuple[str,list]:
    """
    Answer the question using rag and return the answer and retrieved context
    """
    
    chunks = fetch_context(question)
    messages = make_rag_messages(question, history, chunks)
    response = llm.invoke(messages)
    return response.content, chunks

