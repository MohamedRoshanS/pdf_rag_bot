import fitz  # PyMuPDF
from typing import Dict, Tuple

class PDFExtractionError(Exception):
    """Raised when a PDF cannot be read or parsed."""
    pass


def extract_text_from_pdf(file_path: str) -> Tuple[str, Dict[int, str]]:
    """
    Extract full text and a mapping of page -> text from a PDF.

    Args:
        file_path: path to PDF

    Returns:
        (full_text, page_map)
        - full_text: all pages concatenated
        - page_map: dict of page_number (1-based) -> text
    """
    try:
        doc = fitz.open(file_path)
        if doc.page_count == 0:
            raise PDFExtractionError("Empty PDF file")

        full_text_parts = []
        page_map: Dict[int, str] = {}

        for i in range(doc.page_count):
            page = doc[i]
            text = page.get_text("text") or ""
            page_map[i + 1] = text
            full_text_parts.append(text)

        doc.close()
        return "\n".join(full_text_parts), page_map

    except Exception as e:
        raise PDFExtractionError(f"Failed to extract text from PDF: {e}")
