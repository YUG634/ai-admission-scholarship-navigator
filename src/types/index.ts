export interface StudentProfile {
  name: string;
  state: string;
  category: string;
  income: string;
  qualification: string;
  marks: string;
}

export interface ScholarshipAnalysis {
  scholarship_name: string;
  deadline: string;
  eligibility_criteria: string[];
  required_documents: string[];
  instructions: string;
}

export interface EligibilityEvaluation {
  status: 'Eligible' | 'Partially Eligible' | 'Not Eligible';
  reasons: string[];
}

export interface ActionPlan {
  checklist: Array<{
    task: string;
    priority: 'High' | 'Medium' | 'Low';
    timeframe?: string;
  }>;
  missing_documents: string[];
  recommendations: string[];
}

export interface AgentPipelineResponse {
  success?: boolean;
  error?: string;
  analysis?: ScholarshipAnalysis;
  eligibility?: EligibilityEvaluation;
  actionPlan?: ActionPlan;
}