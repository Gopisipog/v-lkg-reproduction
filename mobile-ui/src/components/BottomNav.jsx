import React from "react";
import { motion } from "framer-motion";
import { LayoutGrid, Tag, Workflow, Mic, MessageSquareCode, Film } from "lucide-react";
import { resolveAppTheme } from "../utils/colorSchemes";

export default function BottomNav({ activeTab, onTabChange, activeApp, activeAppTheme: propTheme, isPhoneFrame }) {
  const theme = propTheme || resolveAppTheme(activeApp);
  const primaryColor = theme.primaryColor || "#0EA5E9";

  const tabs = [
    { id: "hub", label: "HUB", icon: LayoutGrid },
    { id: "words", label: "WORDS", icon: Tag },
    { id: "player", label: "SEMANTICS", icon: Workflow },
    { id: "voice", label: "VOICE", icon: Mic, isHighlight: true },
    { id: "ask", label: "QUERY", icon: MessageSquareCode },
    { id: "library", label: "LIBRARY", icon: Film },
  ];

  return (
    <nav className={`${isPhoneFrame ? "absolute" : "fixed"} bottom-0 left-0 right-0 z-40 bg-slate-950/95 backdrop-blur-md border-t border-slate-800/80 safe-bottom`}>
      {/* Top subtle dynamic theme line */}
      <div className="h-[1.5px] w-full" style={{ background: theme.background }} />
      <div className="max-w-md md:max-w-2xl mx-auto flex items-center justify-around px-2 py-1">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          
          if (tab.isHighlight) {
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className="tactile-btn flex flex-col items-center justify-center -mt-3.5 group relative px-2"
              >
                <div 
                  className={`w-10 h-10 rounded-xl flex items-center justify-center shadow-md transition-colors duration-200 ${
                    isActive 
                      ? "bg-rose-600 text-white ring-2 ring-rose-500/30" 
                      : "bg-slate-900 hover:bg-slate-850 text-rose-400 border border-rose-500/30"
                  }`}
                >
                  <Icon className="w-5 h-5 animate-pulse" />
                </div>
                <span className={`text-[9px] font-mono tracking-wider mt-1 font-bold ${isActive ? "text-rose-400" : "text-slate-400"}`}>
                  {tab.label}
                </span>
              </button>
            );
          }

          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              style={isActive ? { color: primaryColor } : undefined}
              className={`tactile-btn relative flex flex-col items-center justify-center py-1 px-2.5 rounded-lg transition-colors ${
                isActive ? "" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {isActive && (
                <motion.div
                  layoutId="bottomNavIndicator"
                  style={{
                    backgroundColor: `${theme.colors[0]}1c`,
                    borderColor: `${theme.colors[0]}55`,
                    boxShadow: `0 0 12px ${theme.colors[0]}22`
                  }}
                  className="absolute inset-0 border rounded-lg -z-10"
                  transition={{ type: "spring", stiffness: 100, damping: 20 }}
                />
              )}
              <Icon className="w-4 h-4 mb-0.5" />
              <span className="text-[9px] font-mono tracking-wider font-semibold">{tab.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}

