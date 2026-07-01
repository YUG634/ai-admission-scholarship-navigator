from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from app.services.gemini_service import GeminiService
import json
import re

class ADKDocumentAgent:
    def __init__(self):
        self.gemini = GeminiService()
        self.agent = self._create_agent()
        self.tool_func = self.agent.tools[0].func
    
    def _create_agent(self):
        def extract_scholarship_info(text: str) -> dict:
            # ✅ First, try to extract documents using regex (no API call)
            documents = self._extract_documents_from_text(text)
            
            # ✅ Build prompt with document extraction emphasis
            prompt = f"""
            You are a document extractor. Extract ALL information from this document.

            Document text:
            {text[:8000]}

            CRITICAL RULES FOR DOCUMENTS:
            1. Look for "LIST OF REQUIRED DOCUMENTS", "Documents Required", "Checklist"
            2. Extract EACH document as a SEPARATE string
            3. Example: If you see "☐ 1. 10th Marksheet", return "10th Marksheet"
            4. DO NOT summarize. DO NOT combine. Return each document individually.
            5. If you find documents in the text, include them ALL.

            Return ONLY valid JSON:
            {{
                "document_type": "admission",
                "scholarship_name": "Name from document",
                "deadline": "Deadline from document",
                "mandatory_requirements": [
                    "Each requirement as separate string"
                ],
                "special_categories": [
                    "Each category as separate string"
                ],
                "alternative_admission_paths": [
                    "Each path as separate string"
                ],
                "required_documents": [
                    "Document 1",
                    "Document 2",
                    "Document 3"
                ],
                "important_instructions": [
                    "Instruction 1",
                    "Instruction 2"
                ]
            }}
            """
            
            result = self.gemini.generate_structured_response(prompt)
            
            # ✅ If Gemini didn't extract documents, use regex extraction as fallback
            if not result.get("required_documents") or len(result.get("required_documents", [])) < 2:
                result["required_documents"] = documents
            
            return result
        
        return Agent(
            name="DocumentAnalysisAgent",
            model="gemini-2.5-flash",
            instruction="""Extract ALL documents individually. NEVER summarize. Each document must be a separate string.""",
            tools=[FunctionTool(extract_scholarship_info)]
        )
    
    def _extract_documents_from_text(self, text: str) -> list:
        """Extract documents using regex - reliable fallback"""
        documents = []
        
        # Look for document list section
        patterns = [
            r'(?:LIST OF REQUIRED DOCUMENTS|Documents Required|Checklist|Enclosures)[\s:]*([^\n]*(?:\n[^\n]+)*?)(?:\n\n|\Z)',
            r'(?:Required Documents|Documents to be attached)[\s:]*([^\n]*(?:\n[^\n]+)*?)(?:\n\n|\Z)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                section = match.group(1)
                # Extract numbered or bulleted items
                items = re.findall(r'(?:☐|•|-|\*|\d+[\.\)])\s*([^\n]+)', section)
                if items:
                    documents = [doc.strip() for doc in items if len(doc.strip()) > 5]
                    break
        
        # If no structured list found, look for document-like patterns
        if not documents:
            doc_patterns = [
                r'(\d+[\.\)]\s*)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*(?:Marksheet|Certificate|Card|Copy|Form|Letter|ID|Proof))',
                r'([A-Z][a-z]+\s+[A-Z][a-z]+\s+(?:Certificate|Card|Marksheet))',
            ]
            for pattern in doc_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    doc_name = match[-1] if isinstance(match, tuple) else match
                    if doc_name.strip() and len(doc_name.strip()) > 5:
                        documents.append(doc_name.strip())
                if documents:
                    break
        
        # Return unique documents
        return list(dict.fromkeys(documents))