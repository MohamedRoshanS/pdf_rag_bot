from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.retrieval import retrieve, answer_with_context
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    doc_id: str | None = None  # Optional override of active doc

@router.post("/query")
async def query_docs(req: QueryRequest):
    try:
        logger.info(f"Received query: '{req.query}' for doc_id: {req.doc_id}")
        sources = retrieve(req.query, target_doc_id=req.doc_id)
        answer, used_sources = answer_with_context(req.query, sources)
        logger.info(f"Query answered; sources used: {len(used_sources)}")
        return {"answer": answer, "sources": used_sources}
    except Exception as e:
        logger.error("Query failed", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
