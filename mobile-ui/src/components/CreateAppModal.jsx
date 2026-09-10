import React, { useState, useEffect } from "react";
import { 
  X, Briefcase, Cpu, Sparkles, TrendingUp, Layers, Check, 
  GraduationCap, ShieldCheck, Users, Crosshair, Database, 
  Palette, Sliders, Eye
} from "lucide-react";
import { ICON_MAP } from "./TopHeader";
import { 
  BI_COLOR_PRESETS, 
  TRI_COLOR_PRESETS, 
  SOLID_PRESETS, 
  PATTERN_MODES, 
  getPatternBackground, 
  getCardAtmosphere 
} from "../utils/colorSchemes";

const AVAILABLE_ICONS = ["Briefcase", "Cpu", "Sparkles", "TrendingUp", "Layers", "GraduationCap", "ShieldCheck", "Users", "Crosshair", "Film"];

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
  const [focusDomains, setFocusDomains] = useState(["executive", "learning"]);
  
  // Color Scheme & Pattern State
  const [paletteType, setPaletteType] = useState("bi"); // "bi" | "tri" | "solid" | "custom"
  const [selectedSchemeId, setSelectedSchemeId] = useState("cyber-cyan");
  const [pattern, setPattern] = useState("gradient-bi");
  const [patternColors, setPatternColors] = useState(["#0EA5E9", "#10B981"]);
  const [saveToAura, setSaveToAura] = useState(true);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (editingApp) {
      setName(editingApp.name || "");
      setDescription(editingApp.description || "");
      setIcon(editingApp.icon || "Layers");
      setFocusDomains(editingApp.focus_domains || ["executive", "learning"]);
      
      const p = editingApp.pattern || "gradient-bi";
      const colors = editingApp.pattern_colors || [editingApp.theme_color || "#0EA5E9", "#10B981"];
      setPattern(p);
      setPatternColors(colors);
      setSelectedSchemeId(editingApp.color_scheme || "custom");
      setPaletteType(colors.length >= 3 ? "tri" : "bi");
      setSaveToAura(true);
    } else {
      setName("");
      setDescription("");
      setIcon("Layers");
      setFocusDomains(["executive", "learning"]);
      setPaletteType("bi");
      setSelectedSchemeId("cyber-cyan");
      setPattern("gradient-bi");
      setPatternColors(["#0EA5E9", "#10B981"]);
      setSaveToAura(true);
    }
  }, [editingApp, isOpen]);

  if (!isOpen) return null;

  const handleSelectPreset = (preset) => {
    setSelectedSchemeId(preset.id);
    setPatternColors(preset.colors);
    if (preset.type === "tri") {
      setPaletteType("tri");
      if (pattern === "split-bi") setPattern("gradient-tri");
    } else if (preset.type === "bi") {
      setPaletteType("bi");
      if (pattern === "gradient-tri") setPattern("gradient-bi");
    } else {
      setPaletteType("solid");
      setPattern("solid");
    }
  };

  const handleCustomColorChange = (index, newColor) => {
    const updated = [...patternColors];
    updated[index] = newColor;
    setPatternColors(updated);
    setSelectedSchemeId("custom");
  };

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
        theme_color: patternColors[0] || "#0EA5E9",
        color_scheme: selectedSchemeId,
        pattern,
        pattern_colors: patternColors,
        focus_domains: focusDomains,
        save_to_aura: saveToAura
      });
      onClose();
    } catch (err) {
      alert(err.message || "Failed to save app");
    } finally {
      setLoading(false);
    }
  };

  const IconComponent = ICON_MAP[icon] || Layers;
  const previewBackground = getPatternBackground(pattern, patternColors);
  const previewCardAtmosphere = getCardAtmosphere(pattern, patternColors);

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/85 backdrop-blur-sm">
      <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-t-2xl sm:rounded-2xl shadow-2xl max-h-[92vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-800 bg-slate-950/70">
          <div className="flex items-center space-x-3">
            <div 
              className="w-8 h-8 rounded-lg flex items-center justify-center text-white shadow-md transition-all"
              style={{ background: previewBackground }}
            >
              <IconComponent className="w-4 h-4 drop-shadow" />
            </div>
            <div>
              <h3 className="text-sm font-semibold tracking-tight text-white flex items-center space-x-2">
                <span>{editingApp ? "Configure Child App" : "Initialize Child Workspace"}</span>
                <span className="text-[9px] font-mono uppercase px-1.5 py-0.2 bg-cyan-950/80 text-cyan-300 border border-cyan-800/60 rounded">
                  {paletteType.toUpperCase()}-PATTERN
                </span>
              </h3>
              <p className="text-[11px] font-mono text-slate-400">Scoped V-LKG Knowledge Graph & Aura DB Store</p>
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
        <form onSubmit={handleSubmit} className="p-5 overflow-y-auto space-y-4 text-slate-200">
          
          {/* Live Real-Time Cockpit Card Preview */}
          <div className="rounded-xl border border-slate-800 p-3 relative overflow-hidden bg-slate-950/60 shadow-inner">
            <div 
              className="absolute inset-0 opacity-40 pointer-events-none transition-all duration-300"
              style={{ background: previewCardAtmosphere }}
            />
            <div 
              className="absolute top-0 left-0 right-0 h-1 transition-all duration-300"
              style={{ background: previewBackground }}
            />
            <div className="relative z-10 flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <div 
                  className="w-7 h-7 rounded-lg flex items-center justify-center text-white shadow transition-all duration-300"
                  style={{ background: previewBackground }}
                >
                  <IconComponent className="w-3.5 h-3.5 drop-shadow" />
                </div>
                <div>
                  <div className="flex items-center space-x-1.5">
                    <span className="text-xs font-bold text-white">
                      {name.trim() || "Untitled Child Workspace"}
                    </span>
                    <span className="text-[9px] font-mono text-cyan-400 bg-cyan-950/60 px-1 py-0.2 rounded border border-cyan-800/40">
                      PREVIEW
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400">
                    Pattern: {pattern} · {patternColors.join(" / ")}
                  </span>
                </div>
              </div>
              <div className="flex items-center space-x-1">
                {patternColors.map((col, idx) => (
                  <span 
                    key={idx} 
                    className="w-3 h-3 rounded-full border border-slate-700 shadow-sm"
                    style={{ backgroundColor: col }}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Title and Scope */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1">
                Workspace Identifier / Title *
              </label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Sales Mastery Hub, AI Lab..."
                className="w-full px-3 py-1.5 bg-slate-800/80 border border-slate-700 rounded-lg text-white placeholder-slate-500 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-cyan-500 transition-all"
              />
            </div>
            <div>
              <label className="block text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1">
                Telemetry Icon
              </label>
              <div className="flex flex-wrap gap-1">
                {AVAILABLE_ICONS.map((iconName) => {
                  const CurrentIcon = ICON_MAP[iconName] || Layers;
                  const isSelected = icon === iconName;
                  return (
                    <button
                      key={iconName}
                      type="button"
                      onClick={() => setIcon(iconName)}
                      className={`p-1.5 rounded-lg border transition-all tactile-btn ${
                        isSelected 
                          ? "bg-slate-800 border-cyan-500 ring-1 ring-cyan-500/40" 
                          : "bg-slate-800/50 border-slate-700/60 text-slate-400 hover:text-white"
                      }`}
                    >
                      <CurrentIcon 
                        className="w-3.5 h-3.5" 
                        style={{ color: isSelected ? patternColors[0] : undefined }} 
                      />
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <div>
            <label className="block text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1">
              Scope Specification / Knowledge Focus
            </label>
            <textarea
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What core knowledge domains or skills does this workspace prioritize?"
              className="w-full px-3 py-1.5 bg-slate-800/80 border border-slate-700 rounded-lg text-white placeholder-slate-500 text-xs focus:outline-none focus:ring-1 focus:ring-cyan-500 transition-all resize-none"
            />
          </div>

          {/* ── Mixed Color Scheme Selection ── */}
          <div className="border border-slate-800 rounded-xl p-3 bg-slate-950/40 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1.5">
                <Palette className="w-3.5 h-3.5 text-cyan-400" />
                <label className="text-[10px] font-mono uppercase tracking-wider text-slate-300 font-bold">
                  Color Scheme Palette
                </label>
              </div>
              
              {/* Palette Mode Selector Tabs */}
              <div className="flex items-center space-x-1 bg-slate-800 p-0.5 rounded-lg border border-slate-700/60 text-[10px] font-mono">
                <button
                  type="button"
                  onClick={() => {
                    setPaletteType("bi");
                    handleSelectPreset(BI_COLOR_PRESETS[0]);
                  }}
                  className={`px-2 py-0.5 rounded transition-colors ${
                    paletteType === "bi" ? "bg-cyan-600 text-slate-950 font-bold" : "text-slate-400 hover:text-white"
                  }`}
                >
                  Bi-Color (Dual)
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setPaletteType("tri");
                    handleSelectPreset(TRI_COLOR_PRESETS[0]);
                  }}
                  className={`px-2 py-0.5 rounded transition-colors ${
                    paletteType === "tri" ? "bg-cyan-600 text-slate-950 font-bold" : "text-slate-400 hover:text-white"
                  }`}
                >
                  Tri-Color (Triple)
                </button>
                <button
                  type="button"
                  onClick={() => setPaletteType("custom")}
                  className={`px-2 py-0.5 rounded transition-colors ${
                    paletteType === "custom" ? "bg-cyan-600 text-slate-950 font-bold" : "text-slate-400 hover:text-white"
                  }`}
                >
                  Custom Mix
                </button>
              </div>
            </div>

            {/* Presets Grid */}
            {paletteType === "bi" && (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {BI_COLOR_PRESETS.map((preset) => {
                  const isSelected = selectedSchemeId === preset.id;
                  return (
                    <button
                      key={preset.id}
                      type="button"
                      onClick={() => handleSelectPreset(preset)}
                      className={`p-2 rounded-lg border text-left flex items-center space-x-2 transition-all tactile-btn ${
                        isSelected 
                          ? "bg-slate-800 border-cyan-500 ring-1 ring-cyan-500/50 text-white" 
                          : "bg-slate-850/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                      }`}
                    >
                      <div 
                        className="w-5 h-5 rounded-md shrink-0 shadow-sm border border-slate-700/50"
                        style={{ background: `linear-gradient(135deg, ${preset.colors[0]} 0%, ${preset.colors[1]} 100%)` }}
                      />
                      <div className="min-w-0 flex-1">
                        <p className="text-[11px] font-semibold truncate leading-tight">{preset.name}</p>
                        <p className="text-[9px] font-mono text-slate-500 truncate">{preset.colors[0]} · {preset.colors[1]}</p>
                      </div>
                      {isSelected && <Check className="w-3 h-3 text-cyan-400 shrink-0" />}
                    </button>
                  );
                })}
              </div>
            )}

            {paletteType === "tri" && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {TRI_COLOR_PRESETS.map((preset) => {
                  const isSelected = selectedSchemeId === preset.id;
                  return (
                    <button
                      key={preset.id}
                      type="button"
                      onClick={() => handleSelectPreset(preset)}
                      className={`p-2 rounded-lg border text-left flex items-center space-x-2 transition-all tactile-btn ${
                        isSelected 
                          ? "bg-slate-800 border-cyan-500 ring-1 ring-cyan-500/50 text-white" 
                          : "bg-slate-850/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                      }`}
                    >
                      <div 
                        className="w-5 h-5 rounded-md shrink-0 shadow-sm border border-slate-700/50"
                        style={{ background: `linear-gradient(135deg, ${preset.colors[0]} 0%, ${preset.colors[1]} 50%, ${preset.colors[2]} 100%)` }}
                      />
                      <div className="min-w-0 flex-1">
                        <p className="text-[11px] font-semibold truncate leading-tight">{preset.name}</p>
                        <p className="text-[9px] font-mono text-slate-500 truncate">{preset.colors.join(" · ")}</p>
                      </div>
                      {isSelected && <Check className="w-3 h-3 text-cyan-400 shrink-0" />}
                    </button>
                  );
                })}
              </div>
            )}

            {/* Custom Color Mixer Pickers */}
            {paletteType === "custom" && (
              <div className="space-y-2 pt-1">
                <p className="text-[10px] font-mono text-slate-400">
                  Select 2 or 3 custom HEX colors to synthesize your bespoke bi or tri color scheme:
                </p>
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="text-[9px] font-mono uppercase text-slate-400 block mb-1">Color 1 (Primary)</label>
                    <div className="flex items-center space-x-1.5 bg-slate-800 px-2 py-1 rounded-lg border border-slate-700">
                      <input 
                        type="color" 
                        value={patternColors[0] || "#0EA5E9"} 
                        onChange={(e) => handleCustomColorChange(0, e.target.value)}
                        className="w-5 h-5 rounded cursor-pointer bg-transparent border-0" 
                      />
                      <input 
                        type="text" 
                        value={patternColors[0] || "#0EA5E9"} 
                        onChange={(e) => handleCustomColorChange(0, e.target.value)}
                        className="text-[10px] font-mono bg-transparent text-white w-full outline-none uppercase" 
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-[9px] font-mono uppercase text-slate-400 block mb-1">Color 2 (Secondary)</label>
                    <div className="flex items-center space-x-1.5 bg-slate-800 px-2 py-1 rounded-lg border border-slate-700">
                      <input 
                        type="color" 
                        value={patternColors[1] || "#10B981"} 
                        onChange={(e) => handleCustomColorChange(1, e.target.value)}
                        className="w-5 h-5 rounded cursor-pointer bg-transparent border-0" 
                      />
                      <input 
                        type="text" 
                        value={patternColors[1] || "#10B981"} 
                        onChange={(e) => handleCustomColorChange(1, e.target.value)}
                        className="text-[10px] font-mono bg-transparent text-white w-full outline-none uppercase" 
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-[9px] font-mono uppercase text-slate-400 block mb-1">Color 3 (Optional)</label>
                    <div className="flex items-center space-x-1.5 bg-slate-800 px-2 py-1 rounded-lg border border-slate-700">
                      <input 
                        type="color" 
                        value={patternColors[2] || "#8B5CF6"} 
                        onChange={(e) => handleCustomColorChange(2, e.target.value)}
                        className="w-5 h-5 rounded cursor-pointer bg-transparent border-0" 
                      />
                      <input 
                        type="text" 
                        value={patternColors[2] || "#8B5CF6"} 
                        onChange={(e) => handleCustomColorChange(2, e.target.value)}
                        className="text-[10px] font-mono bg-transparent text-white w-full outline-none uppercase" 
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ── Pattern Mode Selection ── */}
            <div className="pt-2 border-t border-slate-800/80">
              <label className="block text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1.5 flex items-center space-x-1">
                <Sliders className="w-3 h-3 text-cyan-400" />
                <span>Bi / Tri Pattern Geometry</span>
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5">
                {PATTERN_MODES.map((mode) => {
                  const isSelected = pattern === mode.id;
                  const modeBackground = getPatternBackground(mode.id, patternColors);
                  return (
                    <button
                      key={mode.id}
                      type="button"
                      onClick={() => setPattern(mode.id)}
                      className={`px-2.5 py-1.5 rounded-lg border text-left flex items-center space-x-2 transition-all tactile-btn ${
                        isSelected 
                          ? "bg-slate-800 border-cyan-500 ring-1 ring-cyan-500/50 text-white" 
                          : "bg-slate-850/60 border-slate-800 text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      <div 
                        className="w-4 h-4 rounded shrink-0 shadow-inner border border-slate-700/50" 
                        style={{ background: modeBackground }} 
                      />
                      <span className="text-[11px] font-mono truncate">{mode.name}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Domain Lenses */}
          <div>
            <label className="block text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">
              Target Domain Lenses ({focusDomains.length} Active)
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5">
              {DOMAIN_OPTIONS.map((domain) => {
                const active = focusDomains.includes(domain.id);
                return (
                  <button
                    key={domain.id}
                    type="button"
                    onClick={() => toggleDomain(domain.id)}
                    className={`px-2 py-1.5 rounded-lg text-left text-xs border transition-all flex items-center justify-between tactile-btn ${
                      active 
                        ? "bg-slate-800/90 border-cyan-500/70 text-white" 
                        : "bg-slate-850/60 border-slate-700/50 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <span className="truncate text-[10px]">{domain.label}</span>
                    {active && <Check className="w-3 h-3 text-cyan-400 shrink-0 ml-1" />}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Aura DB Persistence Switch */}
          <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-3 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="w-7 h-7 rounded-lg bg-emerald-950/80 border border-emerald-800/60 flex items-center justify-center text-emerald-400">
                <Database className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-semibold text-white flex items-center space-x-1.5">
                  <span>Persist Child App in Neo4j Aura DB</span>
                  <span className="text-[9px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-800/60 px-1 rounded">
                    AURA SYNC
                  </span>
                </p>
                <p className="text-[10px] font-mono text-slate-400">
                  Creates (:ChildApp) node & graph relationships with videos and entities
                </p>
              </div>
            </div>

            <label className="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                checked={saveToAura} 
                onChange={(e) => setSaveToAura(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-9 h-5 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-emerald-600"></div>
            </label>
          </div>

          {/* Submit */}
          <div className="pt-2">
            <button
              type="submit"
              disabled={loading || !name.trim()}
              className="w-full py-2.5 px-4 rounded-lg text-slate-950 font-bold text-xs shadow-md transition-all active:scale-98 disabled:opacity-50 flex items-center justify-center space-x-2 tactile-btn font-mono"
              style={{ background: previewBackground }}
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
              ) : (
                <span>{editingApp ? "Save Child Workspace & Aura DB" : "Initialize Child Workspace & Aura DB"}</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
