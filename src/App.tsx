import Hero from "./components/Hero";
import AgentGuide from "./components/AgentGuide";
import Dashboard from "./components/Dashboard";
import Footer from "./components/Footer";

export default function App() {
  const handleScrollToConsole = () => {
    const consoleSection = document.getElementById("navigator");
    if (consoleSection) {
      consoleSection.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="relative min-h-screen bg-bg-dark text-white selection:bg-accent-blue/30 selection:text-white">
      {/* 1. Stunning Hero Section with Full-Screen WebGL Shader */}
      <Hero onStartClick={handleScrollToConsole} />

      {/* 2. Visual Multi-Agent Architecture Explanation */}
      <AgentGuide />

      {/* 3. Core Operational Dashboard (Candidate profile & PDF Uploader) */}
      <Dashboard />

      {/* 4. Footer with Scroll-reveal & Parallax Sliding */}
      <Footer />
    </div>
  );
}
