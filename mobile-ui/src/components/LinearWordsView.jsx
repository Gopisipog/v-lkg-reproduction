import React, { useState, useEffect } from "react";
import { 
  Search, PlayCircle, Filter, ArrowRight, TrendingUp, 
  Sparkles, Tag, Layers, Check, ExternalLink, X, ListOrdered, Star
} from "lucide-react";
import { getAppGraph } from "../services/api";

const INTELLIGENCE_FILTERS = [
  { id: "all", label: "All Words", color: "#6366f1" },
  { id: "executive", label: "Executive", color: "#6366f1" },
  { id: "sales", label: "Sales & Revenue", color: "#10b981" },
  { id: "learning", label: "Learning & Mastery", color: "#f59e0b" },
  { id: "engineering", label: "R&D / AI Tools", color: "#3b82f6" },
  { id: "compliance", label: "Governance", color: "#ef4444" },
  { id: "customer", label: "Customer Success", color: "#ec4899" },
  { id: "competitive", label: "Competitive", color: "#8b5cf6" },
  { id: "thought_leadership", label: "Leadership", color: "#14b8a6" }
];

const VIEW_MODES = [
  { id: "ladder", label: "Ranked Ladder" },
  { id: "pathways", label: "Linear Pathways" },
  { id: "categories", label: "By Category" }
];

