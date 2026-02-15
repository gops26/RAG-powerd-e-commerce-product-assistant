# Product RAG

a chatbot that actually knows what products you have. ask it stuff in plain english, it finds the right products and gives you a solid answer.

built with RAG (retrieval augmented generation) — basically it searches your product database semantically and feeds the results to an LLM so it doesn't hallucinate.

## how it works

1. **ingest** — product data (JSONL files) gets chunked using an LLM, embedded with snowflake arctic embed, and stored in chromadb
2. **retrieve** — user asks a question, we do vector similarity search and pull the top 10 relevant chunks
3. **rerank** — LLM reranks those chunks so the best ones float to the top
4. **answer** — everything gets fed to the LLM with a system prompt, it generates a proper answer with product recommendations

## tech stack

**backend**: python, fastapi, langchain, chromadb, ollama, groq api

**frontend**: react, vite, react-markdown

**models**: llama 3.1 8b (groq), snowflake-arctic-embed:335m (ollama)

## setup

### prerequisites

- python 3.x
- node.js + npm
- [ollama](https://ollama.ai) running locally
- groq api key

### pull the models

```bash
ollama pull llama3.2
ollama pull snowflake-arctic-embed:335m
```

### backend

```bash
pip install -r requirements.txt
```

create a `.env` file:

```
GROQ=your_groq_api_key
```

ingest the product data:

```bash
python ingest.py
```

start the api:

```bash
uvicorn api:app --reload
```

runs on `http://localhost:8000`

### frontend

```bash
cd frontend
npm install
npm run dev
```

runs on `http://localhost:5173`

### or just use gradio

if you don't wanna deal with the react frontend:

```bash
python app.py
```

## project structure

```
productrag/
├── api.py              # fastapi endpoint
├── app.py              # gradio ui (alternative)
├── answer.py           # rag pipeline - retrieval, reranking, generation
├── ingest.py           # chunking + embedding + storing
├── documentloader.py   # converts products to langchain docs
├── data.py             # loads jsonl files
├── experiments.py      # messing around with openrouter/claude
├── knowledge-base/     # product data (jsonl files)
├── vector_db/          # chromadb storage
└── frontend/           # react app
    └── src/
        ├── App.jsx
        ├── api/chat.js
        └── components/
            ├── ChatPanel.jsx
            ├── ChatMessage.jsx
            ├── ContextPanel.jsx
            ├── ContextCard.jsx
            └── LoadingIndicator.jsx
```

## api

**POST** `/api/chat`

```json
{
  "question": "show me some laptops under 2000",
  "history": []
}
```

returns the answer + retrieved context chunks.
