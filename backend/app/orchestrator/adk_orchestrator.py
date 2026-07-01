import time
import json
from app.agents.adk_document_agent import ADKDocumentAgent
from app.agents.adk_eligibility_agent import ADKEligibilityAgent
from app.agents.adk_action_agent import ADKActionAgent
from app.models.schemas import StudentProfile, DocumentAnalysis, EligibilityResult, ActionPlan, AnalysisResponse

class ADKOrchestrator:
    def __init__(self):
        self.doc_agent = ADKDocumentAgent()
        self.eligibility_agent = ADKEligibilityAgent()
        self.action_agent = ADKActionAgent()
    
    async def process(self, pdf_text: str, profile: StudentProfile) -> AnalysisResponse:
        overall_start = time.time()
        
        print("=" * 60)
        print("🚀 Admission Eligibility Engine")
        print("=" * 60)
        print(f"📄 PDF Length: {len(pdf_text)} chars")
        print(f"👤 Student: {profile.full_name}")
        print("=" * 60)
        
        # Agent 1: Document Analysis
        print("\n🤖 Agent 1: Document Analysis")
        analysis_data = {}
        try:
            analysis_data = self.doc_agent.tool_func(pdf_text[:8000])
            print(f"✅ Found: {analysis_data.get('scholarship_name', 'Unknown')}")
            print(f"📎 Documents: {len(analysis_data.get('required_documents', []))} items")
        except Exception as e:
            print(f"❌ Error: {e}")
            analysis_data = {
                "document_type": "unknown",
                "scholarship_name": "Unknown",
                "deadline": "Not specified",
                "mandatory_requirements": [],
                "special_categories": [],
                "alternative_admission_paths": [],
                "required_documents": [],
                "important_instructions": []
            }
        
        analysis = DocumentAnalysis(**analysis_data)
        
        # Agent 2: Eligibility
        print("\n🤖 Agent 2: Eligibility Check")
        elig_data = {}
        try:
            elig_data = self.eligibility_agent.tool_func(
                json.dumps(profile.dict()),
                json.dumps(analysis.dict())
            )
            print(f"✅ Status: {elig_data.get('status', 'Unknown')}")
            print(f"📎 Missing Docs: {len(elig_data.get('missing_documents', []))} items")
        except Exception as e:
            print(f"❌ Error: {e}")
            elig_data = {
                "status": "Partially Eligible",
                "score": 50,
                "reasons": ["Eligibility check in progress."],
                "missing_documents": analysis.required_documents[:4] if analysis.required_documents else [],
                "mandatory_met": False
            }
        
        # ✅ Ensure missing_documents is populated
        if not elig_data.get("missing_documents") and analysis.required_documents:
            elig_data["missing_documents"] = analysis.required_documents[:4]
        
        eligibility = EligibilityResult(**elig_data)
        
        # Agent 3: Action Plan
        print("\n🤖 Agent 3: Action Plan")
        action_data = {}
        try:
            action_data = self.action_agent.tool_func(
                json.dumps(profile.dict()),
                json.dumps(analysis.dict()),
                json.dumps(eligibility.dict())
            )
            print(f"✅ Checklist: {len(action_data.get('checklist', []))} items")
        except Exception as e:
            print(f"❌ Error: {e}")
            action_data = {
                "immediate_actions": ["Complete online application"],
                "checklist": [
                    {"task": "Submit application", "priority": "High", "deadline": analysis.deadline if analysis.deadline else "ASAP"},
                    {"task": "Upload required documents", "priority": "High", "deadline": analysis.deadline if analysis.deadline else "ASAP"}
                ],
                "missing_documents": elig_data.get("missing_documents", []),
                "recommendations": ["Submit application before deadline"],
                "next_steps": ["Step 1: Complete application", "Step 2: Upload documents"],
                "timeline": {"week_1": "Complete application", "week_2": "Submit documents"}
            }
        
        action_plan = ActionPlan(**action_data) if action_data else ActionPlan()
        
        print("=" * 60)
        
        return AnalysisResponse(
            analysis=analysis,
            eligibility=eligibility,
            action_plan=action_plan,
            processing_time_ms=(time.time() - overall_start) * 1000
        )
    # DEBUG: Print first 2000 chars of PDF text to see what Gemini sees
print("📄 PDF PREVIEW:")
print(pdf_text[:2000])
print("=" * 60)