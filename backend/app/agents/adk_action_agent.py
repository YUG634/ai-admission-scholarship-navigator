from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from app.services.gemini_service import GeminiService
import json

class ADKActionAgent:
    def __init__(self):
        self.gemini = GeminiService()
        self.agent = self._create_agent()
        # Fix: Use 'func' instead of '_func'
        self.tool_func = self.agent.tools[0].func
    
    def _create_agent(self):
        def generate_action_plan(profile_json: str, analysis_json: str, eligibility_json: str) -> dict:
            prompt = f"""
            You are a strategic advisor. Create a personalized action plan.

            STUDENT: {profile_json}
            DOCUMENT ANALYSIS: {analysis_json}
            ELIGIBILITY: {eligibility_json}

            Consider:
            - Document type (scholarship vs admission)
            - If admission: focus on application steps and deadlines
            - If scholarship: focus on eligibility requirements and missing documents
            - Special categories mentioned are OPTIONAL, not mandatory

            Return ONLY valid JSON:
            {{
                "immediate_actions": [
                    "Most urgent actions first"
                ],
                "checklist": [
                    {{"task": "Task description", "priority": "High/Medium/Low", "deadline": "Date or timeframe"}}
                ],
                "missing_documents": [
                    "Documents to gather",
                    "Be specific about what's needed"
                ],
                "recommendations": [
                    "Strategic advice for successful application"
                ],
                "next_steps": [
                    "Step 1",
                    "Step 2",
                    "Step 3"
                ],
                "timeline": {{
                    "week_1": "Tasks for week 1",
                    "week_2": "Tasks for week 2",
                    "week_3": "Tasks for week 3",
                    "week_4": "Tasks for week 4"
                }}
            }}
            """
            return self.gemini.generate_structured_response(prompt)
        
        return Agent(
            name="ActionPlanAgent",
            model="gemini-2.5-flash",
            instruction="""You are an action plan generator agent.
            Create personalized, actionable plans.
            If this is an admission notification, focus on application process and deadlines.
            If this is a scholarship, focus on eligibility and document gathering.
            Always be encouraging and practical.""",
            tools=[FunctionTool(generate_action_plan)]
        )