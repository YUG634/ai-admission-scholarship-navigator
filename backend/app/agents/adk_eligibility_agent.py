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
            1. NEVER treat special_categories as mandatory requirements
            2. If student meets all mandatory_requirements, they are ELIGIBLE
            3. If student meets mandatory_requirements but some information is missing, use PARTIALLY ELIGIBLE
            4. Only reject as NOT ELIGIBLE if mandatory_requirements are clearly not met

            Return ONLY valid JSON:
            {{
                "status": "Partially Eligible",
                "score": 25,
                "reasons": [
                    "Student meets academic requirements",
                    "Entrance exam information missing"
                ],
                "matching_criteria": [
                    "Class 12 pass requirement met"
                ],
                "missing_criteria": [
                    "Entrance exam information not provided"
                ],
                "missing_documents": [
                    "10th Marksheet",
                    "12th Marksheet",
                    "Aadhaar Card Copy",
                    "Entrance exam certificate"
                ],
                "mandatory_met": true,
                "special_category_eligible": false,
                "has_alternative_path": true
            }}
            """
            return self.gemini.generate_structured_response(prompt)
        
        return Agent(
            name="EligibilityAgent",
            model="gemini-2.5-flash",
            instruction="""Compare student profiles against requirements.
            ALWAYS include missing_documents field in your response.
            For General category students, DO NOT include Caste Certificate.
            Always include basic documents: 10th Marksheet, 12th Marksheet, Aadhaar Card.""",
            tools=[FunctionTool(check_eligibility)]
        )