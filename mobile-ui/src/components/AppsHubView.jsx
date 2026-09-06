import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Plus, Video, Sparkles, Tag,
  Trash2, Edit3, ArrowRight, Star, ChevronDown, ChevronUp, Workflow, Radio, Database, CheckCircle2, Palette, Check
} from "lucide-react";
import { ICON_MAP } from "./TopHeader";
import { 
  BI_COLOR_PRESETS, 
  TRI_COLOR_PRESETS, 
  PATTERN_MODES, 
  getPatternBackground, 
  resolveAppTheme 
} from "../utils/colorSchemes";
import { saveAppToAura, updateApp } from "../services/api";

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
  const [auraSyncStatus, setAuraSyncStatus] = useState({});
  const [auraMessage, setAuraMessage] = useState(null);

  // Cockpit Color Schemes & Bi/Tri Patterns State
  const [activeSchemeTab, setActiveSchemeTab] = useState("bi"); // "bi" | "tri"
  const [selectedScheme, setSelectedScheme] = useState(BI_COLOR_PRESETS[0]);
  const [selectedPattern, setSelectedPattern] = useState("gradient-bi");
  const [schemeFeedback, setSchemeFeedback] = useState(null);
  const [savingScheme, setSavingScheme] = useState(false);

  const toggleExpand = (appId) => {
    setExpandedCards((prev) => ({
      ...prev,
      [appId]: !prev[appId]
    }));
  };

  const handleSyncAppToAura = async (appId, e) => {
    e.stopPropagation();
    setAuraSyncStatus(prev => ({ ...prev, [appId]: "syncing" }));
    try {
      const res = await saveAppToAura(appId);
      if (res.success) {
        setAuraSyncStatus(prev => ({ ...prev, [appId]: "synced" }));
        setAuraMessage(`Persisted child app '${appId}' to Neo4j Aura DB.`);
      } else {
        setAuraSyncStatus(prev => ({ ...prev, [appId]: "queued" }));
        setAuraMessage(res.message || "Aura DB paused/offline; child app queued for sync.");
      }
      setTimeout(() => setAuraMessage(null), 5000);
    } catch (err) {
      setAuraSyncStatus(prev => ({ ...prev, [appId]: "queued" }));
      setAuraMessage("Child app saved locally; Aura DB sync queued.");
      setTimeout(() => setAuraMessage(null), 5000);
    }
  };

  const handleApplySchemeToWorkspace = async (targetApp, scheme, pattern) => {
    if (!targetApp) return;
    setSavingScheme(true);
    try {
      const updated = await updateApp(targetApp.id, {
        ...targetApp,
        color_scheme: scheme.id,
        pattern: pattern,
        pattern_colors: scheme.colors,
        theme_color: scheme.colors[0]
      });
      await saveAppToAura(targetApp.id);
      setSchemeFeedback(`Saved '${scheme.name}' (${pattern}) to workspace '${targetApp.name}' & synced Aura DB.`);
      if (onSelectApp) onSelectApp(updated);
      setTimeout(() => setSchemeFeedback(null), 5000);
    } catch (err) {
      setSchemeFeedback(`Updated locally: ${err.message}`);
      setTimeout(() => setSchemeFeedback(null), 5000);
    } finally {
      setSavingScheme(false);
    }
  };

  const handleSaveCockpitTheme = (scheme, pattern) => {
    const payload = {
      id: scheme.id,
      name: scheme.name,
      type: scheme.type,
      pattern: pattern,
      colors: scheme.colors
    };
    try {
      localStorage.setItem("vlkg_cockpit_scheme", JSON.stringify(payload));
      setSchemeFeedback(`Cockpit global theme set to '${scheme.name}'.`);
      setTimeout(() => setSchemeFeedback(null), 5000);
    } catch (e) {
      console.warn("Failed to set localStorage", e);
    }
  };

  const totalVideos = apps.reduce((acc, a) => acc + (a.stats?.video_count || 0), 0);
  const totalWords = apps.reduce((acc, a) => acc + (a.stats?.entity_count || 0), 0);
  const activeAppTheme = resolveAppTheme(activeApp);

  return (
    <div className="p-3 sm:p-5 space-y-4 pb-48 max-w-4xl mx-auto">
      {/* Aura DB Toast Feedback */}
      <AnimatePresence>
        {auraMessage && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="p-2.5 rounded-lg bg-emerald-950/90 border border-emerald-700/60 text-emerald-200 text-xs font-mono flex items-center justify-between shadow-lg"
          >
            <div className="flex items-center space-x-2">
              <Database className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>{auraMessage}</span>
            </div>
            <button 
              onClick={() => setAuraMessage(null)}
              className="text-emerald-400 hover:text-white ml-2 text-xs"
            >
              [X]
            </button>
          </motion.div>
        )}
      </AnimatePresence>
      {/* ── Asymmetric Bento 2.0 Cockpit Hero ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Left Asymmetric Tile (2 cols) */}
        <div className="md:col-span-2 relative overflow-hidden rounded-xl bg-slate-900 border border-slate-800 p-4 flex flex-col justify-between">
          <div 
            className="absolute inset-0 pointer-events-none opacity-50 transition-all duration-500" 
            style={{ background: activeAppTheme.cardAtmosphere }}
          />
          <div 
            className="absolute top-0 left-0 right-0 h-1 transition-all duration-500" 
            style={{ background: activeAppTheme.background }}
          />
          <div className="space-y-1.5 relative z-10">
            <div className="inline-flex items-center space-x-1.5 px-2 py-0.5 rounded bg-slate-950/80 border border-slate-800 text-slate-300 text-[10px] font-mono uppercase tracking-wider">
              <Radio className="w-3 h-3 text-cyan-400 animate-pulse" />
              <span>VLKG Telemetry Engine · {activeApp?.name || "Global"}</span>
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

      {/* ── Cockpit Mixed Color Schemes & Bi/Tri Patterns Section ── */}
      <div className="rounded-xl bg-slate-900 border border-slate-800 p-4 space-y-3.5 shadow-md">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded-md bg-cyan-950/80 border border-cyan-800/60 flex items-center justify-center text-cyan-400">
              <Palette className="w-3.5 h-3.5" />
            </div>
            <div>
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-white flex items-center space-x-2">
                <span>Cockpit Color Schemes & Patterns</span>
                <span className="text-[9px] px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/40">
                  BI & TRI MIXED
                </span>
              </h3>
              <p className="text-[11px] text-slate-400">
                Mixed colorways & geometric patterns. Select below to customize & persist to Neo4j Aura DB.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-1.5">
            <button
              onClick={() => {
                setActiveSchemeTab("bi");
                setSelectedScheme(BI_COLOR_PRESETS[0]);
              }}
              className={`px-2.5 py-1 rounded-md text-xs font-mono font-medium transition-all ${
                activeSchemeTab === "bi"
                  ? "bg-cyan-600 text-slate-950 font-bold shadow-sm"
                  : "bg-slate-800 text-slate-400 hover:text-slate-200"
              }`}
            >
              Bi-Color (Dual)
            </button>
            <button
              onClick={() => {
                setActiveSchemeTab("tri");
                setSelectedScheme(TRI_COLOR_PRESETS[0]);
                if (selectedPattern === "gradient-bi") setSelectedPattern("gradient-tri");
              }}
              className={`px-2.5 py-1 rounded-md text-xs font-mono font-medium transition-all ${
                activeSchemeTab === "tri"
                  ? "bg-cyan-600 text-slate-950 font-bold shadow-sm"
                  : "bg-slate-800 text-slate-400 hover:text-slate-200"
              }`}
            >
              Tri-Color (Triple)
            </button>
          </div>
        </div>

        {/* Scheme Feedback Notification */}
        <AnimatePresence>
          {schemeFeedback && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="px-3 py-1.5 rounded-lg bg-cyan-950/80 border border-cyan-700/60 text-cyan-300 text-xs font-mono flex items-center justify-between"
            >
              <span>{schemeFeedback}</span>
              <button onClick={() => setSchemeFeedback(null)} className="text-cyan-400 text-xs font-bold">[X]</button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Preset Tiles Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {(activeSchemeTab === "bi" ? BI_COLOR_PRESETS : TRI_COLOR_PRESETS).map((preset) => {
            const isSelected = selectedScheme.id === preset.id;
            return (
              <button
                key={preset.id}
                onClick={() => setSelectedScheme(preset)}
                className={`tactile-btn p-2 rounded-lg border text-left flex flex-col justify-between space-y-1.5 transition-all ${
                  isSelected
                    ? "bg-slate-850 border-cyan-500 ring-1 ring-cyan-500/50"
                    : "bg-slate-950/60 border-slate-800/80 hover:border-slate-700 text-slate-400"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-white tracking-tight truncate">
                    {preset.name}
                  </span>
                  {isSelected && <Check className="w-3 h-3 text-cyan-400 shrink-0" />}
                </div>

                {/* Color Swatch Bar */}
                <div className="w-full h-3 rounded overflow-hidden flex border border-slate-700/50">
                  {preset.colors.map((c, i) => (
                    <div key={i} className="h-full flex-1" style={{ backgroundColor: c }} />
                  ))}
                </div>

                <div className="flex items-center justify-between text-[9px] font-mono text-slate-400">
                  <span>{preset.colors.join(" · ")}</span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Geometric Pattern Selector */}
        <div className="space-y-1.5 pt-1 border-t border-slate-800/60">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
              Geometric Pattern Geometry
            </span>
            <span className="text-[9px] font-mono text-slate-500">Selected: {selectedPattern}</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-5 gap-1.5">
            {PATTERN_MODES.map((mode) => {
              const isPatternActive = selectedPattern === mode.id;
              const previewBg = getPatternBackground(mode.id, selectedScheme.colors);
              return (
                <button
                  key={mode.id}
                  onClick={() => setSelectedPattern(mode.id)}
                  className={`px-2 py-1.5 rounded-lg border text-left flex items-center space-x-2 transition-all ${
                    isPatternActive
                      ? "bg-slate-800 border-cyan-500 text-white ring-1 ring-cyan-500/40"
                      : "bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <div
                    className="w-4 h-4 rounded-full border border-slate-700 shrink-0 shadow-sm"
                    style={{ background: previewBg }}
                  />
                  <span className="text-[10px] font-mono truncate">{mode.name.split(" ")[0]}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Live Preview & Apply / Save Bar */}
        <div 
          className="p-3 rounded-lg border border-slate-700/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 relative overflow-hidden"
        >
          {/* Subtle atmosphere background */}
          <div 
            className="absolute inset-0 opacity-20 pointer-events-none transition-all duration-500" 
            style={{ background: getPatternBackground(selectedPattern, selectedScheme.colors) }}
          />
          <div className="relative z-10 flex items-center space-x-3">
            <div 
              className="w-9 h-9 rounded-lg border border-slate-700 flex items-center justify-center shrink-0 shadow-md"
              style={{ background: getPatternBackground(selectedPattern, selectedScheme.colors) }}
            >
              <Palette className="w-4 h-4 text-white drop-shadow" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <p className="text-xs font-bold text-white font-mono">{selectedScheme.name}</p>
                <span className="text-[9px] font-mono uppercase px-1 py-0.2 rounded bg-slate-800 text-cyan-300 border border-slate-700">
                  {selectedPattern}
                </span>
              </div>
              <p className="text-[10px] font-mono text-slate-400">
                {selectedScheme.colors.length}-Color Mix · {selectedScheme.description}
              </p>
            </div>
          </div>

          <div className="relative z-10 flex items-center space-x-2 w-full sm:w-auto">
            {activeApp && (
              <button
                onClick={() => handleApplySchemeToWorkspace(activeApp, selectedScheme, selectedPattern)}
                disabled={savingScheme}
                className="tactile-btn flex-1 sm:flex-initial flex items-center justify-center space-x-1 px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-slate-950 text-xs font-mono font-bold transition-all shadow-sm"
              >
                <Check className="w-3.5 h-3.5" />
                <span>Save to '{activeApp.name.substring(0, 14)}...'</span>
              </button>
            )}

            <button
              onClick={() => handleSaveCockpitTheme(selectedScheme, selectedPattern)}
              className="tactile-btn px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 text-xs font-mono transition-all"
              title="Save as Global Cockpit Theme"
            >
              Set Default
            </button>
          </div>
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
            const appTheme = resolveAppTheme(app);
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
                className={`rounded-xl border transition-all duration-150 p-3.5 flex flex-col justify-between overflow-hidden relative ${
                  isSelected 
                    ? "bg-slate-900/95 border-cyan-500/70 shadow-md ring-1 ring-cyan-500/30" 
                    : "bg-slate-900/70 border-slate-800/80 hover:border-slate-750 hover:bg-slate-900"
                }`}
              >
                {/* Top Pattern Accent Bar */}
                <div 
                  className="h-1 -mx-3.5 -mt-3.5 mb-3 transition-all opacity-85"
                  style={{ background: appTheme.background }}
                />

                <div>
                  {/* Top Bar: Icon, Name, Telemetry Badges, Action triggers */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2.5">
                      <div 
                        className="w-8 h-8 rounded-lg flex items-center justify-center text-white shrink-0 cursor-pointer tactile-btn shadow-md transition-all"
                        style={{ background: appTheme.background }}
                        onClick={() => onSelectApp(app)}
                      >
                        <AppIcon className="w-4 h-4 drop-shadow" />
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
                          <span className="text-[9px] font-mono text-slate-400 bg-slate-800/80 px-1 py-0.2 rounded border border-slate-700/50 uppercase hidden sm:inline">
                            {appTheme.pattern}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2 text-[10px] font-mono text-slate-400 mt-0.5">
                          <span>{app.stats?.video_count || 0} VIDS</span>
                          <span className="text-slate-600">·</span>
                          <span>{app.stats?.entity_count || 0} LINEAR WORDS</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-1.5">
                      <button
                        onClick={(e) => handleSyncAppToAura(app.id, e)}
                        className={`tactile-btn flex items-center space-x-1 px-2 py-1 rounded-md text-[10px] font-mono border transition-all ${
                          auraSyncStatus[app.id] === "synced"
                            ? "bg-emerald-950/80 border-emerald-600/70 text-emerald-300"
                            : auraSyncStatus[app.id] === "syncing"
                            ? "bg-cyan-950/80 border-cyan-600/70 text-cyan-300 animate-pulse"
                            : "bg-slate-800/80 border-slate-700/60 text-slate-300 hover:text-white hover:border-emerald-500/50"
                        }`}
                        title="Persist or sync this child app into Neo4j Aura DB"
                      >
                        <Database className="w-3 h-3 text-emerald-400" />
                        <span>
                          {auraSyncStatus[app.id] === "synced" ? "AURA SYNCED" : auraSyncStatus[app.id] === "syncing" ? "SYNCING..." : "AURA DB"}
                        </span>
                      </button>

                      <button
                        onClick={() => onEditAppClick(app)}
                        className="tactile-btn p-1.5 rounded-md hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                        title="Edit app details & pattern"
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

