
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentChunk
from app.services.embeddings import embed_texts


def embed_pending_chunks(
    db: Session,
    document_id: int | None = None,
    batch_size: int = 5,
) -> dict:
    """Generate and save embeddings for all pending chunks in batches."""

    if batch_size < 1 or batch_size > 20:
        raise ValueError("batch_size must be between 1 and 20.")

    base_statement = (
        select(DocumentChunk)
        .where(DocumentChunk.embedding.is_(None))
        .order_by(DocumentChunk.id)
    )
    if document_id is not None:
        base_statement = base_statement.where(
            DocumentChunk.document_id == document_id
        )

    pending_chunks = db.scalars(base_statement).all()

    if not pending_chunks:
        return {
            "processed": 0,
            "message": "No chunks need embeddings.",
        }

    processed = 0
    chunk_ids = []

    try:
        for start in range(0, len(pending_chunks), batch_size):
            batch = pending_chunks[start:start + batch_size]
            embeddings = embed_texts([chunk.text for chunk in batch])

            for chunk, embedding in zip(batch, embeddings):
                chunk.embedding = embedding
                chunk_ids.append(chunk.id)
                processed += 1

            db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "processed": processed,
        "chunk_ids": chunk_ids,
        "message": "Embeddings saved successfully.",
    }
