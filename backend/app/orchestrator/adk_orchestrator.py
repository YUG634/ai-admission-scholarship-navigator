import time
import json
import re
import logging
from typing import Dict, Any, Optional, List

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
        
        # Fallback: Extract using regex with enhanced patterns
        logger.warning("⚠️ Using regex fallback for document analysis")
        return {
            "document_type": "unknown",
            "document_name": self._extract_document_name_from_text(pdf_text),
            "organization": self._extract_organization_from_text(pdf_text),
            "deadline": self._extract_deadline_from_text(pdf_text),
            "required_documents": self._extract_documents_from_text(pdf_text),
            "mandatory_requirements": self._extract_mandatory_requirements(pdf_text),
            "special_categories": self._extract_special_categories(pdf_text),
            "alternative_admission_paths": self._extract_alternative_paths(pdf_text),
            "important_instructions": self._extract_important_instructions(pdf_text),
            "important_dates": self._extract_important_dates(pdf_text),
            "contact_info": self._extract_contact_info(pdf_text),
            "application_phases": self._extract_application_phases(pdf_text),
            "merit_schedule": self._extract_merit_schedule(pdf_text),
            "entrance_exams": self._extract_entrance_exams(pdf_text),
            "direct_admission_programs": self._extract_direct_admission_programs(pdf_text),
            "seat_limits": self._extract_seat_limits(pdf_text),
        }
    
    # ============================================================
    # ENHANCED EXTRACTION METHODS
    # ============================================================
    
    def _extract_document_name_from_text(self, text: str) -> str:
        """Extract document title/name"""
        patterns = [
            r'#\s*([^\n]+?)(?:\s*\n|$)',  # Header pattern
            r'CIRCULAR[-–]\s*([A-Z]+)',  # Circular number
            r'ADMISSION COMMENCEMENT FOR ([^\n]+)',  # Admission title
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "Admission Document"
    
    def _extract_documents_from_text(self, text: str) -> List[str]:
        """
        Enhanced document extraction - specifically looks for PART-G pattern
        """
        documents = []
        
        # Method 1: Look for PART-G section
        part_g_pattern = r'PART-G[:\s]*LIST OF REQUIRED DOCUMENTS[:\s]*([\s\S]*?)(?=PART-|Kindly note|Students Help Desk|\Z)'
        part_g_match = re.search(part_g_pattern, text, re.IGNORECASE)
        
        if part_g_match:
            section_text = part_g_match.group(1)
            # Extract numbered items
            doc_pattern = r'(\d+)\.\s*([^□\n]+?)(?:\s*□|\s*\(If applicable\)|\s*\(if applicable\)|\s*$|\.|\,)'
            matches = re.findall(doc_pattern, section_text)
            if matches:
                for _, doc_name in matches:
                    clean_name = doc_name.strip()
                    # Clean up common artifacts
                    clean_name = re.sub(r'\s+', ' ', clean_name)
                    if clean_name and len(clean_name) > 3:
                        documents.append(clean_name)
        
        # Method 2: Fallback - look for document patterns
        if not documents:
            doc_patterns = [
                r'(\d+\.\s*([^\n]+?)(?:\s*\([^)]*\))?\s*(?:□|$))',
                r'(?:☐|✓|•|-|\*)\s*([^\n]+)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*(?:Marksheet|Certificate|Card|Copy|Form|Letter|ID|Proof|Report|Undertaking))',
                r'(Migration|Transfer|Conduct|Caste|Income|Domicile|Character|Disability|Gap|Cultural|Sports)\s+(?:Certificate)',
            ]
            for pattern in doc_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    doc_name = match if isinstance(match, str) else match[-1] if isinstance(match, tuple) else str(match)
                    clean_name = doc_name.strip()
                    clean_name = re.sub(r'^\d+\.\s*', '', clean_name)
                    clean_name = re.sub(r'\s*\([^)]*\)\s*$', '', clean_name)
                    if clean_name and len(clean_name) > 3 and clean_name not in documents:
                        documents.append(clean_name)
                if documents:
                    break
        
        # Method 3: Look for specific document keywords
        if not documents:
            doc_keywords = [
                'Marksheet', 'Certificate', 'Card', 'Copy', 'Form', 'Letter', 
                'ID', 'Proof', 'Report', 'Undertaking', 'Migration', 'Transfer',
                'Conduct', 'Caste', 'Income', 'Domicile', 'Character', 'Disability',
                'Gap', 'Cultural', 'Sports', 'APAAR', 'Aadhaar'
            ]
            for keyword in doc_keywords:
                pattern = rf'([^\n]*{keyword}[^\n]*(?:\s*\([^)]*\))?)'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    clean_name = match.strip()
                    clean_name = re.sub(r'^\d+\.\s*', '', clean_name)
                    clean_name = re.sub(r'\s*[□✓☐]', '', clean_name)
                    if clean_name and len(clean_name) > 3 and clean_name not in documents:
                        documents.append(clean_name)
        
        return list(dict.fromkeys(documents))[:20]  # Limit to 20 documents
    
    def _extract_deadline_from_text(self, text: str) -> str:
        """Enhanced deadline extraction"""
        patterns = [
            r'Phase\s+II[:\s]*[^\n]*?\b(\d{1,2}(?:nd|st|rd|th)?\s+[A-Za-z]+\s+\d{4})',
            r'(?:Last\s*date|Deadline|Closing\s*date|Application\s*ends?)\s*(?:for|on)?\s*[:\s]*([\d]{1,2}(?:nd|st|rd|th)?\s+[A-Za-z]+\s+[\d]{4})',
            r'(?:Apply\s*before|Submit\s*by)\s*[:\s]*([\d]{1,2}(?:nd|st|rd|th)?\s+[A-Za-z]+\s+[\d]{4})',
            r'([\d]{1,2}(?:nd|st|rd|th)?\s+[A-Za-z]+\s+[\d]{4})\s*(?:at\s+[\d:]+\s*(?:am|pm))?\s*(?:for\s+Phase|is\s+the\s+last)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                deadline = match.group(1).strip()
                # Clean up
                deadline = re.sub(r'\s+', ' ', deadline)
                return deadline
        
        # Check for specific Phase II date
        phase_ii_match = re.search(r'Phase\s+II.*?(\d{1,2}(?:nd|st|rd|th)?\s+[A-Za-z]+\s+\d{4})', text, re.IGNORECASE | re.DOTALL)
        if phase_ii_match:
            return phase_ii_match.group(1).strip()
        
        return "Deadline not specified"
    
    def _extract_organization_from_text(self, text: str) -> str:
        """Extract organization name with better patterns"""
        patterns = [
            r'(?:University|College|Institute|Board)\s*[oO]f\s*([^\n,.]+)',
            r'([A-Z][a-z]+\s+(?:University|College|Institute))\s*(?:,|\n|$)',
            r'(HSNC\s+University|HNSC\s+University)',
            r'(KC\s+College|HR\s+College)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Look for organization in footer
        footer_match = re.search(r'Dean\s+([^\n]+)', text, re.IGNORECASE)
        if footer_match:
            org_text = footer_match.group(1).strip()
            # Try to extract organization from footer
            org_match = re.search(r'([A-Z][a-z]+\s+(?:University|College))', org_text)
            if org_match:
                return org_match.group(1).strip()
        
        return "Organization not identified"
    
    def _extract_mandatory_requirements(self, text: str) -> List[str]:
        """Extract mandatory requirements"""
        requirements = []
        
        # Look for requirements sections
        sections = [
            r'(?:Eligibility|Criteria|Requirements|Conditions)\s*[:\s]*([\s\S]*?)(?=\n\n|\Z)',
            r'(?:Qualifying|Entrance)\s*(?:Exam|Test)\s*[:\s]*([^\n]+)',
            r'(?:Applicable for|Required for)\s*([^\n]+)',
        ]
        
        for pattern in sections:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                section = match.group(1)
                # Extract bullet points
                items = re.findall(r'[•·●○◆◇▪▫]\s*([^\n]+)', section)
                if items:
                    requirements.extend([item.strip() for item in items if item.strip()])
                else:
                    # Extract sentences
                    sentences = re.findall(r'([A-Z][^.!?]*[.!?])', section)
                    requirements.extend([s.strip() for s in sentences if len(s.strip()) > 10])
        
        return list(dict.fromkeys(requirements))[:10]
    
    def _extract_special_categories(self, text: str) -> List[str]:
        """Extract special categories (SC, ST, OBC, EWS, etc.)"""
        categories = []
        
        category_patterns = [
            r'(SC|ST|OBC|EWS|General|Unreserved|Sindhi Minority)',
            r'(Economically\s+Weaker\s+Section)',
            r'(Scheduled\s+(?:Caste|Tribe))',
            r'(Other\s+Backward\s+Class)',
            r'(Minority)\s+(?:Students?|Communities?)',
        ]
        
        for pattern in category_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                cat = match if isinstance(match, str) else match[0]
                cat = cat.strip()
                if cat and cat not in categories:
                    categories.append(cat)
        
        return categories
    
    def _extract_alternative_paths(self, text: str) -> List[str]:
        """Extract alternative admission paths"""
        paths = []
        
        # Look for H-CET, H-LAT, MHCET alternatives
        alt_patterns = [
            r'(Students\s+who\s+missed\s+the\s+MHCET\s+can\s+appear\s+for\s+the\s+H-CET)',
            r'(Exempted\s+from\s+H-CET\s+if\s+appeared\s+for\s+the\s+Maharashtra\s+Common\s+Entrance\s+Test)',
            r'(Exempted\s+from\s+H-LAT\s+if\s+appeared\s+for\s+Maharashtra\s+State\s+&\s+National\s+level\s+Entrance\s+Examinations)',
            r'(Direct\s+Admission\s+Schedule\s+for\s+All\s+Categories)',
            r'(Alternative\s+admission\s+paths?\s+are\s+available)',
        ]
        
        for pattern in alt_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                paths.append(match.group(1).strip() if isinstance(match.group(1), str) else match.group(0).strip())
        
        return list(dict.fromkeys(paths))
    
    def _extract_important_instructions(self, text: str) -> List[str]:
        """Extract important instructions"""
        instructions = []
        
        # Look for instruction sections
        instruction_patterns = [
            r'(?:Key\s+Portal\s+Instructions)[:\s]*([\s\S]*?)(?=\n\n|\Z)',
            r'(?:Kindly\s+note|Please\s+note|Important\s+Note)[:\s]*([^\n]+)',
            r'(?:Instructions|Guidelines)[:\s]*([\s\S]*?)(?=\n\n|\Z)',
        ]
        
        for pattern in instruction_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                section = match.group(1)
                # Extract bullet points
                items = re.findall(r'[•·●○◆◇▪▫]\s*([^\n]+)', section)
                if items:
                    instructions.extend([item.strip() for item in items if item.strip()])
                else:
                    # Extract sentences
                    sentences = re.findall(r'([A-Z][^.!?]*[.!?])', section)
                    instructions.extend([s.strip() for s in sentences if len(s.strip()) > 10])
        
        return list(dict.fromkeys(instructions))[:10]
    
    def _extract_important_dates(self, text: str) -> Dict[str, str]:
        """Extract important dates with better patterns"""
        dates = {}
        
        date_patterns = {
            "phase1_open": r'Phase\s+1[:\s]*[^\n]*?(\d{1,2}(?:nd|st|rd|th)?\s+[A-Za-z]+\s+\d{4})',
            "phase1_close": r'Phase\s+1.*?(\d{1,2}(?:nd|st|rd|th)?\s+[A-Za-z]+\s+\d{4})\s*(?:at\s+[\d:]+\s*(?:am|pm))?.*?5\.00\s*pm',
            "phase2_open": r'Phase\s+II[:\s]*[^\n]*?(\d{1,2}(?:nd|st|rd|th)?\s+[A-Za-z]+\s+\d{4})',
            "phase2_close": r'Phase\s+II.*?(\d{1,2}(?:nd|st|rd|th)?\s+[A-Za-z]+\s+\d{4})\s*(?:at\s+[\d:]+\s*(?:am|pm))?\s*.*?10\.00\s*am',
            "application_start": r'(?:Application|Registration)\s*(?:starts|begins|opens)\s*(?:from|on)?\s*[:\s]*([\d]{1,2}(?:nd|st|rd|th)?\s+[A-Za-z]+\s+[\d]{4})',
            "application_last_date": r'(?:Last\s*date|Deadline|Closing\s*date)\s*(?:for|on)?\s*[:\s]*([\d]{1,2}(?:nd|st|rd|th)?\s+[A-Za-z]+\s+[\d]{4})',
            "exam_date": r'(?:Exam|Test|Entrance)\s*(?:date|on|will\s*be\s*held\s*on)\s*[:\s]*([\d]{1,2}(?:nd|st|rd|th)?\s+[A-Za-z]+\s+[\d]{4})',
            "result_date": r'(?:Result|Merit\s*list)\s*(?:date|announced?|declared?)\s*(?:on)?\s*[:\s]*([\d]{1,2}(?:nd|st|rd|th)?\s+[A-Za-z]+\s+[\d]{4})',
            "term_start": r'(?:Commencement\s+of\s+Term|Academic\s+session\s+starts)\s*(?:from|on)?\s*[:\s]*([\d]{1,2}(?:nd|st|rd|th)?\s+[A-Za-z]+\s+[\d]{4})',
        }
        
        for key, pattern in date_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                date_str = match.group(1).strip()
                date_str = re.sub(r'\s+', ' ', date_str)
                dates[key] = date_str
        
        return dates
    
    def _extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract contact information"""
        result = {"email": "", "phone": [], "zoom": {}}
        
        # Extract email
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        email_matches = re.findall(email_pattern, text)
        if email_matches:
            result["email"] = email_matches[0]
        
        # Extract phone numbers
        phone_pattern = r'\+?91?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_matches = re.findall(phone_pattern, text)
        if phone_matches:
            result["phone"] = phone_matches
        
        # Extract Zoom meeting details
        zoom_pattern = r'Zoom\s+link:?\s*(https://zoom\.us/[^\s]+)'
        zoom_match = re.search(zoom_pattern, text, re.IGNORECASE)
        if zoom_match:
            result["zoom"]["link"] = zoom_match.group(1)
        
        # Extract Meeting ID
        meeting_pattern = r'Meeting\s+ID:?\s*([\d\s]+)'
        meeting_match = re.search(meeting_pattern, text, re.IGNORECASE)
        if meeting_match:
            result["zoom"]["meeting_id"] = meeting_match.group(1).strip()
        
        # Extract Passcode
        passcode_pattern = r'Passcode:?\s*([^\s]+)'
        passcode_match = re.search(passcode_pattern, text, re.IGNORECASE)
        if passcode_match:
            result["zoom"]["passcode"] = passcode_match.group(1).strip()
        
        return result
    
    def _extract_application_phases(self, text: str) -> List[Dict[str, str]]:
        """Extract application phases"""
        phases = []
        
        phase_pattern = r'Phase\s+(\d+)[:\s]*([^\n]*?)(\d{1,2}(?:nd|st|rd|th)?\s+[A-Za-z]+\s+\d{4})[.\s]*([\d:]+[ap]m)?[.\s]*to?[.\s]*(?:[\d:]+[ap]m)?[.\s]*(\d{1,2}(?:nd|st|rd|th)?\s+[A-Za-z]+\s+\d{4})[.\s]*([\d:]+[ap]m)?'
        matches = re.findall(phase_pattern, text, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            phase_num = match[0].strip()
            phase_desc = match[1].strip()
            open_date = match[2].strip()
            open_time = match[3].strip() if len(match) > 3 and match[3] else ""
            close_date = match[4].strip()
            close_time = match[5].strip() if len(match) > 5 and match[5] else ""
            
            phases.append({
                "phase": f"Phase {phase_num}",
                "open_date": open_date,
                "open_time": open_time,
                "close_date": close_date,
                "close_time": close_time,
                "description": phase_desc
            })
        
        return phases
    
    def _extract_merit_schedule(self, text: str) -> List[Dict[str, str]]:
        """Extract merit list schedule"""
        merit_lists = []
        
        merit_pattern = r'([A-Z][a-z]+)\s+Merit\s+List[:\s]*([A-Z][a-z]+,\s+[A-Z][a-z]+\s+\d{4})'
        matches = re.findall(merit_pattern, text, re.IGNORECASE)
        
        for match in matches:
            merit_lists.append({
                "name": f"{match[0].strip()} Merit List",
                "date": match[1].strip()
            })
        
        return merit_lists
    
    def _extract_entrance_exams(self, text: str) -> Dict[str, Any]:
        """Extract entrance exam details"""
        result = {
            "h_cet": {"may_dates": [], "june_dates": [], "link": ""},
            "h_lat": {"may_dates": [], "june_dates": [], "link": ""}
        }
        
        # Extract H-CET dates
        h_cet_pattern = r'H-CET[-\s]*(?:II)?[:\s]*([\s\S]*?)(?:H-LAT|$|Kindly Note)'
        h_cet_match = re.search(h_cet_pattern, text, re.IGNORECASE)
        
        if h_cet_match:
            section = h_cet_match.group(1)
            # May dates
            may_dates = re.findall(r'(\d{1,2}(?:nd|st|rd|th)?\s+May\s+\d{4})', section)
            if may_dates:
                result["h_cet"]["may_dates"] = may_dates
            
            # June dates
            june_dates = re.findall(r'(\d{1,2}(?:nd|st|rd|th)?\s+June\s+\d{4})', section)
            if june_dates:
                result["h_cet"]["june_dates"] = june_dates
            
            # Link
            link_match = re.search(r'(http[^\s]+)', section)
            if link_match:
                result["h_cet"]["link"] = link_match.group(1)
        
        # Extract H-LAT dates
        h_lat_pattern = r'H-LAT[-\s]*(?:I)?[:\s]*([\s\S]*?)(?:Kindly Note|$|H-CET)'
        h_lat_match = re.search(h_lat_pattern, text, re.IGNORECASE)
        
        if h_lat_match:
            section = h_lat_match.group(1)
            # May dates
            may_dates = re.findall(r'(\d{1,2}(?:nd|st|rd|th)?\s+May\s+\d{4})', section)
            if may_dates:
                result["h_lat"]["may_dates"] = may_dates
            
            # June dates
            june_dates = re.findall(r'(\d{1,2}(?:nd|st|rd|th)?\s+June\s+\d{4})', section)
            if june_dates:
                result["h_lat"]["june_dates"] = june_dates
            
            # Link
            link_match = re.search(r'(http[^\s]+)', section)
            if link_match:
                result["h_lat"]["link"] = link_match.group(1)
        
        return result
    
    def _extract_direct_admission_programs(self, text: str) -> List[str]:
        """Extract direct admission programs"""
        programs = []
        
        # Look for PART-C section
        part_c_pattern = r'PART-C[:\s]*DIRECT ADMISSION SCHEDULE[–\s]*ALL CATEGORIES[:\s]*([\s\S]*?)(?=PART-|$|image)'
        part_c_match = re.search(part_c_pattern, text, re.IGNORECASE)
        
        if part_c_match:
            section = part_c_match.group(1)
            # Extract numbered program names
            program_pattern = r'(\d+)\.\s*([^\n]+?)(?:$|Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday)'
            matches = re.findall(program_pattern, section, re.IGNORECASE)
            for _, program in matches:
                clean_program = program.strip()
                clean_program = re.sub(r'\s+', ' ', clean_program)
                if clean_program and len(clean_program) > 5:
                    programs.append(clean_program)
        
        return list(dict.fromkeys(programs))
    
    def _extract_seat_limits(self, text: str) -> Dict[str, str]:
        """Extract seat limits"""
        seat_limits = {}
        
        # BMS seats
        bms_match = re.search(r'Bachelor of Management Studies \(BMS\).*?\(Only\s+(\d+)\s+Seats? Each\)', text, re.IGNORECASE | re.DOTALL)
        if bms_match:
            seat_limits["BMS"] = bms_match.group(1)
        
        # BBA seats
        bba_match = re.search(r'Bachelor of Business Administration \(BBA\).*?\(Only\s+(\d+)\s+Seats? Each\)', text, re.IGNORECASE | re.DOTALL)
        if bba_match:
            seat_limits["BBA"] = bba_match.group(1)
        
        return seat_limits
    
    # ============================================================
    # EXISTING METHODS (keep as is)
    # ============================================================
    
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
        
        if hasattr(profile.category, 'value'):
            category_value = profile.category.value
        else:
            category_value = str(profile.category)
        
        if category_value in ["SC", "ST", "EWS"]:
            strengths.append(f"Eligible for {category_value} category benefits")
        
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
        
        # Enhanced fallback eligibility
        logger.warning("⚠️ Using fallback eligibility")
        
        # Extract missing documents from analysis
        missing_docs = analysis.required_documents[:5] if analysis.required_documents else []
        
        return {
            "status": "Partially Eligible",
            "score": 50,
            "reasons": ["Analysis completed with fallback methods. Please review manually."],
            "matching_criteria": ["Basic profile requirements met"],
            "missing_criteria": ["Full analysis requires better PDF quality"],
            "missing_documents": missing_docs,
            "mandatory_met": False,
            "special_category_eligible": False,
            "has_alternative_path": True,
            "conditional_requirements": ["Please verify all requirements manually"],
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
        
        # Enhanced fallback action plan
        logger.warning("⚠️ Using fallback action plan")
        
        # Build checklist from extracted documents
        checklist = []
        if analysis.required_documents:
            for doc in analysis.required_documents[:5]:
                checklist.append({
                    "task": f"Prepare {doc}",
                    "priority": "High",
                    "deadline": analysis.deadline if analysis.deadline else "ASAP",
                    "category": "Document"
                })
        
        # Add application form task
        checklist.append({
            "task": "Complete the online admission application form",
            "priority": "High",
            "deadline": analysis.deadline if analysis.deadline else "ASAP",
            "category": "Application"
        })
        
        return {
            "immediate_actions": ["Review requirements manually", "Gather required documents"],
            "checklist": checklist,
            "missing_documents": eligibility.missing_documents if eligibility.missing_documents else analysis.required_documents[:3],
            "recommendations": ["Upload a clearer PDF for better analysis"],
            "next_steps": ["Step 1: Verify requirements", "Step 2: Gather documents"],
            "timeline": {"week_1": "Review requirements", "week_2": "Apply"},
            "application_deadline": analysis.deadline,
            "submission_priority": "High"
        }