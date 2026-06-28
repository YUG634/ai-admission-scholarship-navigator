import json
import time
from app.services.gemini_service import GeminiService
from app.models.schemas import StudentProfile, DocumentAnalysis, EligibilityResult

class EligibilityAgent:
    def __init__(self):
        self.name = "EligibilityAgent"
        self.gemini = GeminiService()
        self.last_trace = None
    
    async def process(self, profile: StudentProfile, analysis: DocumentAnalysis) -> EligibilityResult:
        start_time = time.time()
        
        try:
            prompt = f"""
            You are an eligibility checker for scholarships.
            Compare the student profile against the requirements.

            STUDENT PROFILE:
            {json.dumps(profile.dict(), indent=2)}

            SCHOLARSHIP REQUIREMENTS:
            {json.dumps(analysis.eligibility_criteria, indent=2)}

            Return ONLY valid JSON:
            {{
                "status": "Eligible" or "Not Eligible" or "Partially Eligible",
                "score": 0-100,
                "reasons": ["Reason 1", "Reason 2"],
                "matching_criteria": ["Criterion 1"],
                "missing_criteria": ["Criterion 2"]
            }}
            """
            
            data = self.gemini.generate_structured_response(prompt)
            
            result = EligibilityResult(
                status=data.get('status', 'Not Eligible'),
                score=data.get('score', 0),
                reasons=data.get('reasons', []),
                matching_criteria=data.get('matching_criteria', []),
                missing_criteria=data.get('missing_criteria', [])
            )
            
            duration = (time.time() - start_time) * 1000
            self.last_trace = {
                "agent_name": self.name,
                "duration_ms": duration
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Eligibility check failed: {str(e)}")