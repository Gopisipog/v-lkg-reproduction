import React, { useState } from "react";
import { 
  ChevronDown, Layers, Sparkles, Briefcase, Cpu, TrendingUp, 
  Plus, Check, Video, Smartphone, Monitor, ShieldCheck, Users, Crosshair, GraduationCap
} from "lucide-react";

export const ICON_MAP = {
  Briefcase,
  Cpu,
  Sparkles,
  TrendingUp,
  Layers,
  GraduationCap,
  ShieldCheck,
  Users,
  Crosshair
};

export default function TopHeader({
  activeApp,
  apps,
  onSelectApp,
  onCreateAppClick,
  onManageVideosClick,
  isPhoneFrame,
  onToggleFrame
}) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const AppIcon = activeApp && ICON_MAP[activeApp.icon] ? ICON_MAP[activeApp.icon] : Layers;

  return (
    <header className="sticky top-0 z-40 bg-slate-950/95 backdrop-blur-md border-b border-slate-800/80 px-3.5 py-2.5 flex items-center justify-between">
      <div className="relative">
        <button
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="tactile-btn flex items-center space-x-2.5 bg-slate-900/90 hover:bg-slate-850 border border-slate-800 rounded-lg px-2.5 py-1.5 shadow-sm text-left"
        >
          {/* Breathing online telemetry indicator */}
          <div className="relative flex items-center justify-center shrink-0">
            <div 
              className="w-5 h-5 rounded-md flex items-center justify-center text-white text-[10px] font-bold shadow-inner"
              style={{ backgroundColor: activeApp?.theme_color || "#0ea5e9" }}
            >
              <AppIcon className="w-3 h-3" />
            </div>
            <span className="absolute -bottom-0.5 -right-0.5 w-1.5 h-1.5 rounded-full bg-emerald-400 animate-status-breathe ring-1 ring-slate-950" />
          </div>

          <div className="flex flex-col min-w-0">
            <div className="flex items-center space-x-1.5">
              <span className="text-xs font-bold text-white tracking-tight truncate max-w-[130px] sm:max-w-[200px]">
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
                          className="w-6 h-6 rounded-md flex items-center justify-center text-white shrink-0"
                          style={{ backgroundColor: app.theme_color || "#0ea5e9" }}
                        >
                          <ItemIcon className="w-3.5 h-3.5" />
                        </div>
                        <div className="min-w-0">
                          <p className="text-xs font-semibold truncate text-white">{app.name}</p>
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

      <div className="flex items-center space-x-2">
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

