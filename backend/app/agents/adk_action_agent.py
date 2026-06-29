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

            Return ONLY valid JSON:
            {{
                "immediate_actions": [
                    "Complete online application by June 5, 2025",
                    "Register for entrance exam"
                ],
                "checklist": [
                    {{"task": "Submit online application", "priority": "High", "deadline": "June 5, 2025"}},
                    {{"task": "Register for H-CET/H-LAT", "priority": "High", "deadline": "May 30, 2025"}},
                    {{"task": "Gather required documents", "priority": "High", "deadline": "May 25, 2025"}},
                    {{"task": "Upload documents for verification", "priority": "High", "deadline": "June 5, 2025"}},
                    {{"task": "Check merit list", "priority": "High", "deadline": "May 26, 2025"}}
                ],
                "missing_documents": [
                    "10th Marksheet",
                    "12th Marksheet",
                    "Aadhaar Card Copy",
                    "Entrance exam certificate"
                ],
                "recommendations": [
                    "Apply early to avoid last-minute issues",
                    "Prepare thoroughly for entrance exam",
                    "Keep documents ready for verification",
                    "Monitor merit list announcements"
                ],
                "next_steps": [
                    "Step 1: Complete online application",
                    "Step 2: Register for entrance exam",
                    "Step 3: Gather all required documents",
                    "Step 4: Upload documents for verification",
                    "Step 5: Pay fees and confirm admission"
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
            Every checklist item must have task, priority, and deadline.
            Include immediate_actions, checklist, missing_documents, recommendations, next_steps, and timeline.""",
            tools=[FunctionTool(generate_action_plan)]
        )