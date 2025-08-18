from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Explicitly load the .env file
load_dotenv()

class Settings(BaseSettings):
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    persist_dir: str = os.getenv("PERSIST_DIR", "./persistence")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", 900))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", 150))
    top_k: int = int(os.getenv("TOP_K", 5))
    max_tokens_answer: int = int(os.getenv("MAX_TOKENS_ANSWER", 512))

settings = Settings()
