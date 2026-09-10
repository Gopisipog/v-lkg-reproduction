import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Search, PlayCircle, Filter, ArrowRight, TrendingUp, 
  Tag, Layers, Check, ExternalLink, X, ListOrdered, Star, Hash
} from "lucide-react";
import { getAppGraph } from "../services/api";
import { resolveAppTheme } from "../utils/colorSchemes";

const INTELLIGENCE_FILTERS = [
  { id: "all", label: "ALL WORDS", color: "#0ea5e9" },
  { id: "executive", label: "EXECUTIVE", color: "#0ea5e9" },
  { id: "sales", label: "SALES & REVENUE", color: "#10b981" },
  { id: "learning", label: "MASTERY", color: "#f59e0b" },
  { id: "engineering", label: "AI TOOLS & R&D", color: "#38bdf8" },
  { id: "compliance", label: "GOVERNANCE", color: "#ef4444" },
  { id: "customer", label: "SUCCESS", color: "#ec4899" },
  { id: "thought_leadership", label: "LEADERSHIP", color: "#14b8a6" }
];

const VIEW_MODES = [
  { id: "ladder", label: "RANKED LADDER" },
  { id: "pathways", label: "LINEAR PATHWAYS" },
  { id: "categories", label: "BY CATEGORY" }
];

