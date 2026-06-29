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

            Return ONLY valid JSON:
            {{
                "status": "Partially Eligible",
                "score": 25,
                "reasons": [
                    "Student meets academic requirements",
                    "Entrance exam information missing"
                ],
                "matching_criteria": [],
                "missing_criteria": [],
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
            model="gemini-2.5-flash",  # ✅ Changed
            instruction="Check eligibility and identify missing documents.",
            tools=[FunctionTool(check_eligibility)]
        )