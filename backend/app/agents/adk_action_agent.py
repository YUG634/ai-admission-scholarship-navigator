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
            You are a strategic advisor. Create a personalized action plan based on the student's profile, document analysis, and eligibility results.

            STUDENT PROFILE:
            {profile_json}

            DOCUMENT ANALYSIS:
            {analysis_json}

            ELIGIBILITY RESULTS:
            {eligibility_json}

            CRITICAL RULES:
            1. Use ONLY information from the provided data - NO hardcoded dates, exams, or tasks
            2. The document analysis contains the actual deadlines - use them
            3. The eligibility results show what's missing - address those gaps
            4. Generate tasks that are SPECIFIC to this student and document

            Return ONLY valid JSON:
            {{
                "immediate_actions": [
                    "Most urgent actions based on document deadlines and student's situation"
                ],
                "checklist": [
                    {{"task": "Specific task based on document", "priority": "High", "deadline": "Date from document"}}
                ],
                "missing_documents": [
                    "Documents from eligibility results that the student needs"
                ],
                "recommendations": [
                    "Strategic advice based on student's eligibility status"
                ],
                "next_steps": [
                    "Step 1",
                    "Step 2",
                    "Step 3"
                ],
                "timeline": {{
                    "week_1": "Tasks for week 1 based on document dates",
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
            instruction="""Generate action plans dynamically from student profile, document analysis, and eligibility results.
            NEVER use hardcoded dates, exams, or tasks.
            Everything must come from the provided data.""",
            tools=[FunctionTool(generate_action_plan)]
        )