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

            IMPORTANT: Identify which documents the student needs to gather based on their profile:
            - If student is General category, DO NOT include Caste Certificate in missing documents
            - All students need: 10th Marksheet, 12th Marksheet, Aadhaar Card, Photographs
            - If no entrance exam info, include "Entrance exam certificate" in missing documents

            Return ONLY valid JSON:
            {{
                "status": "Partially Eligible",
                "score": 25,
                "reasons": [
                    "Clear explanation of why student is partially eligible",
                    "List specific requirements met and not met"
                ],
                "matching_criteria": [
                    "List of mandatory requirements the student meets"
                ],
                "missing_criteria": [
                    "List of requirements the student doesn't meet or information missing"
                ],
                "missing_documents": [
                    "Documents the student needs to gather based on their profile",
                    "Only include documents that are actually required for this student"
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
            instruction="""You compare student profiles against requirements and identify missing documents.
            NEVER treat optional special categories as mandatory requirements.
            Only include documents that are actually required based on the student's profile.
            For a General category student, DO NOT include Caste Certificate in missing documents.
            Always include basic documents like 10th Marksheet, 12th Marksheet, Aadhaar Card if they are required.""",
            tools=[FunctionTool(check_eligibility)]
        )