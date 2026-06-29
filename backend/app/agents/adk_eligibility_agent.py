from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from app.services.gemini_service import GeminiService
import json

class ADKEligibilityAgent:
    def __init__(self):
        self.gemini = GeminiService()
        self.agent = self._create_agent()
        self.tool_func = self.agent.tools[0].func
    
    def _create_agent(self):
        def check_eligibility(profile_json: str, analysis_json: str) -> dict:
            prompt = f"""
            You are an eligibility checker. Compare the student profile against the requirements.

            STUDENT PROFILE:
            {profile_json}

            DOCUMENT ANALYSIS:
            {analysis_json}

            CRITICAL RULES:
            1. NEVER treat special_categories as mandatory
            2. If student meets mandatory_requirements, they are ELIGIBLE
            3. If information is missing, use PARTIALLY ELIGIBLE

            For MISSING DOCUMENTS:
            - Look at the required_documents list from the analysis
            - Compare against the student's profile
            - Decide which documents the student needs to gather
            - If student is General category, don't include Caste Certificate
            - Include all basic documents (marksheets, ID, photographs, etc.)

            Return ONLY valid JSON:
            {{
                "status": "Eligible" or "Partially Eligible" or "Not Eligible",
                "score": 0-100,
                "reasons": [
                    "Clear explanation of why student is eligible/partially/not eligible"
                ],
                "matching_criteria": [
                    "List of mandatory requirements the student meets"
                ],
                "missing_criteria": [
                    "List of requirements the student doesn't meet or information missing"
                ],
                "missing_documents": [
                    "Documents the student needs to gather",
                    "Only include documents that are actually required"
                ],
                "mandatory_met": true/false,
                "special_category_eligible": true/false,
                "has_alternative_path": true/false
            }}
            """
            return self.gemini.generate_structured_response(prompt)
        
        return Agent(
            name="EligibilityAgent",
            model="gemini-2.5-flash",
            instruction="""Compare student profiles against requirements and identify missing documents.
            Only include documents that are actually required based on the student's profile.
            For a General category student, DO NOT include Caste Certificate in missing documents.""",
            tools=[FunctionTool(check_eligibility)]
        )