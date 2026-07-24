import io

import pdfplumber
from docx import Document


def extract_text_from_pdf(content: bytes) -> str:
    text_pages = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_pages.append(page_text)
    return "\n".join(text_pages)


def extract_text_from_docx(content: bytes) -> str:
    doc = Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text(filename: str, content: bytes) -> str | None:
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(content)
    elif filename.lower().endswith(".docx"):
        return extract_text_from_docx(content)
    return None
