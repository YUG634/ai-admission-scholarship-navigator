from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime

# ✅ ADD THIS - DocumentType Enum
class DocumentType(str, Enum):
    SCHOLARSHIP = "scholarship"
    ADMISSION = "admission"
    BOTH = "both"
    UNKNOWN = "unknown"

class Category(str, Enum):
    GENERAL = "General"
    OBC = "OBC"
    SC = "SC"
    ST = "ST"
    EWS = "EWS"

class StudentProfile(BaseModel):
    full_name: str
    state: str
    category: Category
    family_income: float
    current_qualification: str
    marks_percentage: float
    cgpa: Optional[float] = None

class DocumentAnalysis(BaseModel):
    document_type: str = "unknown"
    scholarship_name: str = ""
    deadline: str = ""
    mandatory_requirements: List[str] = Field(default_factory=list)
    special_categories: List[str] = Field(default_factory=list)
    alternative_admission_paths: List[str] = Field(default_factory=list)
    required_documents: List[str] = Field(default_factory=list)
    important_instructions: List[str] = Field(default_factory=list)
    
    # ✅ ADD VALIDATORS TO HANDLE BAD DATA
    @validator('scholarship_name', pre=True)
    def validate_scholarship_name(cls, v):
        if v is None:
            return ""
        if isinstance(v, list):
            return v[0] if v else ""
        return str(v)
    
    @validator('deadline', pre=True)
    def validate_deadline(cls, v):
        if v is None:
            return ""
        if isinstance(v, list):
            # Join list items into a single string
            return ", ".join(v) if v else ""
        return str(v)

class EligibilityResult(BaseModel):
    status: str = "Not Eligible"
    score: float = 0
    reasons: List[str] = Field(default_factory=list)
    matching_criteria: List[str] = Field(default_factory=list)
    missing_criteria: List[str] = Field(default_factory=list)
    missing_documents: List[str] = Field(default_factory=list)
    mandatory_met: bool = False
    special_category_eligible: bool = False
    has_alternative_path: bool = False

class ActionItem(BaseModel):
    task: str
    priority: str = "Medium"
    deadline: Optional[str] = None

class ActionPlan(BaseModel):
    immediate_actions: List[str] = Field(default_factory=list)
    checklist: List[ActionItem] = Field(default_factory=list)
    missing_documents: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    timeline: Dict[str, str] = Field(default_factory=dict)

class ComparisonResult(BaseModel):
    student_profile_matches: bool = False
    eligibility_score: float = 0
    document_completeness: float = 0
    missing_requirements: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    overall_assessment: str = ""

class AnalysisResponse(BaseModel):
    analysis: DocumentAnalysis
    eligibility: EligibilityResult
    action_plan: ActionPlan
    document_type: DocumentType = DocumentType.UNKNOWN
    comparison: Optional[ComparisonResult] = None
    processing_time_ms: Optional[float] = None
    message: Optional[str] = None