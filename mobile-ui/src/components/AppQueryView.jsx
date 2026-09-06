import React, { useState } from "react";
import { motion } from "framer-motion";
import { 
  Send, Sparkles, Brain, Check, Layers, PlayCircle, 
  ArrowRight, MessageSquareCode, Share2, HelpCircle, Radio
} from "lucide-react";
import { querySingleApp, queryMultiApps } from "../services/api";

const INTELLIGENCE_LENSES = [
  { id: "all", name: "CONSOLIDATED" },
  { id: "executive", name: "EXECUTIVE" },
  { id: "sales", name: "SALES" },
  { id: "learning", name: "LEARNING" },
  { id: "engineering", name: "AI TOOLS & R&D" },
  { id: "thought_leadership", name: "LEADERSHIP" }
];

const SUGGESTED_PROMPTS = [
  "How do elite presenters use contrast to persuade audiences?",
  "What are the core engineering workflows using Claude Code for GTM?",
  "How should leaders set boundaries and protect high-leverage time?",
  "What is the foundational discipline required to achieve the first $100K?"
];

export default function AppQueryView({ 
  activeApp, 
  apps, 
  onJumpToVideo 
}) {
  const [mode, setMode] = useState("single"); // "single" | "multi"
  const [question, setQuestion] = useState("");
  const [selectedLens, setSelectedLens] = useState("all");
  const [selectedAppIds, setSelectedAppIds] = useState(
    apps.slice(0, 2).map((a) => a.id)
  );

  const [singleResponse, setSingleResponse] = useState(null);
  const [multiResponse, setMultiResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const toggleAppSelection = (appId) => {
    if (selectedAppIds.includes(appId)) {
      if (selectedAppIds.length > 1) {
        setSelectedAppIds(selectedAppIds.filter((id) => id !== appId));
      }
    } else {
      setSelectedAppIds([...selectedAppIds, appId]);
    }
  };

  const handleQuery = async (e) => {
    if (e) e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setSingleResponse(null);
    setMultiResponse(null);

    try {
      if (mode === "single") {
        if (!activeApp) return;
        const res = await querySingleApp(
          activeApp.id, 
          question.trim(), 
          selectedLens === "all" ? null : selectedLens
        );
        setSingleResponse(res);
      } else {
        const res = await queryMultiApps(selectedAppIds, question.trim());
        setMultiResponse(res);
      }
    } catch (err) {
      alert(err.message || "Query failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-3 sm:p-5 space-y-3.5 pb-48 max-w-3xl mx-auto">
      {/* Mode Selector Pill with Framer Motion layoutId */}
      <div className="flex items-center justify-center">
        <div className="bg-slate-900 border border-slate-800 p-0.5 rounded-lg flex items-center space-x-1 shadow-sm">
          <button
            onClick={() => setMode("single")}
            className={`tactile-btn relative px-3 py-1.5 rounded-md text-[11px] font-mono font-bold transition-colors ${
              mode === "single" ? "text-slate-950" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            {mode === "single" && (
              <motion.div
                layoutId="queryModeIndicator"
                className="absolute inset-0 bg-cyan-400 rounded-md -z-10"
                transition={{ type: "spring", stiffness: 100, damping: 20 }}
              />
            )}
            SINGLE APP: {activeApp?.name ? activeApp.name.split(" ")[0].toUpperCase() : "ACTIVE"}
          </button>
          <button
            onClick={() => setMode("multi")}
            className={`tactile-btn relative px-3 py-1.5 rounded-md text-[11px] font-mono font-bold transition-colors ${
              mode === "multi" ? "text-slate-950" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            {mode === "multi" && (
              <motion.div
                layoutId="queryModeIndicator"
                className="absolute inset-0 bg-cyan-400 rounded-md -z-10"
                transition={{ type: "spring", stiffness: 100, damping: 20 }}
              />
            )}
            COMPARE APPS ("TWICE ANSWERED")
          </button>
        </div>
      </div>

      {/* Query Header & Multi-App Selection */}
      {mode === "single" ? (
        <div className="flex items-center space-x-1 overflow-x-auto pb-1 no-scrollbar">
          <span className="text-[10px] font-mono uppercase text-slate-500 mr-1 shrink-0">LENS:</span>
          {INTELLIGENCE_LENSES.map((lens) => (
            <button
              key={lens.id}
              onClick={() => setSelectedLens(lens.id)}
              className={`tactile-btn px-2 py-0.5 rounded text-[10px] font-mono font-medium whitespace-nowrap transition-colors border shrink-0 ${
                selectedLens === lens.id
                  ? "bg-cyan-950/60 text-cyan-300 border-cyan-700/60 font-bold"
                  : "bg-slate-900 text-slate-400 border-slate-800 hover:border-slate-750 hover:text-slate-200"
              }`}
            >
              {lens.name}
            </button>
          ))}
        </div>
      ) : (
        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1.5">
          <span className="text-[10px] font-mono uppercase tracking-wider text-cyan-400 block font-bold">
            Select 2+ Child Workspaces for Dual Verification:
          </span>
          <div className="grid grid-cols-2 gap-1.5">
            {apps.map((app) => {
              const active = selectedAppIds.includes(app.id);
              return (
                <button
                  key={app.id}
                  onClick={() => toggleAppSelection(app.id)}
                  className={`tactile-btn p-2 rounded-md text-left text-xs font-mono border transition-colors flex items-center justify-between ${
                    active 
                      ? "bg-cyan-950/40 border-cyan-700/60 text-cyan-200 font-bold" 
                      : "bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <span className="truncate">{app.name}</span>
                  {active && <Check className="w-3.5 h-3.5 text-cyan-400 shrink-0 ml-1" />}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Suggested Prompts - One Question per Row */}
      <div className="space-y-1.5">
        <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500 block font-semibold">
          Suggested Question Prompts
        </span>
        <div className="flex flex-col space-y-1.5 w-full">
          {SUGGESTED_PROMPTS.map((prompt, i) => (
            <button
              key={i}
              onClick={() => setQuestion(prompt)}
              className="tactile-btn w-full text-left text-xs font-mono px-3 py-2 rounded-lg bg-slate-900/90 hover:bg-slate-850 text-slate-300 hover:text-white border border-slate-800 hover:border-cyan-500/50 transition-all flex items-center justify-between group shadow-sm"
            >
              <span className="truncate pr-2">{prompt}</span>
              <ArrowRight className="w-3 h-3 text-slate-600 group-hover:text-cyan-400 shrink-0 transition-colors" />
            </button>
          ))}
        </div>
      </div>

      {/* Question Form */}
      <form onSubmit={handleQuery} className="relative">
        <textarea
          rows={2}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={mode === "single" ? `Ask ${activeApp?.name || 'app'} (entities & linear words)...` : "Ask across selected child apps..."}
          className="w-full px-3 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 font-mono focus:outline-none focus:border-cyan-500 pr-12 resize-none shadow-inner"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="tactile-btn absolute right-2.5 bottom-2.5 p-1.5 rounded-lg bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold transition-all disabled:opacity-40"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>

      {/* Loading State */}
      {loading && (
        <div className="py-12 flex flex-col items-center justify-center space-y-2">
          <div className="w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs font-mono text-slate-400">
            {mode === "single" ? "Synthesizing scoped entity pathways..." : "Generating dual-verified comparative analysis..."}
          </p>
        </div>
      )}

      {/* SINGLE APP RESPONSE */}
      {singleResponse && mode === "single" && (
        <div className="space-y-3 animate-slide-up">
          {/* Main Answer Card */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2.5">
            <div className="flex items-center justify-between pb-1.5 border-b border-slate-800/80">
              <div className="flex items-center space-x-1.5">
                <Brain className="w-3.5 h-3.5 text-cyan-400" />
                <h4 className="text-xs font-mono font-bold text-white uppercase tracking-wide">
                  {singleResponse.app_name} Knowledge Response
                </h4>
              </div>
              <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-cyan-950/60 text-cyan-300 border border-cyan-800/40">
                {singleResponse.intelligence_lens}
              </span>
            </div>

            <div className="text-xs text-slate-200 leading-relaxed whitespace-pre-line font-sans">
              {singleResponse.answer}
            </div>
          </div>

          {/* Referenced Entities Chips */}
          {singleResponse.referenced_entities?.length > 0 && (
            <div className="space-y-1">
              <span className="text-[9px] font-mono uppercase tracking-wider text-slate-500 block">
                Grounded Entities ({singleResponse.referenced_entities.length})
              </span>
              <div className="flex flex-wrap gap-1">
                {singleResponse.referenced_entities.map((ent) => (
                  <span
                    key={ent.id}
                    className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-200 flex items-center space-x-1"
                  >
                    <span>{ent.label}</span>
                    <span className="text-cyan-400 font-bold">({ent.centrality}%)</span>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Clickable Timestamp Citations */}
          {singleResponse.timestamp_citations?.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[9px] font-mono uppercase tracking-wider text-cyan-400 block font-bold">
                Citations & Evidence
              </span>
              <div className="space-y-1">
                {singleResponse.timestamp_citations.map((cite, idx) => (
                  <div
                    key={idx}
                    onClick={() => onJumpToVideo(cite.video_id, cite.timestamp)}
                    className="tactile-btn p-2 rounded-lg bg-slate-900 hover:bg-slate-850 border border-slate-800 hover:border-cyan-800/60 cursor-pointer flex items-center justify-between group"
                  >
                    <div className="flex items-center space-x-2 min-w-0 pr-2">
                      <PlayCircle className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                      <div className="min-w-0">
                        <p className="text-xs font-semibold text-white truncate">{cite.video_title}</p>
                        <p className="text-[10px] font-mono text-slate-400 truncate">"{cite.text}"</p>
                      </div>
                    </div>
                    <span className="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded bg-cyan-950/50 text-cyan-300 border border-cyan-800/40 shrink-0">
                      [{cite.timestamp}]
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* MULTI-APP "TWICE ANSWERED" RESPONSE */}
      {multiResponse && mode === "multi" && (
        <div className="space-y-3 animate-slide-up">
          {/* Comparative Synthesis Card */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <div className="flex items-center space-x-1.5 pb-1.5 border-b border-slate-800/80">
              <Radio className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
              <h4 className="text-xs font-mono font-bold text-white uppercase tracking-wide">
                Cross-App Comparative Synthesis ("Twice Answered")
              </h4>
            </div>
            <div className="text-xs text-slate-200 leading-relaxed whitespace-pre-line font-sans">
              {multiResponse.comparative_synthesis}
            </div>
          </div>

          {/* Individual Child App Answers Side-by-Side */}
          <div className="space-y-2">
            <h4 className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
              Individual App Linear Entities & Answers ({multiResponse.apps.length})
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
              {multiResponse.apps.map((appAns, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-2"
                >
                  <div className="flex items-center justify-between pb-1 border-b border-slate-800/80">
                    <h5 className="text-xs font-bold text-white truncate">{appAns.app_name}</h5>
                    <span
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: appAns.theme_color || "#0ea5e9" }}
                    />
                  </div>

                  <div className="text-xs text-slate-300 leading-relaxed max-h-56 overflow-y-auto whitespace-pre-line pr-1 font-sans">
                    {appAns.answer}
                  </div>

                  {appAns.timestamp_citations?.length > 0 && (
                    <div className="pt-1.5 border-t border-slate-800/80">
                      <span className="text-[9px] font-mono uppercase text-slate-500 block mb-1">
                        Timestamps:
                      </span>
                      <div className="flex flex-wrap gap-1">
                        {appAns.timestamp_citations.map((c, i) => (
                          <button
                            key={i}
                            onClick={() => onJumpToVideo(c.video_id, c.timestamp)}
                            className="tactile-btn text-[9px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-cyan-300 border border-slate-700"
                          >
                            [{c.timestamp}]
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

