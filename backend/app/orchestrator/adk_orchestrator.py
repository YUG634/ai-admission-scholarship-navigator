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
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # VALIDATION: Apply deterministic business rules
        elig_data = self._validate_eligibility(elig_data, analysis, profile)
        
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
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
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
        
        # Ensure all required fields exist
        if not elig_data:
            elig_data = {
                "status": "Not Eligible",
                "score": 0,
                "reasons": [],
                "matching_criteria": [],
                "missing_criteria": [],
                "mandatory_met": False,
                "special_category_eligible": False,
                "has_alternative_path": False
            }
        
        # Check if mandatory requirements are met
        mandatory_met = self._check_mandatory_requirements(analysis.mandatory_requirements, profile)
        
        # Check if student qualifies for any special category (OPTIONAL)
        special_eligible = self._check_special_categories(analysis.special_categories, profile)
        
        # Check if student has alternative admission paths
        has_alternative = len(analysis.alternative_admission_paths) > 0
        
        # BUSINESS RULES:
        # 1. If mandatory requirements are met -> status should NOT be "Not Eligible"
        # 2. If mandatory requirements met but some info missing -> "Partially Eligible"
        # 3. Special categories are ALWAYS optional and should never cause rejection
        
        current_status = elig_data.get("status", "Not Eligible")
        
        # Rule 1: Never reject if mandatory requirements are met
        if mandatory_met and current_status == "Not Eligible":
            print("⚠️ Fixed: Student meets mandatory requirements - changing status from 'Not Eligible'")
            current_status = "Partially Eligible" if len(elig_data.get("missing_criteria", [])) > 0 else "Eligible"
            elig_data["status"] = current_status
            
            # Add explanation to reasons
            if "Special categories are optional" not in str(elig_data.get("reasons", [])):
                elig_data["reasons"].append(
                    "You meet all mandatory requirements. Special categories are optional benefits, not requirements."
                )
        
        # Rule 2: If missing criteria are only special categories, don't penalize
        missing = elig_data.get("missing_criteria", [])
        special_related_missing = [
            m for m in missing 
            if any(keyword in m.lower() for keyword in ["minority", "in-house", "sindhi", "special category", "reserved"])
        ]
        
        if special_related_missing and mandatory_met:
            # Remove special category-related missing criteria from the list
            for item in special_related_missing:
                if item in missing:
                    missing.remove(item)
            elig_data["missing_criteria"] = missing
            
            # Update score if needed
            if elig_data.get("score", 0) < 60 and mandatory_met:
                elig_data["score"] = max(60, elig_data.get("score", 0) + 20)
        
        # Rule 3: If student has alternative paths, they are Partially Eligible at minimum
        if has_alternative and current_status == "Not Eligible" and not mandatory_met:
            print("⚠️ Fixed: Student has alternative admission paths - changing status to 'Partially Eligible'")
            elig_data["status"] = "Partially Eligible"
            elig_data["score"] = max(30, elig_data.get("score", 0))
            
            if "Alternative admission paths available" not in str(elig_data.get("reasons", [])):
                elig_data["reasons"].append(
                    "Alternative admission paths are available for this program. Please check the specific requirements."
                )
        
        # Update tracking fields
        elig_data["mandatory_met"] = mandatory_met
        elig_data["special_category_eligible"] = special_eligible
        elig_data["has_alternative_path"] = has_alternative
        
        return elig_data
    
    def _check_mandatory_requirements(self, requirements: list, profile: StudentProfile) -> bool:
        """Check if the student meets all mandatory requirements."""
        if not requirements:
            # No mandatory requirements means automatically eligible
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