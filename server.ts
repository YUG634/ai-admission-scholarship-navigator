import express from "express";
import path from "path";
import multer from "multer";
import dotenv from "dotenv";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI, Type } from "@google/genai";

dotenv.config();

const app = express();
const PORT = 3000;

// Setup multer in-memory storage for PDF uploads
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024, // Limit to 10MB
  },
});

app.use(express.json());

// Initialize Gemini Client
const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
  httpOptions: {
    headers: {
      "User-Agent": "aistudio-build",
    },
  },
});

// Health check API endpoint
app.get("/api/health", (req, res) => {
  res.json({ status: "healthy", timestamp: new Date().toISOString() });
});

// Primary PDF Upload and Agent System Endpoint
app.post("/api/upload-pdf", upload.single("pdf"), async (req, res) => {
  try {
    const file = req.file;
    const profileString = req.body.profile;

    if (!file) {
      return res.status(400).json({ error: "No PDF file uploaded" });
    }

    if (!profileString) {
      return res.status(400).json({ error: "Missing student profile data" });
    }

    let profile;
    try {
      profile = JSON.parse(profileString);
    } catch (e) {
      return res.status(400).json({ error: "Invalid profile JSON format" });
    }

    // Convert PDF buffer to Base64 Part for Gemini API
    const pdfBase64 = file.buffer.toString("base64");
    const pdfPart = {
      inlineData: {
        data: pdfBase64,
        mimeType: "application/pdf",
      },
    };

    console.log("Starting Agent Pipeline...");

    // ==========================================
    // AGENT 1: Document Analysis Agent
    // ==========================================
    console.log("Invoking Agent 1: Document Analysis Agent...");
    const agent1Prompt = `You are an expert document analyst. Extract the following structured data from the provided scholarship or admission notification PDF:
- scholarship_name: Name of the scholarship or scheme.
- deadline: Application deadline or closing date.
- eligibility_criteria: Key eligibility conditions (income limits, academic criteria, state, categories).
- required_documents: List of necessary certificates, ID proofs, marksheet, income certificates.
- instructions: Key application steps, links, or crucial instructions.

Be precise. If some information is not present, write 'Not specified' or list what is available.`;

    const agent1Response = await ai.models.generateContent({
      model: "gemini-3.1-flash-lite",  // ✅ CHANGED: Using available model
      contents: [pdfPart, { text: agent1Prompt }],
      config: {
        systemInstruction: "You are the Document Analysis Agent, specialized in analyzing institutional notifications and scholarship announcements.",
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            scholarship_name: { type: Type.STRING },
            deadline: { type: Type.STRING },
            eligibility_criteria: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
            },
            required_documents: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
            },
            instructions: { type: Type.STRING },
          },
          required: ["scholarship_name", "deadline", "eligibility_criteria", "required_documents", "instructions"],
        },
      },
    });

    const docAnalysis = JSON.parse(agent1Response.text || "{}");
    console.log("Agent 1 analysis complete:", docAnalysis.scholarship_name);

    // ==========================================
    // AGENT 2: Eligibility Agent
    // ==========================================
    console.log("Invoking Agent 2: Eligibility Agent...");
    const studentProfileText = `
Student Profile:
- Name: ${profile.name || "N/A"}
- State of Residence: ${profile.state || "N/A"}
- Social Category (Cast/Category): ${profile.category || "N/A"}
- Annual Family Income (INR): ${profile.income || "N/A"}
- Qualification/Current Grade: ${profile.qualification || "N/A"}
- Current Marks / Percentage / CGPA: ${profile.marks || "N/A"}
`;

    const agent2Prompt = `You are an eligibility evaluation agent.
Compare the student profile against the extracted scholarship/admission eligibility criteria.

Student Profile:
${studentProfileText}

Extracted Criteria:
${JSON.stringify(docAnalysis.eligibility_criteria)}

Determine the eligibility status:
- "Eligible": Student meets all specified requirements.
- "Partially Eligible": Student meets most but might need to clarify family income/state/marks, or needs optional requirements.
- "Not Eligible": Student fails to meet major critical requirements (e.g., qualification, minimum marks, state limitations).

Provide a list of detailed reasons explaining why the student is eligible, partially eligible, or not eligible. Make it positive, encouraging, and clear for rural or first-generation students.`;

    const agent2Response = await ai.models.generateContent({
      model: "gemini-3.1-flash-lite",  // ✅ CHANGED: Using available model
      contents: [{ text: agent2Prompt }],
      config: {
        systemInstruction: "You are the Eligibility Evaluation Agent. Your goal is to map student metrics directly against institutional rules and produce highly accurate status breakdowns.",
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            status: { type: Type.STRING, description: "Must be 'Eligible', 'Not Eligible', or 'Partially Eligible'" },
            reasons: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
              description: "Clear list of reasons detailing how student profile meets/fails criteria",
            },
          },
          required: ["status", "reasons"],
        },
      },
    });

    const eligibilityCheck = JSON.parse(agent2Response.text || "{}");
    console.log("Agent 2 evaluation complete:", eligibilityCheck.status);

    // ==========================================
    // AGENT 3: Action Plan Agent
    // ==========================================
    console.log("Invoking Agent 3: Action Plan Agent...");
    const agent3Prompt = `You are a strategic advisor and action plan generator.
Generate a personalized, actionable guide for the student based on the scholarship requirements and their eligibility status.

Student Profile:
${studentProfileText}

Scholarship Analysis:
- Name: ${docAnalysis.scholarship_name}
- Deadline: ${docAnalysis.deadline}
- Required Documents: ${JSON.stringify(docAnalysis.required_documents)}

Eligibility Evaluation:
- Status: ${eligibilityCheck.status}
- Reasons: ${JSON.stringify(eligibilityCheck.reasons)}

Provide:
1. checklist: A detailed timeline list of immediate next actions. Each action must have a task description, priority ('High', 'Medium', 'Low'), and timeframe ('Immediate', 'Within 3 Days', 'Before Deadline').
2. missing_documents: A list of documents the student must prepare or obtain (e.g., State Domicile Certificate, Caste Certificate, Income Certificate, Previous marksheets) based on their profile and the scholarship's required list.
3. recommendations: Step-by-step encouraging advice, including application submission strategy, check-ins, or alternative suggestions if they are not eligible.`;

    const agent3Response = await ai.models.generateContent({
      model: "gemini-3.1-flash-lite",  // ✅ CHANGED: Using available model
      contents: [{ text: agent3Prompt }],
      config: {
        systemInstruction: "You are the Action Plan Agent. You craft highly structured, reassuring, step-by-step guides for students applying to higher education or financial aid schemes.",
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            checklist: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  task: { type: Type.STRING },
                  priority: { type: Type.STRING },
                  timeframe: { type: Type.STRING },
                },
                required: ["task", "priority", "timeframe"],
              },
            },
            missing_documents: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
            },
            recommendations: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
            },
          },
          required: ["checklist", "missing_documents", "recommendations"],
        },
      },
    });

    const actionPlan = JSON.parse(agent3Response.text || "{}");
    console.log("Agent 3 plan complete.");

    // Return combined agent results to the frontend
    res.json({
      success: true,
      analysis: docAnalysis,
      eligibility: eligibilityCheck,
      actionPlan: actionPlan,
    });

  } catch (error: any) {
    console.error("Pipeline processing failed:", error);
    res.status(500).json({
      success: false,
      error: error.message || "An error occurred during agent analysis pipeline",
    });
  }
});

// Vite Middleware & Static Asset Delivery Setup
async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server successfully started on http://0.0.0.0:${PORT}`);
  });
}

startServer();