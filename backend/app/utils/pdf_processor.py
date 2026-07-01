# backend/app/utils/pdf_processor.py

import re
import io
import logging
from typing import Tuple, Optional, List

logger = logging.getLogger(__name__)

# ============================================================
# ADD THESE FUNCTIONS (at the top of the file)
# ============================================================

def clean_pdf_text(text: str) -> str:
    """
    Clean extracted PDF text by removing extra whitespace, fixing line breaks,
    and normalizing common formatting issues.
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Fix common PDF extraction artifacts
    text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)  # Fix hyphenated words
    text = re.sub(r'(\w)\s+-\s+(\w)', r'\1-\2', text)  # Fix spaced hyphens
    
    # Remove special characters that often appear in PDFs
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
    
    # Normalize bullet points
    text = re.sub(r'[•·●○◆◇▪▫]', '•', text)
    
    # Clean up multiple spaces
    text = re.sub(r' +', ' ', text)
    
    return text.strip()


def normalize_space(text: str) -> str:
    """
    Normalize whitespace in text - collapse multiple spaces, remove leading/trailing spaces.
    """
    if not text:
        return ""
    
    # Collapse multiple spaces into single space
    text = re.sub(r' +', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Normalize newlines - keep single newlines but collapse multiple
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text


def chunk_text(text: str, chunk_size: int = 2000) -> List[str]:
    """
    Split text into chunks for processing by AI models.
    """
    if not text:
        return []
    
    chunks = []
    words = text.split()
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks


# ============================================================
# YOUR EXISTING FUNCTIONS (keep these)
# ============================================================

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None
    logger.warning("pypdf not installed. Install with: pip install pypdf")

try:
    import pdfplumber
except ImportError:
    pdfplumber = None
    logger.warning("pdfplumber not installed. Install with: pip install pdfplumber")


def validate_pdf(pdf_bytes: bytes) -> Tuple[bool, str]:
    # ... your existing code ...
    pass


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    # ... your existing code ...
    # Make sure to call clean_pdf_text on the extracted text
    pass


def get_pdf_info(pdf_bytes: bytes) -> dict:
    # ... your existing code ...
    pass