import React, { useState, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import { 
  Upload, FileText, CheckCircle, AlertTriangle, XCircle, 
  Clock, Calendar, FileCheck, MapPin, User, GraduationCap, 
  Percent, IndianRupee, Sparkles, ShieldAlert, ArrowRight, 
  Layers, HelpCircle, RefreshCw, FileQuestion
} from "lucide-react";
import { 
  StudentProfile, ScholarshipAnalysis, 
  EligibilityEvaluation, ActionPlan, AgentPipelineResponse 
} from "../types";
import { analyzeScholarship, healthCheck } from "../services/api";

export default function Dashboard() {
  // Student Profile state
  const [profile, setProfile] = useState<StudentProfile>({
    name: "",
    state: "",
    category: "General",
    income: "",
    qualification: "",
    marks: "",
  });

  // File Upload State
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);

  // Agent Pipeline Processing State
  const [loading, setLoading] = useState(false);
  const [activeAgent, setActiveAgent] = useState<number>(0);
  const [currentStatusText, setCurrentStatusText] = useState("");
  
  // Results
  const [results, setResults] = useState<AgentPipelineResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Interactive Checklist completed items
  const [completedTasks, setCompletedTasks] = useState<Record<string, boolean>>({});

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Pre-seeded high-fidelity sample datasets to let the user instantly test the multi-agent system
  const sampleScholarships = [
    {
      title: "National Means-cum-Merit Scholarship (NMMSS)",
      filename: "nmmss_guidelines_2026.pdf",
      profile: {
        name: "Aarav Sharma",
        state: "Maharashtra",
        category: "OBC",
        income: "120000",
        qualification: "Class 8 Passed",
        marks: "65%",
      },
      data: {
        analysis: {
          scholarship_name: "National Means-cum-Merit Scholarship Scheme (NMMSS)",
          deadline: "December 31, 2026",
          eligibility_criteria: [
            "Students whose parental income from all sources is not more than INR 3,500,000 per annum are eligible.",
            "Must have scored at least 55% marks or equivalent grade in Class 7 examination (5% relaxation for SC/ST).",
            "Must be studying as a regular student in a Government, Government-aided or local body school.",
            "Students of Jawahar Navodaya Vidyalaya, Kendriya Vidyalaya, and private schools are NOT eligible."
          ],
          required_documents: [
            "Class 7 or 8 Marksheet / Progress report",
            "Caste Certificate (for SC/ST/OBC representation)",
            "Parental Income Certificate issued by competent state authority",
            "Disability Certificate (if applicable)",
            "Domicile Certificate of Maharashtra"
          ],
          instructions: "Apply online through the National Scholarship Portal (NSP). Create a student profile, upload required certificates, and submit before the local district verification deadline."
        },
        eligibility: {
          status: "Eligible",
          reasons: [
            "Your annual family income of INR 120,000 is well below the maximum limit of INR 350,000.",
            "Your academic score of 65% meets the 55% requirement easily.",
            "Maharashtra state regular government school criteria is satisfied by your profile parameters."
          ]
        },
        actionPlan: {
          checklist: [
            { task: "Register and create student profile on National Scholarship Portal (NSP)", priority: "High", timeframe: "Within 3 Days" },
            { task: "Obtain Income Certificate from local Tehsildar office", priority: "High", timeframe: "Within 1 week" },
            { task: "Get Class 7 official marksheet attested by the School Principal", priority: "Medium", timeframe: "Before Deadline" },
            { task: "Submit Caste Certificate for OBC quota verification", priority: "Medium", timeframe: "Before Deadline" }
          ],
          missing_documents: [
            "Parental Income Certificate (issued by State Authority)",
            "Domicile Certificate of Maharashtra",
            "School Registration ID and Principal's Attestation Form"
          ],
          recommendations: [
            "Start the income certificate application immediately since regional administrative offices can take up to 7-10 working days.",
            "Double check that the name spelled in your school marksheet matches your Aadhaar card exactly to prevent NSP portal verification rejection."
          ]
        }
      }
    },
    {
      title: "Pragati Scholarship for Girls (Technical Degree)",
      filename: "aicte_pragati_scheme_2026.pdf",
      profile: {
        name: "Ananya Iyer",
        state: "Tamil Nadu",
        category: "General",
        income: "450000",
        qualification: "First Year B.Tech / BE",
        marks: "85%",
      },
      data: {
        analysis: {
          scholarship_name: "AICTE Pragati Scholarship Scheme for Girl Students",
          deadline: "November 15, 2026",
          eligibility_criteria: [
            "The girl student should be admitted to the First year of Degree level course in an AICTE approved institution.",
            "Maximum of two girl children per family are eligible.",
            "Family income from all sources should not exceed INR 800,000 per annum during the current financial year."
          ],
          required_documents: [
            "Class 10 and 12 Marksheets",
            "Admission letter issued by central counseling authority",
            "Tuition fee receipt paid for the current academic year",
            "Family Income Certificate issued by Tehsildar",
            "Declaration by parent stating that the education details are true"
          ],
          instructions: "Eligible girls must register on the National Scholarship Portal (NSP). Ensure the college is AICTE approved during portal selection."
        },
        eligibility: {
          status: "Partially Eligible",
          reasons: [
            "Your family income (INR 450,000) is well below the INR 800,000 threshold.",
            "Academic qualification and marks (85%) meet central AICTE guidelines.",
            "Need to ensure your college/institution is formally listed as AICTE approved before submitting."
          ]
        },
        actionPlan: {
          checklist: [
            { task: "Confirm college AICTE approval status in the administrative office", priority: "High", timeframe: "Immediate" },
            { task: "Retrieve original Tuition Fee receipt and Admission Letter", priority: "High", timeframe: "Within 3 Days" },
            { task: "Prepare signed Parent Self-Declaration Form", priority: "Medium", timeframe: "Before Deadline" }
          ],
          missing_documents: [
            "College Admission Letter & Tuition Fee Receipt",
            "AICTE College Approval Certificate Copy",
            "Parental Declaration Form"
          ],
          recommendations: [
            "Check with your institute's nodal officer first. Colleges often have a designated desk to fast-track Pragati scholarship approvals.",
            "Since you are 'Partially Eligible', verifying the AICTE college status is your top priority before filling out any online forms."
          ]
        }
      }
    }
  ];

  // Drag and drop handlers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === "application/pdf") {
        setPdfFile(file);
        setError(null);
      } else {
        setError("Only PDF documents are supported.");
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.type === "application/pdf") {
        setPdfFile(file);
        setError(null);
      } else {
        setError("Only PDF documents are supported.");
      }
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  const loadSample = (sampleIdx: number) => {
    const sample = sampleScholarships[sampleIdx];
    setProfile(sample.profile);
    setPdfFile(new File([], sample.filename, { type: "application/pdf" }));
    setResults(sample.data);
    setError(null);
    setCompletedTasks({});
    // Scroll smoothly to dashboard results
    document.getElementById("results-scroll-anchor")?.scrollIntoView({ behavior: "smooth" });
  };

  // Submit the form and run the actual API pipeline
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate PDF
    if (!pdfFile) {
      setError("Please upload a Scholarship/Admission PDF or select a sample above.");
      return;
    }

    // Validate profile fields
    const requiredFields = ['name', 'state', 'category', 'income', 'qualification', 'marks'];
    const missingFields = requiredFields.filter(field => !profile[field as keyof StudentProfile]);
    
    if (missingFields.length > 0) {
      setError(`Please fill in all required fields: ${missingFields.join(', ')}`);
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);
    setCompletedTasks({});

    try {
      // Step 1: Document Analysis Agent
      setActiveAgent(1);
      setCurrentStatusText("Agent 1: Extracting guidelines, dates & eligibility criteria from PDF...");
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Step 2: Eligibility Agent
      setActiveAgent(2);
      setCurrentStatusText("Agent 2: Mapping your student profile against extracted guidelines...");
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Step 3: Action Plan Agent
      setActiveAgent(3);
      setCurrentStatusText("Agent 3: Generating personalized checklist and application strategy...");
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Call the actual API
      const response = await analyzeScholarship(pdfFile, profile);
      
      console.log('📊 Full response:', response);
      console.log('📊 Analysis:', response.analysis);
      console.log('📊 Eligibility:', response.eligibility);
      console.log('📊 Action Plan:', response.actionPlan || response.action_plan);

      // ✅ FIX: Check both camelCase (actionPlan) and snake_case (action_plan)
      const actionPlanData = response.actionPlan || response.action_plan || {};
      
      // Transform API response to match your UI structure
      const transformedResults: AgentPipelineResponse = {
        success: true,
        analysis: {
          scholarship_name: response.analysis?.scholarship_name || "Scholarship Name Not Found",
          deadline: response.analysis?.deadline || "Deadline Not Specified",
          eligibility_criteria: response.analysis?.eligibility_criteria || [],
          required_documents: response.analysis?.required_documents || [],
          instructions: response.analysis?.instructions || 
                        response.analysis?.important_instructions?.join('\n') || 
                        "Instructions not available"
        },
        eligibility: {
          status: response.eligibility?.status as 'Eligible' | 'Partially Eligible' | 'Not Eligible' || 'Not Eligible',
          reasons: response.eligibility?.reasons || ["Unable to determine eligibility"]
        },
        actionPlan: {
          checklist: actionPlanData.checklist?.map((item: any) => ({
            task: item.task,
            priority: item.priority as 'High' | 'Medium' | 'Low',
            timeframe: item.timeframe || item.deadline || 'ASAP'
          })) || [],
          missing_documents: actionPlanData.missing_documents || [],
          recommendations: actionPlanData.recommendations || []
        }
      };

      console.log('📊 Transformed results:', transformedResults);
      setResults(transformedResults);
      
      // Scroll to results
      setTimeout(() => {
        document.getElementById("results-scroll-anchor")?.scrollIntoView({ behavior: "smooth" });
      }, 100);

    } catch (err: any) {
      console.error('❌ Error in handleSubmit:', err);
      setError(err.message || "An unexpected error occurred during the analysis pipeline. Please try again.");
    } finally {
      setLoading(false);
      setActiveAgent(0);
    }
  };

  const toggleTask = (taskName: string) => {
    setCompletedTasks((prev) => ({
      ...prev,
      [taskName]: !prev[taskName],
    }));
  };

  const resetConsole = () => {
    setPdfFile(null);
    setResults(null);
    setError(null);
    setCompletedTasks({});
    setProfile({
      name: "",
      state: "",
      category: "General",
      income: "",
      qualification: "",
      marks: "",
    });
  };

  return (
    <section id="navigator" className="py-20 px-4 md:px-8 max-w-[1400px] mx-auto border-t border-white/5 bg-zinc-950">
      {/* Section Title */}
      <div className="text-center mb-16">
        <span className="text-accent-blue text-xs font-bold uppercase tracking-widest bg-accent-deep/20 px-3 py-1 rounded-full">
          OPERATIONAL DESK
        </span>
        <h2 className="font-display font-bold text-3xl md:text-5xl text-white mt-3">
          AI Navigator Control Console
        </h2>
        <p className="text-zinc-400 mt-2 max-w-xl mx-auto text-sm md:text-base">
          Fill out your candidate metrics and upload the scholarship criteria PDF. Our active agent system will map out your route.
        </p>

        {/* Pre-seeded Samples Banner */}
        <div className="mt-8 flex flex-wrap justify-center gap-4">
          <span className="text-xs text-zinc-500 self-center w-full md:w-auto mb-2 md:mb-0">
            💡 No PDF handy? Load a high-fidelity sample:
          </span>
          {sampleScholarships.map((sample, idx) => (
            <button
              key={idx}
              onClick={() => loadSample(idx)}
              className="px-4 py-2 text-xs font-medium bg-zinc-900 border border-zinc-800 text-zinc-300 rounded-xl hover:border-accent-blue/50 hover:bg-zinc-800/80 transition-all flex items-center gap-2 cursor-pointer"
            >
              <FileCheck className="w-3.5 h-3.5 text-accent-blue" />
              {sample.title.split("(")[0]}
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* LEFT COLUMN: UPLOADER & STUDENT FORM */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-zinc-900/50 border border-white/5 rounded-3xl p-6 md:p-8 backdrop-blur-md shadow-xl">
            <h3 className="font-display font-bold text-xl text-white mb-6 flex items-center gap-2">
              <span className="w-2.5 h-2.5 bg-accent-blue rounded-full animate-ping" />
              Candidate Profile & Document File
            </h3>

            <form onSubmit={handleSubmit} className="space-y-6">
              
              {/* FILE UPLOAD FIELD */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider block">
                  Scholarship / Admission PDF Circular
                </label>
                
                <div
                  onDragEnter={handleDrag}
                  onDragOver={handleDrag}
                  onDragLeave={handleDrag}
                  onDrop={handleDrop}
                  onClick={triggerFileSelect}
                  className={`relative cursor-pointer border-2 border-dashed rounded-2xl p-6 flex flex-col items-center justify-center text-center transition-all min-h-[160px] ${
                    dragActive 
                      ? "border-accent-blue bg-accent-deep/10" 
                      : pdfFile 
                        ? "border-emerald-500/50 bg-emerald-950/10" 
                        : "border-zinc-800 hover:border-zinc-700 bg-zinc-950/50"
                  }`}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="application/pdf"
                    onChange={handleFileChange}
                    className="hidden"
                  />

                  {pdfFile ? (
                    <div className="space-y-2">
                      <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl w-fit mx-auto">
                        <FileCheck className="w-8 h-8" />
                      </div>
                      <p className="text-sm font-semibold text-white max-w-[250px] truncate mx-auto">
                        {pdfFile.name}
                      </p>
                      <p className="text-xs text-zinc-500">
                        File loaded successfully. Ready to analyze.
                      </p>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setPdfFile(null);
                        }}
                        className="text-xs font-semibold text-rose-400 hover:text-rose-300 underline mt-2 inline-block cursor-pointer"
                      >
                        Remove file
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-2 text-zinc-400">
                      <div className="p-3 bg-white/5 rounded-xl w-fit mx-auto group-hover:scale-105 transition-transform">
                        <Upload className="w-8 h-8 text-accent-blue" />
                      </div>
                      <p className="text-sm font-medium">
                        Drag & Drop or <span className="text-accent-blue underline">browse file</span>
                      </p>
                      <p className="text-xs text-zinc-500">
                        Supports PDF circular notifications up to 10MB
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* CANDIDATE PROFILE PARAMETERS */}
              <div className="space-y-4 pt-4 border-t border-zinc-800">
                <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest block">
                  CANDIDATE METRICS
                </span>

                {/* Name */}
                <div className="grid grid-cols-1 gap-1">
                  <label className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5 text-accent-blue" /> Full Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={profile.name}
                    onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                    className="px-4 py-2.5 rounded-xl bg-zinc-950 border border-zinc-850 text-white text-sm focus:outline-hidden focus:border-accent-blue transition-all"
                    placeholder="Enter full name"
                  />
                </div>

                {/* State & social Category */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="grid grid-cols-1 gap-1">
                    <label className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-accent-blue" /> State *
                    </label>
                    <input
                      type="text"
                      required
                      value={profile.state}
                      onChange={(e) => setProfile({ ...profile, state: e.target.value })}
                      className="px-4 py-2.5 rounded-xl bg-zinc-950 border border-zinc-850 text-white text-sm focus:outline-hidden focus:border-accent-blue transition-all"
                      placeholder="e.g., Maharashtra"
                    />
                  </div>

                  <div className="grid grid-cols-1 gap-1">
                    <label className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-accent-blue" /> Category *
                    </label>
                    <select
                      value={profile.category}
                      onChange={(e) => setProfile({ ...profile, category: e.target.value })}
                      className="px-4 py-2.5 rounded-xl bg-zinc-950 border border-zinc-850 text-white text-sm focus:outline-hidden focus:border-accent-blue transition-all"
                    >
                      <option value="General">General / Open</option>
                      <option value="OBC">OBC</option>
                      <option value="SC">Scheduled Caste (SC)</option>
                      <option value="ST">Scheduled Tribe (ST)</option>
                      <option value="EWS">Economically Weaker Section (EWS)</option>
                    </select>
                  </div>
                </div>

                {/* Income & Qualification */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="grid grid-cols-1 gap-1">
                    <label className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5">
                      <IndianRupee className="w-3.5 h-3.5 text-accent-blue" /> Family Income (INR) *
                    </label>
                    <input
                      type="number"
                      required
                      value={profile.income}
                      onChange={(e) => setProfile({ ...profile, income: e.target.value })}
                      className="px-4 py-2.5 rounded-xl bg-zinc-950 border border-zinc-850 text-white text-sm focus:outline-hidden focus:border-accent-blue transition-all"
                      placeholder="Annual Income in INR"
                    />
                  </div>

                  <div className="grid grid-cols-1 gap-1">
                    <label className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5">
                      <GraduationCap className="w-3.5 h-3.5 text-accent-blue" /> Qualification *
                    </label>
                    <input
                      type="text"
                      required
                      value={profile.qualification}
                      onChange={(e) => setProfile({ ...profile, qualification: e.target.value })}
                      className="px-4 py-2.5 rounded-xl bg-zinc-950 border border-zinc-850 text-white text-sm focus:outline-hidden focus:border-accent-blue transition-all"
                      placeholder="e.g., Class 12 Passed"
                    />
                  </div>
                </div>

                {/* Marks Percentage */}
                <div className="grid grid-cols-1 gap-1">
                  <label className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5">
                    <Percent className="w-3.5 h-3.5 text-accent-blue" /> Previous Examination Marks *
                  </label>
                  <input
                    type="text"
                    required
                    value={profile.marks}
                    onChange={(e) => setProfile({ ...profile, marks: e.target.value })}
                    className="px-4 py-2.5 rounded-xl bg-zinc-950 border border-zinc-850 text-white text-sm focus:outline-hidden focus:border-accent-blue transition-all"
                    placeholder="e.g., 85% or 9.2 CGPA"
                  />
                </div>
              </div>

              {/* ACTION BTN */}
              <button
                type="submit"
                disabled={loading}
                className="w-full relative overflow-hidden py-4 rounded-xl bg-accent-blue hover:bg-accent-blue/90 disabled:bg-zinc-800 text-white font-semibold flex items-center justify-center gap-3 shadow-lg hover:shadow-accent-blue/20 transition-all cursor-pointer"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin text-white" />
                    <span>Executing Agent System...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 text-yellow-300" />
                    <span>Compare & Map Eligibility</span>
                  </>
                )}
              </button>

            </form>
          </div>
        </div>

        {/* RIGHT COLUMN: DETAILED ANALYSIS & RESULTS */}
        <div id="results-scroll-anchor" className="lg:col-span-7 space-y-6 min-h-[500px]">
          
          <AnimatePresence mode="wait">
            
            {/* 1. AGENTS RUNNING LOADER */}
            {loading && (
              <motion.div
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                className="bg-zinc-900 border border-accent-blue/30 rounded-3xl p-8 flex flex-col items-center justify-center min-h-[480px] text-center"
              >
                {/* Visual pulse core */}
                <div className="relative mb-8">
                  <div className="w-24 h-24 rounded-full bg-accent-deep/20 border border-accent-blue/40 flex items-center justify-center">
                    <Layers className="w-10 h-10 text-accent-blue animate-pulse" />
                  </div>
                  <div className="absolute top-0 left-0 w-24 h-24 rounded-full border border-accent-blue/50 animate-ping opacity-25" />
                </div>

                <h3 className="font-display font-bold text-2xl text-white">
                  Active Multi-Agent Collaboration
                </h3>
                
                {/* Interactive Status Bar */}
                <div className="w-full max-w-md bg-zinc-950 rounded-full h-2.5 overflow-hidden border border-zinc-800 mt-6 relative">
                  <motion.div
                    className="bg-accent-blue h-full rounded-full"
                    animate={{ 
                      width: activeAgent === 1 ? "33%" : activeAgent === 2 ? "66%" : "100%" 
                    }}
                    transition={{ duration: 1.5, ease: "easeInOut" }}
                  />
                </div>

                {/* Sub status steps */}
                <div className="w-full max-w-md grid grid-cols-3 gap-2 mt-4 text-[10px] font-bold text-zinc-500 uppercase tracking-wider">
                  <span className={activeAgent >= 1 ? "text-accent-blue" : ""}>01. Document</span>
                  <span className={activeAgent >= 2 ? "text-accent-blue" : ""}>02. Eligibility</span>
                  <span className={activeAgent >= 3 ? "text-accent-blue" : ""}>03. Action Plan</span>
                </div>

                <p className="text-zinc-300 mt-8 font-mono text-sm max-w-md bg-zinc-950 p-4 rounded-xl border border-zinc-800">
                  {currentStatusText}
                </p>

                <p className="text-zinc-500 text-xs mt-4">
                  Gemini is reading coordinates and distilling scholarship parameters in real-time.
                </p>
              </motion.div>
            )}

            {/* 2. INITIAL IDLE STATE (NO RESULT / NOT LOADING) */}
            {!loading && !results && !error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-zinc-900/20 border border-zinc-800 border-dashed rounded-3xl p-8 flex flex-col items-center justify-center min-h-[480px] text-center"
              >
                <div className="p-4 bg-zinc-900 rounded-2xl text-zinc-600 mb-4 border border-zinc-800">
                  <FileQuestion className="w-12 h-12" />
                </div>
                <h4 className="font-display font-semibold text-lg text-zinc-300">
                  Console Standby Mode
                </h4>
                <p className="text-zinc-500 text-sm max-w-sm mt-2">
                  No active documents evaluated. Please fill out the profile form on the left, upload a circular, and run the mapper to receive AI reports.
                </p>
                <div className="mt-6 flex gap-2">
                  <button
                    onClick={() => loadSample(0)}
                    className="px-4 py-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 text-xs font-semibold text-zinc-300 cursor-pointer"
                  >
                    Load NMMSS Sample
                  </button>
                  <button
                    onClick={() => loadSample(1)}
                    className="px-4 py-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 text-xs font-semibold text-zinc-300 cursor-pointer"
                  >
                    Load Pragati Girls Sample
                  </button>
                </div>
              </motion.div>
            )}

            {/* 3. ERROR OUT */}
            {error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-rose-950/20 border border-rose-900/40 rounded-3xl p-8 flex flex-col items-center justify-center min-h-[480px] text-center"
              >
                <div className="p-3 bg-rose-500/10 text-rose-400 rounded-xl mb-4">
                  <ShieldAlert className="w-10 h-10" />
                </div>
                <h4 className="font-display font-bold text-xl text-rose-300">
                  Analysis Pipeline Interrupted
                </h4>
                <p className="text-zinc-400 text-sm max-w-md mt-2">
                  {error}
                </p>
                <button
                  onClick={resetConsole}
                  className="px-5 py-2.5 rounded-xl bg-rose-900 text-white font-semibold text-xs mt-6 hover:bg-rose-800 transition-colors cursor-pointer"
                >
                  Reset Operational Desk
                </button>
              </motion.div>
            )}

            {/* 4. HIGH-FIDELITY RESULTS PRESENTATION */}
            {results && !loading && (
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                className="space-y-6"
              >
                
                {/* 4a. ELIGIBILITY GLOW STATUS BANNER */}
                <div className={`p-6 rounded-3xl border flex items-start gap-4 shadow-lg ${
                  results.eligibility?.status === "Eligible" 
                    ? "bg-emerald-950/20 border-emerald-500/30 text-emerald-300"
                    : results.eligibility?.status === "Partially Eligible"
                      ? "bg-amber-950/20 border-amber-500/30 text-amber-300"
                      : "bg-rose-950/20 border-rose-500/30 text-rose-300"
                }`}>
                  <div className="p-3 bg-white/5 rounded-2xl">
                    {results.eligibility?.status === "Eligible" && <CheckCircle className="w-8 h-8 text-emerald-400" />}
                    {results.eligibility?.status === "Partially Eligible" && <AlertTriangle className="w-8 h-8 text-amber-400" />}
                    {results.eligibility?.status === "Not Eligible" && <XCircle className="w-8 h-8 text-rose-400" />}
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] uppercase font-bold tracking-widest text-zinc-400">Agent Eligibility Determination</span>
                    <h4 className="font-display font-bold text-2xl text-white">
                      {results.eligibility?.status}
                    </h4>
                    <p className="text-sm text-zinc-300">
                      {results.eligibility?.status === "Eligible" 
                        ? "Congratulations! Your metrics align seamlessly with institutional rules." 
                        : results.eligibility?.status === "Partially Eligible"
                          ? "Review is recommended. You satisfy primary fields but action is required to verify specific criteria."
                          : "Requirements missed. Review the mismatch reasons below or look for alternative opportunities."
                      }
                    </p>
                  </div>
                </div>

                {/* 4b. SCHOLARSHIP SUMMARY CARD */}
                <div className="bg-zinc-900/70 border border-white/5 rounded-3xl p-6 md:p-8 backdrop-blur-md shadow-xl space-y-6">
                  <div className="flex justify-between items-start border-b border-zinc-800 pb-4">
                    <div>
                      <span className="text-[10px] uppercase font-bold tracking-widest text-accent-blue">AGENT 01 REPORT</span>
                      <h3 className="font-display font-bold text-xl text-white mt-1">
                        {results.analysis?.scholarship_name}
                      </h3>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-semibold text-zinc-400 block">APPLICATION DEADLINE</span>
                      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-zinc-950 border border-zinc-850 mt-1 text-zinc-200">
                        <Calendar className="w-3.5 h-3.5 text-accent-blue" />
                        <span className="text-xs font-bold">{results.analysis?.deadline}</span>
                      </div>
                    </div>
                  </div>

                  {/* Extract Criteria list */}
                  <div className="space-y-3">
                    <h5 className="text-xs font-bold text-zinc-400 uppercase tracking-widest">Extracted Criteria Guidelines</h5>
                    <ul className="space-y-2">
                      {results.analysis?.eligibility_criteria.map((rule, idx) => (
                        <li key={idx} className="text-sm text-zinc-300 flex items-start gap-2">
                          <span className="text-accent-blue mt-1 font-bold">▪</span>
                          <span>{rule}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Extract Guidelines */}
                  <div className="space-y-2 pt-4 border-t border-zinc-800">
                    <h5 className="text-xs font-bold text-zinc-400 uppercase tracking-widest">Key Portal Instructions</h5>
                    <p className="text-sm text-zinc-300 leading-relaxed">
                      {results.analysis?.instructions}
                    </p>
                  </div>
                </div>

                {/* 4c. PROFILE MATRIX ANALYSIS (REASONS FOR ELIGIBILITY) */}
                <div className="bg-zinc-900/70 border border-white/5 rounded-3xl p-6 md:p-8 backdrop-blur-md shadow-xl space-y-4">
                  <span className="text-[10px] uppercase font-bold tracking-widest text-accent-blue">AGENT 02 COMPARISON MATRIX</span>
                  <h3 className="font-display font-bold text-lg text-white">
                    Eligibility Mapping Analysis
                  </h3>
                  <div className="space-y-3 mt-4">
                    {results.eligibility?.reasons.map((reason, idx) => (
                      <div key={idx} className="flex gap-3 p-3 bg-zinc-950/40 rounded-xl border border-zinc-900 items-start">
                        <CheckCircle className="w-5 h-5 text-accent-blue shrink-0 mt-0.5" />
                        <p className="text-sm text-zinc-300">{reason}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 4d. REQUIRED VS MISSING DOCUMENTS CARDS */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  
                  {/* Required */}
                  <div className="bg-zinc-900/70 border border-white/5 rounded-3xl p-6 backdrop-blur-md shadow-xl space-y-4">
                    <div className="flex items-center gap-2">
                      <FileText className="w-5 h-5 text-accent-blue" />
                      <h4 className="font-display font-bold text-md text-white">Required Documents</h4>
                    </div>
                    <ul className="space-y-2 pt-2">
                      {results.analysis?.required_documents.map((doc, idx) => (
                        <li key={idx} className="text-xs font-medium text-zinc-300 bg-zinc-950 p-2.5 rounded-xl border border-zinc-850 flex items-center gap-2">
                          <div className="w-1.5 h-1.5 rounded-full bg-accent-blue" />
                          <span className="truncate">{doc}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Missing */}
                  <div className="bg-zinc-900/70 border border-white/5 rounded-3xl p-6 backdrop-blur-md shadow-xl space-y-4">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5 text-amber-500" />
                      <h4 className="font-display font-bold text-md text-white">Missing / Prep List</h4>
                    </div>
                    <ul className="space-y-2 pt-2">
                      {results.actionPlan?.missing_documents.length === 0 ? (
                        <p className="text-xs text-zinc-400">All documents are ready or present in candidate registry.</p>
                      ) : (
                        results.actionPlan?.missing_documents.map((doc, idx) => (
                          <li key={idx} className="text-xs font-medium text-amber-300 bg-amber-500/5 p-2.5 rounded-xl border border-amber-500/20 flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                            <span className="truncate">{doc}</span>
                          </li>
                        ))
                      )}
                    </ul>
                  </div>

                </div>

                {/* 4e. PERSONALIZED CHECKLIST & RECOMMENDATIONS */}
                <div className="bg-zinc-900/70 border border-white/5 rounded-3xl p-6 md:p-8 backdrop-blur-md shadow-xl space-y-6">
                  <div className="flex justify-between items-center pb-4 border-b border-zinc-850">
                    <div>
                      <span className="text-[10px] uppercase font-bold tracking-widest text-accent-blue">AGENT 03 STRATEGY ROUTE</span>
                      <h3 className="font-display font-bold text-xl text-white mt-1">
                        Personalized Action Plan Checklist
                      </h3>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-medium text-zinc-400">COMPLETED TASKS</span>
                      <p className="text-sm font-bold text-accent-blue">
                        {Object.values(completedTasks).filter(Boolean).length} / {results.actionPlan?.checklist.length}
                      </p>
                    </div>
                  </div>

                  {/* Checklist Table */}
                  <div className="space-y-3">
                    {results.actionPlan?.checklist.map((item, idx) => {
                      const isChecked = !!completedTasks[item.task];
                      return (
                        <div 
                          key={idx}
                          onClick={() => toggleTask(item.task)}
                          className={`flex items-start gap-3 p-4 rounded-2xl border transition-all cursor-pointer hover:bg-zinc-900 ${
                            isChecked 
                              ? "bg-zinc-950/20 border-emerald-500/10 opacity-70" 
                              : "bg-zinc-950/60 border-zinc-850 hover:border-zinc-700"
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => {}} // toggled on container click
                            className="mt-1 h-4 w-4 rounded-sm border-zinc-700 text-accent-blue focus:ring-accent-blue cursor-pointer"
                          />
                          <div className="flex-grow space-y-1">
                            <p className={`text-sm font-medium ${isChecked ? "line-through text-zinc-500" : "text-white"}`}>
                              {item.task}
                            </p>
                            <div className="flex flex-wrap items-center gap-2 mt-2">
                              {/* Priority badge */}
                              <span className={`text-[9px] uppercase font-extrabold px-2 py-0.5 rounded-full ${
                                item.priority === "High" 
                                  ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                                  : item.priority === "Medium"
                                    ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                                    : "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                              }`}>
                                {item.priority} Priority
                              </span>
                              {/* Timeframe badge */}
                              <span className="text-[10px] font-mono text-zinc-400 flex items-center gap-1">
                                <Clock className="w-3 h-3" /> {item.timeframe}
                              </span>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Strategic Advisor recommendations */}
                  <div className="pt-6 border-t border-zinc-850 space-y-3">
                    <h5 className="text-xs font-bold text-zinc-400 uppercase tracking-widest">
                      Strategic Advisor Guidance
                    </h5>
                    <div className="space-y-3">
                      {results.actionPlan?.recommendations.map((rec, idx) => (
                        <p key={idx} className="text-sm text-zinc-300 leading-relaxed font-light">
                          💡 <strong className="font-semibold text-white">Advice {idx + 1}:</strong> {rec}
                        </p>
                      ))}
                    </div>
                  </div>

                  {/* Reset console desk button */}
                  <div className="pt-6 flex justify-end">
                    <button
                      onClick={resetConsole}
                      className="px-6 py-2.5 rounded-xl bg-zinc-950 border border-zinc-850 text-zinc-400 hover:text-white transition-colors text-xs font-semibold cursor-pointer"
                    >
                      Clear & Analyze New PDF
                    </button>
                  </div>
                </div>

              </motion.div>
            )}

          </AnimatePresence>
        </div>

      </div>
    </section>
  );
}