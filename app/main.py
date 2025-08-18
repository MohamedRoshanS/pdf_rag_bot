from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import setup_logging
from app.api.documents import router as documents_router
from app.api.query import router as query_router

setup_logging()
app = FastAPI(title="Project B — RAG PDF Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router, prefix="/api", tags=["documents"])
app.include_router(query_router, prefix="/api", tags=["query"])

@app.get("/")
def root():
    return {"message": "RAG PDF API is running"}