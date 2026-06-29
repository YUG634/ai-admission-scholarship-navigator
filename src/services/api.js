// src/services/api.js
const API_BASE_URL = 'https://ai-admission-scholarship-navigator.onrender.com';

export const analyzeScholarship = async (pdfFile, profileData) => {
  if (!pdfFile) {
    throw new Error('No PDF file provided');
  }

  const formData = new FormData();
  // FastAPI expects 'pdf_file' and individual fields
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
    console.log('👤 Profile:', {
      full_name: profileData.name,
      state: profileData.state,
      category: profileData.category,
      family_income: parseFloat(profileData.income || 0),
      current_qualification: profileData.qualification,
      marks_percentage: parseFloat(profileData.marks || 0)
    });

    // ✅ FastAPI endpoint
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
    return data;
  } catch (error) {
    console.error('❌ API Error:', error);
    throw error;
  }
};

export const healthCheck = async () => {
  try {
    // ✅ FastAPI health endpoint
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