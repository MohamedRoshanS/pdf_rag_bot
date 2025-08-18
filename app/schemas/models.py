# app/schemas/models.py
from typing import List
from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    doc_id: str

class SourceItem(BaseModel):
    doc_id: str
    page: int
    chunk_id: str
    score: float
    text: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
