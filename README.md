# 🎓 AI Admission & Scholarship Navigator

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=white)](https://reactjs.org/)
[![Google ADK](https://img.shields.io/badge/Google_ADK-0.1.0-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://github.com/google/adk-python)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

</div>

---

## 📖 Overview

**AI Admission & Scholarship Navigator** is a multi-agent AI system that helps students understand complex admission notifications and scholarship PDFs. It uses Google ADK and Gemini 2.5 Flash to transform confusing documents into personalized, actionable insights.

### The Problem

Students face significant challenges with admission and scholarship documents:
- Complex legal and educational jargon
- Confusing eligibility criteria
- Difficult-to-track deadlines
- Unclear document requirements
- Misinterpreted special categories as mandatory

### The Solution

Three specialized AI agents work together to:
1. **Analyze Documents** - Extract and classify information
2. **Check Eligibility** - Fairly compare student profiles against requirements
3. **Generate Action Plans** - Create personalized checklists and timelines

---

## ✨ Features

### Multi-Agent AI System

| Agent | Function | Key Capabilities |
|-------|----------|------------------|
| Document Analysis | PDF Processing & Classification | Extracts details, distinguishes mandatory vs optional |
| Eligibility Check | Profile Comparison | Fair assessment, never rejects for optional categories |
| Action Plan | Personalized Planning | Creates checklists with priorities, deadlines, and timelines |

### Smart Document Classification

- Distinguishes between Scholarship and Admission notifications
- Separates Mandatory Requirements from Optional Special Categories
- Identifies Alternative Admission Paths
- Never treats special categories as mandatory

### Personalized Action Plans

- Immediate actions with priorities
- Checklist with High/Medium/Low priorities
- Missing documents identification
- Strategic recommendations
- Week-by-week timeline
- Interactive checklist tracking

### Beautiful User Interface

- Modern, Google-inspired design
- Fully responsive for mobile and desktop
- Real-time agent status updates
- Smooth animations with Framer Motion
- Drag-and-drop PDF upload

---

## 🏗️ Architecture

### System Flow

```
User Browser → React Frontend → FastAPI Backend → Google ADK Agents → Gemini 2.5 Flash
```

### Agent Pipeline

**1. Document Analysis Agent**
- Extracts and classifies document information
- Separates mandatory from optional criteria
- Identifies alternative admission paths

**2. Eligibility Agent**
- Compares profile against requirements
- Never penalizes for optional categories
- Provides detailed reasoning

**3. Action Plan Agent**
- Creates personalized checklists
- Identifies missing documents
- Generates timeline and next steps

---

## 🛠️ Tech Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Core language |
| FastAPI | 0.115+ | Web framework |
| Google ADK | 0.1.0 | Agent framework |
| Gemini 2.5 Flash | Latest | AI model |
| PyPDF2 | 3.0+ | PDF text extraction |
| Uvicorn | 0.24+ | ASGI server |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18 | UI library |
| Vite | 5.0+ | Build tool |
| Tailwind CSS | 4.0+ | Styling |
| Framer Motion | 10.0+ | Animations |
| Lucide React | Latest | Icons |
| TypeScript | 5.0+ | Type safety |

### Deployment

| Service | Purpose |
|---------|---------|
| Render | Backend hosting (free tier) |
| Netlify | Frontend hosting (free tier) |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- Google Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/YUG634/ai-admission-scholarship-navigator.git
cd ai-admission-scholarship-navigator

# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# Run the server
python run.py
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

## 📊 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint with service info |
| GET | `/health` | Health check with component status |
| POST | `/api/v1/analyze` | Analyze PDF with student profile |

### Example Request

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "pdf_file=@scholarship.pdf" \
  -F "full_name=John Doe" \
  -F "state=Maharashtra" \
  -F "category=General" \
  -F "family_income=500000" \
  -F "current_qualification=B.Sc" \
  -F "marks_percentage=85"
```

### Example Response

```json
{
  "analysis": {
    "document_type": "admission",
    "scholarship_name": "First-Year Undergraduate Programme",
    "deadline": "June 05, 2025",
    "mandatory_requirements": ["12th pass", "Entrance exam required"],
    "special_categories": ["Sindhi Minority", "In-house students"],
    "alternative_admission_paths": ["MHCET", "H-CET"]
  },
  "eligibility": {
    "status": "Partially Eligible",
    "score": 65,
    "reasons": ["Meets academic requirements", "Entrance exam info missing"]
  },
  "action_plan": {
    "immediate_actions": ["Register for entrance exam"],
    "checklist": [],
    "missing_documents": [],
    "timeline": {}
  }
}
```

---

## 🚢 Deployment

### Backend (Render)

1. Create account at [Render](https://render.com)
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables: `GEMINI_API_KEY`, `ALLOWED_ORIGINS`
5. Click "Create Web Service"

### Frontend (Netlify)

1. Create account at [Netlify](https://netlify.com)
2. Click "Add new site" → "Import an existing project"
3. Connect GitHub repository
4. Settings:
   - Build Command: `npm run build`
   - Publish Directory: `dist`
   - Add environment variable: `VITE_API_BASE_URL`
5. Click "Deploy site"

---

## 📁 Project Structure

```
ai-admission-scholarship-navigator/
├── backend/
│   ├── app/
│   │   ├── agents/          # ADK agents
│   │   ├── api/             # FastAPI routes
│   │   ├── models/          # Pydantic schemas
│   │   ├── orchestrator/    # Agent orchestration
│   │   ├── services/        # Gemini service
│   │   └── utils/           # Utilities
│   ├── tests/               # Unit tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   └── types/           # TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Guidelines

- Follow PEP 8 for Python
- Use ESLint and Prettier for frontend
- Write tests for new features
- Update documentation

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Google ADK - Agent framework
- Google Gemini - AI capabilities
- FastAPI - Web framework
- React - UI library
- Google Cloud & Gen AI Academy - "Meet the Builders" initiative

---

## 👨‍💻 Made By

### Yug Agrawal

[![GitHub](https://img.shields.io/badge/GitHub-YUG634-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/YUG634)
[![LinkedIn](www.linkedin.com/in/yug-agrawal-101bb11a0)
[![Email](https://img.shields.io/badge/Email-yugagrawalmng%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white)](mailto:yugagrawalmng@gmail.com)

---

<div align="center">
  <p>Built with ❤️ for the Google Cloud & Gen AI Academy "Meet the Builders" initiative</p>
</div>
