"""
Elasticsearch BM25 RAG module.
Mirrors ingest.py (chunking + indexing) and answer.py (retrieval + generation)
but uses Elasticsearch BM25 instead of ChromaDB vector search.

Run directly to ingest:
    python es_rag.py
"""

import os
import time
from tqdm import tqdm
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_elasticsearch import ElasticsearchStore, BM25RetrievalStrategy
from experiments import get_response
from documentloader import documents

load_dotenv()


MODEL       = "llama3.2:latest"
ES_URL      = os.getenv("ES_URL", "http://localhost:9200")
ES_USER     = os.getenv("ES_USER", "elastic")
ES_PASSWORD = os.getenv("ES_PASSWORD", "")
INDEX_NAME  = "products_bm25"
RETRIEVAL_N = 10
RERANK_TOP_K = 4
AVG_CHUNK_SIZE = 40

llm = ChatOllama(model=MODEL)


class Result(BaseModel):
    page_content: str
    metadata: dict

class Chunk(BaseModel):
    title: str = Field(description="A brief title for this chunk, 3-4 words most likely surfaced in a query")
    summary: str = Field(description="A few sentences summarising the chunk to answer questions about the product")
    original_text: str = Field(description="The original text of this chunk, exactly as-is")

    def as_result(self, document):
        meta = {
            "source": document.metadata.get("id", ""),
            "type":   document.metadata.get("category", ""),
        }
        return Result(
            page_content=f"{self.title}\n\n{self.summary}\n\n{self.original_text}",
            metadata=meta,
        )

class Chunks(BaseModel):
    chunks: list[Chunk]

class RankOrder(BaseModel):
    order: list[int] = Field(
        description="Chunk ids ordered from most to least relevant to the question"
    )


def _chunk_prompt(document):
    n = len(document.page_content) // AVG_CHUNK_SIZE + 1
    return (
        f"You are a product data specialist preparing documents for a search engine.\n\n"
        f"Break the following product document into exactly {n} semantic chunks. "
        "Each chunk should focus on a distinct aspect (overview, pricing, specs, vendor, use cases).\n\n"
        "Rules:\n"
        "- title: 3-4 word phrase a user would likely search for\n"
        "- summary: 1-2 sentences answering 'what would someone learn from this chunk?'\n"
        "- original_text: exact copy of the relevant portion, unmodified\n\n"
        f"Product document:\n{document.page_content}"
    )

def _process_document(document):
    messages = [{"role": "user", "content": _chunk_prompt(document)}]
    return get_response(messages)

def create_chunks(docs):
    chunks = []
    for doc in tqdm(docs):
        try:
            result = _process_document(doc)
            for chunk in result.chunks:
                chunks.append(chunk.as_result(doc))
        except Exception:
            print("skipped document")
    return chunks

def _build_store():
    kwargs = dict(
        index_name=INDEX_NAME,
        es_url=ES_URL,
        strategy=BM25RetrievalStrategy(),
    )
    if ES_PASSWORD:
        kwargs["es_user"] = ES_USER
        kwargs["es_password"] = ES_PASSWORD
    return ElasticsearchStore(**kwargs)

def index_documents(chunks):
    store = _build_store()
    texts     = [c.page_content for c in chunks]
    metadatas = [c.metadata      for c in chunks]
    store.add_texts(texts, metadatas=metadatas)
    print(f"Indexed {len(chunks)} chunks into Elasticsearch index '{INDEX_NAME}'")


SYSTEM_PROMPT = """
You are an inventory bot of an E-Commerce Company.
You have entries for all products sold by the company.
Answer user queries about products they wish to buy and suggest related products.

If you don't know the answer, say so.

Context from knowledge base:
{context}

Be accurate, relevant, complete, and engaging.
"""

def _rerank(question, chunks):
    sys_p = (
        "You are a systematic document reranker. "
        "Given a question and numbered chunks, return them ordered by relevance, "
        "most relevant first. Include all chunk ids."
    )
    user_p = f"Question:\n{question}\n\nChunks:\n\n"
    for i, chunk in enumerate(chunks):
        user_p += f"Chunk Id {i + 1}:\n{chunk.page_content}\n\n"
    user_p += "Reply only with the ranked chunk id list."

    reply = llm.with_structured_output(RankOrder).invoke([
        {"role": "system", "content": sys_p},
        {"role": "user",   "content": user_p},
    ])
    return [chunks[i - 1] for i in reply.order]

def fetch_context(question):
    store = _build_store()
    retriever = store.as_retriever(search_kwargs={"k": RETRIEVAL_N})
    docs = retriever.invoke(question)
    return [Result(page_content=d.page_content, metadata=d.metadata) for d in docs]

def fetch_reranked_context(question):
    chunks = fetch_context(question)
    return _rerank(question, chunks)

def _make_messages(question, history, chunks):
    context = "\n\n".join(
        f"Extract from {c.metadata['source']}:\n{c.page_content}" for c in chunks
    )
    return (
        [{"role": "system", "content": SYSTEM_PROMPT.format(context=context)}]
        + history
        + [{"role": "user", "content": question}]
    )

def answer_question(question: str, history: list[dict] = []) -> tuple[str, list]:
    """Return (answer_text, retrieved_chunks) using BM25 retrieval."""
    chunks   = fetch_reranked_context(question)
    messages = _make_messages(question, history, chunks)
    response = llm.invoke(messages)
    return response.content, chunks

if __name__ == "__main__":
    print("Creating chunks…")
    chunks = create_chunks(documents)
    print(f"Created {len(chunks)} chunks.")
    index_documents(chunks)
    print("Done.")
