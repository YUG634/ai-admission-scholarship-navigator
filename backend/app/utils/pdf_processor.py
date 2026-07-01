import io
import logging
from typing import Tuple, Optional

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
                return text
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
                    return text
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
        return combined_text
    
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