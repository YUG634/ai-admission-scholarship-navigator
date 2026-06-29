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
            You are an expert document analyst. Analyze this document and extract structured information.

            Document text:
            {text[:10000]}

            CRITICAL: Classify EVERY piece of information into the correct category:

            1. **mandatory_requirements**: Requirements that ALL applicants MUST meet.
               - Examples: "Must have passed 12th standard", "Must be an Indian citizen", "Must have appeared for entrance exam"
               - These are NOT optional - every applicant needs these

            2. **special_categories**: OPTIONAL categories that provide benefits or special consideration.
               - Examples: "Sindhi Minority students", "In-house students", "SC/ST/OBC/EWS categories"
               - These are benefits, NOT requirements

            3. **alternative_admission_paths**: Different ways to qualify for admission.
               - Examples: "MHCET scores", "H-CET exam", "National level entrance exams", "Direct admission"

            4. **required_documents**: Documents needed for application.
               - Examples: "10th Marksheet", "12th Marksheet", "Aadhaar Card", "Caste Certificate"
               - Extract each document separately

            5. **important_instructions**: Key application instructions.
               - Examples: "Apply online by deadline", "Document verification required"

            Return ONLY valid JSON:
            {{
                "document_type": "scholarship" or "admission" or "unknown",
                "scholarship_name": "Full name of the program/scholarship",
                "deadline": "Application deadline",
                "mandatory_requirements": [
                    "Requirement 1",
                    "Requirement 2"
                ],
                "special_categories": [
                    "Category 1",
                    "Category 2"
                ],
                "alternative_admission_paths": [
                    "Path 1",
                    "Path 2"
                ],
                "required_documents": [
                    "Document 1",
                    "Document 2"
                ],
                "important_instructions": [
                    "Instruction 1",
                    "Instruction 2"
                ]
            }}
            """
            return self.gemini.generate_structured_response(prompt)
        
        return Agent(
            name="DocumentAnalysisAgent",
            model="gemini-2.5-flash",
            instruction="""Extract structured information and classify it into mandatory_requirements, special_categories, alternative_admission_paths, required_documents, and important_instructions.
            NEVER mix these categories. special_categories are OPTIONAL, not mandatory.""",
            tools=[FunctionTool(extract_scholarship_info)]
        )