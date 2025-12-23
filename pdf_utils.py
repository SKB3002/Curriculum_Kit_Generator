# pdf_utils.py
from typing import Tuple
import fitz  # PyMuPDF

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts text from a PDF file (bytes) using PyMuPDF.
    Returns full text as a single string.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    texts = []
    for page in doc:
        text = page.get_text("text")
        texts.append(text)
    doc.close()
    full_text = "\n".join(texts)
    return clean_extracted_text(full_text)


def clean_extracted_text(text: str) -> str:
    """
    Basic cleanup: remove extra spaces, normalize newlines.
    """
    # Normalize Windows newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove repeated blank lines
    lines = [line.strip() for line in text.split("\n")]
    cleaned_lines = []
    prev_blank = False
    for line in lines:
        if not line:
            if not prev_blank:
                cleaned_lines.append("")
            prev_blank = True
        else:
            cleaned_lines.append(line)
            prev_blank = False

    cleaned = "\n".join(cleaned_lines).strip()
    return cleaned


def rough_word_count(text: str) -> int:
    return len(text.split())
