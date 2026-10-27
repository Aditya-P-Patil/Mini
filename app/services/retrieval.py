
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Document, DocumentChunk
from app.services.embeddings import embed_text


# Retrieve extra candidates so duplicate passages can be skipped.
CANDIDATE_MULTIPLIER = 4
MAX_CANDIDATES = 40


def _normalize_text(text: str) -> str:
    """Normalize whitespace and casing for duplicate detection."""
    return " ".join(text.lower().split())


def _is_duplicate(candidate: str, selected: list[str]) -> bool:
    """
    Detect exact and near-exact duplicate passages.

    This deliberately uses conservative text matching rather than
    treating semantically related passages as duplicates.
    """
    candidate_normalized = _normalize_text(candidate)

    if not candidate_normalized:
        return True

    for existing in selected:
        existing_normalized = _normalize_text(existing)

        if candidate_normalized == existing_normalized:
            return True

        # Avoid returning a short passage already contained in a
        # longer passage, or vice versa.
        shorter, longer = sorted(
            (candidate_normalized, existing_normalized),
            key=len,
        )

        if len(shorter) >= 80 and shorter in longer:
            return True

    return False


def search_similar_chunks(
    db: Session,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """Retrieve relevant embedded chunks while reducing duplicate text."""

    if not query or not query.strip():
        raise ValueError("Query must not be empty.")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20.")

    query_embedding = embed_text(
        query.strip(),
        task_type="RETRIEVAL_QUERY",
    )

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    candidate_limit = min(
        top_k * CANDIDATE_MULTIPLIER,
        MAX_CANDIDATES,
    )

    statement = (
        select(
            DocumentChunk,
            Document.filename,
            distance.label("distance"),
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .where(DocumentChunk.embedding.is_not(None))
        .order_by(distance)
        .limit(candidate_limit)
    )

    rows = db.execute(statement).all()

    results = []
    selected_texts = []

    for chunk, filename, cosine_distance in rows:
        if _is_duplicate(chunk.text, selected_texts):
            continue

        similarity_score = 1.0 - float(cosine_distance)

        results.append(
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "filename": filename,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "similarity_score": round(similarity_score, 4),
            }
        )

        selected_texts.append(chunk.text)

        if len(results) >= top_k:
            break

    return results
