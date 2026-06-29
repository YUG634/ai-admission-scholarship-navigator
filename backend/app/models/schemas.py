from pydantic import BaseModel, Field
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
    """Extracted information from scholarship/admission document"""
    document_type: str = "unknown"  # "scholarship", "admission", "unknown"
    scholarship_name: str = ""
    deadline: str = ""
    # ✅ NEW: Separate fields for different types of requirements
    mandatory_requirements: List[str] = Field(
        default_factory=list,
        description="Requirements that ALL applicants MUST meet"
    )
    special_categories: List[str] = Field(
        default_factory=list,
        description="OPTIONAL categories that provide benefits"
    )
    alternative_admission_paths: List[str] = Field(
        default_factory=list,
        description="Different ways to qualify for admission"
    )
    required_documents: List[str] = Field(
        default_factory=list,
        description="Documents required for application"
    )
    important_instructions: List[str] = Field(
        default_factory=list,
        description="Important application instructions"
    )

class EligibilityResult(BaseModel):
    """Eligibility check results"""
    status: str = "Not Eligible"  # "Eligible", "Partially Eligible", "Not Eligible"
    score: float = 0
    reasons: List[str] = Field(default_factory=list)
    matching_criteria: List[str] = Field(default_factory=list)
    missing_criteria: List[str] = Field(default_factory=list)
    # ✅ NEW: Additional fields for better eligibility tracking
    missing_documents: List[str] = Field(
        default_factory=list,
        description="Documents the student needs to gather"
    )
    mandatory_met: bool = Field(
        default=False,
        description="Whether all mandatory requirements are met"
    )
    special_category_eligible: bool = Field(
        default=False,
        description="Whether student qualifies for any special category"
    )
    has_alternative_path: bool = Field(
        default=False,
        description="Whether alternative admission paths are available"
    )

class ActionItem(BaseModel):
    task: str
    priority: str = "Medium"  # "High", "Medium", "Low"
    deadline: Optional[str] = None

class ActionPlan(BaseModel):
    immediate_actions: List[str] = Field(default_factory=list)
    checklist: List[ActionItem] = Field(default_factory=list)
    missing_documents: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    timeline: Dict[str, str] = Field(default_factory=dict)

class AnalysisResponse(BaseModel):
    """Complete response from the agent system"""
    analysis: DocumentAnalysis
    eligibility: EligibilityResult
    action_plan: ActionPlan
    processing_time_ms: Optional[float] = None