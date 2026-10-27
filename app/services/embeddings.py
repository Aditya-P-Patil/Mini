
import os
from collections.abc import Sequence

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

    embeddings = embed_texts([text], task_type=task_type)
    return embeddings[0]


def embed_texts(
    texts: Sequence[str],
    task_type: str = "RETRIEVAL_DOCUMENT",
) -> list[list[float]]:
    """Generate embeddings for multiple texts in one Gemini request."""

    normalized_texts = [text.strip() for text in texts]

    if not normalized_texts or any(not text for text in normalized_texts):
        raise ValueError("Texts must not be empty.")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing from the environment."
        )

    if task_type not in {"RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"}:
        raise ValueError("Unsupported embedding task type.")

    client = genai.Client(api_key=api_key)
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=text)],
        )
        for text in normalized_texts
    ]

    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=contents,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=EMBEDDING_DIMENSIONS,
        ),
    )

    if not result.embeddings or len(result.embeddings) != len(normalized_texts):
        raise RuntimeError(
            "Gemini returned an unexpected number of embeddings."
        )

    embeddings = []
    for embedding_result in result.embeddings:
        embedding = embedding_result.values

        if not embedding or len(embedding) != EMBEDDING_DIMENSIONS:
            raise RuntimeError(
                f"Expected {EMBEDDING_DIMENSIONS} dimensions, "
                f"received {len(embedding) if embedding else 0}."
            )

        embeddings.append(embedding)

    return embeddings
