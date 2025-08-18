import re
from typing import List

def clean_text(text: str) -> str:
    """Normalize whitespace and trivial artifacts."""
    # collapse multiple whitespace
    text = re.sub(r"[ \t]+", " ", text)
    # normalize newlines -> single spaces (we chunk by chars, not lines)
    text = re.sub(r"\s*\n\s*", " ", text)
    return text.strip()

def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Split text into overlapping chunks, trying to end on sentence boundaries.

    Args:
        text: input string
        chunk_size: max chars per chunk (e.g., 900)
        overlap: overlap size (e.g., 150)

    Returns:
        list of chunk strings
    """
    text = clean_text(text)
    if not text:
        return []

    chunks: List[str] = []
    n = len(text)
    start = 0

    while start < n:
        end = min(start + chunk_size, n)
        # try to cut on a sentence boundary (., ?, !) nearest to end
        if end < n:
            boundary = max(text.rfind(".", start, end),
                           text.rfind("?", start, end),
                           text.rfind("!", start, end))
            if boundary != -1 and boundary > start + int(0.4 * chunk_size):
                end = boundary + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end == n:
            break
        start = max(0, end - overlap)

    return chunks
