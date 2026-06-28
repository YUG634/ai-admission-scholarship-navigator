from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import Optional
from app.models.schemas import StudentProfile, Category
from app.orchestrator.adk_orchestrator import ADKOrchestrator
from app.utils.pdf_processor import extract_text_from_pdf, validate_pdf

router = APIRouter()
orchestrator = ADKOrchestrator()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "framework": "Google ADK",
        "agents": ["DocumentAnalysisAgent", "EligibilityAgent", "ActionPlanAgent"],
        "features": [
            "Document classification (scholarship/admission)",
            "Mandatory vs optional requirements",
            "Special categories are not treated as mandatory"
        ]
    }

@router.post("/analyze")
async def analyze_document(
    pdf_file: UploadFile = File(...),
    full_name: str = Form(...),
    state: str = Form(...),
    category: str = Form(...),
    family_income: float = Form(...),
    current_qualification: str = Form(...),
    marks_percentage: float = Form(...),
    cgpa: Optional[float] = Form(None)
):
    try:
        if not pdf_file.filename.endswith('.pdf'):
            raise HTTPException(400, "Only PDF files are supported")
        
        pdf_bytes = await pdf_file.read()
        if not validate_pdf(pdf_bytes):
            raise HTTPException(400, "Invalid PDF file")
        
        pdf_text = extract_text_from_pdf(pdf_bytes)
        if not pdf_text.strip():
            raise HTTPException(400, "Could not extract text from PDF")
        
        # Handle category - case insensitive
        category_enum = None
        for cat in Category:
            if cat.value.lower() == category.lower():
                category_enum = cat
                break
        
        if not category_enum:
            raise HTTPException(400, f"Invalid category: {category}. Must be one of: General, OBC, SC, ST, EWS")
        
        profile = StudentProfile(
            full_name=full_name,
            state=state,
            category=category_enum,
            family_income=family_income,
            current_qualification=current_qualification,
            marks_percentage=marks_percentage,
            cgpa=cgpa
        )
        
        response = await orchestrator.process(pdf_text, profile)
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, str(e))