import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Send, Sparkles, Brain, Check, Layers, PlayCircle, 
  ArrowRight, MessageSquareCode, Share2, HelpCircle, Radio
} from "lucide-react";
import { querySingleApp, queryMultiApps } from "../services/api";
import { resolveAppTheme } from "../utils/colorSchemes";
import { ICON_MAP } from "./TopHeader";

const INTELLIGENCE_LENSES = [
  { id: "all", name: "CONSOLIDATED" },
  { id: "executive", name: "EXECUTIVE" },
  { id: "sales", name: "SALES" },
  { id: "learning", name: "LEARNING" },
  { id: "engineering", name: "AI TOOLS & R&D" },
  { id: "thought_leadership", name: "LEADERSHIP" }
];

const INITIAL_PROMPTS = [
  "How do elite presenters use contrast to persuade audiences?",
  "What are the core engineering workflows using Claude Code for GTM?",
  "How should leaders set boundaries and protect high-leverage time?",
  "What is the foundational discipline required to achieve the first $100K?"
];

const CURATED_QUESTIONS_POOL = [
  "How do recursive feedback loops accelerate executive learning curves?",
  "What heuristics distinguish high-agency operators from conventional managers?",
  "How can asynchronous knowledge triplets minimize meeting overhead?",
  "What are the critical inflection points when scaling an AI workflow from 1 to 10?",
  "How do leaders navigate asymmetric risk during high-stakes strategic negotiations?",
  "What telemetry metrics best indicate authentic audience resonance in presentations?",
  "How does radical candor prevent organizational debt in fast-moving engineering teams?",
  "What mental models help executives de-risk aggressive product roadmap bets?",
  "How do top engineers leverage declarative knowledge graphs in real-time?",
  "What are the non-obvious trade-offs between execution speed and architectural purity?",
  "How can teams build antifragile systems that benefit from market volatility?",
  "How do first principles simplify complex multi-agent system design?",
  "What role does emotional regulation play during high-velocity crisis response?",
  "How does strategic boundary setting increase output density per engineer?",
  "What are the foundational metrics for measuring cross-workspace entity alignment?"
];

function generateNewQuestion(answeredQuestion, usedQuestionsSet, activeApp) {
  // 1. Prioritized entities from active child app
  if (activeApp && activeApp.prioritized_entities && activeApp.prioritized_entities.length > 0) {
    const entities = activeApp.prioritized_entities;
    const randomEntity = entities[Math.floor(Math.random() * entities.length)];
    const entityTemplates = [
      `How does ${randomEntity} directly drive execution velocity in this workspace?`,
      `What are the core operational principles behind ${randomEntity}?`,
      `How can teams leverage ${randomEntity} to de-risk high-stakes decisions?`,
      `Where does ${randomEntity} intersect with long-term strategy?`,
      `What failure modes arise when ${randomEntity} is ignored?`
    ];
    for (const q of entityTemplates) {
      if (!usedQuestionsSet.has(q) && q !== answeredQuestion) {
        return q;
      }
    }
  }

  // 2. Active app strategic focus
  if (activeApp && activeApp.name) {
    const appTemplates = [
      `What is the primary strategic thesis behind ${activeApp.name}?`,
      `How does ${activeApp.name} synthesize cross-video knowledge triplets?`,
      `What are the highest-leverage concepts cataloged in ${activeApp.name}?`
    ];
    for (const q of appTemplates) {
      if (!usedQuestionsSet.has(q) && q !== answeredQuestion) {
        return q;
      }
    }
  }

  // 3. Fall back to unused curated pool questions
  const available = CURATED_QUESTIONS_POOL.filter(q => !usedQuestionsSet.has(q) && q !== answeredQuestion);
  if (available.length > 0) {
    return available[Math.floor(Math.random() * available.length)];
  }

  // 4. Default dynamic generative question
  return `How can teams apply dynamic knowledge graphs to accelerate strategic execution?`;
}

