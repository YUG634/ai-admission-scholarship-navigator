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
            You are an expert document analyst. Extract EVERYTHING from this document.

            Document text:
            {text[:10000]}

            CRITICAL: Find the document list in this document. Look for:
            - "LIST OF REQUIRED DOCUMENTS"
            - "Documents Required"  
            - "Checklist"
            - Numbered lists with ☐ or • or -

            Extract EACH document individually. DO NOT summarize.

            For example, if you see:
            ☐ 1. 10th Marksheet
            ☐ 2. 12th Marksheet
            ☐ 3. 12th Leaving Certificate

            You MUST return:
            "required_documents": [
                "10th Marksheet",
                "12th Marksheet", 
                "12th Leaving Certificate"
            ]

            Return ONLY valid JSON:
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
                    "Extract EVERY document from the list",
                    "10th Marksheet",
                    "12th Marksheet",
                    "12th Leaving Certificate",
                    "Aadhaar Card Copy",
                    "Include ALL documents, even optional ones"
                ],
                "important_instructions": [
                    "Important application instructions"
                ]
            }}
            """
            return self.gemini.generate_structured_response(prompt)
        
        return Agent(
            name="DocumentAnalysisAgent",
            model="gemini-2.5-flash",
            instruction="""Extract ALL required documents from lists. NEVER summarize. Extract each document individually.
            If the document has a checkbox list with 14 items, return all 14 items as separate strings.""",
            tools=[FunctionTool(extract_scholarship_info)]
        )