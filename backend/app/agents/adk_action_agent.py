from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from app.services.gemini_service import GeminiService
import json

class ADKActionAgent:
    def __init__(self):
        self.gemini = GeminiService()
        self.agent = self._create_agent()
        self.tool_func = self.agent.tools[0].func
    
    def _create_agent(self):
        def generate_action_plan(profile_json: str, analysis_json: str, eligibility_json: str) -> dict:
            prompt = f"""
            You are a strategic advisor. Create a personalized action plan.

            STUDENT: {profile_json}
            DOCUMENT ANALYSIS: {analysis_json}
            ELIGIBILITY: {eligibility_json}

            CRITICAL RULES:
            1. Use the actual deadlines from the document
            2. Create checklist items based on the admission process
            3. Include tasks for gathering missing documents
            4. Use the eligibility status and reasons to guide recommendations

            Return ONLY valid JSON:
            {{
                "immediate_actions": [
                    "Most urgent actions first based on earliest deadlines"
                ],
                "checklist": [
                    {{"task": "Complete online application form", "priority": "High", "deadline": "June 5, 2025"}},
                    {{"task": "Register for entrance exam (H-CET/H-LAT)", "priority": "High", "deadline": "May 30, 2025"}},
                    {{"task": "Gather missing documents", "priority": "High", "deadline": "May 25, 2025"}},
                    {{"task": "Upload documents for verification", "priority": "High", "deadline": "June 5, 2025"}},
                    {{"task": "Check merit list on May 26, 2025", "priority": "High", "deadline": "May 26, 2025"}}
                ],
                "missing_documents": [
                    "10th Marksheet",
                    "12th Marksheet",
                    "Aadhaar Card Copy",
                    "Entrance exam certificate"
                ],
                "recommendations": [
                    "Apply early to avoid last-minute issues",
                    "Prepare for entrance exam",
                    "Keep scanned copies of all documents ready"
                ],
                "next_steps": [
                    "Step 1: Complete online application",
                    "Step 2: Register for entrance exam",
                    "Step 3: Gather all required documents",
                    "Step 4: Upload documents for verification"
                ],
                "timeline": {{
                    "week_1": "Complete application and gather documents",
                    "week_2": "Prepare for entrance exam",
                    "week_3": "Submit documents for verification",
                    "week_4": "Pay fees and confirm admission"
                }}
            }}
            """
            return self.gemini.generate_structured_response(prompt)
        
        return Agent(
            name="ActionPlanAgent",
            model="gemini-2.5-flash",
            instruction="""Create personalized action plans with specific deadlines.
            Every checklist item should have a priority and deadline.
            Include tasks for gathering missing documents identified by the eligibility agent.""",
            tools=[FunctionTool(generate_action_plan)]
        )