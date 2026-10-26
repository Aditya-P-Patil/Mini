
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

EMBEDDING_MODEL = "gemini-embedding-2"
EMBEDDING_DIMENSIONS = 768


def embed_text(
    text: str,
    task_type: str = "RETRIEVAL_DOCUMENT",
) -> list[float]:
    """Generate a Gemini embedding for document text or a search query."""

    if not text or not text.strip():
        raise ValueError("Text must not be empty.")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing from the environment."
        )

    if task_type not in {"RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"}:
        raise ValueError("Unsupported embedding task type.")

    client = genai.Client(api_key=api_key)

    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text.strip(),
        config=types.EmbedContentConfig(
    task_type=task_type,
    output_dimensionality=EMBEDDING_DIMENSIONS,
),
    )

    if not result.embeddings or not result.embeddings[0].values:
        raise RuntimeError("Gemini returned no embedding.")

    embedding = result.embeddings[0].values

    if len(embedding) != EMBEDDING_DIMENSIONS:
        raise RuntimeError(
            f"Expected {EMBEDDING_DIMENSIONS} dimensions, "
            f"received {len(embedding)}."
        )

    return embedding
