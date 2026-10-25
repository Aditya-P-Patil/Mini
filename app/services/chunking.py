
def chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200
) -> list[str]:
    text=" ".join(text.split())

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size")

    chunks=[]
    start=0
    text_length=len(text)

    while start < text_length:
        end=min(start+chunk_size, text_length)
        chunk=text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == text_length:
            break

        start=end-overlap

    return chunks
