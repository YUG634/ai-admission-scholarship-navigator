import time
from app.agents.document_analysis_agent import DocumentAnalysisAgent
from app.agents.eligibility_agent import EligibilityAgent
from app.agents.action_plan_agent import ActionPlanAgent
from app.models.schemas import StudentProfile, AnalysisResponse

class AgentOrchestrator:
    def __init__(self):
        self.doc_agent = DocumentAnalysisAgent()
        self.eligibility_agent = EligibilityAgent()
        self.action_agent = ActionPlanAgent()
        self.traces = []
    
    async def process_application(self, pdf_text: str, profile: StudentProfile) -> AnalysisResponse:
        overall_start = time.time()
        
        print("🤖 Agent 1: Analyzing document...")
        analysis = await self.doc_agent.process(pdf_text)
        
        print("🤖 Agent 2: Checking eligibility...")
        eligibility = await self.eligibility_agent.process(profile, analysis)
        
        print("🤖 Agent 3: Generating action plan...")
        action_plan = await self.action_agent.process(profile, analysis, eligibility)
        
        overall_duration = (time.time() - overall_start) * 1000
        
        return AnalysisResponse(
            analysis=analysis,
            eligibility=eligibility,
            action_plan=action_plan,
            processing_time_ms=overall_duration
        )