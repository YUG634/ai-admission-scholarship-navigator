import { useRef } from "react";
import { motion, useScroll, useTransform } from "motion/react";
import { ArrowUp, Compass, Award, ExternalLink, Github, Heart } from "lucide-react";

export default function Footer() {
  const footerRef = useRef<HTMLDivElement | null>(null);

  // useScroll to track the scrolling progress at the bottom of the page
  const { scrollYProgress } = useScroll({
    target: footerRef,
    offset: ["start end", "end end"]
  });

  // Parallax reveal: slide up from -30% to 0%
  const translateY = useTransform(scrollYProgress, [0, 1], ["-30%", "0%"]);
  const opacity = useTransform(scrollYProgress, [0, 1], [0.3, 1]);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  };

  return (
    <footer 
      ref={footerRef} 
      className="relative w-full bg-zinc-950 overflow-hidden border-t border-white/5 pt-20 pb-12 px-6 md:px-16"
    >
      <motion.div 
        style={{ y: translateY, opacity }}
        className="max-w-[1200px] mx-auto space-y-12"
      >
        {/* Top Split */}
        <div className="flex flex-col md:flex-row items-start justify-between gap-8 pb-12 border-b border-zinc-900">
          
          {/* Logo Brand info */}
          <div className="space-y-4 max-w-sm">
            <div className="flex items-center gap-2.5">
              <Compass className="w-6 h-6 text-accent-blue" />
              <span className="font-display font-bold text-lg tracking-wider text-white">
                AI NAVIGATOR
              </span>
            </div>
            <p className="text-zinc-400 text-sm leading-relaxed">
              Demystifying higher education admissions and scholarship circulars globally, helping candidates find their ideal funding routes.
            </p>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[10px] font-bold text-zinc-300">
              <Award className="w-3.5 h-3.5 text-accent-blue" />
              APAC Meet the Builders Edition
            </div>
          </div>

          {/* Links Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-10">
            <div className="space-y-3">
              <h5 className="text-xs font-bold text-white uppercase tracking-wider">Resources</h5>
              <ul className="space-y-2">
                <li>
                  <a href="https://ai.google.dev" target="_blank" referrerPolicy="no-referrer" className="text-xs text-zinc-400 hover:text-white flex items-center gap-1 transition-colors">
                    Gemini API <ExternalLink className="w-3 h-3 text-zinc-500" />
                  </a>
                </li>
                <li>
                  <a href="https://cloud.google.com" target="_blank" referrerPolicy="no-referrer" className="text-xs text-zinc-400 hover:text-white flex items-center gap-1 transition-colors">
                    Google Cloud <ExternalLink className="w-3 h-3 text-zinc-500" />
                  </a>
                </li>
                <li>
                  <a href="https://scholarships.gov.in/" target="_blank" referrerPolicy="no-referrer" className="text-xs text-zinc-400 hover:text-white flex items-center gap-1 transition-colors">
                    NSP Portal <ExternalLink className="w-3 h-3 text-zinc-500" />
                  </a>
                </li>
              </ul>
            </div>

            <div className="space-y-3">
              <h5 className="text-xs font-bold text-white uppercase tracking-wider">Agents</h5>
              <ul className="space-y-2 text-xs text-zinc-400">
                <li>01. Document Extraction</li>
                <li>02. Eligibility Mapper</li>
                <li>03. Strategic Action Planner</li>
              </ul>
            </div>

            <div className="space-y-3 col-span-2 sm:col-span-1">
              <h5 className="text-xs font-bold text-white uppercase tracking-wider">Initiative</h5>
              <p className="text-xs text-zinc-400 leading-relaxed max-w-[200px]">
                Built for the Google Cloud & Gen AI Academy APAC Meet the Builders program.
              </p>
            </div>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-6 pt-4">
          <p className="text-xs text-zinc-500 flex items-center gap-1">
            © {new Date().getFullYear()} AI Admission & Scholarship Navigator. Built with 
            <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500 inline mx-0.5" /> 
            for APAC Builders.
          </p>

          <div className="flex items-center gap-6">
            <button
              onClick={scrollToTop}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-full bg-zinc-900 border border-zinc-800 text-xs font-semibold text-zinc-300 hover:text-white hover:border-accent-blue/30 transition-all cursor-pointer shadow-lg"
            >
              Back to Top
              <ArrowUp className="w-3.5 h-3.5 text-accent-blue animate-bounce" />
            </button>
          </div>
        </div>

      </motion.div>
    </footer>
  );
}
