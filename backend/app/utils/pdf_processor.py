# backend/app/utils/pdf_processor.py

import io
import logging
import re
from typing import Tuple, Optional, List

logger = logging.getLogger(__name__)

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


# ============================================================
# ADD THESE FUNCTIONS (NEW)
# ============================================================

def clean_pdf_text(text: str) -> str:
    """
    Clean extracted PDF text by removing extra whitespace, fixing line breaks,
    and normalizing common formatting issues.
    
    Args:
        text: Raw text extracted from PDF
        
    Returns:
        Cleaned text
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
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
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
    
    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk
        
    Returns:
        List of text chunks
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
# EXISTING FUNCTIONS (keep these)
# ============================================================

def validate_pdf(pdf_bytes: bytes) -> Tuple[bool, str]:
    """
    Validate if the bytes represent a valid PDF
    
    Returns:
        (True, "Valid PDF") if valid
        (False, "Error message") if invalid
    """
    try:
        # Check PDF signature
        if not pdf_bytes.startswith(b'%PDF'):
            return False, "File is not a valid PDF (missing PDF signature)"
        
        # Try to read with pypdf first
        if PdfReader:
            try:
                reader = PdfReader(io.BytesIO(pdf_bytes))
                if len(reader.pages) == 0:
                    return False, "PDF has no pages"
                return True, "Valid PDF"
            except Exception as e:
                logger.warning(f"pypdf validation failed: {e}")
        
        # Fallback to pdfplumber
        if pdfplumber:
            try:
                with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                    if len(pdf.pages) == 0:
                        return False, "PDF has no pages"
                    return True, "Valid PDF"
            except Exception as e:
                logger.warning(f"pdfplumber validation failed: {e}")
        
        return False, "Could not read PDF file"
        
    except Exception as e:
        return False, f"PDF validation error: {str(e)}"


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF using multiple fallback methods
    
    Returns:
        Extracted text as string
    Raises:
        ValueError: If text cannot be extracted
    """
    # Method 1: PyPDF (fast, handles most PDFs)
    if PdfReader:
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if text and len(text.strip()) > 100:
                logger.info(f"✅ Extracted {len(text)} chars using pypdf")
                # Clean the extracted text
                cleaned_text = clean_pdf_text(text)
                return cleaned_text
            elif text.strip():
                logger.warning(f"⚠️ pypdf extracted only {len(text)} chars, trying fallback")
        except Exception as e:
            logger.warning(f"pypdf extraction failed: {e}")
    
    # Method 2: pdfplumber (better for complex/table PDFs)
    if pdfplumber:
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                if text and len(text.strip()) > 100:
                    logger.info(f"✅ Extracted {len(text)} chars using pdfplumber")
                    cleaned_text = clean_pdf_text(text)
                    return cleaned_text
                elif text.strip():
                    logger.warning(f"⚠️ pdfplumber extracted only {len(text)} chars")
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")
    
    # Method 3: Try both and combine
    combined_text = ""
    if PdfReader:
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    combined_text += page_text + "\n"
        except:
            pass
    
    if pdfplumber and not combined_text.strip():
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        combined_text += page_text + "\n"
        except:
            pass
    
    if combined_text.strip():
        logger.info(f"✅ Combined extraction: {len(combined_text)} chars")
        cleaned_text = clean_pdf_text(combined_text)
        return cleaned_text
    
    # All methods failed
    raise ValueError(
        "Could not extract text from PDF. "
        "The PDF might be scanned, password-protected, or corrupted. "
        "Try using a text-based PDF file."
    )


def get_pdf_info(pdf_bytes: bytes) -> dict:
    """
    Get basic PDF info without extracting all text
    """
    info = {
        "is_valid": False,
        "page_count": 0,
        "size_kb": len(pdf_bytes) // 1024
    }
    
    try:
        if PdfReader:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            info["page_count"] = len(reader.pages)
            info["is_valid"] = True
        elif pdfplumber:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                info["page_count"] = len(pdf.pages)
                info["is_valid"] = True
    except Exception as e:
        logger.warning(f"Could not get PDF info: {e}")
    
    return info