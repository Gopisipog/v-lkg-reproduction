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
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-700/80 rounded-t-3xl sm:rounded-3xl shadow-2xl max-h-[90vh] flex flex-col overflow-hidden animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div 
              className="w-9 h-9 rounded-xl flex items-center justify-center text-white shadow-md"
              style={{ backgroundColor: themeColor }}
            >
              <IconComponent className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">
                {editingApp ? "Edit Child App" : "Create New Child App"}
              </h3>
              <p className="text-xs text-slate-400">Customized V-LKG Knowledge Workspace</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 rounded-full bg-slate-800 hover:bg-slate-750 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto space-y-5">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
              App Title *
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Sales Mastery Hub, GTM AI Lab..."
              className="w-full px-4 py-2.5 bg-slate-800/80 border border-slate-700 rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
              Description / Focus Goal
            </label>
            <textarea
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What core knowledge domains or skills does this app track?"
              className="w-full px-4 py-2.5 bg-slate-800/80 border border-slate-700 rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all resize-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
              App Icon
            </label>
            <div className="flex flex-wrap gap-2">
              {AVAILABLE_ICONS.map((iconName) => {
                const CurrentIcon = ICON_MAP[iconName] || Layers;
                const isSelected = icon === iconName;
                return (
                  <button
                    key={iconName}
                    type="button"
                    onClick={() => setIcon(iconName)}
                    className={`p-2.5 rounded-xl border transition-all ${
                      isSelected 
                        ? "bg-slate-750 border-indigo-500 ring-2 ring-indigo-500/30 scale-105" 
                        : "bg-slate-800/60 border-slate-700/60 text-slate-400 hover:text-white"
                    }`}
                  >
                    <CurrentIcon 
                      className="w-5 h-5" 
                      style={{ color: isSelected ? themeColor : undefined }} 
                    />
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
              Accent Theme
            </label>
            <div className="grid grid-cols-4 sm:grid-cols-8 gap-2">
              {THEME_COLORS.map((color) => {
                const isSelected = themeColor === color.value;
                return (
                  <button
                    key={color.value}
                    type="button"
                    onClick={() => setThemeColor(color.value)}
                    className="flex flex-col items-center space-y-1 group"
                  >
                    <div 
                      className={`w-8 h-8 rounded-full flex items-center justify-center transition-all ${
                        isSelected ? "ring-2 ring-white scale-110 shadow-lg" : "opacity-80 hover:opacity-100"
                      }`}
                      style={{ backgroundColor: color.value }}
                    >
                      {isSelected && <Check className="w-4 h-4 text-white drop-shadow-md" />}
                    </div>
                    <span className="text-[10px] text-slate-400 group-hover:text-slate-200">
                      {color.name}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
              Target Intelligence Domains
            </label>
            <div className="grid grid-cols-2 gap-2">
              {DOMAIN_OPTIONS.map((domain) => {
                const active = focusDomains.includes(domain.id);
                return (
                  <button
                    key={domain.id}
                    type="button"
                    onClick={() => toggleDomain(domain.id)}
                    className={`px-3 py-2 rounded-xl text-left text-xs font-medium border transition-all flex items-center justify-between ${
                      active 
                        ? "bg-slate-800 border-indigo-500 text-white" 
                        : "bg-slate-850/60 border-slate-700/50 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <span className="truncate">{domain.label}</span>
                    {active && <Check className="w-3.5 h-3.5 text-indigo-400 shrink-0 ml-1" />}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={loading || !name.trim()}
              className="w-full py-3 px-4 rounded-xl text-white font-semibold text-sm shadow-lg transition-all active:scale-98 disabled:opacity-50 flex items-center justify-center space-x-2"
              style={{ backgroundColor: themeColor }}
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <span>{editingApp ? "Save App Changes" : "Launch Child App"}</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
