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
  status: "Eligible" | "Not Eligible" | "Partially Eligible" | string;
  reasons: string[];
}

export interface ChecklistItem {
  task: string;
  priority: "High" | "Medium" | "Low" | string;
  timeframe: string;
}

export interface ActionPlan {
  checklist: ChecklistItem[];
  missing_documents: string[];
  recommendations: string[];
}

export interface AgentPipelineResponse {
  success: boolean;
  analysis?: ScholarshipAnalysis;
  eligibility?: EligibilityEvaluation;
  actionPlan?: ActionPlan;
  error?: string;
}
