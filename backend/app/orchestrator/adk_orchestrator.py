import time
import json
import re
import logging
from typing import Dict, Any, Optional

from app.agents.adk_document_agent import ADKDocumentAgent
from app.agents.adk_eligibility_agent import ADKEligibilityAgent
from app.agents.adk_action_agent import ADKActionAgent
from app.models.schemas import (
    StudentProfile, DocumentAnalysis, DocumentType,
    EligibilityResult, ActionPlan, AnalysisResponse,
    ComparisonResult
)

logger = logging.getLogger(__name__)


class ADKOrchestrator:
    def __init__(self):
        self.doc_agent = ADKDocumentAgent()
        self.eligibility_agent = ADKEligibilityAgent()
        self.action_agent = ADKActionAgent()
    
    async def process(self, pdf_text: str, profile: StudentProfile) -> AnalysisResponse:
        """Primary processing method with fallbacks"""
        overall_start = time.time()
        
        logger.info("=" * 60)
        logger.info("🎓 Education Navigator - Multi-Agent System")
        logger.info("=" * 60)
        logger.info(f"📄 PDF Length: {len(pdf_text)} chars")
        logger.info(f"👤 Student: {profile.full_name}")
        
        # Agent 1: Document Analysis with fallback
        logger.info("\n🤖 Agent 1: Document Analysis")
        analysis_data = await self._safe_document_analysis(pdf_text)
        
        # Detect document type
        doc_type = self._detect_document_type(pdf_text, analysis_data)
        analysis_data["document_type"] = doc_type
        
        analysis = DocumentAnalysis(**analysis_data)
        logger.info(f"✅ Document Type: {doc_type}")
        logger.info(f"📎 Documents: {len(analysis.required_documents)} items")
        
        # Agent 2: Eligibility with fallback
        logger.info("\n🤖 Agent 2: Eligibility Check")
        elig_data = await self._safe_eligibility_check(profile, analysis)
        eligibility = EligibilityResult(**elig_data)
        logger.info(f"✅ Status: {eligibility.status}")
        
        # Agent 3: Action Plan with fallback
        logger.info("\n🤖 Agent 3: Action Plan")
        action_data = await self._safe_action_plan(profile, analysis, eligibility)
        action_plan = ActionPlan(**action_data) if action_data else ActionPlan()
        logger.info(f"✅ Checklist: {len(action_plan.checklist)} items")
        
        # Generate comparison
        comparison = self._generate_comparison(profile, analysis, eligibility)
        
        # Generate message
        message = self._generate_message(doc_type, eligibility.status)
        
        logger.info("=" * 60)
        
        return AnalysisResponse(
            analysis=analysis,
            eligibility=eligibility,
            action_plan=action_plan,
            document_type=doc_type,
            comparison=comparison,
            processing_time_ms=(time.time() - overall_start) * 1000,
            message=message
        )
    
    async def _safe_document_analysis(self, pdf_text: str) -> Dict[str, Any]:
        """Safe document analysis with fallback"""
        try:
            result = self.doc_agent.tool_func(pdf_text[:8000])
            if result and isinstance(result, dict):
                return result
        except Exception as e:
            logger.error(f"❌ Document Analysis failed: {e}")
        
        # Fallback: Extract using regex
        logger.warning("⚠️ Using regex fallback for document analysis")
        return {
            "document_type": "unknown",
            "document_name": "Extracted Document",
            "organization": self._extract_organization_from_text(pdf_text),
            "deadline": self._extract_deadline_from_text(pdf_text),
            "required_documents": self._extract_documents_from_text(pdf_text),
            "mandatory_requirements": [],
            "special_categories": [],
            "alternative_admission_paths": [],
            "important_instructions": [],
            "important_dates": self._extract_important_dates(pdf_text),
            "contact_info": {}
        }
    
    async def _safe_eligibility_check(self, profile: StudentProfile, analysis: DocumentAnalysis) -> Dict[str, Any]:
        """Safe eligibility check with fallback"""
        try:
            result = self.eligibility_agent.tool_func(
                json.dumps(profile.model_dump()),
                json.dumps(analysis.model_dump())
            )
            if result and isinstance(result, dict):
                return result
        except Exception as e:
            logger.error(f"❌ Eligibility Check failed: {e}")
        
        # Fallback eligibility
        logger.warning("⚠️ Using fallback eligibility")
        missing_docs = analysis.required_documents[:4] if analysis.required_documents else []
        return {
            "status": "Partially Eligible",
            "score": 50,
            "reasons": ["Analysis completed with fallback methods. Please review manually."],
            "matching_criteria": ["Basic profile requirements met"],
            "missing_criteria": ["Full analysis requires better PDF quality"],
            "missing_documents": missing_docs,
            "mandatory_met": False,
            "special_category_eligible": False,
            "has_alternative_path": False,
            "conditional_requirements": [],
            "recommendations": ["Please upload a clearer PDF for better analysis"]
        }
    
    async def _safe_action_plan(self, profile: StudentProfile, analysis: DocumentAnalysis, eligibility: EligibilityResult) -> Dict[str, Any]:
        """Safe action plan with fallback"""
        try:
            result = self.action_agent.tool_func(
                json.dumps(profile.model_dump()),
                json.dumps(analysis.model_dump()),
                json.dumps(eligibility.model_dump())
            )
            if result and isinstance(result, dict):
                return result
        except Exception as e:
            logger.error(f"❌ Action Plan failed: {e}")
        
        # Fallback action plan
        logger.warning("⚠️ Using fallback action plan")
        return {
            "immediate_actions": ["Review requirements manually", "Gather required documents"],
            "checklist": [
                {"task": "Verify eligibility", "priority": "High", "deadline": "ASAP", "category": "Document"},
                {"task": "Gather required documents", "priority": "High", "deadline": analysis.deadline if analysis.deadline else "ASAP", "category": "Document"}
            ],
            "missing_documents": eligibility.missing_documents if eligibility.missing_documents else analysis.required_documents[:3],
            "recommendations": ["Upload a clearer PDF for better analysis"],
            "next_steps": ["Step 1: Verify requirements", "Step 2: Gather documents"],
            "timeline": {"week_1": "Review requirements", "week_2": "Apply"},
            "application_deadline": analysis.deadline,
            "submission_priority": "High"
        }
    
    def _detect_document_type(self, text: str, analysis_data: dict) -> DocumentType:
        """Smart detection of document type"""
        text_lower = text.lower()
        
        scholarship_keywords = ['scholarship', 'fellowship', 'financial aid', 'grant', 'stipend', 'merit-cum-means']
        admission_keywords = ['admission', 'enrollment', 'application', 'prospectus', 'admit card', 'entrance']
        
        is_scholarship = any(keyword in text_lower for keyword in scholarship_keywords)
        is_admission = any(keyword in text_lower for keyword in admission_keywords)
        
        if analysis_data.get('scholarship_name'):
            is_scholarship = True
        if analysis_data.get('course_name'):
            is_admission = True
        
        if is_scholarship and is_admission:
            return DocumentType.BOTH
        elif is_scholarship:
            return DocumentType.SCHOLARSHIP
        elif is_admission:
            return DocumentType.ADMISSION
        else:
            return DocumentType.UNKNOWN
    
    def _generate_comparison(self, profile: StudentProfile, analysis: DocumentAnalysis, eligibility: EligibilityResult) -> ComparisonResult:
        """Generate profile comparison"""
        strengths = []
        weaknesses = []
        
        if profile.marks_percentage >= 60:
            strengths.append(f"Strong academic performance ({profile.marks_percentage}%)")
        elif profile.marks_percentage >= 45:
            strengths.append(f"Good academic performance ({profile.marks_percentage}%)")
        else:
            weaknesses.append(f"Academic score ({profile.marks_percentage}%) may be below requirements")
        
        if profile.family_income < 250000:
            strengths.append("Low family income - eligible for financial aid")
        elif profile.family_income < 500000:
            strengths.append("Moderate family income")
        else:
            weaknesses.append("Higher family income may affect scholarship eligibility")
        
        if profile.category.value in ["SC", "ST", "EWS"]:
            strengths.append(f"Eligible for {profile.category.value} category benefits")
        
        if analysis.required_documents:
            strengths.append("Required documents identified")
        else:
            weaknesses.append("Required documents not clearly specified")
        
        if len(strengths) > len(weaknesses):
            overall = "Strong candidate with good chances"
        elif len(strengths) == len(weaknesses):
            overall = "Candidate needs to address some requirements"
        else:
            overall = "Candidate needs significant preparation"
        
        doc_completeness = 0
        if analysis.required_documents:
            missing_count = len(eligibility.missing_documents) if eligibility.missing_documents else 0
            doc_completeness = ((len(analysis.required_documents) - missing_count) / len(analysis.required_documents)) * 100
        
        return ComparisonResult(
            student_profile_matches=eligibility.mandatory_met,
            eligibility_score=eligibility.score,
            document_completeness=doc_completeness,
            missing_requirements=eligibility.missing_criteria + eligibility.missing_documents,
            strengths=strengths,
            weaknesses=weaknesses,
            overall_assessment=overall
        )
    
    def _generate_message(self, doc_type: DocumentType, status: str) -> str:
        """Generate user-friendly message"""
        type_map = {
            DocumentType.SCHOLARSHIP: "scholarship",
            DocumentType.ADMISSION: "admission",
            DocumentType.BOTH: "scholarship and admission",
            DocumentType.UNKNOWN: "document"
        }
        type_text = type_map.get(doc_type, "document")
        
        if status == "Eligible":
            return f"🎉 Congratulations! Based on your profile, you are eligible for this {type_text}."
        elif status == "Partially Eligible":
            return f"📋 You are partially eligible for this {type_text}. Please check the action plan for next steps."
        elif status == "Conditional":
            return f"⚠️ Your eligibility is conditional. Please address the requirements mentioned."
        else:
            return f"❌ You may not be eligible for this {type_text}. Check alternative paths."
    
    # ---------- Extraction Helper Methods (Fallbacks) ----------
    
    def _extract_documents_from_text(self, text: str) -> list:
        """Extract documents using regex"""
        documents = []
        patterns = [
            r'(?:LIST OF REQUIRED DOCUMENTS|Documents Required|Checklist|Enclosures)[\s:]*([^\n]*(?:\n[^\n]+)*?)(?:\n\n|\Z)',
            r'(?:Required Documents|Documents to be attached)[\s:]*([^\n]*(?:\n[^\n]+)*?)(?:\n\n|\Z)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                section = match.group(1)
                items = re.findall(r'(?:☐|•|-|\*|\d+[\.\)])\s*([^\n]+)', section)
                if items:
                    documents = [doc.strip() for doc in items if len(doc.strip()) > 5]
                    break
        
        if not documents:
            doc_patterns = [
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*(?:Marksheet|Certificate|Card|Copy|Form|Letter|ID|Proof|Report))',
                r'(Migration|Transfer|Conduct|Caste|Income|Domicile|Character)\s+(?:Certificate)',
            ]
            for pattern in doc_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    doc_name = match if isinstance(match, str) else match[-1]
                    if doc_name.strip() and len(doc_name.strip()) > 5:
                        documents.append(doc_name.strip())
                if documents:
                    break
        
        return list(dict.fromkeys(documents))
    
    def _extract_deadline_from_text(self, text: str) -> str:
        """Extract deadline from text"""
        patterns = [
            r'(?:Last\s*date|Deadline|Closing\s*date|Application\s*ends?)\s*(?:for|on)?\s*([\d]{1,2}[-/][\d]{1,2}[-/][\d]{2,4})',
            r'(?:Apply\s*before|Submit\s*by)\s*([\d]{1,2}[-/][\d]{1,2}[-/][\d]{2,4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return "Deadline not specified"
    
    def _extract_organization_from_text(self, text: str) -> str:
        """Extract organization name"""
        patterns = [
            r'(?:University|College|Institute|Board)\s*[oO]f\s*([^\n,.]+)',
            r'([A-Z][a-z]+\s+(?:University|College|Institute))',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "Organization not identified"
    
    def _extract_important_dates(self, text: str) -> dict:
        """Extract important dates"""
        dates = {}
        date_patterns = {
            "application_start": r"(?:Application|Registration)\s*(?:starts|begins|opens)\s*(?:from|on)?\s*([\d]{1,2}[-/][\d]{1,2}[-/][\d]{2,4})",
            "application_last_date": r"(?:Last\s*date|Deadline|Closing\s*date)\s*(?:for|on)?\s*([\d]{1,2}[-/][\d]{1,2}[-/][\d]{2,4})",
            "exam_date": r"(?:Exam|Test|Entrance)\s*(?:date|on|will\s*be\s*held\s*on)\s*([\d]{1,2}[-/][\d]{1,2}[-/][\d]{2,4})",
            "result_date": r"(?:Result|Merit\s*list)\s*(?:date|announced?|declared?)\s*(?:on)?\s*([\d]{1,2}[-/][\d]{1,2}[-/][\d]{2,4})",
        }
        
        for key, pattern in date_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                dates[key] = match.group(1)
        
        return dates