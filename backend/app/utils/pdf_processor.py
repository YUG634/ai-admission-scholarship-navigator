# backend/app/utils/pdf_processor.py

import re
import io
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def extract_tables_from_pdf(pdf_bytes: bytes) -> List[List[List[str]]]:
    """
    Extract tables from PDF using pdfplumber
    """
    if not pdfplumber:
        logger.warning("pdfplumber not installed. Tables won't be extracted.")
        return []
    
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            tables = []
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
            return tables
    except Exception as e:
        logger.error(f"Error extracting tables: {e}")
        return []

def extract_pdf_structure(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Extract structured data from PDF including:
    - Full text
    - Tables
    - Page structure
    """
    result = {
        "text": "",
        "tables": [],
        "pages": []
    }
    
    # Extract text
    try:
        result["text"] = extract_text_from_pdf(pdf_bytes)
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
    
    # Extract tables
    try:
        result["tables"] = extract_tables_from_pdf(pdf_bytes)
    except Exception as e:
        logger.error(f"Table extraction failed: {e}")
    
    return result