export default function LinearWordsView({ 
  activeApp, 
  onJumpToVideo,
  onToggleEntityPriority
}) {
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
    <div className="p-4 space-y-4 pb-40 max-w-2xl mx-auto animate-fade-in">
      {/* Header Banner */}
      <div className="p-4 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Tag className="w-4 h-4 text-indigo-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-white">
              Linear Word & Concept Registry
            </h3>
          </div>
          <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-bold border border-indigo-500/30">
            {rankedNodes.length} Words in {activeApp?.name ? activeApp.name.split(" ")[0] : "Scope"}
          </span>
        </div>
        <p className="text-xs text-slate-300">
          Explore key leadership words and sequential pathways extracted from assigned videos.
        </p>

        {/* View Mode Toggle */}
        <div className="pt-2 flex items-center space-x-1.5 border-t border-slate-800/80">
          {VIEW_MODES.map((mode) => (
            <button
              key={mode.id}
              onClick={() => setViewMode(mode.id)}
              className={`px-3 py-1 rounded-xl text-xs font-semibold transition-all ${
                viewMode === mode.id
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/25"
                  : "bg-slate-800/80 text-slate-400 hover:text-slate-200"
              }`}
            >
              {mode.label}
            </button>
          ))}
        </div>
      </div>

      {/* Search Bar */}
      <div className="flex items-center space-x-2 bg-slate-900 p-2.5 rounded-2xl border border-slate-800 shadow-md">
        <Search className="w-4 h-4 text-slate-400 ml-1 shrink-0" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search linear words (e.g. Active Listening, Clarity, GTM)..."
          className="w-full bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none"
        />
        {searchQuery && (
          <button onClick={() => setSearchQuery("")} className="text-slate-400 p-1">
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
              className={`px-3 py-1 rounded-xl text-xs font-semibold whitespace-nowrap transition-all border shrink-0 ${
                isSelected
                  ? "bg-indigo-600 text-white border-indigo-500 shadow-sm"
                  : "bg-slate-900 text-slate-400 border-slate-800 hover:text-white"
              }`}
            >
              {lens.label}
            </button>
          );
        })}
      </div>

      {/* Content Area based on View Mode */}
      {loading ? (
        <div className="py-12 flex flex-col items-center justify-center space-y-3">
          <div className="w-8 h-8 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-slate-400">Loading linear words...</p>
        </div>
      ) : viewMode === "ladder" ? (
        /* Ranked Ladder View */
        <div className="space-y-2.5">
          {rankedNodes.map((node, idx) => {
            const isPri = node.is_priority || prioritizedSet.has(node.label) || prioritizedSet.has(node.id);
            return (
              <div
                key={node.id}
                className={`p-3.5 rounded-2xl border transition-all shadow-md flex items-center justify-between group ${
                  isPri
                    ? "bg-slate-900 border-amber-500/40 ring-1 ring-amber-500/20 shadow-amber-500/5"
                    : "bg-slate-900 hover:bg-slate-850 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center space-x-3 min-w-0">
                  <button
                    onClick={() => onToggleEntityPriority && onToggleEntityPriority(node.label)}
                    className={`p-1.5 rounded-xl border transition-all shrink-0 ${
                      isPri
                        ? "bg-amber-500/20 border-amber-500/50 text-amber-400 shadow-sm"
                        : "bg-slate-800/80 hover:bg-slate-750 border-slate-700/60 text-slate-500 hover:text-amber-300"
                    }`}
                    title={isPri ? "Remove priority" : "Mark as priority word"}
                  >
                    <Star className={`w-3.5 h-3.5 ${isPri ? "fill-amber-400 text-amber-400" : ""}`} />
                  </button>

                  <span className="w-5 h-5 rounded-lg bg-slate-800 text-slate-400 text-[10px] font-bold flex items-center justify-center shrink-0">
                    #{idx + 1}
                  </span>
                  <div className="min-w-0">
                    <div className="flex items-center space-x-2">
                      <h4 className="text-xs font-bold text-white truncate">{node.label}</h4>
                      {isPri && (
                        <span className="text-[9px] px-1.5 py-0.2 rounded font-black uppercase bg-amber-400/20 text-amber-300 border border-amber-500/30 shrink-0">
                          Priority
                        </span>
                      )}
                      <span
                        className="text-[9px] px-1.5 py-0.2 rounded font-bold uppercase shrink-0"
                        style={{ backgroundColor: `${node.color}25`, color: node.color }}
                      >
                        {node.type}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2 text-[10px] text-slate-400 mt-0.5">
                      <span>Influence: <strong className="text-indigo-400">{node.centrality}%</strong></span>
                      <span>·</span>
                      <span>{node.intelligences?.slice(0, 2).join(", ")}</span>
                    </div>
                  </div>
                </div>

                {/* Jump Timestamps */}
                <div className="flex items-center space-x-1 shrink-0">
                  {node.timestamps?.slice(0, 2).map((ts, i) => (
                    <button
                      key={i}
                      onClick={() => onJumpToVideo(ts.video_id, ts.time || ts.timestamp || "00:00")}
                      className="flex items-center space-x-1 px-2.5 py-1 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-[11px] font-bold transition-all active:scale-95"
                      title={`Jump to [${ts.time || ts.timestamp}]`}
                    >
                      <PlayCircle className="w-3 h-3 text-indigo-400" />
                      <span>[{ts.time || ts.timestamp || "00:00"}]</span>
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      ) : viewMode === "pathways" ? (
        /* Linear Pathways View (A -> B -> C) */
        <div className="space-y-2.5">
          {links.length > 0 ? (
            links.map((link, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 shadow-md flex items-center justify-between text-xs"
              >
                <div className="flex items-center space-x-2 min-w-0 flex-1">
                  <span className="font-bold text-white truncate max-w-[120px]">{link.source}</span>
                  <div className="flex items-center space-x-1 px-2 py-0.5 rounded-md bg-slate-800 text-[10px] text-indigo-400 font-bold uppercase shrink-0">
                    <span>{link.relation}</span>
                    <ArrowRight className="w-3 h-3 text-slate-400" />
                  </div>
                  <span className="font-bold text-white truncate max-w-[120px]">{link.target}</span>
                </div>

                {link.source_time && (
                  <button
                    onClick={() => onJumpToVideo(link.video_id || "dF3GFpIKPlE", link.source_time)}
                    className="ml-2 text-[10px] font-bold px-2 py-1 rounded-lg bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 shrink-0 hover:bg-indigo-600 hover:text-white transition-colors"
                  >
                    [{link.source_time}]
                  </button>
                )}
              </div>
            ))
          ) : (
            <div className="py-8 text-center text-slate-500 text-xs">No linear pathways found in current scope.</div>
          )}
        </div>
      ) : (
        /* By Category Grouping */
        <div className="space-y-4">
          {Object.entries(categoriesMap).map(([category, catNodes]) => (
            <div key={category} className="space-y-2">
              <div className="flex items-center justify-between pb-1 border-b border-slate-800">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: catNodes[0]?.color || "#6366f1" }}
                  />
                  <span>{category} ({catNodes.length})</span>
                </h4>
              </div>

              <div className="flex flex-wrap gap-2">
                {catNodes.map((node) => {
                  const isPri = node.is_priority || prioritizedSet.has(node.label) || prioritizedSet.has(node.id);
                  return (
                    <div
                      key={node.id}
                      className={`px-3 py-1.5 rounded-2xl border transition-all flex items-center space-x-2 shadow-sm ${
                        isPri 
                          ? "bg-amber-500/15 border-amber-500/50 text-amber-200 shadow-sm shadow-amber-500/10" 
                          : "bg-slate-900 hover:bg-slate-850 border-slate-800 hover:border-indigo-500/50"
                      }`}
                    >
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          if (onToggleEntityPriority) onToggleEntityPriority(node.label);
                        }}
                        className="hover:scale-110 transition-transform shrink-0"
                        title={isPri ? "Remove priority" : "Prioritize word"}
                      >
                        <Star className={`w-3 h-3 ${isPri ? "fill-amber-400 text-amber-400" : "text-slate-500 hover:text-amber-300"}`} />
                      </button>
                      <span 
                        onClick={() => {
                          if (node.timestamps?.[0]) {
                            onJumpToVideo(node.timestamps[0].video_id, node.timestamps[0].time || "00:00");
                          }
                        }}
                        className="text-xs font-semibold text-white hover:text-indigo-300 cursor-pointer transition-colors"
                      >
                        {node.label}
                      </span>
                      {node.timestamps?.[0] && (
                        <span 
                          onClick={() => onJumpToVideo(node.timestamps[0].video_id, node.timestamps[0].time || "00:00")}
                          className="text-[10px] text-indigo-400 font-bold cursor-pointer"
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
