from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

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
    scholarship_name: str = ""  # ✅ Default empty string
    deadline: str = ""
    mandatory_requirements: List[str] = Field(default_factory=list)
    special_categories: List[str] = Field(default_factory=list)
    alternative_admission_paths: List[str] = Field(default_factory=list)
    required_documents: List[str] = Field(default_factory=list)
    important_instructions: List[str] = Field(default_factory=list)
    
    @validator('scholarship_name', pre=True)
    def handle_none(cls, v):
        return v if v is not None else ""

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

class AnalysisResponse(BaseModel):
    analysis: DocumentAnalysis
    eligibility: EligibilityResult
    action_plan: ActionPlan
    processing_time_ms: Optional[float] = None