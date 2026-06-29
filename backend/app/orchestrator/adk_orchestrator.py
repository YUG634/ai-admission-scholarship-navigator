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
        print("🚀 Google ADK Multi-Agent Pipeline")
        print("=" * 60)
        print(f"📄 PDF Length: {len(pdf_text)} chars")
        print(f"👤 Student: {profile.full_name}")
        print("=" * 60)
        
        # Agent 1: Document Analysis
        print("\n🤖 Agent 1: Document Analysis (ADK)")
        analysis_data = {}
        try:
            analysis_data = self.doc_agent.tool_func(pdf_text[:8000])
            print(f"✅ Document Type: {analysis_data.get('document_type', 'unknown')}")
            print(f"✅ Found: {analysis_data.get('scholarship_name', 'Unknown')}")
            print(f"📋 Mandatory: {len(analysis_data.get('mandatory_requirements', []))} items")
            print(f"⭐ Special Categories: {len(analysis_data.get('special_categories', []))} items")
            print(f"🔄 Alternative Paths: {len(analysis_data.get('alternative_admission_paths', []))} items")
            print(f"📎 Documents: {len(analysis_data.get('required_documents', []))} items")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        analysis = DocumentAnalysis(**analysis_data)
        
        # Agent 2: Eligibility
        print("\n🤖 Agent 2: Eligibility Check (ADK)")
        elig_data = {}
        try:
            elig_data = self.eligibility_agent.tool_func(
                json.dumps(profile.dict()),
                json.dumps(analysis.dict())
            )
            print(f"✅ Status: {elig_data.get('status', 'Unknown')}")
            print(f"📊 Score: {elig_data.get('score', 0)}%")
            print(f"📎 Missing Docs: {len(elig_data.get('missing_documents', []))} items")
            print(f"✅ Mandatory Met: {elig_data.get('mandatory_met', False)}")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # VALIDATION: Apply deterministic business rules
        elig_data = self._validate_eligibility(elig_data, analysis, profile)
        
        # ✅ Ensure all fields exist
        if "missing_documents" not in elig_data:
            elig_data["missing_documents"] = []
        if "mandatory_met" not in elig_data:
            elig_data["mandatory_met"] = False
        if "special_category_eligible" not in elig_data:
            elig_data["special_category_eligible"] = False
        if "has_alternative_path" not in elig_data:
            elig_data["has_alternative_path"] = len(analysis.alternative_admission_paths) > 0
        
        eligibility = EligibilityResult(**elig_data)
        
        # Agent 3: Action Plan
        print("\n🤖 Agent 3: Action Plan (ADK)")
        action_data = {}
        try:
            action_data = self.action_agent.tool_func(
                json.dumps(profile.dict()),
                json.dumps(analysis.dict()),
                json.dumps(eligibility.dict())
            )
            print(f"✅ Action plan generated")
            print(f"📋 Checklist: {len(action_data.get('checklist', []))} items")
            print(f"📎 Missing: {len(action_data.get('missing_documents', []))} items")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # ✅ Ensure action_plan always has required fields
        if not action_data:
            action_data = {
                "immediate_actions": [],
                "checklist": [],
                "missing_documents": elig_data.get("missing_documents", []),
                "recommendations": [],
                "next_steps": [],
                "timeline": {}
            }
        
        action_plan = ActionPlan(**action_data) if action_data else ActionPlan()
        
        print("=" * 60)
        
        return AnalysisResponse(
            analysis=analysis,
            eligibility=eligibility,
            action_plan=action_plan,
            processing_time_ms=(time.time() - overall_start) * 1000
        )
    
    def _validate_eligibility(self, elig_data: dict, analysis: DocumentAnalysis, profile: StudentProfile) -> dict:
        """Apply deterministic business rules to validate and correct eligibility decisions."""
        
        # ✅ Initialize with defaults
        default_data = {
            "status": "Not Eligible",
            "score": 0,
            "reasons": [],
            "matching_criteria": [],
            "missing_criteria": [],
            "missing_documents": [],
            "mandatory_met": False,
            "special_category_eligible": False,
            "has_alternative_path": False
        }
        
        if not elig_data:
            elig_data = default_data.copy()
        
        # ✅ Check mandatory requirements
        mandatory_met = self._check_mandatory_requirements(analysis.mandatory_requirements, profile)
        special_eligible = self._check_special_categories(analysis.special_categories, profile)
        has_alternative = len(analysis.alternative_admission_paths) > 0
        
        current_status = elig_data.get("status", "Not Eligible")
        missing_criteria = elig_data.get("missing_criteria", [])
        
        # ✅ Rule 1: NEVER treat special categories as mandatory
        # Remove any special category-related missing criteria
        special_related = [
            "minority", "in-house", "sindhi", "special category", "reserved"
        ]
        filtered_missing = [
            m for m in missing_criteria 
            if not any(keyword in m.lower() for keyword in special_related)
        ]
        elig_data["missing_criteria"] = filtered_missing
        
        # ✅ Rule 2: If mandatory requirements are met, status should NOT be "Not Eligible"
        if mandatory_met and current_status == "Not Eligible":
            print("⚠️ Fixed: Student meets mandatory requirements - changing status")
            current_status = "Partially Eligible" if filtered_missing else "Eligible"
            elig_data["status"] = current_status
            if "Special categories are optional" not in str(elig_data.get("reasons", [])):
                elig_data["reasons"].append(
                    "You meet all mandatory requirements. Special categories are optional benefits, not requirements."
                )
        
        # ✅ Rule 3: If mandatory requirements met but info missing → Partially Eligible
        if mandatory_met and filtered_missing and current_status == "Eligible":
            print("⚠️ Fixed: Student meets mandatory requirements but info missing - changing to Partially Eligible")
            elig_data["status"] = "Partially Eligible"
        
        # ✅ Rule 4: Alternative paths should IMPROVE eligibility, not reduce it
        if has_alternative and current_status == "Not Eligible" and not mandatory_met:
            print("⚠️ Fixed: Student has alternative admission paths - improving status")
            elig_data["status"] = "Partially Eligible"
            elig_data["score"] = max(30, elig_data.get("score", 0))
            if "Alternative admission paths available" not in str(elig_data.get("reasons", [])):
                elig_data["reasons"].append(
                    "Alternative admission paths are available for this program."
                )
        
        # ✅ Rule 5: Only "Not Eligible" when mandatory requirements are clearly violated
        # This is already handled by the logic above
        
        # ✅ Ensure all fields are present
        if "missing_documents" not in elig_data:
            elig_data["missing_documents"] = []
        if "mandatory_met" not in elig_data:
            elig_data["mandatory_met"] = mandatory_met
        if "special_category_eligible" not in elig_data:
            elig_data["special_category_eligible"] = special_eligible
        if "has_alternative_path" not in elig_data:
            elig_data["has_alternative_path"] = has_alternative
        
        return elig_data
    
    def _check_mandatory_requirements(self, requirements: list, profile: StudentProfile) -> bool:
        """Check if the student meets all mandatory requirements."""
        if not requirements:
            return True
        
        met_count = 0
        total = len(requirements)
        
        for req in requirements:
            req_lower = req.lower()
            
            # Check qualification
            if "12th" in req_lower or "class 12" in req_lower or "higher secondary" in req_lower:
                if "12" in profile.current_qualification or "higher secondary" in profile.current_qualification.lower():
                    met_count += 1
                continue
            
            # Check marks/percentage
            if "percentage" in req_lower or "marks" in req_lower or "cgpa" in req_lower:
                import re
                percentages = re.findall(r'(\d+)\s*%', req)
                if percentages:
                    required_pct = float(percentages[0])
                    if profile.marks_percentage >= required_pct:
                        met_count += 1
                continue
            
            # Check income
            if "income" in req_lower or "family income" in req_lower:
                import re
                incomes = re.findall(r'[\d,]+', req)
                if incomes:
                    max_income = float(incomes[0].replace(',', ''))
                    if profile.family_income <= max_income:
                        met_count += 1
                continue
            
            # Check category
            if "category" in req_lower or "caste" in req_lower:
                if profile.category.value.lower() in req_lower or req_lower in profile.category.value.lower():
                    met_count += 1
                continue
            
            # Check state/domicile
            if "state" in req_lower or "domicile" in req_lower:
                if profile.state.lower() in req_lower or req_lower in profile.state.lower():
                    met_count += 1
                continue
            
            # Check entrance exam - don't count as failed if missing
            if "entrance" in req_lower or "exam" in req_lower or "test" in req_lower:
                met_count += 0.5
                continue
            
            # Default: assume student meets requirement
            met_count += 1
        
        # Calculate percentage of mandatory requirements met
        met_percentage = met_count / total if total > 0 else 1.0
        
        # Consider mandatory requirements met if at least 70% are satisfied
        return met_percentage >= 0.7
    
    def _check_special_categories(self, categories: list, profile: StudentProfile) -> bool:
        """Check if the student qualifies for any special category."""
        if not categories:
            return False
        
        for cat in categories:
            cat_lower = cat.lower()
            
            if "minority" in cat_lower:
                if "minority" in profile.category.value.lower():
                    return True
            if "in-house" in cat_lower:
                return False
            if "reserved" in cat_lower or "quota" in cat_lower:
                if profile.category.value.lower() in cat_lower:
                    return True
            if "sindhi" in cat_lower:
                return False
            
            if any(keyword in cat_lower for keyword in [profile.category.value.lower(), profile.state.lower()]):
                return True
        
        return False