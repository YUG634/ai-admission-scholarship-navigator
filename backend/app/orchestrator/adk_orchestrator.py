import time
import json
import re  # ✅ Add this import
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
        
        # ✅ DEBUG: Print PDF preview to see what Gemini sees
        print("\n📄 PDF PREVIEW (first 2000 chars):")
        print("=" * 60)
        print(pdf_text[:2000])
        print("=" * 60)
        
        # Agent 1: Document Analysis
        print("\n🤖 Agent 1: Document Analysis")
        analysis_data = {}
        try:
            analysis_data = self.doc_agent.tool_func(pdf_text[:8000])
            print(f"✅ Found: {analysis_data.get('scholarship_name', 'Unknown')}")
            print(f"📎 Documents: {len(analysis_data.get('required_documents', []))} items")
            
            # ✅ If Gemini didn't extract documents properly, try regex fallback
            if not analysis_data.get("required_documents") or len(analysis_data.get("required_documents", [])) < 3:
                print("⚠️ Gemini extraction incomplete, using regex fallback...")
                extracted_docs = self._extract_documents_from_text(pdf_text)
                if extracted_docs:
                    analysis_data["required_documents"] = extracted_docs
                    print(f"📎 Regex extracted {len(extracted_docs)} documents")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            analysis_data = {
                "document_type": "unknown",
                "scholarship_name": "",
                "deadline": "",
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
    
    def _extract_documents_from_text(self, text: str) -> list:
        """Extract documents using regex - dynamic fallback"""
        documents = []
        
        # Look for document list section
        patterns = [
            r'(?:LIST OF REQUIRED DOCUMENTS|Documents Required|Checklist|Enclosures)[\s:]*([^\n]*(?:\n[^\n]+)*?)(?:\n\n|\Z)',
            r'(?:Required Documents|Documents to be attached)[\s:]*([^\n]*(?:\n[^\n]+)*?)(?:\n\n|\Z)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                section = match.group(1)
                # Extract numbered or bulleted items
                items = re.findall(r'(?:☐|•|-|\*|\d+[\.\)])\s*([^\n]+)', section)
                if items:
                    documents = [doc.strip() for doc in items if len(doc.strip()) > 5]
                    break
        
        # If no structured list found, look for document-like patterns
        if not documents:
            doc_patterns = [
                r'(\d+[\.\)]\s*)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*(?:Marksheet|Certificate|Card|Copy|Form|Letter|ID|Proof))',
                r'([A-Z][a-z]+\s+[A-Z][a-z]+\s+(?:Certificate|Card|Marksheet))',
            ]
            for pattern in doc_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    doc_name = match[-1] if isinstance(match, tuple) else match
                    if doc_name.strip() and len(doc_name.strip()) > 5:
                        documents.append(doc_name.strip())
                if documents:
                    break
        
        # Return unique documents
        return list(dict.fromkeys(documents))