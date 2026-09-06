import React, { useState, useEffect } from "react";
import { X, Briefcase, Cpu, Sparkles, TrendingUp, Layers, Check, GraduationCap, ShieldCheck, Users, Crosshair } from "lucide-react";
import { ICON_MAP } from "./TopHeader";

const THEME_COLORS = [
  { name: "Indigo", value: "#6366f1" },
  { name: "Blue", value: "#3b82f6" },
  { name: "Teal", value: "#14b8a6" },
  { name: "Emerald", value: "#10b981" },
  { name: "Amber", value: "#f59e0b" },
  { name: "Purple", value: "#8b5cf6" },
  { name: "Rose", value: "#f43f5e" },
  { name: "Pink", value: "#ec4899" }
];

const AVAILABLE_ICONS = ["Briefcase", "Cpu", "Sparkles", "TrendingUp", "Layers", "GraduationCap", "ShieldCheck", "Users", "Crosshair"];

const DOMAIN_OPTIONS = [
  { id: "executive", label: "Executive Strategy" },
  { id: "sales", label: "Sales & Revenue" },
  { id: "learning", label: "Learning & Mastery" },
  { id: "engineering", label: "R&D & Engineering" },
  { id: "compliance", label: "Risk & Governance" },
  { id: "customer", label: "Customer Success" },
  { id: "competitive", label: "Competitive Intelligence" },
  { id: "thought_leadership", label: "Thought Leadership" }
];

export default function CreateAppModal({ isOpen, onClose, onSave, editingApp }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [icon, setIcon] = useState("Layers");
  const [themeColor, setThemeColor] = useState("#6366f1");
  const [focusDomains, setFocusDomains] = useState(["executive", "learning"]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (editingApp) {
      setName(editingApp.name || "");
      setDescription(editingApp.description || "");
      setIcon(editingApp.icon || "Layers");
      setThemeColor(editingApp.theme_color || "#6366f1");
      setFocusDomains(editingApp.focus_domains || ["executive", "learning"]);
    } else {
      setName("");
      setDescription("");
      setIcon("Layers");
      setThemeColor("#6366f1");
      setFocusDomains(["executive", "learning"]);
    }
  }, [editingApp, isOpen]);

  if (!isOpen) return null;

  const toggleDomain = (domainId) => {
    if (focusDomains.includes(domainId)) {
      if (focusDomains.length > 1) {
        setFocusDomains(focusDomains.filter((d) => d !== domainId));
      }
    } else {
      setFocusDomains([...focusDomains, domainId]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    setLoading(true);
    try {
      await onSave({
        name: name.trim(),
        description: description.trim(),
        icon,
        theme_color: themeColor,
        focus_domains: focusDomains
      });
      onClose();
    } catch (err) {
      alert(err.message || "Failed to save app");
    } finally {
      setLoading(false);
    }
  };

  const IconComponent = ICON_MAP[icon] || Layers;

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/80 backdrop-blur-sm">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-t-2xl sm:rounded-2xl shadow-2xl max-h-[90vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center space-x-3">
            <div 
              className="w-8 h-8 rounded-lg flex items-center justify-center text-white shadow-sm"
              style={{ backgroundColor: themeColor }}
            >
              <IconComponent className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold tracking-tight text-white">
                {editingApp ? "Configure Child App" : "Initialize Child Workspace"}
              </h3>
              <p className="text-[11px] font-mono text-slate-400">Scoped V-LKG Knowledge Graph</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1 rounded-lg bg-slate-800/80 hover:bg-slate-750 text-slate-400 hover:text-white transition-colors tactile-btn"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-5 overflow-y-auto space-y-4">
          <div>
            <label className="block text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">
              Workspace Identifier / Title *
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Sales Mastery Hub, GTM AI Lab..."
              className="w-full px-3 py-2 bg-slate-800/80 border border-slate-700 rounded-lg text-white placeholder-slate-500 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-sky-500 transition-all"
            />
          </div>

          <div>
            <label className="block text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">
              Scope Specification / Goal
            </label>
            <textarea
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What core knowledge domains or skills does this workspace prioritize?"
              className="w-full px-3 py-2 bg-slate-800/80 border border-slate-700 rounded-lg text-white placeholder-slate-500 text-xs focus:outline-none focus:ring-1 focus:ring-sky-500 transition-all resize-none"
            />
          </div>

          <div>
            <label className="block text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">
              Telemetry Icon
            </label>
            <div className="flex flex-wrap gap-1.5">
              {AVAILABLE_ICONS.map((iconName) => {
                const CurrentIcon = ICON_MAP[iconName] || Layers;
                const isSelected = icon === iconName;
                return (
                  <button
                    key={iconName}
                    type="button"
                    onClick={() => setIcon(iconName)}
                    className={`p-2 rounded-lg border transition-all tactile-btn ${
                      isSelected 
                        ? "bg-slate-800 border-sky-500 ring-1 ring-sky-500/40" 
                        : "bg-slate-800/50 border-slate-700/60 text-slate-400 hover:text-white"
                    }`}
                  >
                    <CurrentIcon 
                      className="w-4 h-4" 
                      style={{ color: isSelected ? themeColor : undefined }} 
                    />
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="block text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">
              Accent Color
            </label>
            <div className="grid grid-cols-4 sm:grid-cols-8 gap-2">
              {THEME_COLORS.map((color) => {
                const isSelected = themeColor === color.value;
                return (
                  <button
                    key={color.value}
                    type="button"
                    onClick={() => setThemeColor(color.value)}
                    className="flex flex-col items-center space-y-1 group tactile-btn"
                  >
                    <div 
                      className={`w-7 h-7 rounded-md flex items-center justify-center transition-all ${
                        isSelected ? "ring-2 ring-white scale-105 shadow-md" : "opacity-80 hover:opacity-100"
                      }`}
                      style={{ backgroundColor: color.value }}
                    >
                      {isSelected && <Check className="w-3.5 h-3.5 text-white" />}
                    </div>
                    <span className="text-[9px] font-mono text-slate-400 group-hover:text-slate-200">
                      {color.name}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="block text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">
              Target Domain Lenses ({focusDomains.length} Active)
            </label>
            <div className="grid grid-cols-2 gap-1.5">
              {DOMAIN_OPTIONS.map((domain) => {
                const active = focusDomains.includes(domain.id);
                return (
                  <button
                    key={domain.id}
                    type="button"
                    onClick={() => toggleDomain(domain.id)}
                    className={`px-2.5 py-1.5 rounded-lg text-left text-xs border transition-all flex items-center justify-between tactile-btn ${
                      active 
                        ? "bg-slate-800/90 border-sky-500/70 text-white" 
                        : "bg-slate-850/60 border-slate-700/50 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <span className="truncate text-[11px]">{domain.label}</span>
                    {active && <Check className="w-3.5 h-3.5 text-sky-400 shrink-0 ml-1" />}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={loading || !name.trim()}
              className="w-full py-2.5 px-4 rounded-lg text-white font-semibold text-xs shadow-md transition-all active:scale-98 disabled:opacity-50 flex items-center justify-center space-x-2 tactile-btn"
              style={{ backgroundColor: themeColor }}
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <span className="font-mono">{editingApp ? "Save Workspace Configuration" : "Initialize Workspace"}</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
