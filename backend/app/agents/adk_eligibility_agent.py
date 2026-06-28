from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from app.services.gemini_service import GeminiService
import json

class ADKEligibilityAgent:
    def __init__(self):
        self.gemini = GeminiService()
        self.agent = self._create_agent()
        # Fix: Use 'func' instead of '_func'
        self.tool_func = self.agent.tools[0].func
    
    def _create_agent(self):
        def check_eligibility(profile_json: str, analysis_json: str) -> dict:
            prompt = f"""
            You are an eligibility checker. Compare the student profile against the requirements.

            CRITICAL RULES:
            1. NEVER treat special_categories as mandatory requirements
            2. If student meets all mandatory_requirements, they are ELIGIBLE
            3. If student meets mandatory_requirements but some information is missing, use PARTIALLY ELIGIBLE
            4. Only reject as NOT ELIGIBLE if mandatory_requirements are clearly not met

            STUDENT PROFILE:
            {profile_json}

            DOCUMENT ANALYSIS:
            {analysis_json}

            Special categories (like Sindhi Minority, In-house students) are OPTIONAL benefits.
            They should NEVER cause a student to be marked Not Eligible.

            If the student doesn't have entrance exam information, mark as Partially Eligible,
            NOT Not Eligible.

            Return ONLY valid JSON:
            {{
                "status": "Eligible" or "Partially Eligible" or "Not Eligible",
                "score": 0-100,
                "reasons": [
                    "Clear explanation of why student is eligible/partially/not eligible",
                    "List specific requirements met and not met"
                ],
                "matching_criteria": [
                    "List of mandatory requirements the student meets"
                ],
                "missing_criteria": [
                    "List of requirements the student doesn't meet or information missing"
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
            instruction="""You are an eligibility checker agent.
            Your primary responsibility is to compare student profiles against requirements.
            NEVER treat optional special categories as mandatory requirements.
            When in doubt, use Partially Eligible instead of Not Eligible.""",
            tools=[FunctionTool(check_eligibility)]
        )