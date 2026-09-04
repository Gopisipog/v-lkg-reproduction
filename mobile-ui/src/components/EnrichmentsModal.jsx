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
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-xl bg-slate-900 border border-slate-700/80 rounded-t-3xl sm:rounded-3xl shadow-2xl max-h-[90vh] flex flex-col overflow-hidden animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div 
              className="w-8 h-8 rounded-xl flex items-center justify-center text-white"
              style={{ backgroundColor: activeApp.theme_color || "#6366f1" }}
            >
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">
                Intelligence Dossier & Enrichments
              </h3>
              <p className="text-xs text-slate-400">
                Grounded in <span className="text-white font-medium">{activeApp.name}</span>
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 rounded-full bg-slate-800 hover:bg-slate-750 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-6">
          {loading ? (
            <div className="py-12 flex flex-col items-center justify-center space-y-3">
              <div className="w-8 h-8 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs text-slate-400">Synthesizing scoped intelligence metrics...</p>
            </div>
          ) : (
            <>
              {/* Summary Card */}
              <div className="p-4 rounded-2xl bg-slate-850 border border-slate-700/70">
                <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-400 mb-1">
                  Executive Brief & Objective
                </h4>
                <p className="text-xs text-slate-200 leading-relaxed">
                  {activeApp.description || "Synthesized leadership intelligence spanning assigned multimedia sources."}
                </p>
                <div className="mt-3 flex items-center space-x-3 text-[11px] text-slate-400">
                  <span>● {insights?.total_nodes || 0} Linear Words / Entities</span>
                  <span>● {insights?.total_links || 0} Sequential Pathways</span>
                  <span>● {activeApp?.stats?.video_count || 0} Video Streams</span>
                </div>
              </div>

              {/* Top Central Entities */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center space-x-1.5">
                  <TrendingUp className="w-4 h-4 text-emerald-400" />
                  <span>Top Central Entities (Influence Ranking)</span>
                </h4>
                <div className="grid grid-cols-2 gap-2">
                  {insights?.top_central_entities?.map((ent) => (
                    <div 
                      key={ent.id} 
                      className="p-2.5 rounded-xl bg-slate-850/80 border border-slate-800 flex items-center justify-between"
                    >
                      <div className="min-w-0 pr-2">
                        <p className="text-xs font-semibold text-white truncate">{ent.label}</p>
                        <p className="text-[10px] text-slate-400">{ent.type}</p>
                      </div>
                      <div className="px-2 py-0.5 rounded-lg bg-indigo-500/20 text-indigo-300 text-[10px] font-bold">
                        {ent.centrality}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Dependency Chains */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center space-x-1.5">
                  <Layers className="w-4 h-4 text-purple-400" />
                  <span>Prerequisite & Dependency Chains</span>
                </h4>
                <div className="space-y-2">
                  {insights?.dependency_chains?.length ? (
                    insights.dependency_chains.map((chain, idx) => (
                      <div 
                        key={idx}
                        className="p-2.5 rounded-xl bg-slate-850/60 border border-slate-800 flex items-center justify-between text-xs"
                      >
                        <span className="font-semibold text-slate-200">{chain.source}</span>
                        <div className="flex items-center space-x-1 text-slate-400 px-2">
                          <span className="text-[10px] uppercase font-bold text-indigo-400">{chain.relation}</span>
                          <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                        </div>
                        <span className="font-semibold text-slate-200">{chain.target}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-500 italic">No direct prerequisite links in current scope.</p>
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
