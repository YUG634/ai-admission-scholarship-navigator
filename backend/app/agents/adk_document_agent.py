# backend/app/agents/adk_document_agent.py

from typing import List, Optional
import re

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from app.services.gemini_service import GeminiService
from app.utils.pdf_processor import clean_pdf_text, normalize_space


def extract_required_documents_from_text(pdf_text: str) -> List[str]:
    """Extract documents from PDF text - enhanced for PART-G extraction"""
    documents = []
    
    # Clean the text first
    cleaned = clean_pdf_text(pdf_text)
    
    # ============================================================
    # Method 1: Look for PART-G section specifically
    # ============================================================
    part_g_pattern = r'PART-G[:\s]*LIST OF REQUIRED DOCUMENTS[:\s]*([\s\S]*?)(?=PART-|Kindly note|Students Help Desk|\Z)'
    part_g_match = re.search(part_g_pattern, cleaned, re.IGNORECASE)
    
    if part_g_match:
        section_text = part_g_match.group(1)
        
        # Extract numbered items (1. Document Name)
        doc_pattern = r'(\d+)\.\s*([^□\n]+?)(?:\s*□|\s*\(If applicable\)|\s*\(if applicable\)|\s*$|\.|\,|\s*-)'
        matches = re.findall(doc_pattern, section_text)
        
        for _, doc_name in matches:
            clean_name = doc_name.strip()
            clean_name = re.sub(r'\s+', ' ', clean_name)
            clean_name = re.sub(r'^[•·●○◆◇▪▫]\s*', '', clean_name)
            clean_name = re.sub(r'\s*[□✓☐]\s*$', '', clean_name)
            
            if clean_name and len(clean_name) > 3 and clean_name not in documents:
                documents.append(clean_name)
        
        # If numbered items found, return them
        if documents:
            return documents
    
    # ============================================================
    # Method 2: Look for document patterns in the full text
    # ============================================================
    doc_patterns = [
        # Pattern for numbered documents
        r'(\d+\.\s*([^\n]+?)(?:\s*\([^)]*\))?\s*(?:□|$))',
        # Pattern for checkbox items
        r'(?:☐|✓|•|-|\*)\s*([^\n]+)',
        # Pattern for common document types
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*(?:Marksheet|Certificate|Card|Copy|Form|Letter|ID|Proof|Report|Undertaking))',
        # Pattern for certificate types
        r'(Migration|Transfer|Conduct|Caste|Income|Domicile|Character|Disability|Gap|Cultural|Sports)\s+(?:Certificate)',
    ]
    
    for pattern in doc_patterns:
        matches = re.findall(pattern, cleaned, re.IGNORECASE)
        for match in matches:
            doc_name = match if isinstance(match, str) else match[-1] if isinstance(match, tuple) else str(match)
            clean_name = doc_name.strip()
            clean_name = re.sub(r'^\d+\.\s*', '', clean_name)
            clean_name = re.sub(r'\s*\([^)]*\)\s*$', '', clean_name)
            clean_name = re.sub(r'\s*[□✓☐]\s*$', '', clean_name)
            clean_name = re.sub(r'^[•·●○◆◇▪▫]\s*', '', clean_name)
            
            # Filter out garbage
            garbage = ['candid', 'inform', 'bachelorofperform', 'schoolofperform', 
                      'closingdates', 'meritlist', 'paymentoffees', 'amonwards',
                      'online verification', 'confirmation', 'admission', 'payment']
            if clean_name and len(clean_name) > 3:
                if not any(g in clean_name.lower() for g in garbage):
                    if clean_name not in documents:
                        documents.append(clean_name)
        
        if documents:
            break
    
    # ============================================================
    # Method 3: Look for specific document keywords
    # ============================================================
    if not documents:
        doc_keywords = [
            'Marksheet', 'Certificate', 'Card', 'Copy', 'Form', 'Letter', 
            'ID', 'Proof', 'Report', 'Undertaking', 'Migration', 'Transfer',
            'Conduct', 'Caste', 'Income', 'Domicile', 'Character', 'Disability',
            'Gap', 'Cultural', 'Sports', 'APAAR', 'Aadhaar', 'Leaving',
            'Anti-Ragging'
        ]
        
        for keyword in doc_keywords:
            pattern = rf'([^\n]*{keyword}[^\n]*(?:\s*\([^)]*\))?)'
            matches = re.findall(pattern, cleaned, re.IGNORECASE)
            for match in matches:
                clean_name = match.strip()
                clean_name = re.sub(r'^\d+\.\s*', '', clean_name)
                clean_name = re.sub(r'\s*[□✓☐]\s*$', '', clean_name)
                clean_name = re.sub(r'^[•·●○◆◇▪▫]\s*', '', clean_name)
                clean_name = re.sub(r'\s+', ' ', clean_name)
                
                if clean_name and len(clean_name) > 3 and clean_name not in documents:
                    documents.append(clean_name)
    
    # ============================================================
    # Method 4: If still no documents, check for "Required Documents" section
    # ============================================================
    if not documents:
        doc_section_pattern = r'(?:Required Documents|Documents Required|List of Documents)[:\s]*([\s\S]*?)(?=\n\n|\Z)'
        doc_section_match = re.search(doc_section_pattern, cleaned, re.IGNORECASE)
        
        if doc_section_match:
            section = doc_section_match.group(1)
            lines = section.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 5 and len(line) < 60:
                    if re.match(r'^[\d•\-*]+', line) or '☐' in line or '✓' in line:
                        clean_name = re.sub(r'^[\d•\-*]+\s*', '', line)
                        clean_name = re.sub(r'\s*[□✓☐]\s*$', '', clean_name)
                        clean_name = clean_name.strip()
                        if clean_name and len(clean_name) > 3 and clean_name not in documents:
                            documents.append(clean_name)
    
    # Limit to 20 documents and remove duplicates
    return list(dict.fromkeys(documents))[:20]


class ADKDocumentAgent:
    def __init__(self):
        self.gemini = GeminiService()
        self.agent = self._create_agent()
        self.tool_func = self.agent.tools[0].func

    def _create_agent(self):
        def extract_scholarship_info(text: str) -> dict:
            # Extract documents using enhanced regex
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

            # Use the extracted documents
            result["required_documents"] = documents
            return result

        return Agent(
            name="DocumentAnalysisAgent",
            model="gemini-2.5-flash",
            instruction="Extract information from documents. Never generate required_documents.",
            tools=[FunctionTool(extract_scholarship_info)],
        )