from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from app.services.gemini_service import GeminiService
import json

class ADKDocumentAgent:
    def __init__(self):
        self.gemini = GeminiService()
        self.agent = self._create_agent()
        self.tool_func = self.agent.tools[0].func
    
    def _create_agent(self):
        def extract_scholarship_info(text: str) -> dict:
            prompt = f"""
            You are an expert document analyst. Analyze this document and classify it properly.

            Document text:
            {text[:8000]}

            CRITICAL: Look for sections like "List of Required Documents", "Documents Required", 
            "Checklist", or numbered/bulleted lists of documents. Extract each document individually.

            For checkbox lists (like ☐ 1. 10th Marksheet), extract each item separately.

            Return ONLY valid JSON with this EXACT structure:
            {{
                "document_type": "scholarship" or "admission" or "unknown",
                "scholarship_name": "Full name of the program/scholarship",
                "deadline": "Application deadline",
                "mandatory_requirements": [
                    "Requirements that ALL applicants MUST meet"
                ],
                "special_categories": [
                    "OPTIONAL categories that provide benefits"
                ],
                "alternative_admission_paths": [
                    "Different ways to qualify"
                ],
                "required_documents": [
                    "List each document separately with full name",
                    "Example: 10th Marksheet",
                    "Example: 12th Marksheet",
                    "Example: Aadhaar Card Copy"
                ],
                "important_instructions": [
                    "Important application instructions"
                ]
            }}

            RULES FOR EXTRACTING REQUIRED DOCUMENTS:
            1. Look for sections with titles like: "LIST OF REQUIRED DOCUMENTS", "Documents Required", "Checklist"
            2. Extract each document individually, including:
               - 10th Marksheet, 12th Marksheet
               - Leaving Certificate, Transfer Certificate, Migration Certificate
               - Aadhaar Card, ID Proof
               - Caste Certificate, Income Certificate, Domicile Certificate
               - Entrance Exam Certificate, Scorecards
               - Photographs, Signature
               - Any other specific documents mentioned
            3. For checkbox lists (☐, ✓, etc.), extract each item
            4. Include ALL documents mentioned in the document
            """
            return self.gemini.generate_structured_response(prompt)
        
        return Agent(
            name="DocumentAnalysisAgent",
            model="gemini-2.0-flash",
            instruction="""You are a specialized agent for analyzing scholarship and admission documents.
            Your primary responsibility is to extract structured information and properly classify documents.
            Always extract specific document names from lists, especially checkbox lists.
            Include ALL documents mentioned in the document.""",
            tools=[FunctionTool(extract_scholarship_info)]
        )