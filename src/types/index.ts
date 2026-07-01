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
  // ✅ ADD THESE NEW FIELDS
  mandatory_requirements?: string[];
  special_categories?: string[];
  alternative_admission_paths?: string[];
  important_instructions?: string[];
  document_type?: string;
}

export interface EligibilityEvaluation {
  status: "Eligible" | "Not Eligible" | "Partially Eligible" | string;
  reasons: string[];
  // ✅ ADD THESE NEW FIELDS
  score?: number;
  matching_criteria?: string[];
  missing_criteria?: string[];
  mandatory_met?: boolean;
  special_category_eligible?: boolean;
  has_alternative_path?: boolean;
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
  // ✅ ADD THESE NEW FIELDS
  immediate_actions?: string[];
  next_steps?: string[];
  timeline?: Record<string, string>;
}

export interface AgentPipelineResponse {
  success: boolean;
  analysis?: ScholarshipAnalysis;
  eligibility?: EligibilityEvaluation;
  actionPlan?: ActionPlan;
  error?: string;
}