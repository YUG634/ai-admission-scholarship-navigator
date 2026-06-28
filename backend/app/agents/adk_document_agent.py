from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from app.services.gemini_service import GeminiService
import json

class ADKDocumentAgent:
    def __init__(self):
        self.gemini = GeminiService()
        self.agent = self._create_agent()
        # Fix: Use 'func' instead of '_func'
        self.tool_func = self.agent.tools[0].func
    
    def _create_agent(self):
        def extract_scholarship_info(text: str) -> dict:
            prompt = f"""
            You are an expert document analyst. Analyze this document and classify it properly.

            CRITICAL CLASSIFICATION RULES:
            1. Determine if this is a SCHOLARSHIP notification or ADMISSION notification
            2. For ADMISSION notifications, eligibility is more flexible - special categories are OPTIONAL
            3. For SCHOLARSHIP notifications, eligibility criteria are usually MANDATORY

            Document text:
            {text[:8000]}

            Return ONLY valid JSON with this EXACT structure:
            {{
                "document_type": "scholarship" or "admission" or "unknown",
                "scholarship_name": "Full name of the program/scholarship",
                "deadline": "Application deadline",
                "mandatory_requirements": [
                    "Requirements that ALL applicants MUST meet",
                    "Example: Must have passed 12th standard",
                    "Example: Must have appeared for entrance exam"
                ],
                "special_categories": [
                    "OPTIONAL categories that provide benefits",
                    "Example: Sindhi Minority students",
                    "Example: In-house students of specific colleges",
                    "Example: SC/ST/OBC/EWS categories"
                ],
                "alternative_admission_paths": [
                    "Different ways to qualify",
                    "Example: MHCET scores",
                    "Example: H-CET exam",
                    "Example: National level entrance exams"
                ],
                "required_documents": [
                    "List of required documents",
                    "Example: 10th marksheet",
                    "Example: 12th marksheet",
                    "Example: Caste certificate"
                ],
                "important_instructions": [
                    "Important application instructions",
                    "Example: Apply online by deadline",
                    "Example: Document verification process"
                ]
            }}

            RULES FOR CLASSIFICATION:
            - For ADMISSION notifications: special_categories are OPTIONAL, not mandatory
            - For SCHOLARSHIP notifications: special_categories are usually MANDATORY
            - mandatory_requirements should only include things EVERY applicant needs
            - If you're unsure, put it in mandatory_requirements
            """
            return self.gemini.generate_structured_response(prompt)
        
        return Agent(
            name="DocumentAnalysisAgent",
            model="gemini-2.5-flash",
            instruction="""You are a specialized agent for analyzing scholarship and admission documents.
            Your primary responsibility is to extract structured information and properly classify documents.
            Always distinguish between MANDATORY requirements and OPTIONAL special categories.
            Never treat special categories as mandatory requirements unless explicitly stated.""",
            tools=[FunctionTool(extract_scholarship_info)]
        )