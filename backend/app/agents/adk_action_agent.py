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
            You are an action planner. Generate specific, actionable tasks.

            STUDENT: {profile_json}
            DOCUMENT: {analysis_json}
            ELIGIBILITY: {eligibility_json}

            RULES:
            1. Each task must be specific and actionable
            2. Each task must trace to a missing requirement or document
            3. Use deadlines from the document
            4. NO generic advice like "Research", "Work hard", "Explore options"

            BAD: "Research opportunities"  → GOOD: "Apply for B.Sc. Web Technologies by June 5"
            BAD: "Prepare for exam"       → GOOD: "Register for H-CET via http://hsncu.epravesh.com/"

            Return:
            {{
                "immediate_actions": ["Specific action 1", "Specific action 2"],
                "checklist": [
                    {{"task": "Specific action", "priority": "High", "deadline": "Date from document"}}
                ],
                "missing_documents": ["Document 1", "Document 2"],
                "recommendations": ["Actionable recommendation 1"],
                "next_steps": ["Step 1", "Step 2"],
                "timeline": {{"week_1": "Tasks", "week_2": "Tasks"}}
            }}
            """
            return self.gemini.generate_structured_response(prompt)
        
        return Agent(
            name="ActionPlanAgent",
            model="gemini-2.5-flash",
            instruction="""Generate specific, actionable tasks only. No generic advice. Every task must trace to a missing requirement.""",
            tools=[FunctionTool(generate_action_plan)]
        )