export default function AppQueryView({ 
  activeApp, 
  activeAppTheme: propTheme,
  apps, 
  onJumpToVideo 
}) {
  const theme = propTheme || resolveAppTheme(activeApp);
  const primaryColor = theme.primaryColor || "#0EA5E9";

  const [mode, setMode] = useState("single"); // "single" | "multi"
  const [question, setQuestion] = useState("");
  const [selectedLens, setSelectedLens] = useState("all");
  const [selectedAppIds, setSelectedAppIds] = useState(
    apps.slice(0, 2).map((a) => a.id)
  );

  // Suggested Prompts Evolution State
  const [suggestedPrompts, setSuggestedPrompts] = useState(INITIAL_PROMPTS);
  const [usedQuestions, setUsedQuestions] = useState(() => new Set(INITIAL_PROMPTS));

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
    e?.preventDefault();
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

  const handleSelectSuggestedQuestion = async (selectedPrompt) => {
    setQuestion(selectedPrompt);

    // 1. Remove selected question from panel & generate replacement question
    setSuggestedPrompts((prev) => {
      const remaining = prev.filter((p) => p !== selectedPrompt);
      const newQuestion = generateNewQuestion(selectedPrompt, usedQuestions, activeApp);
      setUsedQuestions((prevSet) => new Set([...prevSet, selectedPrompt, newQuestion]));
      return [...remaining, newQuestion];
    });

    // 2. Automatically execute query answering
    setLoading(true);
    setSingleResponse(null);
    setMultiResponse(null);

    try {
      if (mode === "single") {
        if (!activeApp) return;
        const res = await querySingleApp(
          activeApp.id, 
          selectedPrompt, 
          selectedLens === "all" ? null : selectedLens
        );
        setSingleResponse(res);
      } else {
        const res = await queryMultiApps(selectedAppIds, selectedPrompt);
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
                style={{ background: theme.background }}
                className="absolute inset-0 rounded-md -z-10 shadow-sm"
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
                style={{ background: theme.background }}
                className="absolute inset-0 rounded-md -z-10 shadow-sm"
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
              style={selectedLens === lens.id ? {
                backgroundColor: `${theme.colors[0]}22`,
                borderColor: `${theme.colors[0]}66`,
                color: theme.colors[0]
              } : undefined}
              className={`tactile-btn px-2 py-0.5 rounded text-[10px] font-mono font-medium whitespace-nowrap transition-colors border shrink-0 ${
                selectedLens === lens.id
                  ? "font-bold shadow-xs"
                  : "bg-slate-900 text-slate-400 border-slate-800 hover:border-slate-750 hover:text-slate-200"
              }`}
            >
              {lens.name}
            </button>
          ))}
        </div>
      ) : (
        <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-1.5">
            <span className="text-[10px] font-mono uppercase tracking-wider font-bold text-white flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: primaryColor }} />
              <span>Select Workspaces to Compare (One Workspace Per Row):</span>
            </span>
            <span className="text-[10px] font-mono text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
              {selectedAppIds.length} Selected
            </span>
          </div>

          {/* Strictly One Workspace Per Row */}
          <div className="flex flex-col space-y-2 w-full pt-1">
            {apps.map((app) => {
              const active = selectedAppIds.includes(app.id);
              const AppIcon = ICON_MAP[app.icon] || Layers;
              const itemTheme = resolveAppTheme(app);
              return (
                <button
                  key={app.id}
                  onClick={() => toggleAppSelection(app.id)}
                  style={active ? {
                    backgroundColor: `${itemTheme.colors[0]}15`,
                    borderColor: `${itemTheme.colors[0]}60`
                  } : undefined}
                  className={`tactile-btn w-full p-2.5 rounded-lg border text-left flex items-center justify-between transition-all ${
                    active 
                      ? "shadow-sm ring-1 ring-white/10" 
                      : "bg-slate-950/70 border-slate-800/80 hover:border-slate-700 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <div className="flex items-center space-x-3 min-w-0">
                    <div 
                      className="w-8 h-8 rounded-lg flex items-center justify-center text-white shrink-0 shadow-md"
                      style={{ background: itemTheme.background }}
                    >
                      <AppIcon className="w-4 h-4 drop-shadow" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-bold text-white truncate">{app.name}</span>
                        <span className="text-[8px] font-mono px-1.5 py-0.2 bg-slate-800 text-slate-400 rounded border border-slate-700/50 uppercase">
                          DOMAIN IN A BOX
                        </span>
                      </div>
                      <span className="text-[10px] font-mono text-slate-400 truncate block mt-0.5">
                        {app.stats?.video_count || 0} streams · {app.stats?.entity_count || 0} linear words · {app.focus_domains?.slice(0, 2).join(", ") || "executive"}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2.5 shrink-0">
                    <div 
                      className={`w-5 h-5 rounded-md flex items-center justify-center border transition-all ${
                        active 
                          ? "text-slate-950 font-bold shadow-xs" 
                          : "border-slate-700 bg-slate-900 text-transparent"
                      }`}
                      style={active ? { backgroundColor: itemTheme.colors[0], borderColor: itemTheme.colors[0] } : undefined}
                    >
                      {active ? <Check className="w-3.5 h-3.5 text-slate-950 stroke-[3]" /> : null}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Suggested Prompts - One Question per Row (Auto-evolves on selection) */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500 block font-semibold">
            Suggested Question Prompts
          </span>
          <span 
            style={{ 
              backgroundColor: `${theme.colors[0]}1a`, 
              color: primaryColor, 
              borderColor: `${theme.colors[0]}44` 
            }}
            className="text-[9px] font-mono px-1.5 py-0.2 rounded border"
          >
            AUTO-GENERATES ON ANSWER
          </span>
        </div>
        <div className="flex flex-col space-y-1.5 w-full">
          <AnimatePresence mode="popLayout">
            {suggestedPrompts.map((prompt) => (
              <motion.button
                key={prompt}
                layout
                initial={{ opacity: 0, y: 6, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, x: -20, transition: { duration: 0.15 } }}
                transition={{ type: "spring", stiffness: 350, damping: 25 }}
                onClick={() => handleSelectSuggestedQuestion(prompt)}
                className="tactile-btn w-full text-left text-xs font-mono px-3 py-2 rounded-lg bg-slate-900/90 hover:bg-slate-850 text-slate-300 hover:text-white border border-slate-800 transition-all flex items-center justify-between group shadow-sm"
              >
                <span className="truncate pr-2">{prompt}</span>
                <ArrowRight 
                  style={{ color: `${theme.colors[0]}aa` }}
                  className="w-3 h-3 group-hover:scale-110 shrink-0 transition-transform" 
                />
              </motion.button>
            ))}
          </AnimatePresence>
        </div>
      </div>

      {/* Question Form */}
      <form onSubmit={handleQuery} className="relative">
        <textarea
          rows={2}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={mode === "single" ? `Ask ${activeApp?.name || 'app'} (entities & linear words)...` : "Ask across selected child apps..."}
          className="w-full px-3 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 font-mono focus:outline-none pr-12 resize-none shadow-inner"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          style={{ 
            background: theme.background, 
            boxShadow: `0 0 14px ${theme.colors[0]}44` 
          }}
          className="tactile-btn absolute right-2.5 bottom-2.5 p-1.5 rounded-lg text-slate-950 font-bold transition-all disabled:opacity-40"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>

      {/* Loading State */}
      {loading && (
        <div className="py-12 flex flex-col items-center justify-center space-y-2">
          <div 
            className="w-6 h-6 border-2 border-t-transparent rounded-full animate-spin" 
            style={{ borderColor: primaryColor, borderTopColor: "transparent" }}
          />
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

          {/* Individual Child App Answers - STRICTLY ONE WORKSPACE PER ROW */}
          <div className="space-y-2">
            <h4 className="text-[10px] font-mono uppercase tracking-wider text-slate-400 font-bold flex items-center justify-between">
              <span>Individual Domain Box Breakdown (One Per Row):</span>
              <span className="text-cyan-400 font-normal">{multiResponse.apps.length} Domains Compared</span>
            </h4>

            {/* Vertically Stacked: One Workspace per Line/Row */}
            <div className="flex flex-col space-y-3 w-full">
              {multiResponse.apps.map((appAns, idx) => {
                const matchedApp = apps.find(a => a.id === appAns.app_id || a.name === appAns.app_name);
                const AppIcon = matchedApp && ICON_MAP[matchedApp.icon] ? ICON_MAP[matchedApp.icon] : Layers;
                const domainTheme = resolveAppTheme(matchedApp);
                return (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl bg-slate-900/95 border border-slate-800 space-y-2.5 relative overflow-hidden shadow-sm"
                  >
                    {/* Top Edge Domain Theme Accent Bar */}
                    <div 
                      className="absolute top-0 left-0 right-0 h-1 transition-all"
                      style={{ background: domainTheme.background }}
                    />

                    {/* Domain in a Box Header */}
                    <div className="flex items-center justify-between pb-2 border-b border-slate-800/80 pt-1">
                      <div className="flex items-center space-x-2.5 min-w-0">
                        <div 
                          className="w-6 h-6 rounded-md flex items-center justify-center text-white shrink-0 shadow-sm"
                          style={{ background: domainTheme.background }}
                        >
                          <AppIcon className="w-3.5 h-3.5" />
                        </div>
                        <div className="flex items-center space-x-2 min-w-0">
                          <h5 className="text-xs font-bold text-white truncate">{appAns.app_name}</h5>
                          <span className="text-[8px] font-mono px-1.5 py-0.2 bg-slate-800 text-slate-400 rounded border border-slate-700/50 uppercase">
                            DOMAIN IN A BOX
                          </span>
                        </div>
                      </div>

                      <span 
                        className="text-[9px] font-mono px-2 py-0.5 rounded font-bold border shrink-0"
                        style={{ 
                          backgroundColor: `${domainTheme.colors[0]}20`, 
                          color: domainTheme.primaryColor,
                          borderColor: `${domainTheme.colors[0]}50`
                        }}
                      >
                        ROW #{idx + 1}
                      </span>
                    </div>

                    {/* Domain Synthesized Answer */}
                    <div className="text-xs text-slate-200 leading-relaxed whitespace-pre-line font-sans">
                      {appAns.answer}
                    </div>

                    {/* Timestamp Citations in this Domain */}
                    {appAns.timestamp_citations?.length > 0 && (
                      <div className="pt-2 border-t border-slate-800/80 flex items-center flex-wrap gap-1.5">
                        <span className="text-[9px] font-mono uppercase text-slate-500 mr-1">
                          Domain Citations:
                        </span>
                        {appAns.timestamp_citations.map((c, i) => (
                          <button
                            key={i}
                            onClick={() => onJumpToVideo(c.video_id, c.timestamp)}
                            className="tactile-btn text-[9px] font-mono px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-750 text-cyan-300 border border-slate-700 hover:border-cyan-500/50 transition-colors flex items-center space-x-1"
                          >
                            <PlayCircle className="w-2.5 h-2.5 text-cyan-400" />
                            <span>[{c.timestamp}]</span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

