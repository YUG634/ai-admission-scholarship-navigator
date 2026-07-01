import PyPDF2
import pdfplumber
from io import BytesIO
import re

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF with better handling of corrupted text"""
    
    # Method 1: Try pdfplumber (better for complex layouts)
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                # Clean up the text
                page_text = clean_pdf_text(page_text)
                text += page_text + "\n"
            if text.strip():
                print(f"✅ pdfplumber extracted {len(text)} chars")
                return text.strip()
    except Exception as e:
        print(f"pdfplumber failed: {e}")
    
    # Method 2: Fallback to PyPDF2
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text() or ""
            page_text = clean_pdf_text(page_text)
            text += page_text + "\n"
        if text.strip():
            print(f"✅ PyPDF2 extracted {len(text)} chars")
            return text.strip()
    except Exception as e:
        print(f"PyPDF2 failed: {e}")
    
    return ""

def clean_pdf_text(text: str) -> str:
    """Clean up corrupted PDF text (fix spacing issues)"""
    # Fix spaced letters: "0 5 t h M a y" → "05th May"
    text = re.sub(r'(\d)\s+(\d)\s+([a-zA-Z])\s+([a-zA-Z])\s+([a-zA-Z])', r'\1\2\3\4\5', text)
    text = re.sub(r'([a-zA-Z])\s+([a-zA-Z])\s+([a-zA-Z])\s+([a-zA-Z])', r'\1\2\3\4', text)
    text = re.sub(r'([a-zA-Z])\s+([a-zA-Z])\s+([a-zA-Z])', r'\1\2\3', text)
    text = re.sub(r'([a-zA-Z])\s+([a-zA-Z])', r'\1\2', text)
    
    # Fix common patterns: "FO R" → "FOR"
    text = re.sub(r'F O R', 'FOR', text)
    text = re.sub(r'T H E', 'THE', text)
    text = re.sub(r'A N D', 'AND', text)
    
    # Fix dates: "0 5 t h M a y" → "05th May"
    text = re.sub(r'(\d)\s+(\d)\s+([a-zA-Z])\s+([a-zA-Z])\s+([a-zA-Z])', r'\1\2\3\4\5', text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text

def validate_pdf(pdf_bytes: bytes) -> bool:
    """Validate if the file is a proper PDF"""
    try:
        PyPDF2.PdfReader(BytesIO(pdf_bytes))
        return True
    except:
        try:
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                return len(pdf.pages) > 0
        except:
            return False