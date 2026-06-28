import json
import time
from app.services.gemini_service import GeminiService
from app.models.schemas import DocumentAnalysis

class DocumentAnalysisAgent:
    def __init__(self):
        self.name = "DocumentAnalysisAgent"
        self.gemini = GeminiService()
        self.last_trace = None
    
    async def process(self, text: str) -> DocumentAnalysis:
        start_time = time.time()
        
        try:
            prompt = f"""
            You are an expert document analyst for scholarship notifications.
            Analyze this document and extract structured information:

            {text[:8000]}

            Return ONLY valid JSON with these fields:
            {{
                "scholarship_name": "Full name of the scholarship",
                "deadline": "Application deadline",
                "eligibility_criteria": ["list", "of", "criteria"],
                "required_documents": ["list", "of", "documents"],
                "important_instructions": ["list", "of", "instructions"]
            }}
            """
            
            data = self.gemini.generate_structured_response(prompt)
            
            analysis = DocumentAnalysis(
                scholarship_name=data.get('scholarship_name', ''),
                deadline=data.get('deadline', ''),
                eligibility_criteria=data.get('eligibility_criteria', []),
                required_documents=data.get('required_documents', []),
                important_instructions=data.get('important_instructions', []),
                raw_text_preview=text[:500]
            )
            
            duration = (time.time() - start_time) * 1000
            self.last_trace = {
                "agent_name": self.name,
                "duration_ms": duration
            }
            
            return analysis
            
        except Exception as e:
            raise Exception(f"Document analysis failed: {str(e)}")