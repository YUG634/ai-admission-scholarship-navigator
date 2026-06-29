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
            2. Create checklist items for each step in the admission process
            3. Include tasks for gathering missing documents
            4. Use the eligibility status and reasons to guide recommendations

            Return ONLY valid JSON:
            {{
                "immediate_actions": [
                    "Most urgent actions first based on earliest deadlines"
                ],
                "checklist": [
                    {{"task": "Task description", "priority": "High/Medium/Low", "deadline": "Actual date from document"}}
                ],
                "missing_documents": [
                    "Documents the student needs to gather"
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
            instruction="""Create action plans using the actual deadlines from the document.
            Every checklist item should have a specific deadline from the document.
            Include tasks for gathering missing documents identified by the eligibility agent.""",
            tools=[FunctionTool(generate_action_plan)]
        )