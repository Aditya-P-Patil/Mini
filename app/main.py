
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Document, DocumentPage
from app.services.pdf_processor import extract_pdf_pages


MAX_FILE_SIZE=25*1024*1024


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app=FastAPI(
    title="AI Financial Research Assistant",
    description="Evidence-backed financial research API",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/")
def home():
    return {
        "message": "Financial Research Assistant API is running!",
        "status": "success"
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed."
        ) from exc


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    filename=Path(file.filename or "").name

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    pdf_bytes=await file.read(MAX_FILE_SIZE+1)
    await file.close()

    if len(pdf_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="PDF must be 25 MB or smaller."
        )

    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid PDF."
        )

    try:
        pages=extract_pdf_pages(pdf_bytes)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Could not read this PDF. It may be damaged or encrypted."
        ) from exc

    if not any(page["text"] for page in pages):
        raise HTTPException(
            status_code=422,
            detail="No embedded text found. This PDF may require OCR."
        )

    document=Document(
        filename=filename,
        page_count=len(pages)
    )

    try:
        db.add(document)
        db.flush()

        for page in pages:
            db.add(DocumentPage(
                document_id=document.id,
                page_number=page["page_number"],
                text=page["text"]
            ))

        db.commit()
        db.refresh(document)

        return {
            "message": "PDF processed and saved successfully.",
            "document_id": document.id,
            "filename": document.filename,
            "page_count": document.page_count,
            "pages_with_text": sum(bool(p["text"]) for p in pages)
        }

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save the document."
        ) from exc


@app.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    documents=db.scalars(
        select(Document).order_by(Document.id.desc())
    ).all()

    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "page_count": doc.page_count,
            "uploaded_at": doc.uploaded_at.isoformat()
        }
        for doc in documents
    ]


@app.get("/documents/{document_id}/pages/{page_number}")
def get_document_page(
    document_id: int,
    page_number: int,
    db: Session = Depends(get_db)
):
    page=db.scalar(
        select(DocumentPage).where(
            DocumentPage.document_id == document_id,
            DocumentPage.page_number == page_number
        )
    )

    if page is None:
        raise HTTPException(
            status_code=404,
            detail="Document page not found."
        )

    return {
        "document_id": page.document_id,
        "page_number": page.page_number,
        "text": page.text
    }