export default function LinearWordsView({ 
  activeApp, 
  activeAppTheme: propTheme,
  onJumpToVideo,
  onToggleEntityPriority
}) {
  const theme = propTheme || resolveAppTheme(activeApp);
  const primaryColor = theme.primaryColor || "#0EA5E9";
  const [nodes, setNodes] = useState([]);
  const [links, setLinks] = useState([]);
  const [selectedLens, setSelectedLens] = useState("all");
  const [viewMode, setViewMode] = useState("ladder"); // "ladder" | "pathways" | "categories"
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedWord, setSelectedWord] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeApp) return;
    setLoading(true);
    getAppGraph(activeApp.id, selectedLens)
      .then((data) => {
        setNodes(data.nodes || []);
        setLinks(data.links || []);
      })
      .catch((err) => console.error("Error loading words:", err))
      .finally(() => setLoading(false));
  }, [activeApp, selectedLens]);

  // Filter nodes by search
  const filteredNodes = nodes.filter((n) =>
    n.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
    n.type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Sort: Prioritized words first, then by centrality
  const prioritizedSet = new Set(activeApp?.prioritized_entities || []);
  const rankedNodes = [...filteredNodes].sort((a, b) => {
    const aPri = a.is_priority || prioritizedSet.has(a.label) || prioritizedSet.has(a.id);
    const bPri = b.is_priority || prioritizedSet.has(b.label) || prioritizedSet.has(b.id);
    if (aPri && !bPri) return -1;
    if (!aPri && bPri) return 1;
    return (b.centrality || 0) - (a.centrality || 0);
  });

  // Group by category
  const categoriesMap = {};
  filteredNodes.forEach((node) => {
    const t = node.type || "Concept";
    if (!categoriesMap[t]) categoriesMap[t] = [];
    categoriesMap[t].push(node);
  });

  return (
    <div className="p-3 sm:p-5 space-y-3.5 pb-48 max-w-3xl mx-auto">
      {/* Cockpit Registry Header */}
      <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Tag className="w-3.5 h-3.5" style={{ color: primaryColor }} />
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-white">
              Linear Word & Concept Registry
            </h3>
          </div>
          <span 
            style={{ 
              backgroundColor: `${theme.colors[0]}1c`, 
              color: primaryColor, 
              borderColor: `${theme.colors[0]}44` 
            }}
            className="text-[10px] font-mono px-2 py-0.5 rounded font-bold border"
          >
            {rankedNodes.length} WORDS IN SCOPE
          </span>
        </div>
        <p className="text-xs text-slate-400 leading-normal">
          High-frequency executive vocabulary and sequential concept pathways extracted from ingested transcripts.
        </p>

        {/* View Mode Toggle with Framer Motion layoutId */}
        <div className="pt-2 flex items-center space-x-1.5 border-t border-slate-800/80">
          {VIEW_MODES.map((mode) => {
            const isSelected = viewMode === mode.id;
            return (
              <button
                key={mode.id}
                onClick={() => setViewMode(mode.id)}
                className={`tactile-btn relative px-2.5 py-1 rounded-lg text-[11px] font-mono font-semibold transition-colors ${
                  isSelected ? "text-slate-950" : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {isSelected && (
                  <motion.div
                    layoutId="wordsViewModeIndicator"
                    style={{ background: theme.background }}
                    className="absolute inset-0 rounded-lg -z-10 shadow-sm"
                    transition={{ type: "spring", stiffness: 100, damping: 20 }}
                  />
                )}
                {mode.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Cockpit Search & Filter Strip */}
      <div className="space-y-2">
        <div className="flex items-center space-x-2 bg-slate-900 px-3 py-2 rounded-xl border border-slate-800">
          <Search className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search linear words (e.g. Active Listening, GTM, Clarity)..."
            className="w-full bg-transparent text-xs text-white placeholder-slate-500 font-mono focus:outline-none"
          />
          {searchQuery && (
            <button onClick={() => setSearchQuery("")} className="text-slate-400 p-0.5 hover:text-white">
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Intelligence Filters Scroll */}
        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 no-scrollbar">
          {INTELLIGENCE_FILTERS.map((lens) => {
            const isSelected = selectedLens === lens.id;
            return (
              <button
                key={lens.id}
                onClick={() => setSelectedLens(lens.id)}
                style={isSelected ? {
                  backgroundColor: `${theme.colors[0]}22`,
                  borderColor: `${theme.colors[0]}66`,
                  color: theme.colors[0]
                } : undefined}
                className={`tactile-btn px-2 py-0.5 rounded text-[10px] font-mono font-medium whitespace-nowrap transition-colors border shrink-0 ${
                  isSelected
                    ? "font-bold shadow-xs"
                    : "bg-slate-900 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200"
                }`}
              >
                {lens.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content Area */}
      {loading ? (
        <div className="py-12 flex flex-col items-center justify-center space-y-2">
          <div 
            className="w-6 h-6 border-2 border-t-transparent rounded-full animate-spin" 
            style={{ borderColor: primaryColor, borderTopColor: "transparent" }}
          />
          <p className="text-xs font-mono text-slate-400">Loading registry stream...</p>
        </div>
      ) : viewMode === "ladder" ? (
        /* Ranked Ladder View (High Visual Density Cockpit Stream) */
        <motion.div 
          className="space-y-1.5"
          initial="hidden"
          animate="visible"
          variants={{
            visible: { transition: { staggerChildren: 0.03 } }
          }}
        >
          {rankedNodes.map((node, idx) => {
            const isPri = node.is_priority || prioritizedSet.has(node.label) || prioritizedSet.has(node.id);
            return (
              <motion.div
                key={node.id}
                variants={{
                  hidden: { opacity: 0, y: 6 },
                  visible: { opacity: 1, y: 0 }
                }}
                className={`p-2.5 rounded-lg border transition-all flex items-center justify-between group ${
                  isPri
                    ? "bg-slate-900/90 border-amber-500/50 shadow-sm"
                    : "bg-slate-900/60 hover:bg-slate-900 border-slate-800/80 hover:border-slate-750"
                }`}
              >
                <div className="flex items-center space-x-2.5 min-w-0">
                  <button
                    onClick={() => onToggleEntityPriority && onToggleEntityPriority(node.label)}
                    className={`tactile-btn p-1 rounded border transition-colors shrink-0 ${
                      isPri
                        ? "bg-amber-950/40 border-amber-500/50 text-amber-400"
                        : "bg-slate-800/70 hover:bg-slate-800 border-slate-700/60 text-slate-500"
                    }`}
                    title={isPri ? "Remove priority" : "Mark as priority word"}
                  >
                    <Star className={`w-3 h-3 ${isPri ? "fill-amber-400 text-amber-400" : ""}`} />
                  </button>

                  <span className="font-mono text-slate-500 text-[10px] w-6 text-right shrink-0">
                    #{String(idx + 1).padStart(2, "0")}
                  </span>

                  <div className="min-w-0">
                    <div className="flex items-center space-x-1.5">
                      <h4 className="text-xs font-bold text-white truncate">{node.label}</h4>
                      {isPri && (
                        <span className="text-[8px] font-mono px-1 rounded uppercase bg-amber-400/20 text-amber-300 font-bold border border-amber-500/30 shrink-0">
                          PRIORITY
                        </span>
                      )}
                      <span
                        className="text-[8px] font-mono px-1 rounded uppercase shrink-0 font-semibold"
                        style={{ backgroundColor: `${node.color || '#0ea5e9'}20`, color: node.color || '#38bdf8' }}
                      >
                        {node.type}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2 text-[10px] font-mono text-slate-400 mt-0.5">
                      <span>INFLUENCE: <strong className="text-cyan-400">{node.centrality || 0}%</strong></span>
                      {node.intelligences?.length > 0 && (
                        <>
                          <span className="text-slate-600">·</span>
                          <span className="truncate max-w-[140px] text-slate-500">{node.intelligences.slice(0, 2).join(", ")}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                {/* Jump Timestamps with Monospace Font */}
                <div className="flex items-center space-x-1 shrink-0">
                  {node.timestamps?.slice(0, 2).map((ts, i) => (
                    <button
                      key={i}
                      onClick={() => onJumpToVideo(ts.video_id, ts.time || ts.timestamp || "00:00")}
                      className="tactile-btn flex items-center space-x-1 px-2 py-0.5 rounded bg-cyan-950/40 hover:bg-cyan-900/50 text-cyan-300 border border-cyan-800/40 text-[10px] font-mono font-bold transition-colors"
                      title={`Jump to [${ts.time || ts.timestamp}]`}
                    >
                      <PlayCircle className="w-2.5 h-2.5 text-cyan-400" />
                      <span>[{ts.time || ts.timestamp || "00:00"}]</span>
                    </button>
                  ))}
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      ) : viewMode === "pathways" ? (
        /* Linear Pathways View (Hairline Connected Rows) */
        <div className="space-y-1.5">
          {links.length > 0 ? (
            links.map((link, idx) => (
              <div
                key={idx}
                className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 flex items-center justify-between text-xs"
              >
                <div className="flex items-center space-x-2 min-w-0 flex-1">
                  <span className="font-bold text-white truncate max-w-[120px]">{link.source}</span>
                  <div className="flex items-center space-x-1 px-1.5 py-0.5 rounded bg-slate-800 text-[9px] font-mono text-cyan-400 font-bold uppercase shrink-0">
                    <span>{link.relation}</span>
                    <ArrowRight className="w-2.5 h-2.5 text-slate-400" />
                  </div>
                  <span className="font-bold text-white truncate max-w-[120px]">{link.target}</span>
                </div>

                {link.source_time && (
                  <button
                    onClick={() => onJumpToVideo(link.video_id || "dF3GFpIKPlE", link.source_time)}
                    className="tactile-btn ml-2 text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-cyan-950/50 text-cyan-300 border border-cyan-800/40 shrink-0 hover:bg-cyan-900/50 transition-colors"
                  >
                    [{link.source_time}]
                  </button>
                )}
              </div>
            ))
          ) : (
            <div className="py-8 text-center text-slate-500 text-xs font-mono">No linear pathways found in current scope.</div>
          )}
        </div>
      ) : (
        /* By Category Grouping */
        <div className="space-y-3">
          {Object.entries(categoriesMap).map(([category, catNodes]) => (
            <div key={category} className="space-y-1.5">
              <div className="flex items-center justify-between pb-1 border-b border-slate-800/80">
                <h4 className="text-[11px] font-mono font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
                  <span
                    className="w-1.5 h-1.5 rounded-full"
                    style={{ backgroundColor: catNodes[0]?.color || "#0ea5e9" }}
                  />
                  <span>{category} ({catNodes.length})</span>
                </h4>
              </div>

              <div className="flex flex-wrap gap-1.5">
                {catNodes.map((node) => {
                  const isPri = node.is_priority || prioritizedSet.has(node.label) || prioritizedSet.has(node.id);
                  return (
                    <div
                      key={node.id}
                      className={`px-2 py-1 rounded-md border transition-all flex items-center space-x-1.5 ${
                        isPri 
                          ? "bg-amber-950/40 border-amber-600/60 text-amber-200" 
                          : "bg-slate-900/80 hover:bg-slate-850 border-slate-800 hover:border-cyan-800/60"
                      }`}
                    >
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          if (onToggleEntityPriority) onToggleEntityPriority(node.label);
                        }}
                        className="shrink-0 tactile-btn"
                        title={isPri ? "Remove priority" : "Prioritize word"}
                      >
                        <Star className={`w-2.5 h-2.5 ${isPri ? "fill-amber-400 text-amber-400" : "text-slate-500 hover:text-amber-300"}`} />
                      </button>
                      <span 
                        onClick={() => {
                          if (node.timestamps?.[0]) {
                            onJumpToVideo(node.timestamps[0].video_id, node.timestamps[0].time || "00:00");
                          }
                        }}
                        className="text-xs font-semibold text-white hover:text-cyan-300 cursor-pointer transition-colors"
                      >
                        {node.label}
                      </span>
                      {node.timestamps?.[0] && (
                        <span 
                          onClick={() => onJumpToVideo(node.timestamps[0].video_id, node.timestamps[0].time || "00:00")}
                          className="text-[9px] font-mono text-cyan-400 font-bold cursor-pointer"
                        >
                          [{node.timestamps[0].time || "00:00"}]
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

