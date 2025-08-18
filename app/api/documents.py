import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.config import settings
from app.db.vectorstore import VectorStore
from app.services.pdf import extract_text_from_pdf
from app.services.chunking import chunk_text
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        filename = file.filename
        if not filename.lower().endswith(".pdf"):
            logger.warning(f"Upload rejected: not a PDF - {filename}")
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Save uploaded file locally
        upload_dir = getattr(settings, "UPLOAD_DIR", "./uploads")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{filename}")

        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"File uploaded and saved: {file_path}")

        # Extract raw text + page map
        full_text, page_map = extract_text_from_pdf(file_path)
        if not full_text.strip():
            logger.warning(f"No text extracted from PDF: {file_path}")
            raise HTTPException(status_code=400, detail="No text could be extracted from PDF")

        # Build chunks per page
        chunks = []
        for page_num, page_text in page_map.items():
            page_chunks = chunk_text(page_text, settings.chunk_size, settings.chunk_overlap)
            for ch in page_chunks:
                chunks.append({"text": ch, "page": page_num})
        logger.info(f"Created {len(chunks)} chunks from PDF: {filename}")


        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks were created from PDF")

        # Store to vectorstore (embeddings computed internally)
        vs = VectorStore()
        doc_id = vs.add_document(doc_name=filename, chunks=chunks)
        logger.info(f"Document indexed with doc_id={doc_id}")


        return {
            "status": "success",
            "doc_id": doc_id,
            "filename": filename,
            "chunks": len(chunks)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Upload failed", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
