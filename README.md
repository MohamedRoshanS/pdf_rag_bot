# Project B — AI-Powered PDF Context Retrieval Chatbot (RAG)

## Overview
Backend that ingests any PDF, indexes it for semantic search, and answers queries via a Retrieval-Augmented Generation (RAG) pipeline.

## Features
- Upload a PDF → extract text → split into chunks.
- Generate embeddings per chunk → store in vector DB (Chroma).
- Query endpoint → retrieve most relevant chunks → pass to LLM (OpenAI, Gemini, or Ollama).
- Context-aware answers with source references.
- FastAPI backend with input validation & error handling.

## Tech Stack
- **FastAPI** for REST API
- **Chroma** as vector database (persistent)
- **LLM Integration** via provider API (OpenAI, Gemini, or Ollama)

## Endpoints
- `POST /api/ingest/upload` → Upload a PDF for indexing
- `POST /api/query` → Ask a question with context retrieval

## Run Locally
```bash
git clone <repo-url>
cd project-b-rag

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

uvicorn app.main:app --reload
