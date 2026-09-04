import React from "react";
import { LayoutGrid, Tag, Workflow, Mic, MessageSquareCode, Film } from "lucide-react";

export default function BottomNav({ activeTab, onTabChange, activeApp, isPhoneFrame }) {
  const tabs = [
    { id: "hub", label: "Apps Hub", icon: LayoutGrid },
    { id: "words", label: "Linear Words", icon: Tag },
    { id: "player", label: "Semantics", icon: Workflow },
    { id: "voice", label: "Live Voice", icon: Mic, isHighlight: true },
    { id: "ask", label: "Ask/Compare", icon: MessageSquareCode },
    { id: "library", label: "Library", icon: Film },
  ];

  return (
    <nav className={`${isPhoneFrame ? "absolute" : "fixed"} bottom-0 left-0 right-0 z-40 bg-slate-900/95 backdrop-blur-lg border-t border-slate-800 safe-bottom`}>
      <div className="max-w-md md:max-w-xl mx-auto flex items-center justify-around px-1 py-1.5">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          
          if (tab.isHighlight) {
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className="flex flex-col items-center justify-center -mt-4 group relative"
              >
                <div 
                  className={`w-12 h-12 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 ${
                    isActive 
                      ? "bg-gradient-to-tr from-rose-500 to-pink-600 ring-4 ring-rose-500/20 text-white scale-105" 
                      : "bg-slate-800 hover:bg-rose-600/30 text-rose-400 border border-rose-500/30 group-hover:scale-105"
                  }`}
                >
                  <Icon className="w-6 h-6 animate-pulse-fast" />
                </div>
                <span className={`text-[10px] font-semibold mt-1 ${isActive ? "text-rose-400 font-bold" : "text-slate-400"}`}>
                  {tab.label}
                </span>
              </button>
            );
          }

          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`flex flex-col items-center justify-center py-1 px-2 rounded-xl transition-all duration-200 relative ${
                isActive ? "text-indigo-400 scale-105 font-medium" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <div className="relative">
                <Icon className="w-5 h-5 mb-0.5" />
                {isActive && (
                  <span 
                    className="absolute -top-1 -right-1 w-1.5 h-1.5 rounded-full"
                    style={{ backgroundColor: activeApp?.theme_color || "#6366f1" }}
                  />
                )}
              </div>
              <span className="text-[10px] tracking-tight">{tab.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
