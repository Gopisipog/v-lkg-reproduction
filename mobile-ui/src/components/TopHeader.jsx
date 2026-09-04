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
    <header className="sticky top-0 z-40 bg-slate-900/90 backdrop-blur-md border-b border-slate-800/80 px-4 py-3 flex items-center justify-between">
      <div className="relative">
        <button
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="flex items-center space-x-2.5 bg-slate-800/90 hover:bg-slate-750 border border-slate-700/70 rounded-full px-3.5 py-1.5 transition-all shadow-sm active:scale-95 text-left"
        >
          <div 
            className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold shadow-sm shrink-0"
            style={{ backgroundColor: activeApp?.theme_color || "#6366f1" }}
          >
            <AppIcon className="w-3.5 h-3.5" />
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-xs font-semibold text-white tracking-tight truncate max-w-[130px] sm:max-w-[200px]">
              {activeApp ? activeApp.name : "Select Child App"}
            </span>
            <span className="text-[10px] text-slate-400 font-medium truncate">
              {activeApp?.stats?.video_count || 0} vids · {activeApp?.stats?.entity_count || 0} entities
            </span>
          </div>
          <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${dropdownOpen ? "rotate-180" : ""}`} />
        </button>

        {dropdownOpen && (
          <>
            <div className="fixed inset-0 z-30" onClick={() => setDropdownOpen(false)} />
            <div className="absolute left-0 mt-2 w-72 bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl z-40 overflow-hidden py-1 animate-fade-in divide-y divide-slate-800/60">
              <div className="px-3 py-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400 bg-slate-850">
                Switch Child App
              </div>
              <div className="max-h-64 overflow-y-auto py-1">
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
                      className={`w-full px-3 py-2.5 flex items-center justify-between text-left transition-colors ${
                        isSelected ? "bg-indigo-950/40 text-white" : "hover:bg-slate-800 text-slate-300"
                      }`}
                    >
                      <div className="flex items-center space-x-3 min-w-0">
                        <div 
                          className="w-7 h-7 rounded-lg flex items-center justify-center text-white shrink-0"
                          style={{ backgroundColor: app.theme_color || "#6366f1" }}
                        >
                          <ItemIcon className="w-4 h-4" />
                        </div>
                        <div className="min-w-0">
                          <p className="text-xs font-medium truncate text-white">{app.name}</p>
                          <p className="text-[10px] text-slate-400">
                            {app.stats?.video_count || 0} vids · {app.stats?.entity_count || 0} entities
                          </p>
                        </div>
                      </div>
                      {isSelected && <Check className="w-4 h-4 text-indigo-400 shrink-0" />}
                    </button>
                  );
                })}
              </div>
              <div className="p-2 bg-slate-900">
                <button
                  onClick={() => {
                    setDropdownOpen(false);
                    onCreateAppClick();
                  }}
                  className="w-full flex items-center justify-center space-x-2 py-2 px-3 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs font-semibold transition-all"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Create New Child App</span>
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      <div className="flex items-center space-x-2">
        <button
          onClick={onManageVideosClick}
          className="flex items-center space-x-1.5 bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 text-xs font-medium py-1.5 px-3 rounded-full transition-colors active:scale-95 shadow-sm"
          title="Manage Videos & Intelligences for this App"
        >
          <Video className="w-3.5 h-3.5 text-indigo-400" />
          <span className="hidden sm:inline">Videos</span>
          <span className="bg-indigo-500/20 text-indigo-300 text-[10px] px-1.5 py-0.2 rounded-full font-bold">
            {activeApp?.stats?.video_count || 0}
          </span>
        </button>

        <button
          onClick={onToggleFrame}
          className="p-1.5 rounded-full bg-slate-800 hover:bg-slate-750 text-slate-400 hover:text-white border border-slate-700 transition-colors hidden md:flex items-center justify-center"
          title={isPhoneFrame ? "Switch to Fullscreen View" : "Switch to Mobile Phone Mockup"}
        >
          {isPhoneFrame ? <Monitor className="w-4 h-4" /> : <Smartphone className="w-4 h-4 text-indigo-400" />}
        </button>
      </div>
    </header>
  );
}
