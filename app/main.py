
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, text, delete
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Document, DocumentPage, DocumentChunk
from app.services.pdf_processor import extract_pdf_pages
from app.services.chunking import chunk_text
from app.services.answer_generation import answer_question
from app.financial_intelligence.routes import router as financial_router


logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 25 * 1024 * 1024


# -------------------------
# RAG request model
# -------------------------

class RAGQuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=10)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Question must not be empty.")

        return value



# -------------------------
# Application lifespan
# -------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


# -------------------------
# FastAPI application
# -------------------------
app = FastAPI(
    title="AI Financial Research Assistant",
    description="Evidence-backed financial research API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(financial_router)


# -------------------------
# Home
# -------------------------
@app.get("/")
def home():
    return {
        "message": "Financial Research Assistant API is running!",
        "status": "success",
    }


# -------------------------
# Health check
# -------------------------
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as exc:
        logger.exception("Database health check failed")
        raise HTTPException(
            status_code=503,
            detail="Database connection failed.",
        ) from exc


# -------------------------
# Upload PDF
# -------------------------
@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    filename = Path(file.filename or "").name

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    pdf_bytes = await file.read(MAX_FILE_SIZE + 1)
    await file.close()

    if len(pdf_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="PDF must be 25 MB or smaller.",
        )

    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid PDF.",
        )

    try:
        pages = extract_pdf_pages(pdf_bytes)
    except Exception as exc:
        logger.exception("PDF extraction failed")
        raise HTTPException(
            status_code=400,
            detail="Could not read this PDF. It may be damaged or encrypted.",
        ) from exc

    if not any(page["text"] for page in pages):
        raise HTTPException(
            status_code=422,
            detail="No embedded text found. This PDF may require OCR.",
        )

    document = Document(
        filename=filename,
        page_count=len(pages),
    )

    try:
        db.add(document)
        db.flush()

        for page in pages:
            db.add(
                DocumentPage(
                    document_id=document.id,
                    page_number=page["page_number"],
                    text=page["text"],
                )
            )

        db.commit()
        db.refresh(document)

        return {
            "message": "PDF processed and saved successfully.",
            "document_id": document.id,
            "filename": document.filename,
            "page_count": document.page_count,
            "pages_with_text": sum(bool(p["text"]) for p in pages),
        }

    except Exception as exc:
        db.rollback()
        logger.exception("Failed to save uploaded document")
        raise HTTPException(
            status_code=500,
            detail="Failed to save the document.",
        ) from exc


# -------------------------
# List documents
# -------------------------
@app.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    documents = db.scalars(
        select(Document).order_by(Document.id.desc())
    ).all()

    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "page_count": doc.page_count,
            "uploaded_at": (
                doc.uploaded_at.isoformat()
                if doc.uploaded_at
                else None
            ),
        }
        for doc in documents
    ]


# -------------------------
# Retrieve a document page
# -------------------------
@app.get("/documents/{document_id}/pages/{page_number}")
def get_document_page(
    document_id: int,
    page_number: int,
    db: Session = Depends(get_db),
):
    page = db.scalar(
        select(DocumentPage).where(
            DocumentPage.document_id == document_id,
            DocumentPage.page_number == page_number,
        )
    )

    if page is None:
        raise HTTPException(
            status_code=404,
            detail="Document page not found.",
        )

    return {
        "document_id": page.document_id,
        "page_number": page.page_number,
        "text": page.text,
    }


# -------------------------
# Create document chunks
# -------------------------
@app.post("/documents/{document_id}/chunk")
def create_document_chunks(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    pages = db.scalars(
        select(DocumentPage)
        .where(DocumentPage.document_id == document_id)
        .order_by(DocumentPage.page_number)
    ).all()

    if not pages:
        raise HTTPException(
            status_code=422,
            detail="Document has no stored pages.",
        )

    new_chunks = []
    next_index = 0

    for page in pages:
        page_chunks = chunk_text(page.text)

        for chunk in page_chunks:
            new_chunks.append(
                DocumentChunk(
                    document_id=document_id,
                    page_number=page.page_number,
                    chunk_index=next_index,
                    text=chunk,
                )
            )
            next_index += 1

    if not new_chunks:
        raise HTTPException(
            status_code=422,
            detail="No text available to chunk.",
        )

    try:
        db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.document_id == document_id
            )
        )

        db.add_all(new_chunks)
        db.commit()

    except Exception as exc:
        db.rollback()
        logger.exception("Failed to save document chunks")
        raise HTTPException(
            status_code=500,
            detail="Failed to save document chunks.",
        ) from exc

    return {
        "message": "Document chunked successfully.",
        "document_id": document_id,
        "total_chunks": len(new_chunks),
        "chunk_size": 1200,
        "overlap": 200,
    }


# -------------------------
# List document chunks
# -------------------------
@app.get("/documents/{document_id}/chunks")
def list_document_chunks(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    chunks = db.scalars(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    ).all()

    return [
        {
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "page_number": chunk.page_number,
            "chunk_index": chunk.chunk_index,
            "text": chunk.text,
        }
        for chunk in chunks
    ]


# -------------------------
# RAG question-answering endpoint
# -------------------------
@app.post("/rag/ask")
def ask_rag(
    request: RAGQuestionRequest,
    db: Session = Depends(get_db),
):
    try:
        return answer_question(
            db=db,
            question=request.question,
            top_k=request.top_k,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        # Keep detailed errors in server logs, not in API responses.
        logger.exception("RAG answer generation failed")

        raise HTTPException(
            status_code=502,
            detail="RAG answer generation failed. Check server logs.",
        ) from exc
