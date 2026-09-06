import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Plus, Video, Sparkles, Tag,
  Trash2, Edit3, ArrowRight, Star, ChevronDown, ChevronUp, Workflow, Radio
} from "lucide-react";
import { ICON_MAP } from "./TopHeader";

export default function AppsHubView({
  apps,
  activeApp,
  onSelectApp,
  onCreateAppClick,
  onEditAppClick,
  onDeleteApp,
  onManageVideosClick,
  onOpenEnrichments,
  onNavigateTab,
  onToggleEntityPriority
}) {
  const [expandedCards, setExpandedCards] = useState({});

  const toggleExpand = (appId) => {
    setExpandedCards((prev) => ({
      ...prev,
      [appId]: !prev[appId]
    }));
  };

  const totalVideos = apps.reduce((acc, a) => acc + (a.stats?.video_count || 0), 0);
  const totalWords = apps.reduce((acc, a) => acc + (a.stats?.entity_count || 0), 0);

  return (
    <div className="p-3 sm:p-5 space-y-4 pb-48 max-w-4xl mx-auto">
      {/* ── Asymmetric Bento 2.0 Cockpit Hero ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Left Asymmetric Tile (2 cols) */}
        <div className="md:col-span-2 relative overflow-hidden rounded-xl bg-slate-900 border border-slate-800 p-4 flex flex-col justify-between">
          <div className="space-y-1.5">
            <div className="inline-flex items-center space-x-1.5 px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/50 text-cyan-300 text-[10px] font-mono uppercase tracking-wider">
              <Radio className="w-3 h-3 text-cyan-400 animate-pulse" />
              <span>VLKG Knowledge Engine · Telemetry Active</span>
            </div>
            <h2 className="text-base sm:text-lg font-bold text-white tracking-tight leading-tight">
              Leadership & Linear Words Platform
            </h2>
            <p className="text-xs text-slate-400 max-w-lg leading-relaxed">
              Isolated knowledge graphs, video ingest pipelines, intelligence lenses, and live entity streams.
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center space-x-3 text-xs font-mono text-slate-400">
              <div>
                <span className="text-white font-bold">{apps.length}</span>
                <span className="text-slate-500 ml-1">WORKSPACES</span>
              </div>
              <span className="text-slate-700">|</span>
              <div>
                <span className="text-white font-bold">{totalVideos}</span>
                <span className="text-slate-500 ml-1">VIDEOS</span>
              </div>
              <span className="text-slate-700">|</span>
              <div>
                <span className="text-cyan-400 font-bold">{totalWords}</span>
                <span className="text-slate-500 ml-1">WORDS</span>
              </div>
            </div>

            <button
              onClick={onCreateAppClick}
              className="tactile-btn flex items-center space-x-1.5 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-mono font-bold text-xs py-1.5 px-3 rounded-lg shadow-sm"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>New Child App</span>
            </button>
          </div>
        </div>

        {/* Right Asymmetric Telemetry Card (1 col) */}
        <div className="rounded-xl bg-slate-900 border border-slate-800 p-4 flex flex-col justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500">Cross-App Engine</span>
            <h3 className="text-xs font-bold text-slate-200">Comparative Queries</h3>
            <p className="text-[11px] text-slate-400 leading-normal">
              Compare executive principles and insights across apps via "Twice Answered" dual-rag.
            </p>
          </div>

          <button
            onClick={() => onNavigateTab("ask")}
            className="tactile-btn mt-3 w-full flex items-center justify-between px-3 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-800 text-slate-200 border border-slate-700/60 text-xs font-mono transition-colors"
          >
            <span>Launch Dual Query</span>
            <ArrowRight className="w-3.5 h-3.5 text-cyan-400" />
          </button>
        </div>
      </div>

      {/* ── Active Workspaces (High Visual Density Cockpit Layout) ── */}
      <div className="space-y-2">
        <div className="flex items-center justify-between px-1">
          <div className="flex items-center space-x-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-status-breathe" />
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
              Active Child Workspaces ({apps.length})
            </h3>
          </div>
          <span className="text-[10px] font-mono text-slate-500">
            Density: 8 · Variance: 8
          </span>
        </div>

        {/* Workspaces List / Asymmetric Cockpit Rows */}
        <motion.div 
          className="space-y-2.5"
          initial="hidden"
          animate="visible"
          variants={{
            visible: { transition: { staggerChildren: 0.05 } }
          }}
        >
          {apps.map((app) => {
            const isSelected = activeApp?.id === app.id;
            const AppIcon = ICON_MAP[app.icon] || ICON_MAP.Layers;
            const entities = app.top_entities || [];
            const prioritizedSet = new Set(app.prioritized_entities || []);
            const isExpanded = !!expandedCards[app.id];
            const visibleEntities = isExpanded ? entities : entities.slice(0, 8);

            return (
              <motion.div
                key={app.id}
                variants={{
                  hidden: { opacity: 0, y: 10 },
                  visible: { opacity: 1, y: 0 }
                }}
                className={`rounded-xl border transition-all duration-150 p-3.5 flex flex-col justify-between ${
                  isSelected 
                    ? "bg-slate-900/95 border-cyan-500/70 shadow-md ring-1 ring-cyan-500/30" 
                    : "bg-slate-900/70 border-slate-800/80 hover:border-slate-750 hover:bg-slate-900"
                }`}
              >
                <div>
                  {/* Top Bar: Icon, Name, Telemetry Badges, Action triggers */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2.5">
                      <div 
                        className="w-8 h-8 rounded-lg flex items-center justify-center text-white shrink-0 cursor-pointer tactile-btn shadow-inner"
                        style={{ backgroundColor: app.theme_color || "#0ea5e9" }}
                        onClick={() => onSelectApp(app)}
                      >
                        <AppIcon className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <h4 
                            className="text-xs sm:text-sm font-bold text-white cursor-pointer hover:text-cyan-300 transition-colors"
                            onClick={() => onSelectApp(app)}
                          >
                            {app.name}
                          </h4>
                          {isSelected && (
                            <span className="text-[9px] font-mono bg-cyan-950/70 text-cyan-300 border border-cyan-700/50 px-1.5 py-0.2 rounded font-bold">
                              ACTIVE
                            </span>
                          )}
                        </div>
                        <div className="flex items-center space-x-2 text-[10px] font-mono text-slate-400 mt-0.5">
                          <span>{app.stats?.video_count || 0} VIDS</span>
                          <span className="text-slate-600">·</span>
                          <span>{app.stats?.entity_count || 0} LINEAR WORDS</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-1">
                      <button
                        onClick={() => onEditAppClick(app)}
                        className="tactile-btn p-1.5 rounded-md hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                        title="Edit app details"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => {
                          if (confirm(`Delete '${app.name}'?`)) {
                            onDeleteApp(app.id);
                          }
                        }}
                        className="tactile-btn p-1.5 rounded-md hover:bg-rose-950/40 text-slate-400 hover:text-rose-400 transition-colors"
                        title="Delete app"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-xs text-slate-300 mt-2 line-clamp-2 leading-relaxed">
                    {app.description}
                  </p>

                  {/* Focus Domains */}
                  {app.focus_domains?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {app.focus_domains.map((dom) => (
                        <span 
                          key={dom}
                          className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/50"
                        >
                          {dom}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Prioritized Linear Words Section (High Density Hairline View) */}
                  <div className="mt-3 pt-2.5 border-t border-slate-800/80 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-1.5 text-[10px] font-mono font-bold text-slate-300">
                        <Tag className="w-3 h-3 text-cyan-400" />
                        <span>LINEAR WORDS & ENTITIES ({entities.length})</span>
                      </div>
                      <span className="text-[9px] font-mono text-slate-500">
                        Tap star to prioritize
                      </span>
                    </div>

                    {entities.length > 0 ? (
                      <div className="space-y-1">
                        <div className="flex flex-wrap gap-1">
                          {visibleEntities.map((ent) => {
                            const isPri = ent.is_priority || prioritizedSet.has(ent.label) || prioritizedSet.has(ent.id);
                            return (
                              <button
                                key={ent.id || ent.label}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  if (onToggleEntityPriority) {
                                    onToggleEntityPriority(app.id, ent.label);
                                  }
                                }}
                                className={`tactile-btn inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-mono transition-all border ${
                                  isPri 
                                    ? "bg-amber-950/40 border-amber-600/60 text-amber-300 font-bold" 
                                    : "bg-slate-800/70 hover:bg-slate-800 border-slate-750 text-slate-300"
                                }`}
                                title={isPri ? "Click to remove priority" : "Click to prioritize this word"}
                              >
                                <Star 
                                  className={`w-2.5 h-2.5 ${
                                    isPri ? "text-amber-400 fill-amber-400" : "text-slate-500"
                                  }`} 
                                />
                                <span>{ent.label}</span>
                                {isPri && (
                                  <span className="text-[8px] bg-amber-500/20 px-1 rounded text-amber-400 font-bold">
                                    TOP
                                  </span>
                                )}
                              </button>
                            );
                          })}
                        </div>

                        {entities.length > 8 && (
                          <button
                            onClick={() => toggleExpand(app.id)}
                            className="tactile-btn text-[10px] font-mono font-semibold text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 pt-0.5"
                          >
                            <span>{isExpanded ? "Collapse words" : `+${entities.length - 8} more words`}</span>
                            {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                          </button>
                        )}
                      </div>
                    ) : (
                      <div className="py-1.5 px-2 rounded bg-slate-950 border border-slate-800/80 text-[10px] font-mono text-slate-400 flex items-center justify-between">
                        <span>No linear words in scope</span>
                        <button
                          onClick={() => {
                            onSelectApp(app);
                            onManageVideosClick();
                          }}
                          className="text-cyan-400 font-bold hover:underline"
                        >
                          + Assign Videos
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Cockpit Actions Toolbar */}
                <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center space-x-1.5">
                    <button
                      onClick={() => {
                        onSelectApp(app);
                        onManageVideosClick();
                      }}
                      className="tactile-btn flex items-center space-x-1 px-2 py-1 rounded bg-slate-800 hover:bg-slate-750 text-slate-300 text-[11px] font-mono border border-slate-700/60"
                    >
                      <Video className="w-3 h-3 text-cyan-400" />
                      <span>Videos</span>
                    </button>

                    <button
                      onClick={() => {
                        onSelectApp(app);
                        onOpenEnrichments();
                      }}
                      className="tactile-btn flex items-center space-x-1 px-2 py-1 rounded bg-slate-800 hover:bg-slate-750 text-slate-300 text-[11px] font-mono border border-slate-700/60"
                    >
                      <Sparkles className="w-3 h-3 text-amber-400" />
                      <span>Dossier</span>
                    </button>

                    <button
                      onClick={() => {
                        onSelectApp(app);
                        onNavigateTab("player");
                      }}
                      className="tactile-btn flex items-center space-x-1 px-2 py-1 rounded bg-slate-800 hover:bg-slate-750 text-slate-300 text-[11px] font-mono border border-slate-700/60"
                      title="Explore relationships & transcript semantics"
                    >
                      <Workflow className="w-3 h-3 text-emerald-400" />
                      <span>Semantics</span>
                    </button>
                  </div>

                  <button
                    onClick={() => {
                      onSelectApp(app);
                      onNavigateTab("words");
                    }}
                    className="tactile-btn flex items-center space-x-1.5 px-2.5 py-1 rounded text-slate-950 text-xs font-mono font-bold transition-all shadow-sm"
                    style={{ backgroundColor: app.theme_color || "#0ea5e9" }}
                  >
                    <span>Linear Words</span>
                    <Tag className="w-3 h-3" />
                  </button>
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </div>
  );
}

