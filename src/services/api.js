// Use the Node.js server on port 3000
const API_BASE_URL = 'http://localhost:3000';

export const analyzeScholarship = async (pdfFile, profileData) => {
  if (!pdfFile) {
    throw new Error('No PDF file provided');
  }

  const formData = new FormData();
  formData.append('pdf', pdfFile);
  formData.append('profile', JSON.stringify({
    name: profileData.name || '',
    state: profileData.state || '',
    category: profileData.category || 'General',
    income: String(profileData.income || '0').replace(/,/g, ''),
    qualification: profileData.qualification || '',
    marks: String(profileData.marks || '0').replace('%', '').trim()
  }));

  try {
    console.log('📤 Sending request to Node.js server...');
    console.log('📄 File:', pdfFile.name, pdfFile.size, 'bytes');
    console.log('👤 Profile:', {
      name: profileData.name,
      state: profileData.state,
      category: profileData.category,
      income: String(profileData.income || '0').replace(/,/g, ''),
      qualification: profileData.qualification,
      marks: String(profileData.marks || '0').replace('%', '').trim()
    });

    const response = await fetch(`${API_BASE_URL}/api/upload-pdf`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('❌ Server error:', errorData);
      throw new Error(errorData.error || 'Analysis failed');
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
    const response = await fetch(`${API_BASE_URL}/api/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return await response.json();
  } catch (error) {
    console.error('Health check failed:', error);
    return { status: 'unhealthy', error: error.message };
  }
};