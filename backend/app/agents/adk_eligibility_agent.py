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
            1. **NEVER treat special_categories as mandatory requirements**
            2. **Only mandatory_requirements should cause rejection**
            3. **If mandatory requirements are met but information is missing → Partially Eligible**
            4. **Only use Not Eligible when mandatory requirements are clearly violated**

            For missing_documents:
            - Look at required_documents and compare with student profile
            - Only include documents that are actually required
            - For General category students, DO NOT include Caste Certificate

            Return ONLY valid JSON:
            {{
                "status": "Eligible" or "Partially Eligible" or "Not Eligible",
                "score": 0-100,
                "reasons": [
                    "Clear explanation of eligibility status"
                ],
                "matching_criteria": [
                    "Mandatory requirements the student meets"
                ],
                "missing_criteria": [
                    "Requirements not met or information missing"
                ],
                "missing_documents": [
                    "Documents the student needs to gather"
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
            instruction="""Compare student profiles against mandatory requirements only.
            NEVER treat special_categories as mandatory.
            Always include missing_documents, mandatory_met, special_category_eligible, and has_alternative_path.""",
            tools=[FunctionTool(check_eligibility)]
        )