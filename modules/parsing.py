import io
from typing import Optional

from PyPDF2 import PdfReader
from docx import Document

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = []
    reader = PdfReader(io.BytesIO(file_bytes))
    for page in reader.pages:
        try:
            text.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(text)

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text_from_txt(file_bytes: bytes, encoding: str = "utf-8") -> str:
    try:
        return file_bytes.decode(encoding, errors="ignore")
    except Exception:
        return file_bytes.decode("latin-1", errors="ignore")

def extract_text_from_file(uploaded_file) -> str:
    file_bytes = uploaded_file.getvalue()
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif name.endswith(".txt"):
        return extract_text_from_txt(file_bytes)
    else:
        # fallback: try pdf, then docx, then txt
        try:
            return extract_text_from_pdf(file_bytes)
        except Exception:
            try:
                return extract_text_from_docx(file_bytes)
            except Exception:
                return extract_text_from_txt(file_bytes)
