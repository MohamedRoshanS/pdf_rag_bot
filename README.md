# AI-Powered PDF Context Retrieval Chatbot (RAG)

## Overview
This backend system allows uploading PDFs, indexing their content for semantic search, and answering user queries using a Retrieval-Augmented Generation (RAG) pipeline via FastAPI.  
It uses **ChromaDB** for embeddings storage and integrates with a **Large Language Model (LLM)** (e.g., Gemini) for context-aware responses.

## Features
- **PDF Upload & Text Extraction**  
  - Accept PDF uploads  
  - Extract text and build page-based chunks  
- **Embedding Generation**  
  - Compute embeddings for each chunk using a sentence-transformers model  
  - Store embeddings persistently in ChromaDB  
  - Track the active document for queries  
- **RAG Pipeline**  
  - Retrieve the most relevant chunks for a query  
  - Generate answers using only the retrieved context  
  - Return supporting sources with page numbers  
- **FastAPI Backend**  
  - REST API with `/api/upload` and `/api/query` endpoints  
  - Input validation and error handling with Pydantic  
  - Modular, production-ready code structure  
- **API Interface**  
  - The main interface to operate the API is the **Swagger UI**:  
    [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Tech Stack
- **Backend**: FastAPI  
- **Vector DB**: ChromaDB  
- **LLM**: Gemini (via `google-generativeai`) or configurable provider  
- **PDF Processing**: PyMuPDF (`fitz`)  
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`  
- **Environment**: Python 3.8+, `.env` configuration  

## Setup & Installation

1. **Clone Repository**:

```bash
git clone https://github.com/MohamedRoshanS/pdf_rag_bot.git
cd pdf_rag_bot
```

2. **Create Virtual Environment**:

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scriptsctivate
```

3. **Install Dependencies**:

```bash
pip install -r requirements.txt
```

4. **Set Environment Variables**:  
Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

**Key variables:**

```ini
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
PERSIST_DIR=./persistence
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=900
CHUNK_OVERLAP=150
TOP_K=5
MAX_TOKENS_ANSWER=1024
```

5. **Run FastAPI Server**:

```bash
uvicorn app.main:app --reload
```

Server runs at [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Quick Test via Swagger UI

Open the Swagger UI in your browser:  
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Upload a PDF:
- Select the `/api/upload` POST endpoint  
- Click "Try it out"  
- Choose a PDF file and execute  
- Response includes `doc_id` and number of chunks

### Query the PDF:
- Select the `/api/query` POST endpoint  
- Enter your query text  
- (Optional) Use `doc_id` to specify a document  
- Execute to get the answer and source references

### View Response:
- Answer is returned as plain text  
- Sources include chunk text and page numbers

## API Endpoints

### Upload PDF

- **Endpoint:** POST `/api/upload`
- **Request:** Multipart/form-data with `file` (PDF)
- **Response:**

```json
{
  "status": "success",
  "doc_id": "<generated_doc_id>",
  "filename": "<uploaded_filename>",
  "chunks": <number_of_chunks>
}
```

### Query PDF Content

- **Endpoint:** POST `/api/query`
- **Request:**

```json
{
  "query": "What is the main topic of the document?",
  "doc_id": "<optional_doc_id_to_override_active_doc>"
}
```

- **Response:**

```json
{
  "answer": "The main topic of the document is AI-powered PDF retrieval systems.",
  "sources": [
    {
      "doc_id": "<doc_id>",
      "page": 2,
      "chunk_id": "<chunk_id>",
      "score": 0.95,
      "text": "Relevant text snippet..."
    },
    {
      "doc_id": "<doc_id>",
      "page": 5,
      "chunk_id": "<chunk_id>",
      "score": 0.93,
      "text": "Another snippet..."
    }
  ]
}
```

## Directory Structure

```
app/
├─ api/
│  ├─ documents.py         # Upload endpoint
│  └─ query.py             # Query endpoint
├─ core/
│  ├─ config.py            # Settings from .env
│  └─ logging.py           # Logging setup
├─ db/
│  └─ vectorstore.py       # ChromaDB wrapper
├─ services/
│  ├─ pdf.py               # PDF extraction
│  ├─ chunking.py          # Text chunking
│  ├─ embedding.py         # Embedding generation
│  ├─ retrieval.py         # RAG retrieval & answering
│  └─ llm_providers.py     # LLM integration logic
├─ schemas/
│  └─ models.py            # Pydantic schemas
├─ utils/
│  └─ ids.py 
main.py                    # FastAPI app entrypoint
.env                       # Environment variables
requirements.txt           # Python dependencies
```

## Evaluation Criteria

- **Accuracy & Relevance:** Retrieved context matches user query  
- **Efficiency:** Fast ingestion and semantic search  
- **API Quality:** Clean, modular endpoints with validation and error handling  
- **Code Quality:** Clear structure, maintainability, and documentation  

---
