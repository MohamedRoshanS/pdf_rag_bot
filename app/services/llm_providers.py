import os
from typing import Protocol

# Optional dependency; only used if GEMINI is configured
try:
    import google.generativeai as genai
except Exception:
    genai = None


class LLM(Protocol):
    def generate(self, prompt: str) -> str: ...


class GeminiLLM:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        if genai is None:
            raise RuntimeError(
                "google-generativeai is not installed. Install with: pip install google-generativeai"
            )
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set.")
        genai.configure(api_key=api_key)
        self.model_name = model
        self.client = genai.GenerativeModel(self.model_name)

    def generate(self, prompt: str) -> str:
        resp = self.client.generate_content(prompt)
        try:
            return (resp.text or "").strip()
        except Exception:
            # Defensive fallback
            return ""


def get_llm() -> LLM:
    """
    Factory that returns the configured LLM backend.
    Currently supports Gemini via env vars:
      - LLM_PROVIDER=gemini
      - GEMINI_API_KEY=...
      - GEMINI_MODEL=gemini-2.0-flash
    """
    provider = (os.getenv("LLM_PROVIDER") or "gemini").lower()

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY", "")
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        return GeminiLLM(api_key=api_key, model=model)

    # Add other providers here as needed.

    raise RuntimeError(f"Unsupported LLM_PROVIDER: {provider}")
