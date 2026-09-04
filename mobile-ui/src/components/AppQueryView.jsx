import React, { useState } from "react";
import { 
  Send, Sparkles, Brain, Check, Layers, PlayCircle, 
  ArrowRight, MessageSquareCode, Share2, HelpCircle
} from "lucide-react";
import { querySingleApp, queryMultiApps } from "../services/api";

const INTELLIGENCE_LENSES = [
  { id: "all", name: "Consolidated" },
  { id: "executive", name: "Executive" },
  { id: "sales", name: "Sales" },
  { id: "learning", name: "Learning" },
  { id: "engineering", name: "R&D/Tech" },
  { id: "thought_leadership", name: "Leadership" }
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
    <div className="p-4 space-y-5 pb-40 max-w-3xl mx-auto animate-fade-in">
      {/* Mode Selector Pill */}
      <div className="flex items-center justify-center">
        <div className="bg-slate-900 border border-slate-800 p-1 rounded-2xl flex items-center space-x-1 shadow-md">
          <button
            onClick={() => setMode("single")}
            className={`px-4 py-1.5 rounded-xl text-xs font-bold transition-all ${
              mode === "single"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Single App: {activeApp?.name ? activeApp.name.split(" ")[0] : "Active"}
          </button>
          <button
            onClick={() => setMode("multi")}
            className={`px-4 py-1.5 rounded-xl text-xs font-bold transition-all ${
              mode === "multi"
                ? "bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-md shadow-purple-600/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Compare Apps ("Twice Answered")
          </button>
        </div>
      </div>

      {/* Query Header & Multi-App Selection */}
      {mode === "single" ? (
        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 no-scrollbar">
          <span className="text-[11px] font-semibold text-slate-400 mr-1 shrink-0">Intelligence Lens:</span>
          {INTELLIGENCE_LENSES.map((lens) => (
            <button
              key={lens.id}
              onClick={() => setSelectedLens(lens.id)}
              className={`px-3 py-1 rounded-xl text-xs font-semibold whitespace-nowrap transition-all border shrink-0 ${
                selectedLens === lens.id
                  ? "bg-indigo-600 text-white border-indigo-500 shadow-sm"
                  : "bg-slate-900 text-slate-400 border-slate-800 hover:text-white"
              }`}
            >
              {lens.name}
            </button>
          ))}
        </div>
      ) : (
        <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-purple-400 block">
            Select 2+ Child Apps to Compare:
          </span>
          <div className="grid grid-cols-2 gap-2">
            {apps.map((app) => {
              const active = selectedAppIds.includes(app.id);
              return (
                <button
                  key={app.id}
                  onClick={() => toggleAppSelection(app.id)}
                  className={`p-2.5 rounded-xl text-left text-xs font-semibold border transition-all flex items-center justify-between ${
                    active 
                      ? "bg-slate-850 border-purple-500 text-white shadow-sm ring-1 ring-purple-500/20" 
                      : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <span className="truncate">{app.name}</span>
                  {active && <Check className="w-3.5 h-3.5 text-purple-400 shrink-0 ml-1" />}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Suggested Prompts */}
      <div className="space-y-1.5">
        <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 block">
          Suggested Question Prompts
        </span>
        <div className="flex flex-wrap gap-1.5">
          {SUGGESTED_PROMPTS.map((prompt, i) => (
            <button
              key={i}
              onClick={() => setQuestion(prompt)}
              className="text-left text-[11px] px-2.5 py-1 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800 hover:border-slate-700 transition-colors line-clamp-1"
            >
              {prompt}
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
          className="w-full px-4 py-3 bg-slate-900 border border-slate-800 rounded-2xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 pr-12 resize-none shadow-xl"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="absolute right-3 bottom-3 p-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30 transition-transform active:scale-95 disabled:opacity-40"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>

      {/* Loading Spinner */}
      {loading && (
        <div className="py-12 flex flex-col items-center justify-center space-y-3">
          <div className="w-8 h-8 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-slate-400">
            {mode === "single" ? "Synthesizing scoped entity pathways..." : "Generating dual-verified comparative analysis..."}
          </p>
        </div>
      )}

      {/* SINGLE APP RESPONSE */}
      {singleResponse && mode === "single" && (
        <div className="space-y-4 animate-slide-up">
          {/* Main Answer Card */}
          <div className="p-5 rounded-3xl bg-slate-900 border border-slate-800 shadow-2xl space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <Brain className="w-4 h-4 text-indigo-400" />
                <h4 className="text-xs font-bold text-white uppercase tracking-wide">
                  {singleResponse.app_name} Knowledge Response
                </h4>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded-md bg-indigo-500/20 text-indigo-300 font-semibold">
                {singleResponse.intelligence_lens}
              </span>
            </div>

            <div className="text-xs text-slate-200 leading-relaxed whitespace-pre-line">
              {singleResponse.answer}
            </div>
          </div>

          {/* Referenced Entities Chips */}
          {singleResponse.referenced_entities?.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">
                Grounded Entities ({singleResponse.referenced_entities.length})
              </span>
              <div className="flex flex-wrap gap-1.5">
                {singleResponse.referenced_entities.map((ent) => (
                  <span
                    key={ent.id}
                    className="text-xs font-medium px-2.5 py-1 rounded-xl bg-slate-850 border border-slate-700/80 text-white flex items-center space-x-1"
                  >
                    <span>{ent.label}</span>
                    <span className="text-[10px] text-indigo-400 font-bold">({ent.centrality}%)</span>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Clickable Timestamp Citations */}
          {singleResponse.timestamp_citations?.length > 0 && (
            <div className="space-y-2">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-indigo-400 block">
                Clickable Timestamp Citations
              </span>
              <div className="space-y-1.5">
                {singleResponse.timestamp_citations.map((cite, idx) => (
                  <div
                    key={idx}
                    onClick={() => onJumpToVideo(cite.video_id, cite.timestamp)}
                    className="p-2.5 rounded-2xl bg-slate-900/90 hover:bg-slate-850 border border-slate-800 hover:border-indigo-500/60 transition-all cursor-pointer flex items-center justify-between group active:scale-98"
                  >
                    <div className="flex items-center space-x-2.5 min-w-0 pr-2">
                      <PlayCircle className="w-4 h-4 text-indigo-400 group-hover:scale-110 transition-transform shrink-0" />
                      <div className="min-w-0">
                        <p className="text-xs font-semibold text-white truncate">{cite.video_title}</p>
                        <p className="text-[11px] text-slate-400 truncate">"{cite.text}"</p>
                      </div>
                    </div>
                    <span className="text-xs font-bold px-2 py-0.5 rounded-lg bg-indigo-600/30 text-indigo-300 shrink-0">
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
        <div className="space-y-5 animate-slide-up">
          {/* Comparative Synthesis Card */}
          <div className="p-5 rounded-3xl bg-gradient-to-br from-indigo-950/70 via-slate-900 to-purple-950/70 border border-purple-500/40 shadow-2xl space-y-3">
            <div className="flex items-center space-x-2 pb-2 border-b border-purple-500/30">
              <Sparkles className="w-4 h-4 text-purple-400" />
              <h4 className="text-xs font-bold text-white uppercase tracking-wide">
                Cross-App Comparative Synthesis ("Twice Answered")
              </h4>
            </div>
            <div className="text-xs text-slate-200 leading-relaxed whitespace-pre-line">
              {multiResponse.comparative_synthesis}
            </div>
          </div>

          {/* Individual Child App Answers Side-by-Side */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Individual App Linear Entities & Answers ({multiResponse.apps.length})
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {multiResponse.apps.map((appAns, idx) => (
                <div
                  key={idx}
                  className="p-4.5 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-3"
                >
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                    <h5 className="text-xs font-bold text-white truncate">{appAns.app_name}</h5>
                    <span
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: appAns.theme_color || "#6366f1" }}
                    />
                  </div>

                  <div className="text-xs text-slate-300 leading-relaxed max-h-56 overflow-y-auto whitespace-pre-line pr-1">
                    {appAns.answer}
                  </div>

                  {appAns.timestamp_citations?.length > 0 && (
                    <div className="pt-2 border-t border-slate-800/80">
                      <span className="text-[10px] font-semibold uppercase text-slate-500 block mb-1">
                        Timestamps:
                      </span>
                      <div className="flex flex-wrap gap-1">
                        {appAns.timestamp_citations.map((c, i) => (
                          <button
                            key={i}
                            onClick={() => onJumpToVideo(c.video_id, c.timestamp)}
                            className="text-[10px] px-2 py-0.5 rounded-md bg-slate-800 hover:bg-slate-750 text-indigo-300 border border-slate-700"
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
