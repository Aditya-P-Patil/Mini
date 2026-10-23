
import pymupdf


def extract_pdf_pages(pdf_bytes: bytes) -> list[dict]:
    pages=[]

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
        if pdf.page_count == 0:
            raise ValueError("The PDF contains no pages.")

        for page_index, page in enumerate(pdf):
            text=page.get_text("text").strip()

            pages.append({
                "page_number": page_index+1,
                "text": text
            })

    return pages
