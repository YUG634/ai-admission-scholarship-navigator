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
            You are an expert document analyst. Analyze this document.

            Document text:
            {text[:8000]}

            Return ONLY valid JSON with these fields:
            {{
                "document_type": "admission",
                "scholarship_name": "First-Year Undergraduate Degree Programme 2025-2026 Admissions",
                "deadline": "Thursday, 05-June-2025, 6.00 pm",
                "mandatory_requirements": [
                    "Apply for First-Year Undergraduate Degree Programme",
                    "Fill the online admission form by deadline",
                    "Appear for Qualifying Entrance Exam",
                    "Online verification of documents",
                    "Payment of fees"
                ],
                "special_categories": [
                    "Sindhi Minority students",
                    "In-house students of HR and KC Colleges"
                ],
                "alternative_admission_paths": [
                    "M-HCET scores",
                    "H-CET entrance exam",
                    "H-LAT entrance exam",
                    "Direct Admission for Sindhi Minority",
                    "Direct Admission for In-house students",
                    "Direct Admission for specific programs"
                ],
                "required_documents": [
                    "10th Marksheet",
                    "12th Marksheet",
                    "12th Leaving Certificate",
                    "Aadhaar Card Copy",
                    "Transfer Certificate",
                    "Migration Certificate",
                    "APAAR ID",
                    "Caste/Sindhi Certificate",
                    "Disability Certificate",
                    "Entrance exam certificate",
                    "Gap Certificate",
                    "Cultural/Sports Certificate",
                    "Any other Certificate",
                    "Anti-Ragging Undertaking form of UGC"
                ],
                "important_instructions": [
                    "Apply online at https://hsncu.admissiondesk.org/",
                    "Phase 1: May 5 - May 24, 2025",
                    "Phase 2: May 27 - June 5, 2025",
                    "H-CET/H-LAT at http://hsncu.epravesh.com/",
                    "Merit lists start May 26, 2025"
                ]
            }}
            """
            return self.gemini.generate_structured_response(prompt)
        
        return Agent(
            name="DocumentAnalysisAgent",
            model="gemini-2.5-flash",
            instruction="Extract structured information from documents.",
            tools=[FunctionTool(extract_scholarship_info)]
        )