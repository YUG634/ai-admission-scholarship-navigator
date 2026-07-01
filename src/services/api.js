const API_BASE_URL = 'https://ai-admission-scholarship-navigator.onrender.com';

export const analyzeScholarship = async (pdfFile, profileData) => {
  if (!pdfFile) {
    throw new Error('No PDF file provided');
  }

  const formData = new FormData();
  formData.append('pdf_file', pdfFile);
  formData.append('full_name', profileData.name || '');
  formData.append('state', profileData.state || '');
  formData.append('category', profileData.category || 'General');
  formData.append('family_income', parseFloat(profileData.income || 0));
  formData.append('current_qualification', profileData.qualification || '');
  formData.append('marks_percentage', parseFloat(profileData.marks || 0));

  try {
    console.log('📤 Sending request to FastAPI backend...');
    console.log('📄 File:', pdfFile.name, pdfFile.size, 'bytes');

    const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('❌ Server error:', errorData);
      throw new Error(errorData.detail || 'Analysis failed');
    }

    const data = await response.json();
    console.log('✅ Analysis successful:', data);

    // ✅ Map backend response to frontend types
    return {
      success: true,
      analysis: {
        scholarship_name: data.analysis?.scholarship_name || '',
        deadline: data.analysis?.deadline || '',
        // ✅ Use mandatory_requirements as eligibility_criteria
        eligibility_criteria: data.analysis?.mandatory_requirements || 
                              data.analysis?.eligibility_criteria || [],
        required_documents: data.analysis?.required_documents || [],
        instructions: data.analysis?.important_instructions?.join('\n') || 
                      data.analysis?.instructions || '',
        // ✅ Pass through new fields
        mandatory_requirements: data.analysis?.mandatory_requirements || [],
        special_categories: data.analysis?.special_categories || [],
        alternative_admission_paths: data.analysis?.alternative_admission_paths || [],
        important_instructions: data.analysis?.important_instructions || [],
        document_type: data.analysis?.document_type
      },
      eligibility: {
        status: data.eligibility?.status || 'Not Eligible',
        reasons: data.eligibility?.reasons || [],
        score: data.eligibility?.score || 0,
        matching_criteria: data.eligibility?.matching_criteria || [],
        missing_criteria: data.eligibility?.missing_criteria || [],
        mandatory_met: data.eligibility?.mandatory_met || false,
        special_category_eligible: data.eligibility?.special_category_eligible || false,
        has_alternative_path: data.eligibility?.has_alternative_path || false
      },
      actionPlan: {
        checklist: data.action_plan?.checklist || [],
        missing_documents: data.action_plan?.missing_documents || [],
        recommendations: data.action_plan?.recommendations || [],
        immediate_actions: data.action_plan?.immediate_actions || [],
        next_steps: data.action_plan?.next_steps || [],
        timeline: data.action_plan?.timeline || {}
      }
    };
  } catch (error) {
    console.error('❌ API Error:', error);
    throw error;
  }
};

export const healthCheck = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return await response.json();
  } catch (error) {
    console.error('Health check failed:', error);
    return { status: 'unhealthy', error: error.message };
  }
};