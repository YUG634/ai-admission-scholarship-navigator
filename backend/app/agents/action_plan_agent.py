import json
import time
from app.services.gemini_service import GeminiService
from app.models.schemas import StudentProfile, DocumentAnalysis, EligibilityResult, ActionPlan, ActionItem

class ActionPlanAgent:
    def __init__(self):
        self.name = "ActionPlanAgent"
        self.gemini = GeminiService()
        self.last_trace = None
    
    async def process(self, profile: StudentProfile, analysis: DocumentAnalysis, eligibility: EligibilityResult) -> ActionPlan:
        start_time = time.time()
        
        try:
            prompt = f"""
            You are a strategic advisor for scholarship applications.
            Create a personalized action plan.

            STUDENT: {json.dumps(profile.dict(), indent=2)}
            SCHOLARSHIP: {json.dumps(analysis.dict(), indent=2)}
            ELIGIBILITY: {json.dumps(eligibility.dict(), indent=2)}

            Return ONLY valid JSON:
            {{
                "immediate_actions": ["Action 1", "Action 2"],
                "checklist": [
                    {{"task": "Task description", "priority": "High", "deadline": "Date"}}
                ],
                "missing_documents": ["Document 1"],
                "recommendations": ["Recommendation 1"],
                "next_steps": ["Step 1", "Step 2"],
                "timeline": {{"week_1": "Tasks for week 1"}}
            }}
            """
            
            data = self.gemini.generate_structured_response(prompt)
            
            checklist = []
            for item in data.get('checklist', []):
                checklist.append(ActionItem(
                    task=item.get('task', ''),
                    priority=item.get('priority', 'Medium'),
                    deadline=item.get('deadline')
                ))
            
            plan = ActionPlan(
                immediate_actions=data.get('immediate_actions', []),
                checklist=checklist,
                missing_documents=data.get('missing_documents', []),
                recommendations=data.get('recommendations', []),
                next_steps=data.get('next_steps', []),
                timeline=data.get('timeline', {})
            )
            
            duration = (time.time() - start_time) * 1000
            self.last_trace = {
                "agent_name": self.name,
                "duration_ms": duration
            }
            
            return plan
            
        except Exception as e:
            raise Exception(f"Action plan generation failed: {str(e)}")