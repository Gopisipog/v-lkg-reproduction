import React, { useState, useEffect } from "react";
import { X, Sparkles, TrendingUp, Layers, ArrowRight } from "lucide-react";
import { getAppInsights } from "../services/api";

export default function EnrichmentsModal({ isOpen, onClose, activeApp }) {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && activeApp) {
      setLoading(true);
      getAppInsights(activeApp.id)
        .then(data => setInsights(data))
        .catch(err => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [isOpen, activeApp]);

  if (!isOpen || !activeApp) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/80 backdrop-blur-sm">
      <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-t-2xl sm:rounded-2xl shadow-2xl max-h-[90vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center space-x-3">
            <div 
              className="w-8 h-8 rounded-lg flex items-center justify-center text-white shadow-sm"
              style={{ backgroundColor: activeApp.theme_color || "#0ea5e9" }}
            >
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-semibold tracking-tight text-white">
                Intelligence Dossier & Enrichments
              </h3>
              <p className="text-[11px] font-mono text-slate-400">
                Grounded in <span className="text-white font-medium">{activeApp.name}</span>
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1 rounded-lg bg-slate-800/80 hover:bg-slate-750 text-slate-400 hover:text-white transition-colors tactile-btn"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 overflow-y-auto space-y-4">
          {loading ? (
            <div className="py-12 flex flex-col items-center justify-center space-y-3">
              <div className="w-7 h-7 border-2 border-sky-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs font-mono text-slate-400">Synthesizing scoped intelligence telemetry...</p>
            </div>
          ) : (
            <>
              {/* Summary Card */}
              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm">
                <h4 className="text-[10px] font-mono uppercase tracking-wider text-sky-400 mb-1">
                  Executive Brief & Objective
                </h4>
                <p className="text-xs text-slate-300 leading-relaxed font-sans">
                  {activeApp.description || "Synthesized leadership intelligence spanning assigned multimedia sources."}
                </p>
                <div className="mt-3 pt-2.5 border-t border-slate-800 flex flex-wrap items-center gap-3 text-[10px] font-mono text-slate-400">
                  <span className="flex items-center space-x-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-sky-400 inline-block" />
                    <span><strong className="text-white">{insights?.total_nodes || 0}</strong> Entities</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block" />
                    <span><strong className="text-white">{insights?.total_links || 0}</strong> Pathways</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 inline-block" />
                    <span><strong className="text-white">{activeApp?.stats?.video_count || 0}</strong> Streams</span>
                  </span>
                </div>
              </div>

              {/* Top Central Entities */}
              <div>
                <h4 className="text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-2 flex items-center space-x-1.5">
                  <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Top Central Entities (Influence Ranking)</span>
                </h4>
                <div className="grid grid-cols-2 gap-2">
                  {insights?.top_central_entities?.map((ent) => (
                    <div 
                      key={ent.id} 
                      className="p-2.5 rounded-lg bg-slate-900/70 border border-slate-800 flex items-center justify-between shadow-xs"
                    >
                      <div className="min-w-0 pr-2">
                        <p className="text-xs font-semibold text-white truncate">{ent.label}</p>
                        <p className="text-[10px] font-mono text-slate-400 uppercase">{ent.type}</p>
                      </div>
                      <div className="px-1.5 py-0.5 rounded bg-sky-500/15 border border-sky-500/30 text-sky-300 text-[10px] font-mono font-bold">
                        {ent.centrality}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Dependency Chains */}
              <div>
                <h4 className="text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-2 flex items-center space-x-1.5">
                  <Layers className="w-3.5 h-3.5 text-sky-400" />
                  <span>Prerequisite & Dependency Chains</span>
                </h4>
                <div className="space-y-1.5">
                  {insights?.dependency_chains?.length ? (
                    insights.dependency_chains.map((chain, idx) => (
                      <div 
                        key={idx}
                        className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs"
                      >
                        <span className="font-medium text-slate-200 truncate max-w-[40%]">{chain.source}</span>
                        <div className="flex items-center space-x-1 text-slate-400 px-1 shrink-0">
                          <span className="text-[9px] font-mono uppercase font-semibold text-sky-400">{chain.relation}</span>
                          <ArrowRight className="w-3 h-3 text-slate-500" />
                        </div>
                        <span className="font-medium text-slate-200 truncate max-w-[40%] text-right">{chain.target}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs font-mono text-slate-500 italic p-3 rounded-lg border border-dashed border-slate-800 text-center">
                      No direct prerequisite links in current scope.
                    </p>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
