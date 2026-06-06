import ChatInterface from "@/components/ChatInterface";

export default function Home() {
  return (
    <>
      {/* Animated background */}
      <div className="bg-mesh" />
      <div className="bg-noise" />

      <main className="relative z-10 flex flex-col h-screen overflow-hidden">
        {/* ── Top nav bar ── */}
        <nav className="flex items-center justify-between px-6 py-3 border-b border-white/5 bg-black/20 backdrop-blur-sm z-50 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <span className="text-sm font-semibold text-white/80 tracking-wide">SANSKAR AI</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 text-xs text-white/30">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              RAG-Grounded
            </div>
            <a
              href="https://github.com/sanskar-502"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-white/30 hover:text-white/60 transition-colors"
            >
              GitHub ↗
            </a>
          </div>
        </nav>

        {/* ── Hero + Chat area ── */}
        <div className="flex-1 flex flex-col items-center px-4 pt-4 pb-4 overflow-hidden">
          {/* Mini hero text (reduced margin for more chat height) */}
          <div className="text-center mb-3 flex-shrink-0">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight mb-1">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-violet-400">
                Talk to Sanskar's AI
              </span>
            </h1>
            <p className="text-sm text-white/40 max-w-xl mx-auto leading-relaxed">
              Ask about my resume, projects, technical skills, or schedule an interview.
            </p>
          </div>

          {/* Chat box - Stretches to fill exact remaining screen height */}
          <div className="w-full max-w-4xl flex-1 min-h-0">
            <ChatInterface />
          </div>

          {/* Footer */}
          <div className="flex-shrink-0 mt-2 text-center">
            <p className="text-[11px] text-white/20">
              Powered by Gemini 2.5 Flash · ChromaDB · Cal.com · Built for SCALER
            </p>
          </div>
        </div>
      </main>
    </>
  );
}
