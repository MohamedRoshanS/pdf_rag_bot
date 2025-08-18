import os
import uuid
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings

from app.services.embedding import LocalEmbedder
from app.core.config import settings


_ACTIVE_FILE = os.path.join(getattr(settings, "persist_dir", "./persistence"), "active_doc_id.txt")


def _read_active_doc_id() -> Optional[str]:
    try:
        if os.path.exists(_ACTIVE_FILE):
            with open(_ACTIVE_FILE, "r", encoding="utf-8") as f:
                v = f.read().strip()
                return v or None
        return None
    except Exception:
        return None


def _write_active_doc_id(doc_id: str) -> None:
    os.makedirs(os.path.dirname(_ACTIVE_FILE), exist_ok=True)
    with open(_ACTIVE_FILE, "w", encoding="utf-8") as f:
        f.write(doc_id)


class VectorStore:
    """
    ChromaDB wrapper.
    - Uses persistent storage at settings.persist_dir
    - Stores embeddings explicitly (no embedding function bound to collection)
    - Persists 'active_doc_id' to a file so it's stable across requests
    """

    def __init__(self):
        persist_path = getattr(settings, "persist_dir", "./persistence")
        os.makedirs(persist_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_path, settings=Settings(allow_reset=False))
        self.collection = self.client.get_or_create_collection(name="documents")
        self._embedder = LocalEmbedder(model_name=settings.embedding_model)

    # ---------- Active doc helpers ----------
    def set_active_doc(self, doc_id: str):
        _write_active_doc_id(doc_id)

    def get_active_doc(self) -> Optional[str]:
        return _read_active_doc_id()

    # ---------- Core ops ----------
    def add_document(self, doc_name: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Add a document's chunks (with pages) to the vector store.
        Each chunk dict must contain: { "text": str, "page": int }
        Returns generated doc_id.
        """
        doc_id = str(uuid.uuid4())

        texts = [c["text"] for c in chunks]
        embeddings = self._embedder.embed_batch(texts)

        ids: List[str] = []
        metas: List[Dict[str, Any]] = []
        docs: List[str] = []

        for c, emb in zip(chunks, embeddings):
            cid = str(uuid.uuid4())
            ids.append(cid)
            metas.append({
                "doc_id": doc_id,
                "doc_name": doc_name,
                "page": int(c.get("page") or 0),
                "chunk_id": cid
            })
            docs.append(c["text"])

        # Add to collection
        self.collection.add(
            ids=ids,
            documents=docs,
            metadatas=metas,
            embeddings=embeddings
        )

        # Mark this as active doc
        self.set_active_doc(doc_id)
        return doc_id

    def query(self, query_embedding: List[float], where: Dict[str, Any] | None = None, top_k: int = 5):
        """
        Query by embedding with optional metadata filter.
        Returns Chroma's dict result (documents, metadatas, distances).
        """
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where or {}
        )
