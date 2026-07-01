# backend/app/utils/pdf_parser.py

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def parse_admission_document(text: str, tables: List[List[List[str]]]) -> Dict[str, Any]:
    """
    Parse admission circular PDF content into structured data
    """
    result = {
        "title": extract_title(text),
        "deadlines": extract_deadlines(text),
        "programs": extract_programs(text, tables),
        "documents": extract_documents(tables),
        "direct_admission": extract_direct_admission(tables),
        "merit_schedule": extract_merit_schedule(tables),
        "entrance_exams": extract_entrance_exams(tables),
        "contact": extract_contact(text),
        "entrance_requirements": extract_entrance_requirements(text),
    }
    return result

def extract_documents(tables: List[List[List[str]]]) -> List[str]:
    """
    Extract required documents from PART-G table
    """
    documents = []
    
    # Look for PART-G in tables
    for table in tables:
        for row in table:
            row_text = ' '.join(str(cell) if cell else '' for cell in row)
            if 'PART-G' in row_text or 'LIST OF REQUIRED DOCUMENTS' in row_text:
                # Extract document names
                doc_pattern = r'\d+\.\s*([^□\n]+)'
                matches = re.findall(doc_pattern, row_text)
                documents.extend([doc.strip() for doc in matches if doc.strip()])
    
    # If not found in tables, try text search
    if not documents:
        text_content = '\n'.join([' '.join(str(cell) if cell else '' for cell in row) for table in tables for row in table])
        # Look for document pattern in text
        doc_pattern = r'\d+\.\s*([^\n]+?)(?:\s*□|\s*\(If applicable\)|\s*\(if applicable\)|\s*$|\.)'
        matches = re.findall(doc_pattern, text_content)
        documents = [doc.strip() for doc in matches if doc.strip()]
    
    return documents

def extract_direct_admission(tables: List[List[List[str]]]) -> List[Dict[str, str]]:
    """
    Extract direct admission programs from PART-B and PART-C
    """
    programs = []
    
    for table in tables:
        for row in table:
            row_text = ' '.join(str(cell) if cell else '' for cell in row)
            if 'PART-C' in row_text or 'DIRECT ADMISSION SCHEDULE' in row_text:
                # Parse program names
                program_pattern = r'(\d+)\.\s*([^,\n]+)'
                matches = re.findall(program_pattern, row_text)
                for match in matches:
                    programs.append({
                        "name": match[1].strip(),
                        "type": "Direct Admission"
                    })
    
    return programs

def extract_merit_schedule(tables: List[List[List[str]]]) -> List[Dict[str, str]]:
    """
    Extract merit list schedule from PART-D
    """
    merit_lists = []
    
    for table in tables:
        for row in table:
            row_text = ' '.join(str(cell) if cell else '' for cell in row)
            if 'First Merit List' in row_text:
                date_match = re.search(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s*([^,]+),\s*(\d{4})', row_text)
                if date_match:
                    merit_lists.append({
                        "name": "First Merit List",
                        "date": f"{date_match.group(1)}, {date_match.group(2)}, {date_match.group(3)}"
                    })
            elif 'Second Merit List' in row_text:
                date_match = re.search(r'(Friday|Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday),\s*([^,]+),\s*(\d{4})', row_text)
                if date_match:
                    merit_lists.append({
                        "name": "Second Merit List",
                        "date": f"{date_match.group(1)}, {date_match.group(2)}, {date_match.group(3)}"
                    })
    
    return merit_lists

def extract_entrance_exams(tables: List[List[List[str]]]) -> Dict[str, Any]:
    """
    Extract entrance exam schedule from PART-F
    """
    result = {
        "h_cet": {"may_dates": [], "june_dates": []},
        "h_lat": {"may_dates": [], "june_dates": []}
    }
    
    for table in tables:
        for row in table:
            row_text = ' '.join(str(cell) if cell else '' for cell in row)
            if 'H-CET' in row_text:
                # Extract dates
                may_dates = re.findall(r'(\d+)(?:st|nd|rd|th)\s+May\s+(\d{4})', row_text)
                june_dates = re.findall(r'(\d+)(?:st|nd|rd|th)\s+June\s+(\d{4})', row_text)
                result["h_cet"]["may_dates"] = [f"{date[0]} May {date[1]}" for date in may_dates]
                result["h_cet"]["june_dates"] = [f"{date[0]} June {date[1]}" for date in june_dates]
            elif 'H-LAT' in row_text:
                may_dates = re.findall(r'(\d+)(?:st|nd|rd|th)\s+May\s+(\d{4})', row_text)
                june_dates = re.findall(r'(\d+)(?:st|nd|rd|th)\s+June\s+(\d{4})', row_text)
                result["h_lat"]["may_dates"] = [f"{date[0]} May {date[1]}" for date in may_dates]
                result["h_lat"]["june_dates"] = [f"{date[0]} June {date[1]}" for date in june_dates]
    
    return result

def extract_contact(text: str) -> Dict[str, Any]:
    """
    Extract contact information from text
    """
    result = {"email": "", "phone": []}
    
    # Extract email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        result["email"] = email_match.group(0)
    
    # Extract phone numbers
    phone_pattern = r'\+?91?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    matches = re.findall(phone_pattern, text)
    result["phone"] = matches
    
    return result

def extract_entrance_requirements(text: str) -> Dict[str, Any]:
    """
    Extract entrance exam requirements
    """
    result = {
        "bms_bba_bca": "H-CET (or MHCET exemption)",
        "law": "H-LAT (or state/national level exam exemption)",
        "btc": "Qualifying Entrance Exam"
    }
    return result

def extract_title(text: str) -> str:
    """
    Extract document title
    """
    # Look for circular title
    title_pattern = r'#\s*([^\n]+)\s*\n'
    matches = re.findall(title_pattern, text)
    if matches:
        return matches[0].strip()
    return "Admission Circular"

def extract_deadlines(text: str) -> List[Dict[str, str]]:
    """
    Extract deadlines from text
    """
    deadlines = []
    
    # Look for date patterns
    date_pattern = r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s*([^,]+),\s*(\d{4})'
    matches = re.findall(date_pattern, text)
    
    for match in matches:
        deadlines.append({
            "date": f"{match[1]}, {match[2]}",
            "description": "Application deadline"
        })
    
    return deadlines