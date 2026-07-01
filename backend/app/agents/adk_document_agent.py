from typing import List, Optional
import re

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from app.services.gemini_service import GeminiService
from app.utils.pdf_processor import clean_pdf_text, normalize_space

def extract_required_documents_from_text(pdf_text: str) -> List[str]:
    """Extract documents from PDF text - simplified robust version"""
    documents = []
    
    # Clean the text first
    cleaned = clean_pdf_text(pdf_text)
    
    # Try to find PART-G section
    start_markers = [
        r"PART[- ]G",
        r"LIST OF REQUIRED DOCUMENTS",
        r"Documents Required",
    ]
    
    section_start = None
    for marker in start_markers:
        match = re.search(marker, cleaned, re.IGNORECASE)
        if match:
            section_start = match.start()
            break
    
    if section_start is None:
        return []
    
    # Get text after the marker
    section_text = cleaned[section_start:section_start + 3000]
    
    # Find checkbox items
    patterns = [
        r'☐\s*(\d+\.\s*)?([^\n]+)',
        r'(\d+\.\s*)([^\n]+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, section_text)
        for match in matches:
            doc_name = match[-1].strip()
            doc_name = re.sub(r'^\d+\.\s*', '', doc_name)
            doc_name = re.sub(r'\s+', ' ', doc_name)
            doc_name = doc_name.strip()
            
            if doc_name and len(doc_name) > 3:
                garbage = ['candid', 'inform', 'bachelorofperform', 'schoolofperform', 
                          'closingdates', 'meritlist', 'paymentoffees', 'amonwards']
                if not any(g in doc_name.lower() for g in garbage):
                    if doc_name not in documents:
                        documents.append(doc_name)
    
    # If still no documents, try line-by-line
    if not documents:
        lines = section_text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 5 and len(line) < 50:
                if any(c in line for c in ['☐', '•', '-', '▪']):
                    doc = re.sub(r'[☐•\-▪]\s*', '', line)
                    doc = doc.strip()
                    if doc and len(doc) > 3:
                        documents.append(doc)
    
    return documents


class ADKDocumentAgent:
    def __init__(self):
        self.gemini = GeminiService()
        self.agent = self._create_agent()
        self.tool_func = self.agent.tools[0].func

    def _create_agent(self):
        def extract_scholarship_info(text: str) -> dict:
            # Extract documents using regex
            documents = extract_required_documents_from_text(text)

            prompt = f"""
Extract from this document. Return ONLY valid JSON.

Document text:
{text[:6000]}

Return format:
{{
    "document_type": "admission",
    "scholarship_name": "Program name from document header",
    "deadline": "Deadline from document",
    "mandatory_requirements": ["List of requirements"],
    "special_categories": ["List of special categories"],
    "alternative_admission_paths": ["List of alternative paths"],
    "important_instructions": ["List of instructions"]
}}
"""

            result = self.gemini.generate_structured_response(prompt)
            if not isinstance(result, dict):
                result = {}

            result["required_documents"] = documents
            return result

        return Agent(
            name="DocumentAnalysisAgent",
            model="gemini-2.5-flash",
            instruction="Extract information from documents. Never generate required_documents.",
            tools=[FunctionTool(extract_scholarship_info)],
        )