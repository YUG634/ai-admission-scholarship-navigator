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
            You are an eligibility evaluator. Determine eligibility based ONLY on extracted facts.

            STUDENT PROFILE:
            {profile_json}

            DOCUMENT ANALYSIS:
            {analysis_json}

            RULES:
            1. status = "Eligible" if ALL mandatory requirements are met
            2. status = "Partially Eligible" if mandatory requirements met but info missing
            3. status = "Not Eligible" ONLY if a mandatory requirement is clearly violated
            4. NEVER reject for: minority status, quota, special categories, missing documents
            5. Missing documents = PARTIALLY ELIGIBLE, NOT Not Eligible

            Return:
            {{
                "status": "Eligible" or "Partially Eligible" or "Not Eligible",
                "score": 0-100,
                "reasons": [
                    "Requirement met: X",
                    "Missing: Y"
                ],
                "matching_criteria": ["Criteria met"],
                "missing_criteria": ["Criteria missing"],
                "missing_documents": ["Documents to gather"],
                "mandatory_met": true/false,
                "special_category_eligible": true/false,
                "has_alternative_path": true/false
            }}
            """
            return self.gemini.generate_structured_response(prompt)
        
        return Agent(
            name="EligibilityAgent",
            model="gemini-2.5-flash",
            instruction="""Evaluate eligibility strictly. Never reject for optional categories. Missing info = Partially Eligible.""",
            tools=[FunctionTool(check_eligibility)]
        )