
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentChunk
from app.services.embeddings import embed_text


def embed_pending_chunks(
    db: Session,
    document_id: int | None = None,
    batch_size: int = 5,
) -> dict:
    """Generate and save embeddings for a small batch of pending chunks."""

    if batch_size < 1 or batch_size > 20:
        raise ValueError("batch_size must be between 1 and 20.")

    statement = (
        select(DocumentChunk)
        .where(DocumentChunk.embedding.is_(None))
        .order_by(DocumentChunk.id)
        .limit(batch_size)
    )

    if document_id is not None:
        statement = statement.where(
            DocumentChunk.document_id == document_id
        )

    chunks = db.scalars(statement).all()

    if not chunks:
        return {
            "processed": 0,
            "message": "No chunks need embeddings.",
        }

    processed = 0

    try:
        for chunk in chunks:
            chunk.embedding = embed_text(chunk.text)
            processed += 1

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "processed": processed,
        "chunk_ids": [chunk.id for chunk in chunks],
        "message": "Embeddings saved successfully.",
    }
