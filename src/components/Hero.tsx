import { useState } from "react";
import { motion } from "motion/react";
import { Sparkles, ArrowRight, Menu, X, Compass, Award, ExternalLink } from "lucide-react";
import WebGLBackground from "./WebGLBackground";

interface HeroProps {
  onStartClick: () => void;
}

export default function Hero({ onStartClick }: HeroProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { name: "Home", href: "#home" },
    { name: "Agent System", href: "#agents" },
    { name: "Navigator Console", href: "#navigator" },
  ];

  return (
    <section id="home" className="relative min-h-screen flex flex-col justify-between overflow-hidden bg-bg-dark z-10">
      {/* Custom WebGL Shader Background */}
      <WebGLBackground />

      {/* Navbar Container */}
      <header className="absolute top-0 left-0 w-full z-50 bg-transparent py-6 px-6 md:px-16 flex items-center justify-between mix-blend-difference border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/10 rounded-xl backdrop-blur-md border border-white/10">
            <Compass className="w-6 h-6 text-accent-blue animate-pulse" />
          </div>
          <span className="font-display font-bold text-xl tracking-wider text-white">
            AI NAVIGATOR
          </span>
        </div>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <a
              key={link.name}
              href={link.href}
              className="text-sm font-medium tracking-wide text-zinc-300 hover:text-white transition-colors duration-300"
            >
              {link.name}
            </a>
          ))}
          <a
            href="https://ai.google.dev"
            target="_blank"
            referrerPolicy="no-referrer"
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-white/10 border border-white/10 text-xs font-semibold text-white backdrop-blur-md hover:bg-white/20 transition-all"
          >
            APAC Builders <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </nav>

        {/* Mobile Menu Btn */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 text-white hover:bg-white/10 rounded-lg transition-colors"
          aria-label="Toggle menu"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </header>

      {/* Mobile Nav Drawer */}
      {mobileMenuOpen && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="absolute top-20 left-0 w-full bg-zinc-950/95 border-b border-white/10 p-6 flex flex-col gap-4 z-40 md:hidden backdrop-blur-lg"
        >
          {navLinks.map((link) => (
            <a
              key={link.name}
              href={link.href}
              onClick={() => setMobileMenuOpen(false)}
              className="text-base font-medium py-2 text-zinc-300 hover:text-white transition-colors"
            >
              {link.name}
            </a>
          ))}
          <a
            href="https://ai.google.dev"
            target="_blank"
            referrerPolicy="no-referrer"
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center justify-center gap-2 w-full py-3 rounded-lg bg-accent-deep border border-accent-blue/30 text-sm font-semibold text-white hover:bg-accent-blue transition-all"
          >
            APAC Builders Initiative <ExternalLink className="w-4 h-4" />
          </a>
        </motion.div>
      )}

      {/* Hero Content Container */}
      <div className="flex-grow flex flex-col items-center justify-center px-6 text-center max-w-[1200px] mx-auto z-10 pt-24">
        {/* Badge Indicator */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-accent-deep/30 border border-accent-blue/40 text-accent-blue text-xs font-semibold uppercase tracking-widest backdrop-blur-md mb-8"
        >
          <Award className="w-4 h-4 text-accent-blue" />
          Google Cloud & Gen AI Academy APAC
        </motion.div>

        {/* Large Display Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="font-display font-bold text-4xl sm:text-6xl md:text-7xl lg:text-8xl tracking-tight leading-[1.1] text-white"
        >
          Demystifying Admissions & <br className="hidden md:inline" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent-blue via-blue-400 to-indigo-400">
            Scholarships with AI
          </span>
        </motion.h1>

        {/* Headline Animated Accent Line */}
        <div className="relative mt-8 mb-8 w-24 sm:w-32 h-[3px] bg-gradient-to-r from-accent-blue to-indigo-500 rounded-full overflow-hidden">
          <motion.div
            initial={{ left: "-100%" }}
            animate={{ left: "100%" }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="absolute top-0 h-full w-1/2 bg-white/40 blur-xs"
          />
        </div>

        {/* Description Text */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="max-w-2xl text-base sm:text-lg md:text-xl text-zinc-300 font-light leading-relaxed mb-12"
        >
          Upload eligibility circulars, notification PDFs, or scholarship criteria. 
          Our multi-agent system analyzes instructions, evaluates your profile, and generates 
          a personalized action plan.
        </motion.p>

        {/* Call to Action Callout */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.7 }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
        >
          <button
            onClick={onStartClick}
            className="group relative inline-flex items-center justify-center gap-3 px-8 py-4 rounded-xl bg-accent-blue font-display font-semibold text-white tracking-wide shadow-[0_0_30px_rgba(59,130,246,0.3)] hover:shadow-[0_0_40px_rgba(59,130,246,0.5)] transition-all duration-300 transform hover:-translate-y-0.5"
          >
            <Sparkles className="w-5 h-5 text-white animate-pulse" />
            Launch Analyzer Console
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
          
          <a
            href="#agents"
            className="px-6 py-3.5 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 text-sm font-medium text-white tracking-wide transition-all duration-200"
          >
            Explore Agent System
          </a>
        </motion.div>
      </div>

      {/* Decorative pulse card info */}
      <div className="w-full max-w-5xl mx-auto px-6 mb-12 z-10 hidden sm:grid grid-cols-3 gap-6">
        {[
          { title: "Document Analysis Agent", desc: "Extracts eligibility limits, deadlines, & critical document lists." },
          { title: "Eligibility Engine", desc: "Compares your social category, state, marks & income dynamically." },
          { title: "Action Plan Generator", desc: "Generates step-by-step checklists, timelines & templates." }
        ].map((feat, idx) => (
          <motion.div
            key={feat.title}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 + idx * 0.15 }}
            className="p-5 rounded-2xl bg-zinc-900/40 border border-white/5 backdrop-blur-md hover:border-accent-blue/30 transition-all group"
          >
            <div className="text-xs font-bold text-accent-blue mb-1 uppercase tracking-wider">Agent 0{idx + 1}</div>
            <h4 className="font-display font-bold text-white group-hover:text-accent-blue transition-colors mb-2">{feat.title}</h4>
            <p className="text-xs text-zinc-400 leading-relaxed">{feat.desc}</p>
          </motion.div>
        ))}
      </div>

      {/* Pulsing Scroll Indicator */}
      <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 flex flex-col items-center gap-2 opacity-50 hover:opacity-100 transition-opacity pointer-events-none">
        <span className="text-[10px] tracking-widest text-zinc-400 uppercase font-medium">SCROLL DOWN</span>
        <div className="w-6 h-10 rounded-full border-2 border-zinc-500 flex justify-center p-1.5">
          <motion.div
            animate={{ y: [0, 12, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
            className="w-1.5 h-1.5 bg-accent-blue rounded-full"
          />
        </div>
      </div>
    </section>
  );
}
