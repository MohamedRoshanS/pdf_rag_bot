from typing import List
import os

try:
    from sentence_transformers import SentenceTransformer
except Exception as e:
    SentenceTransformer = None  # Allow import even if not installed

class LocalEmbedder:
    """
    Thin wrapper around SentenceTransformer with safe fallbacks.
    Configure model name via settings.embedding_model.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        if SentenceTransformer is None:
            raise RuntimeError(
                "sentence-transformers is not installed. Please install it: "
                "pip install sentence-transformers"
            )
        self.model_name = model_name or "sentence-transformers/all-MiniLM-L6-v2"
        self.model = SentenceTransformer(self.model_name)

    def embed_one(self, text: str) -> List[float]:
        emb = self.model.encode([text], normalize_embeddings=True)
        return emb[0].tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embs = self.model.encode(texts, batch_size=32, normalize_embeddings=True)
        return [e.tolist() for e in embs]
