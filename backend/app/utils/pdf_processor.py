# backend/app/utils/pdf_processor.py

import io
import logging
import re
from typing import Tuple, Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# ============================================================
# TEXT CLEANING FUNCTIONS
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
# PDF LIBRARY IMPORTS
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


# ============================================================
# PDF VALIDATION FUNCTIONS
# ============================================================

def validate_pdf(pdf_bytes: bytes) -> Tuple[bool, str]:
    """
    Validate if the bytes represent a valid PDF
    
    Args:
        pdf_bytes: PDF file as bytes
        
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


def get_pdf_info(pdf_bytes: bytes) -> dict:
    """
    Get basic PDF info without extracting all text
    
    Args:
        pdf_bytes: PDF file as bytes
        
    Returns:
        Dictionary with PDF metadata
    """
    info = {
        "is_valid": False,
        "page_count": 0,
        "size_kb": len(pdf_bytes) // 1024,
        "size_mb": len(pdf_bytes) / (1024 * 1024),
        "has_text": False,
        "text_preview": ""
    }
    
    try:
        if PdfReader:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            info["page_count"] = len(reader.pages)
            info["is_valid"] = True
            
            # Check if PDF has text
            sample_text = ""
            for i, page in enumerate(reader.pages[:3]):  # Check first 3 pages
                try:
                    page_text = page.extract_text()
                    if page_text:
                        sample_text += page_text[:500]
                except:
                    pass
            
            if sample_text.strip():
                info["has_text"] = True
                info["text_preview"] = sample_text[:200] + "..." if len(sample_text) > 200 else sample_text
                
        elif pdfplumber:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                info["page_count"] = len(pdf.pages)
                info["is_valid"] = True
                
                # Check if PDF has text
                sample_text = ""
                for i, page in enumerate(pdf.pages[:3]):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            sample_text += page_text[:500]
                    except:
                        pass
                
                if sample_text.strip():
                    info["has_text"] = True
                    info["text_preview"] = sample_text[:200] + "..." if len(sample_text) > 200 else sample_text
                    
    except Exception as e:
        logger.warning(f"Could not get PDF info: {e}")
    
    return info


# ============================================================
# TEXT EXTRACTION FUNCTIONS
# ============================================================

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF using multiple fallback methods
    
    Args:
        pdf_bytes: PDF file as bytes
        
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
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except:
                    continue
            
            if text and len(text.strip()) > 100:
                logger.info(f"✅ Extracted {len(text)} chars using pypdf")
                return clean_pdf_text(text)
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
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except:
                        continue
                
                if text and len(text.strip()) > 100:
                    logger.info(f"✅ Extracted {len(text)} chars using pdfplumber")
                    return clean_pdf_text(text)
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
                try:
                    page_text = page.extract_text()
                    if page_text:
                        combined_text += page_text + "\n"
                except:
                    continue
        except:
            pass
    
    if pdfplumber and not combined_text.strip():
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            combined_text += page_text + "\n"
                    except:
                        continue
        except:
            pass
    
    if combined_text.strip():
        logger.info(f"✅ Combined extraction: {len(combined_text)} chars")
        return clean_pdf_text(combined_text)
    
    # All methods failed
    raise ValueError(
        "Could not extract text from PDF. "
        "The PDF might be scanned, password-protected, or corrupted. "
        "Try using a text-based PDF file."
    )


def extract_structured_data(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Extract structured data from PDF including text and tables
    
    Args:
        pdf_bytes: PDF file as bytes
        
    Returns:
        Dictionary with structured data
    """
    result = {
        "text": "",
        "tables": [],
        "pages": 0,
        "has_text": False
    }
    
    # Extract text
    try:
        result["text"] = extract_text_from_pdf(pdf_bytes)
        result["has_text"] = bool(result["text"].strip())
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        result["text"] = ""
    
    # Extract tables using pdfplumber
    if pdfplumber:
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                result["pages"] = len(pdf.pages)
                
                # Extract tables from each page
                for page_num, page in enumerate(pdf.pages):
                    try:
                        tables = page.extract_tables()
                        if tables:
                            for table in tables:
                                if table and len(table) > 1:  # Valid table has multiple rows
                                    result["tables"].append({
                                        "page": page_num + 1,
                                        "data": table
                                    })
                    except Exception as e:
                        logger.warning(f"Table extraction failed on page {page_num}: {e}")
                        
        except Exception as e:
            logger.error(f"pdfplumber processing failed: {e}")
    
    # Fallback: Use pypdf if pdfplumber failed
    elif PdfReader:
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            result["pages"] = len(reader.pages)
            
            # Extract text with pypdf
            if not result["text"]:
                text = ""
                for page in reader.pages:
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except:
                        continue
                result["text"] = clean_pdf_text(text) if text else ""
                result["has_text"] = bool(result["text"].strip())
                
        except Exception as e:
            logger.error(f"pypdf processing failed: {e}")
    
    # Extract tables from text using regex (fallback)
    if not result["tables"] and result["text"]:
        try:
            tables = extract_tables_from_text(result["text"])
            if tables:
                result["tables"] = [{"page": 0, "data": table} for table in tables]
        except Exception as e:
            logger.warning(f"Text-based table extraction failed: {e}")
    
    return result


def extract_tables_from_text(text: str) -> List[List[List[str]]]:
    """
    Extract tables from text using regex patterns
    
    Args:
        text: Text to extract tables from
        
    Returns:
        List of tables (each table is a list of rows, each row is a list of strings)
    """
    tables = []
    
    # Look for table-like structures
    # Pattern 1: Numbered items (like PART-G)
    pattern1 = r'(?:PART-G|LIST OF REQUIRED DOCUMENTS)[:\s]*([\s\S]*?)(?=PART-|Kindly note|Students Help Desk|\Z)'
    match1 = re.search(pattern1, text, re.IGNORECASE)
    if match1:
        section = match1.group(1)
        # Extract numbered items
        items = re.findall(r'(\d+)\.\s*([^□\n]+?)(?:\s*□|\s*\(If applicable\)|\s*\(if applicable\)|\s*$|\.|\,)', section)
        if items:
            table = [[str(i), doc.strip()] for i, doc in items]
            tables.append(table)
    
    # Pattern 2: Phase schedules
    pattern2 = r'(Phase\s+\d+)[:\s]*([^\n]*?)(\d{1,2}(?:nd|st|rd|th)?\s+[A-Za-z]+\s+\d{4})[.\s]*([\d:]+[ap]m)?'
    matches = re.findall(pattern2, text, re.IGNORECASE)
    if matches:
        table = []
        for match in matches:
            table.append([match[0].strip(), match[2].strip(), match[3].strip() if len(match) > 3 else ""])
        if table:
            tables.append(table)
    
    # Pattern 3: Merit lists
    pattern3 = r'([A-Z][a-z]+)\s+Merit\s+List[:\s]*([A-Z][a-z]+,\s+[A-Z][a-z]+\s+\d{4})'
    matches = re.findall(pattern3, text, re.IGNORECASE)
    if matches:
        table = []
        for match in matches:
            table.append([f"{match[0].strip()} Merit List", match[1].strip()])
        if table:
            tables.append(table)
    
    return tables


# ============================================================
# EXPORTED FUNCTIONS
# ============================================================

__all__ = [
    'clean_pdf_text',
    'normalize_space',
    'chunk_text',
    'validate_pdf',
    'get_pdf_info',
    'extract_text_from_pdf',
    'extract_structured_data',
    'extract_tables_from_text',
]