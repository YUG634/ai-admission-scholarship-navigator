import PyPDF2
import pdfplumber
from io import BytesIO
from typing import Optional

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text content from PDF bytes"""
    try:
        # Try pdfplumber first (better for complex layouts)
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            if text.strip():
                return text.strip()
    except Exception as e:
        print(f"pdfplumber failed: {e}")
    
    try:
        # Fallback to PyPDF2
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        raise Exception(f"PDF extraction failed: {str(e)}")

def validate_pdf(pdf_bytes: bytes) -> bool:
    """Validate if the file is a proper PDF"""
    try:
        PyPDF2.PdfReader(BytesIO(pdf_bytes))
        return True
    except:
        return False