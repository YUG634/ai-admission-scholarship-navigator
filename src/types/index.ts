// src/types/index.ts
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
  // ✅ New fields that match backend
  mandatory_requirements: string[];
  special_categories: string[];
  alternative_admission_paths: string[];
  required_documents: string[];
  important_instructions: string[];
  // Legacy support (will be removed)
  eligibility_criteria?: string[];
  instructions?: string;
  document_type?: string;
}

export interface EligibilityEvaluation {
  status: "Eligible" | "Partially Eligible" | "Not Eligible" | string;
  reasons: string[];
  score?: number;
  matching_criteria?: string[];
  missing_criteria?: string[];
  // ✅ New fields that match backend
  missing_documents: string[];
  mandatory_met: boolean;
  special_category_eligible: boolean;
  has_alternative_path: boolean;
}

export interface ChecklistItem {
  task: string;
  priority: "High" | "Medium" | "Low" | string;
  // ✅ Standardized on 'deadline'
  deadline: string;
  // Legacy support
  timeframe?: string;
}

export interface ActionPlan {
  immediate_actions: string[];
  checklist: ChecklistItem[];
  missing_documents: string[];
  recommendations: string[];
  next_steps: string[];
  timeline: Record<string, string>;
}

export interface AgentPipelineResponse {
  success: boolean;
  analysis?: ScholarshipAnalysis;
  eligibility?: EligibilityEvaluation;
  actionPlan?: ActionPlan;
  error?: string;
}