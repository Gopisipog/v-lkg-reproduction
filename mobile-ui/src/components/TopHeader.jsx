import React, { useState, useEffect } from "react";
import { 
  ChevronDown, Layers, Sparkles, Briefcase, Cpu, TrendingUp, 
  Plus, Check, Video, Smartphone, Monitor, ShieldCheck, Users, 
  Crosshair, GraduationCap, Palette, Database, CheckCircle2, Film
} from "lucide-react";
import { 
  BI_COLOR_PRESETS, 
  TRI_COLOR_PRESETS, 
  PATTERN_MODES, 
  getPatternBackground, 
  resolveAppTheme 
} from "../utils/colorSchemes";
import { getDatabaseStatus, syncDataToAura } from "../services/api";

export const ICON_MAP = {
  Briefcase,
  Cpu,
  Sparkles,
  TrendingUp,
  Layers,
  GraduationCap,
  ShieldCheck,
  Users,
  Crosshair,
  Film
};

export default function TopHeader({
  activeApp,
  apps,
  onSelectApp,
  onCreateAppClick,
  onUpdateAppScheme,
  onManageVideosClick,
  isPhoneFrame,
  onToggleFrame,
  onOpenDatabaseModal
}) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [themeModalOpen, setThemeModalOpen] = useState(false);
  const [auraSyncing, setAuraSyncing] = useState(false);
  const [auraFeedback, setAuraFeedback] = useState(null);
  const [dbState, setDbState] = useState({ connected: false, label: "DATA STORE" });

  useEffect(() => {
    let isMounted = true;
    getDatabaseStatus()
      .then((res) => {
        if (isMounted && res) {
          const isAura = Boolean(res.is_connected_to_aura || res.status === "connected");
          setDbState({
            connected: isAura,
            label: isAura ? "AURA DB" : "DATA STORE"
          });
        }
      })
      .catch(() => {});
    return () => {
      isMounted = false;
    };
  }, []);

  // Global Cockpit Scheme State (saved in localStorage)
  const [cockpitScheme, setCockpitScheme] = useState(() => {
    try {
      const saved = localStorage.getItem("vlkg_cockpit_scheme");
      return saved ? JSON.parse(saved) : {
        id: "cyber-cyan",
        name: "Cyber Cyan & Emerald",
        type: "bi",
        pattern: "gradient-bi",
        colors: ["#0EA5E9", "#10B981"]
      };
    } catch {
      return {
        id: "cyber-cyan",
        name: "Cyber Cyan & Emerald",
        type: "bi",
        pattern: "gradient-bi",
        colors: ["#0EA5E9", "#10B981"]
      };
    }
  });

  const saveCockpitScheme = (scheme, pattern = cockpitScheme.pattern) => {
    const updated = {
      ...scheme,
      pattern
    };
    setCockpitScheme(updated);
    try {
      localStorage.setItem("vlkg_cockpit_scheme", JSON.stringify(updated));
    } catch (e) {
      console.warn("Failed to persist cockpit scheme to localStorage", e);
    }
    // Update the same active app directly without creating a new app
    if (onUpdateAppScheme) {
      onUpdateAppScheme(scheme, pattern);
    }
  };

  const savePatternMode = (patternId) => {
    const updated = {
      ...cockpitScheme,
      pattern: patternId
    };
    setCockpitScheme(updated);
    try {
      localStorage.setItem("vlkg_cockpit_scheme", JSON.stringify(updated));
    } catch (e) {
      console.warn("Failed to persist pattern to localStorage", e);
    }
    // Update the same active app directly without creating a new app
    if (onUpdateAppScheme) {
      onUpdateAppScheme(cockpitScheme, patternId);
    }
  };

  const handleGlobalAuraSync = async () => {
    setAuraSyncing(true);
    try {
      const res = await syncDataToAura();
      setAuraFeedback(res.message || "Synced graph to Neo4j Aura DB.");
      setTimeout(() => setAuraFeedback(null), 5000);
    } catch (err) {
      setAuraFeedback(err.message || "Aura DB offline; local store active.");
      setTimeout(() => setAuraFeedback(null), 5000);
    } finally {
      setAuraSyncing(false);
    }
  };

  const AppIcon = activeApp && ICON_MAP[activeApp.icon] ? ICON_MAP[activeApp.icon] : Layers;
  const currentAppTheme = resolveAppTheme(activeApp);
  const globalPatternBg = getPatternBackground(cockpitScheme.pattern, cockpitScheme.colors);

  return (
    <header className="sticky top-0 z-40 bg-slate-950/95 backdrop-blur-md border-b border-slate-800/80 px-3.5 py-2.5 flex items-center justify-between relative">
      {/* Dynamic Top Edge Telemetry Accent Bar */}
      <div 
        className="absolute top-0 left-0 right-0 h-[2.5px] z-50 transition-all duration-500 shadow-sm" 
        style={{ background: currentAppTheme.background }}
      />

      {/* App Workspace Selector */}
      <div className="relative">
        <button
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="tactile-btn flex items-center space-x-2.5 bg-slate-900/90 hover:bg-slate-850 border border-slate-800 rounded-lg px-2.5 py-1.5 shadow-sm text-left"
        >
          {/* Breathing online telemetry indicator with custom pattern background */}
          <div className="relative flex items-center justify-center shrink-0">
            <div 
              className="w-5 h-5 rounded-md flex items-center justify-center text-white text-[10px] font-bold shadow-inner transition-all duration-300"
              style={{ background: currentAppTheme.background }}
            >
              <AppIcon className="w-3 h-3 drop-shadow" />
            </div>
            <span 
              className="absolute -bottom-0.5 -right-0.5 w-1.5 h-1.5 rounded-full animate-status-breathe ring-1 ring-slate-950" 
              style={{ backgroundColor: currentAppTheme.colors[1] || currentAppTheme.colors[0] }}
            />
          </div>

          <div className="flex flex-col min-w-0">
            <div className="flex items-center space-x-1.5">
              <span className="text-xs font-bold text-white tracking-tight truncate max-w-[130px] sm:max-w-[180px]">
                {activeApp ? activeApp.name : "Select Child App"}
              </span>
              <span className="text-[9px] font-mono uppercase px-1 py-0.2 bg-slate-800 text-slate-400 rounded border border-slate-700/50">
                APP
              </span>
            </div>
            <span className="text-[10px] font-mono text-slate-400 truncate">
              {activeApp?.stats?.video_count || 0} vids · {activeApp?.stats?.entity_count || 0} entities
            </span>
          </div>
          <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${dropdownOpen ? "rotate-180" : ""}`} />
        </button>

        {dropdownOpen && (
          <>
            <div className="fixed inset-0 z-30" onClick={() => setDropdownOpen(false)} />
            <div className="absolute left-0 mt-1.5 w-72 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl z-40 overflow-hidden py-1 divide-y divide-slate-800/60">
              <div className="px-3 py-1.5 text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-400 bg-slate-950 flex items-center justify-between">
                <span>Active Workspaces</span>
                <span className="text-cyan-400">{apps.length} Online</span>
              </div>
              <div className="max-h-64 overflow-y-auto py-1 divide-y divide-slate-800/30">
                {apps.map((app) => {
                  const ItemIcon = ICON_MAP[app.icon] || Layers;
                  const isSelected = activeApp?.id === app.id;
                  const itemTheme = resolveAppTheme(app);
                  return (
                    <button
                      key={app.id}
                      onClick={() => {
                        onSelectApp(app);
                        setDropdownOpen(false);
                      }}
                      className={`w-full px-3 py-2 flex items-center justify-between text-left transition-colors tactile-btn ${
                        isSelected ? "bg-cyan-950/30 text-white" : "hover:bg-slate-850 text-slate-300"
                      }`}
                    >
                      <div className="flex items-center space-x-2.5 min-w-0">
                        <div 
                          className="w-6 h-6 rounded-md flex items-center justify-center text-white shrink-0 shadow-sm"
                          style={{ background: itemTheme.background }}
                        >
                          <ItemIcon className="w-3.5 h-3.5 drop-shadow" />
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center space-x-1.5">
                            <p className="text-xs font-semibold truncate text-white">{app.name}</p>
                            <span className="text-[8px] font-mono text-slate-400 uppercase bg-slate-800 px-1 py-0.2 rounded border border-slate-700/40">
                              {itemTheme.pattern}
                            </span>
                          </div>
                          <p className="text-[10px] font-mono text-slate-400">
                            {app.stats?.video_count || 0} vids · {app.stats?.entity_count || 0} ent
                          </p>
                        </div>
                      </div>
                      {isSelected && <Check className="w-3.5 h-3.5 text-cyan-400 shrink-0" />}
                    </button>
                  );
                })}
              </div>
              <div className="p-2 bg-slate-950">
                <button
                  onClick={() => {
                    setDropdownOpen(false);
                    onCreateAppClick();
                  }}
                  className="tactile-btn w-full flex items-center justify-center space-x-1.5 py-1.5 px-3 rounded-lg bg-cyan-950/40 hover:bg-cyan-900/40 text-cyan-300 border border-cyan-800/40 text-xs font-mono font-medium transition-all"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>+ New Child App</span>
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Right Controls: Scheme Picker, Aura DB, Videos, Frame Toggle */}
      <div className="flex items-center space-x-2">
        {/* Global Color Scheme & Pattern Switcher */}
        <div className="relative">
          <button
            onClick={() => setThemeModalOpen(!themeModalOpen)}
            className="tactile-btn flex items-center space-x-1.5 bg-slate-900 hover:bg-slate-850 text-slate-200 border border-slate-700/80 text-xs font-mono py-1 px-2 rounded-lg transition-colors shadow-sm"
            title="Cockpit Color Schemes & Bi/Tri Patterns"
          >
            <div 
              className="w-3.5 h-3.5 rounded-full border border-slate-600 shadow-sm"
              style={{ background: globalPatternBg }}
            />
            <span className="text-slate-200 font-bold text-[11px] font-mono">SCHEMES</span>
            <span className="text-[8px] font-mono uppercase px-1 py-0.2 bg-cyan-950/80 text-cyan-300 rounded border border-cyan-800/40">
              BI/TRI
            </span>
          </button>

          {themeModalOpen && (
            <>
              <div className="fixed inset-0 z-30" onClick={() => setThemeModalOpen(false)} />
              <div className="absolute right-0 mt-1.5 w-80 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl z-40 overflow-hidden py-2 px-3 divide-y divide-slate-800/60 text-slate-200">
                <div className="pb-2 flex items-center justify-between">
                  <div className="flex items-center space-x-1.5">
                    <Palette className="w-3.5 h-3.5 text-cyan-400" />
                    <span className="text-xs font-bold text-white font-mono uppercase">Cockpit Color Schemes</span>
                  </div>
                  <span className="text-[9px] font-mono bg-cyan-950 text-cyan-300 px-1.5 py-0.2 rounded border border-cyan-800/40">
                    SAVED IN STORE
                  </span>
                </div>

                {/* Bi-Color Presets */}
                <div className="py-2 space-y-1.5">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">Bi-Color Schemes (Dual)</span>
                  <div className="grid grid-cols-2 gap-1.5">
                    {BI_COLOR_PRESETS.map((preset) => (
                      <button
                        key={preset.id}
                        onClick={() => saveCockpitScheme(preset)}
                        className={`px-2 py-1.5 rounded-lg border text-left flex items-center space-x-1.5 text-xs transition-all ${
                          cockpitScheme.id === preset.id 
                            ? "bg-slate-800 border-cyan-500 ring-1 ring-cyan-500/50 text-white" 
                            : "bg-slate-850/60 border-slate-800 text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <div 
                          className="w-3.5 h-3.5 rounded-sm shrink-0 border border-slate-700" 
                          style={{ background: `linear-gradient(135deg, ${preset.colors[0]}, ${preset.colors[1]})` }} 
                        />
                        <span className="text-[10px] font-mono truncate">{preset.name.split(" ")[0]}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Tri-Color Presets */}
                <div className="py-2 space-y-1.5">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">Tri-Color Schemes (Triple)</span>
                  <div className="grid grid-cols-2 gap-1.5">
                    {TRI_COLOR_PRESETS.map((preset) => (
                      <button
                        key={preset.id}
                        onClick={() => saveCockpitScheme(preset)}
                        className={`px-2 py-1.5 rounded-lg border text-left flex items-center space-x-1.5 text-xs transition-all ${
                          cockpitScheme.id === preset.id 
                            ? "bg-slate-800 border-cyan-500 ring-1 ring-cyan-500/50 text-white" 
                            : "bg-slate-850/60 border-slate-800 text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <div 
                          className="w-3.5 h-3.5 rounded-sm shrink-0 border border-slate-700" 
                          style={{ background: `linear-gradient(135deg, ${preset.colors[0]} 0%, ${preset.colors[1]} 50%, ${preset.colors[2]} 100%)` }} 
                        />
                        <span className="text-[10px] font-mono truncate">{preset.name.split(" ")[0]}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Pattern Modes */}
                <div className="pt-2 space-y-1.5">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">Bi / Tri Pattern Flow</span>
                  <div className="grid grid-cols-2 gap-1.5">
                    {PATTERN_MODES.map((mode) => (
                      <button
                        key={mode.id}
                        onClick={() => savePatternMode(mode.id)}
                        className={`px-2 py-1 rounded-md border text-left flex items-center space-x-1.5 transition-all ${
                          cockpitScheme.pattern === mode.id 
                            ? "bg-slate-800 border-cyan-500 text-white" 
                            : "bg-slate-850/50 border-slate-800 text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <div 
                          className="w-3 h-3 rounded-xs shrink-0" 
                          style={{ background: getPatternBackground(mode.id, cockpitScheme.colors) }} 
                        />
                        <span className="text-[10px] font-mono truncate">{mode.name}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Knowledge Graph Data Store & Connection Button */}
        <button
          onClick={onOpenDatabaseModal || handleGlobalAuraSync}
          className="tactile-btn flex items-center space-x-1.5 bg-slate-900 hover:bg-slate-850 text-slate-200 border border-slate-800 text-xs font-mono py-1 px-2.5 rounded-lg transition-colors shadow-sm"
          title="Open Database Connection Manager (Neo4j AuraDB / LocalGraphStore)"
        >
          <Database className={`w-3.5 h-3.5 ${dbState.connected ? "text-emerald-400" : "text-cyan-400"}`} />
          <span className="hidden sm:inline">{dbState.label}</span>
          <span className={`w-1.5 h-1.5 rounded-full ${dbState.connected ? "bg-emerald-400 animate-pulse" : "bg-cyan-400"}`} />
        </button>

        {/* Videos Counter Button */}
        <button
          onClick={onManageVideosClick}
          className="tactile-btn flex items-center space-x-1.5 bg-slate-900 hover:bg-slate-850 text-slate-200 border border-slate-800 text-xs font-mono py-1 px-2.5 rounded-lg transition-colors shadow-sm"
          title="Manage Videos & Intelligences for this App"
        >
          <Video className="w-3.5 h-3.5 text-cyan-400" />
          <span className="hidden sm:inline">VIDEOS:</span>
          <span className="text-cyan-300 font-mono font-bold text-[11px]">
            {activeApp?.stats?.video_count || 0}
          </span>
        </button>

        {/* Frame Toggle */}
        <button
          onClick={onToggleFrame}
          className="tactile-btn p-1.5 rounded-lg bg-slate-900 hover:bg-slate-850 text-slate-400 hover:text-white border border-slate-800 transition-colors hidden md:flex items-center justify-center"
          title={isPhoneFrame ? "Switch to Fullscreen View" : "Switch to Mobile Phone Mockup"}
        >
          {isPhoneFrame ? <Monitor className="w-4 h-4" /> : <Smartphone className="w-4 h-4 text-cyan-400" />}
        </button>
      </div>
    </header>
  );
}
