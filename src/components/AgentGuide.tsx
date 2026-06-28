import { motion } from "motion/react";
import { 
  FileText, ShieldCheck, ClipboardList, 
  Cpu, ArrowDown, Network, Database
} from "lucide-react";

export default function AgentGuide() {
  const agents = [
    {
      num: "01",
      name: "Document Analysis Agent",
      role: "Parser & Guideline Extractor",
      desc: "Uses multimodal understanding to ingest institutional PDFs directly. Extracts complex rules, income cutoffs, cast reservations, required mark-sheets, and deadline details.",
      instruction: "System: You are an expert document analyst. Extract structured notification metrics and return in verified JSON.",
      icon: FileText,
      color: "border-blue-500/30 text-blue-400 bg-blue-500/5",
    },
    {
      num: "02",
      name: "Eligibility Evaluation Agent",
      role: "Profile Matcher & Compliance Inspector",
      desc: "Takes the extracted rules from Agent 1 and conducts a point-by-point logical mapping against the candidate's metrics (State, Income, social Category, Marks). Detects partial matching cases.",
      instruction: "System: Map candidate parameters directly against extracted criteria, determine status, and document exact matches or gaps.",
      icon: ShieldCheck,
      color: "border-purple-500/30 text-purple-400 bg-purple-500/5",
    },
    {
      num: "03",
      name: "Strategic Action Plan Agent",
      role: "Advisor & Checklist Compiler",
      desc: "Compiles a final action blueprint: creates a prioritised, chronological task checklist, warns about missing documents, and provides encouraging guidance advice.",
      instruction: "System: Compile interactive candidate checklists, highlight required local certificates, and offer application guidance.",
      icon: ClipboardList,
      color: "border-indigo-500/30 text-indigo-400 bg-indigo-500/5",
    },
  ];

  return (
    <section id="agents" className="py-24 px-6 md:px-16 max-w-[1200px] mx-auto space-y-16 bg-bg-dark border-t border-white/5">
      
      {/* Title block */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs text-zinc-400">
          <Network className="w-3.5 h-3.5 text-accent-blue" />
          True Multi-Agent Collaboration
        </div>
        <h2 className="font-display font-bold text-3xl md:text-5xl text-white">
          Under the Hood: The Agent Framework
        </h2>
        <p className="text-zinc-400 max-w-xl mx-auto text-sm md:text-base">
          Our specialized agent system orchestrates three consecutive Gemini 2.5 Flash operations, passing validated state representations down the pipeline.
        </p>
      </div>

      {/* Agents Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {agents.map((agent, idx) => {
          const Icon = agent.icon;
          return (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: idx * 0.2 }}
              className="p-6 rounded-3xl bg-zinc-900/40 border border-white/5 flex flex-col justify-between hover:border-accent-blue/20 hover:bg-zinc-900/60 transition-all group shadow-lg"
            >
              <div className="space-y-4">
                {/* Header icon row */}
                <div className="flex justify-between items-center">
                  <div className={`p-3 rounded-2xl border ${agent.color}`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <span className="font-display font-extrabold text-2xl text-zinc-700 group-hover:text-accent-blue/30 transition-colors">
                    {agent.num}
                  </span>
                </div>

                {/* Info titles */}
                <div>
                  <span className="text-[10px] uppercase font-bold text-zinc-500 tracking-wider">
                    {agent.role}
                  </span>
                  <h4 className="font-display font-bold text-lg text-white mt-1 group-hover:text-accent-blue transition-colors">
                    {agent.name}
                  </h4>
                </div>

                <p className="text-zinc-400 text-xs leading-relaxed font-light">
                  {agent.desc}
                </p>
              </div>

              {/* System Instruction Panel */}
              <div className="mt-6 p-3 rounded-xl bg-zinc-950 border border-zinc-850">
                <span className="text-[9px] font-mono text-zinc-500 font-bold uppercase tracking-wider block mb-1">
                  Prompt Guideline
                </span>
                <p className="text-[10px] text-zinc-400 font-mono leading-normal">
                  {agent.instruction}
                </p>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Interactive Process Pipeline visualization */}
      <div className="p-8 rounded-3xl bg-zinc-900/20 border border-white/5 relative overflow-hidden flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="absolute inset-0 bg-radial from-accent-blue/5 via-transparent to-transparent opacity-50" />
        
        <div className="space-y-2 relative z-10 text-center sm:text-left">
          <h4 className="font-display font-bold text-lg text-white flex items-center justify-center sm:justify-start gap-2">
            <Cpu className="w-5 h-5 text-accent-blue" />
            Sequential Context Propagation
          </h4>
          <p className="text-xs text-zinc-400 max-w-md">
            Instead of executing a massive prompt, we chain independent agents. The structured output of each step serves as contextual facts for the next, reducing hallucination and keeping processing costs low.
          </p>
        </div>

        <div className="flex items-center gap-2 relative z-10 font-mono text-[10px] text-zinc-400">
          <span className="px-3 py-1 rounded bg-zinc-950 border border-zinc-850">PDF In</span>
          <ArrowDown className="w-4 h-4 text-accent-blue rotate-275" />
          <span className="px-3 py-1 rounded bg-zinc-950 border border-zinc-850">Schema Out</span>
          <ArrowDown className="w-4 h-4 text-accent-blue rotate-275" />
          <span className="px-3 py-1 rounded bg-zinc-950 border border-zinc-850">Evaluation</span>
          <ArrowDown className="w-4 h-4 text-accent-blue rotate-275" />
          <span className="px-3 py-1 rounded bg-zinc-950 border border-zinc-850">Plan</span>
        </div>
      </div>

    </section>
  );
}
