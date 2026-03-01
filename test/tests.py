from chromadb import PersistentClient
from langchain_ollama import ChatOllama,

DB_NAME = R"C:\Users\Gopinath\Desktop\RAG-powerd-e-commerce-product-assistant\vector_db"
chroma = PersistentClient(path=DB_NAME)

collections = chroma.list_collections()

print(collections)