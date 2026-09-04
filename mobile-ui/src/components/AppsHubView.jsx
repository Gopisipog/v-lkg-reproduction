import React, { useState } from "react";
import { 
  Plus, Video, Sparkles, Tag,
  Trash2, Edit3, ArrowRight, Brain, Star, ChevronDown, ChevronUp, Workflow
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
  return (
    <div className="p-4 sm:p-6 space-y-6 pb-60 max-w-3xl mx-auto animate-fade-in">
      {/* Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-950/80 via-slate-900 to-purple-950/60 border border-indigo-500/30 p-5 shadow-2xl">
        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 text-[11px] font-semibold">
              <Sparkles className="w-3 h-3 text-indigo-400" />
              <span>Multi-Child-App Knowledge Hub</span>
            </div>
            <h2 className="text-lg sm:text-xl font-black text-white tracking-tight">
              Leadership & Linear Words Platform
            </h2>
            <p className="text-xs text-slate-300 max-w-md">
              Create isolated knowledge apps, assign YouTube videos, configure intelligence lenses, and explore linear word streams.
            </p>
          </div>

          <button
            onClick={onCreateAppClick}
            className="flex items-center justify-center space-x-2 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-bold text-xs py-2.5 px-4 rounded-2xl shadow-lg shadow-indigo-500/25 transition-all active:scale-95 shrink-0"
          >
            <Plus className="w-4 h-4" />
            <span>New Child App</span>
          </button>
        </div>
      </div>

      {/* Child Apps Grid - 1 card per row */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Active Child Workspaces ({apps.length})
          </h3>
          <button
            onClick={() => onNavigateTab("ask")}
            className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center space-x-1"
          >
            <span>Compare Apps ("Twice Answered")</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {apps.map((app) => {
            const isSelected = activeApp?.id === app.id;
            const AppIcon = ICON_MAP[app.icon] || ICON_MAP.Layers;
            const entities = app.top_entities || [];
            const prioritizedSet = new Set(app.prioritized_entities || []);
            const isExpanded = !!expandedCards[app.id];
            const visibleEntities = isExpanded ? entities : entities.slice(0, 10);

            return (
              <div
                key={app.id}
                className={`relative rounded-2xl border p-4.5 transition-all duration-200 flex flex-col justify-between ${
                  isSelected 
                    ? "bg-slate-850/90 border-indigo-500 ring-2 ring-indigo-500/20 shadow-xl" 
                    : "bg-slate-900/80 border-slate-800 hover:border-slate-700 hover:bg-slate-850/50"
                }`}
              >
                <div>
                  {/* Card Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-10 h-10 rounded-2xl flex items-center justify-center text-white shadow-md cursor-pointer"
                        style={{ backgroundColor: app.theme_color || "#6366f1" }}
                        onClick={() => onSelectApp(app)}
                      >
                        <AppIcon className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 
                          className="text-sm font-bold text-white flex items-center space-x-2 cursor-pointer hover:text-indigo-300 transition-colors"
                          onClick={() => onSelectApp(app)}
                        >
                          <span>{app.name}</span>
                          {isSelected && (
                            <span className="text-[10px] bg-indigo-500/30 text-indigo-300 border border-indigo-500/40 px-2 py-0.2 rounded-full font-semibold">
                              ACTIVE
                            </span>
                          )}
                        </h4>
                        <div className="flex items-center space-x-2 text-[11px] text-slate-400 mt-0.5">
                          <span>{app.stats?.video_count || 0} Videos</span>
                          <span>·</span>
                          <span>{app.stats?.entity_count || 0} Linear Words</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-1">
                      <button
                        onClick={() => onEditAppClick(app)}
                        className="p-1.5 rounded-xl hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
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
                        className="p-1.5 rounded-xl hover:bg-rose-950/40 text-slate-400 hover:text-rose-400 transition-colors"
                        title="Delete app"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-xs text-slate-300 mt-3 line-clamp-2 leading-relaxed">
                    {app.description}
                  </p>

                  {/* Intelligence Domains */}
                  <div className="flex flex-wrap gap-1.5 mt-2.5">
                    {app.focus_domains?.map((dom) => (
                      <span 
                        key={dom}
                        className="text-[10px] px-2 py-0.5 rounded-lg bg-slate-800 text-slate-400 font-medium border border-slate-700/60"
                      >
                        {dom}
                      </span>
                    ))}
                  </div>

                  {/* Prioritisable Linear Words / Entities Section */}
                  <div className="mt-3.5 pt-3 border-t border-slate-800/80 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-1.5 text-[11px] font-bold text-slate-300">
                        <Tag className="w-3.5 h-3.5 text-indigo-400" />
                        <span>Linear Words & Entities ({entities.length})</span>
                      </div>
                      <span className="text-[10px] text-slate-400">
                        Tap <Star className="w-2.5 h-2.5 inline text-amber-400 fill-amber-400 -mt-0.5" /> to prioritize
                      </span>
                    </div>

                    {entities.length > 0 ? (
                      <div className="space-y-1.5">
                        <div className="flex flex-wrap gap-1.5">
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
                                className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-xl text-[10px] font-semibold transition-all border ${
                                  isPri 
                                    ? "bg-amber-500/15 border-amber-500/50 text-amber-300 shadow-sm shadow-amber-500/10" 
                                    : "bg-slate-800/90 hover:bg-slate-750 border-slate-700/80 text-slate-300"
                                }`}
                                title={isPri ? "Click to remove priority" : "Click to prioritize this word"}
                              >
                                <Star 
                                  className={`w-3 h-3 ${
                                    isPri ? "text-amber-400 fill-amber-400" : "text-slate-500 hover:text-amber-300"
                                  }`} 
                                />
                                <span>{ent.label}</span>
                                {isPri && (
                                  <span className="text-[8px] uppercase tracking-wider bg-amber-400/25 px-1 py-0.2 rounded font-black text-amber-300">
                                    Top
                                  </span>
                                )}
                              </button>
                            );
                          })}
                        </div>

                        {entities.length > 10 && (
                          <button
                            onClick={() => toggleExpand(app.id)}
                            className="text-[10px] font-bold text-indigo-400 hover:text-indigo-300 flex items-center space-x-1 pt-0.5"
                          >
                            <span>{isExpanded ? "Show fewer words" : `+${entities.length - 10} more words`}</span>
                            {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                          </button>
                        )}
                      </div>
                    ) : (
                      <div className="py-2 px-3 rounded-xl bg-slate-900/60 border border-dashed border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
                        <span>No linear words in scope yet</span>
                        <button
                          onClick={() => {
                            onSelectApp(app);
                            onManageVideosClick();
                          }}
                          className="text-indigo-400 font-bold hover:underline text-[10px]"
                        >
                          + Assign Videos
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => {
                        onSelectApp(app);
                        onManageVideosClick();
                      }}
                      className="flex items-center space-x-1 px-2.5 py-1 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-300 text-xs font-semibold border border-slate-700 transition-colors"
                    >
                      <Video className="w-3 h-3 text-indigo-400" />
                      <span>Videos</span>
                    </button>

                    <button
                      onClick={() => {
                        onSelectApp(app);
                        onOpenEnrichments();
                      }}
                      className="flex items-center space-x-1 px-2.5 py-1 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-300 text-xs font-semibold border border-slate-700 transition-colors"
                    >
                      <Sparkles className="w-3 h-3 text-amber-400" />
                      <span>Dossier</span>
                    </button>

                    <button
                      onClick={() => {
                        onSelectApp(app);
                        onNavigateTab("player");
                      }}
                      className="flex items-center space-x-1 px-2.5 py-1 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-300 text-xs font-semibold border border-slate-700 transition-colors"
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
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-white text-xs font-bold transition-all active:scale-95 shadow-sm"
                    style={{ backgroundColor: app.theme_color || "#6366f1" }}
                  >
                    <span>Linear Words</span>
                    <Tag className="w-3 h-3" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Extra Bottom Buffer Space */}
        <div className="h-20 w-full" aria-hidden="true" />
      </div>
    </div>
  );
}
