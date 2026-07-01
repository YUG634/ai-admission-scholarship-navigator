from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

from app.api.routes import router

app = FastAPI(
    title="AI Admission & Scholarship Navigator",
    description="Multi-agent system with Google ADK",
    version="2.0.0"
)

# ✅ Add your Vercel URL to allowed origins
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://ai-admission-scholarship-navigator.vercel.app",  # ✅ ADD THIS
    "https://ai-admission-scholarship-navigator.netlify.app",  # Keep this if you have
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "name": "AI Admission & Scholarship Navigator",
        "version": "2.0.0",
        "framework": "FastAPI + Google ADK",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "framework": "Google ADK", "agents": ["DocumentAnalysis", "Eligibility", "ActionPlan"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=False
    )