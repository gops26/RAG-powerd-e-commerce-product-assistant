from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_ollama import OllamaEmbeddings,ChatOllama
from chromadb import PersistentClient
from tqdm import tqdm
from experiments import get_response
from pydantic import BaseModel,Field


MODEL = "llama-3.1-8b-instant"
MODEL_EMBED = "snowflake-arctic-embed:335m"
DB_NAME = "vector_db"
COLLECTION_NAME = "docs"
RETRIEVAL_N = 10
RERANK_TOP_K = 4
AVG_CHUNK_SIZE = 40


llm = ChatOllama(model="llama3.2:latest")

class Result(BaseModel):
    page_content: str
    metadata: dict
    
class Chunk(BaseModel):
    title:str = Field(description="A brief title for this chunk of product, typically 3,4 words that is most likely surfaced in a query")
    summary:str = Field(description="A few sentence summarizing the chunk about the product to answer questions")
    original_text :str = Field(description="The original text of this chunk from the provided document, exactly as is, not changed in any way")

    def as_result(self, document):
        metadata = {"source": document.metadata.get("id", ""), "type": document.metadata.get("category", "")}
        return Result(page_content=self.title + "\n\n" + self.summary +  "\n\n" + self.original_text,metadata=metadata)

class Chunks(BaseModel):
    chunks : list[Chunk]

from documentloader import documents


def load_prompt(document):
    n_chunks = len(document.page_content) // AVG_CHUNK_SIZE + 1
    return f"""You are a product data specialist preparing documents for a search engine.

Break the following product document into exactly {n_chunks} semantic chunks. Each chunk should focus on a distinct aspect of the product (e.g., overview, pricing, technical specs, vendor info, use cases).

Rules:
- title: A short 3-4 word phrase a user would likely search for (e.g., "4K Wireless Display", "Cyber Insurance Pricing")
- summary: 1-2 sentences answering the question "what would someone learn from this chunk?"
- original_text: Copy the relevant portion of the document text exactly as-is, do not modify it

Product document:
{document.page_content}"""


def create_messages(document):
    return [
        {"role": "user", "content":load_prompt(document)}
    ]

import time


def process_document(document):
    messages = create_messages(document)
    response = llm.with_structured_output(Chunks).invoke(messages)
    time.sleep(4)
    return response

def process2_document(document):
    messages = create_messages(document)
    response = get_response(messages)
    return response

def create_chunks(documents):

    chunks = []
    for doc in tqdm(documents):
        try:
            result = process2_document(doc)
            for chunk in result.chunks:
                chunks.append(chunk.as_result(doc))
        except Exception:
            print("skipped document")
            continue
    return chunks


def create_embeddings(chunks):
    chroma = PersistentClient(path=DB_NAME)

    if COLLECTION_NAME in [c.name for c in chroma.list_collections()]:
        chroma.delete_collection(COLLECTION_NAME)

    texts = [chunk.page_content for chunk in chunks]
    vectors = OllamaEmbeddings(model=MODEL_EMBED).embed_documents(texts)

    collection = chroma.get_or_create_collection(COLLECTION_NAME)

    ids = [str(i) for i in range(len(chunks))]
    metas = [chunk.metadata for chunk in chunks]

    collection.add(ids=ids, embeddings=vectors, documents=texts, metadatas=metas)
    print(f"Vectorstore created with {collection.count()} documents")



if __name__ == "__main__":
    chunks = create_chunks(documents=documents)
    print('created 100 chunks ....')
    
    create_embeddings(chunks)
    print('created embeddings ....')
