"""
pdf_extractor.py
----------------
Extracts raw text from a PDF file using pdfplumber (handles most modern PDFs).
Falls back to pypdf if pdfplumber yields empty text.
"""

import pdfplumber
from pypdf import PdfReader
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF given its raw bytes.

    Args:
        file_bytes: Raw bytes of the uploaded PDF file.

    Returns:
        Extracted text as a single string.

    Raises:
        ValueError: If no text could be extracted from the PDF.
    """
    text = _extract_with_pdfplumber(file_bytes)

    # Fallback to pypdf if pdfplumber returns empty
    if not text.strip():
        text = _extract_with_pypdf(file_bytes)

    if not text.strip():
        raise ValueError(
            "Could not extract any text from the PDF. "
            "The file may be scanned/image-based. "
            "Please upload a text-based PDF."
        )

    return text


def _extract_with_pdfplumber(file_bytes: bytes) -> str:
    """Extract text using pdfplumber (better layout preservation)."""
    text_parts = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception:
        pass
    return "\n".join(text_parts)


def _extract_with_pypdf(file_bytes: bytes) -> str:
    """Fallback: extract text using pypdf."""
    text_parts = []
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    except Exception:
        pass
    return "\n".join(text_parts)
