from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Category(str, Enum):
    GENERAL = "General"
    OBC = "OBC"
    SC = "SC"
    ST = "ST"
    EWS = "EWS"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value_lower = value.lower()
            for member in cls:
                if member.value.lower() == value_lower:
                    return member
        return None

class DocumentType(str, Enum):
    SCHOLARSHIP = "scholarship"
    ADMISSION = "admission"
    UNKNOWN = "unknown"

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
    mandatory_requirements: List[str] = Field(default_factory=list, description="Requirements that ALL applicants must meet (e.g., 12th pass, entrance exam required)")
    special_categories: List[str] = Field(default_factory=list, description="Optional categories that provide benefits (e.g., Sindhi Minority, In-house students)")
    alternative_admission_paths: List[str] = Field(default_factory=list, description="Different ways to qualify (e.g., MHCET, H-CET, National entrance exams)")
    required_documents: List[str] = Field(default_factory=list)
    important_instructions: List[str] = Field(default_factory=list)

class EligibilityResult(BaseModel):
    status: str = "Not Eligible"  # "Eligible", "Partially Eligible", "Not Eligible"
    score: float = 0
    reasons: List[str] = Field(default_factory=list)
    matching_criteria: List[str] = Field(default_factory=list)
    missing_criteria: List[str] = Field(default_factory=list)
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
    timeline: dict = Field(default_factory=dict)

class AnalysisResponse(BaseModel):
    analysis: DocumentAnalysis
    eligibility: EligibilityResult
    action_plan: ActionPlan
    processing_time_ms: Optional[float] = None