import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Workflow, Tag, Clock, Search, ExternalLink, Sparkles, Film, Mic, 
  ArrowRight, ChevronDown, ChevronUp, Filter, X, Layers, Check,
  Share2, Compass, PlayCircle, Radio
} from "lucide-react";
import { getVideoSemantics } from "../services/api";

export default function VideoPlayerView({ 
  activeApp, 
  allVideos, 
  targetVideoId, 
  targetTimestamp 
}) {
  const [currentVideoId, setCurrentVideoId] = useState(null);
  const [semanticsData, setSemanticsData] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRelation, setSelectedRelation] = useState("ALL");
  const [selectedEntityFilter, setSelectedEntityFilter] = useState(null);
  const [activeViewMode, setActiveViewMode] = useState("split"); // "split" | "relationships" | "transcript"
  const [showPillsSection, setShowPillsSection] = useState(false);
  const [loading, setLoading] = useState(false);
  const [highlightedTime, setHighlightedTime] = useState(null);

  const transcriptListRef = useRef(null);

  // Determine assigned videos
  const assignedVideoIds = activeApp?.video_ids || [];
  const assignedVideos = allVideos.filter((v) => assignedVideoIds.includes(v.video_id));
  const displayVideos = assignedVideos.length > 0 ? assignedVideos : allVideos;

  // Switch video when targetVideoId changes or default to first
  useEffect(() => {
    if (targetVideoId) {
      setCurrentVideoId(targetVideoId);
    } else if (displayVideos.length > 0 && !currentVideoId) {
      setCurrentVideoId(displayVideos[0].video_id);
    }
  }, [targetVideoId, displayVideos]);

  // Load semantics when currentVideoId changes
  useEffect(() => {
    if (!currentVideoId) return;
    setLoading(true);
    getVideoSemantics(currentVideoId)
      .then((data) => {
        setSemanticsData(data);
        setSelectedEntityFilter(null);
        setSelectedRelation("ALL");
      })
      .catch((err) => {
        console.error("Failed to load video semantics:", err);
      })
      .finally(() => setLoading(false));
  }, [currentVideoId]);

  // Jump to timestamp if requested
  useEffect(() => {
    if (targetTimestamp) {
      setHighlightedTime(targetTimestamp);
      scrollToTimestamp(targetTimestamp);
    }
  }, [targetTimestamp]);

  const scrollToTimestamp = (timeStr) => {
    if (!timeStr || !transcriptListRef.current) return;
    setHighlightedTime(timeStr);
    const element = document.getElementById(`seg-${timeStr.replace(":", "-")}`);
    if (element) {
      element.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  };

  const highlightMatch = (text, query) => {
    if (!query || !query.trim()) return text;
    const q = query.trim();
    const regex = new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, "gi");
    const parts = text.split(regex);
    return parts.map((part, i) =>
      regex.test(part) ? (
        <mark key={i} className="bg-cyan-950/60 text-cyan-300 font-mono px-1 py-0.2 rounded border border-cyan-700/50">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  const currentVideo = displayVideos.find((v) => v.video_id === currentVideoId) || semanticsData?.metadata;
  const isVoice = currentVideo?.is_voice_recording || currentVideoId?.startsWith("voice_") || currentVideoId?.startsWith("live_");

  const rawRelationships = semanticsData?.relationships || [];
  const relationships = React.useMemo(() => {
    const seen = new Set();
    return rawRelationships.filter((r) => {
      const sub = (r.subject || "").trim().toLowerCase();
      const rel = (r.relation || "").trim().toLowerCase();
      const obj = (r.object || "").trim().toLowerCase();
      if (!sub || !obj) return false;
      const key = `${sub}|${rel}|${obj}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }, [rawRelationships]);
  const segments = semanticsData?.segments || [];
  const extractedPills = semanticsData?.extracted_pills || [];
  const enrichedPills = semanticsData?.enriched_pills || [];
  const intelPills = semanticsData?.intel_pills || [];

  // Get distinct relation types for filter
  const relationTypes = ["ALL", ...Array.from(new Set(relationships.map((r) => r.relation))).filter(Boolean)];

  // Filter relationships
  const filteredRelationships = relationships.filter((r) => {
    if (selectedRelation !== "ALL" && r.relation !== selectedRelation) return false;
    if (selectedEntityFilter) {
      const efLower = selectedEntityFilter.toLowerCase();
      const subMatch = r.subject?.toLowerCase().includes(efLower);
      const objMatch = r.object?.toLowerCase().includes(efLower);
      if (!subMatch && !objMatch) return false;
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const subMatch = r.subject?.toLowerCase().includes(q);
      const objMatch = r.object?.toLowerCase().includes(q);
      const relMatch = r.relation?.toLowerCase().includes(q);
      if (!subMatch && !objMatch && !relMatch) return false;
    }
    return true;
  });

  // Filter transcript segments
  const filteredSegments = segments.filter((s) => {
    if (selectedEntityFilter) {
      const efLower = selectedEntityFilter.toLowerCase();
      const textMatch = s.text.toLowerCase().includes(efLower);
      const entMatch = s.detected_entities?.some((e) => e.toLowerCase().includes(efLower));
      if (!textMatch && !entMatch) return false;
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const textMatch = s.text.toLowerCase().includes(q);
      const entMatch = s.detected_entities?.some((e) => e.toLowerCase().includes(q));
      if (!textMatch && !entMatch) return false;
    }
    return true;
  });

  const durationMin = Math.round((currentVideo?.duration_sec || (segments.length * 5)) / 60);

  return (
    <div className="p-3 sm:p-5 space-y-3.5 pb-48 max-w-4xl mx-auto">
      {/* Video Stream Selector Bar */}
      <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 no-scrollbar">
        {displayVideos.map((v) => {
          const isSelected = v.video_id === currentVideoId;
          const isV = v.is_voice_recording || v.video_id.startsWith("voice_");
          return (
            <button
              key={v.video_id}
              onClick={() => setCurrentVideoId(v.video_id)}
              className={`tactile-btn flex items-center space-x-1.5 px-2.5 py-1 rounded-lg border text-xs font-mono whitespace-nowrap transition-colors shrink-0 ${
                isSelected
                  ? "bg-cyan-950/60 text-cyan-300 border-cyan-700/60 font-bold"
                  : "bg-slate-900 text-slate-400 border-slate-800 hover:border-slate-750 hover:text-slate-200"
              }`}
            >
              {isV ? <Mic className="w-3 h-3 text-rose-400" /> : <Film className="w-3 h-3 text-cyan-400" />}
              <span className="truncate max-w-[140px]">{v.title}</span>
            </button>
          );
        })}
      </div>

      {/* Main Cockpit Telemetry Card */}
      <div className="rounded-xl overflow-hidden bg-slate-900 border border-slate-800 p-4 space-y-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="inline-flex items-center space-x-1.5 px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/40 text-cyan-300 text-[10px] font-mono uppercase tracking-wider font-bold">
                <Radio className="w-2.5 h-2.5 text-cyan-400 animate-pulse" />
                <span>Recorded VLKG Knowledge & Transcript Semantics</span>
              </span>
              <span className="text-[10px] text-slate-500 font-mono">ID: {currentVideoId}</span>
            </div>

            <h2 className="text-sm sm:text-base font-bold text-white tracking-tight leading-snug">
              {currentVideo?.title || `Video Archive [${currentVideoId}]`}
            </h2>

            <div className="flex items-center space-x-2 text-[11px] font-mono text-slate-400">
              <span>{currentVideo?.channel || "Leadership Series"}</span>
              <span className="text-slate-600">·</span>
              <span>{durationMin > 0 ? `${durationMin}m duration` : "Ingested Recording"}</span>
              {currentVideo?.url && (
                <>
                  <span className="text-slate-600">·</span>
                  <a 
                    href={currentVideo.url} 
                    target="_blank" 
                    rel="noreferrer"
                    className="text-cyan-400 hover:text-cyan-300 inline-flex items-center space-x-0.5 underline font-bold"
                  >
                    <span>YouTube source</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                </>
              )}
            </div>
          </div>

          {/* Quick Metrics Cockpit Boxes */}
          <div className="flex items-center gap-1.5 shrink-0">
            <div className="px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center min-w-[70px]">
              <div className="text-xs font-mono font-bold text-cyan-400">{relationships.length}</div>
              <div className="text-[9px] font-mono text-slate-500 uppercase">TRIPLETS</div>
            </div>
            <div className="px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center min-w-[70px]">
              <div className="text-xs font-mono font-bold text-slate-300">{segments.length}</div>
              <div className="text-[9px] font-mono text-slate-500 uppercase">SEGMENTS</div>
            </div>
            <div className="px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center min-w-[70px]">
              <div className="text-xs font-mono font-bold text-emerald-400">{intelPills.length}</div>
              <div className="text-[9px] font-mono text-slate-500 uppercase">LENSES</div>
            </div>
          </div>
        </div>

        {/* Video Summary */}
        {currentVideo?.summary && (
          <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
            <strong className="text-slate-200 font-mono text-[11px] uppercase tracking-wider">Summary: </strong>{currentVideo.summary}
          </p>
        )}

        {/* Expandable VLKG Recorded Knowledge Badges */}
        <div className="pt-2 border-t border-slate-800/80 space-y-2">
          <button
            onClick={() => setShowPillsSection(!showPillsSection)}
            className="tactile-btn w-full flex items-center justify-between text-xs font-mono font-bold text-slate-300 hover:text-white transition-colors"
          >
            <div className="flex items-center space-x-1.5">
              <Sparkles className="w-3 h-3 text-cyan-400" />
              <span>RECORDED ENTITY & INTELLIGENCE PILLS ({extractedPills.length + enrichedPills.length + intelPills.length} CATEGORIES)</span>
            </div>
            {showPillsSection ? <ChevronUp className="w-3.5 h-3.5 text-slate-400" /> : <ChevronDown className="w-3.5 h-3.5 text-slate-400" />}
          </button>

          {showPillsSection && (
            <div className="space-y-2.5 pt-1.5">
              {/* Extracted */}
              {extractedPills.length > 0 && (
                <div className="space-y-1">
                  <div className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider">Extracted from Video</div>
                  <div className="flex flex-wrap gap-1">
                    {extractedPills.map((group) =>
                      group.entities.slice(0, 15).map((name) => (
                        <button
                          key={name}
                          onClick={() => setSelectedEntityFilter(selectedEntityFilter === name ? null : name)}
                          className={`tactile-btn text-[10px] font-mono px-2 py-0.5 rounded border transition-colors ${
                            selectedEntityFilter === name
                              ? "bg-cyan-500 text-slate-950 font-bold border-cyan-400"
                              : "bg-slate-800/70 hover:bg-slate-800 text-slate-300 border-slate-700/60"
                          }`}
                        >
                          {name}
                        </button>
                      ))
                    )}
                  </div>
                </div>
              )}

              {/* Enriched */}
              {enrichedPills.length > 0 && (
                <div className="space-y-1">
                  <div className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider">Enriched Pathways</div>
                  <div className="flex flex-wrap gap-1">
                    {enrichedPills.map((group) =>
                      group.entities.slice(0, 15).map((name) => (
                        <button
                          key={name}
                          onClick={() => setSelectedEntityFilter(selectedEntityFilter === name ? null : name)}
                          className={`tactile-btn text-[10px] font-mono px-2 py-0.5 rounded border transition-colors ${
                            selectedEntityFilter === name
                              ? "bg-cyan-500 text-slate-950 font-bold border-cyan-400"
                              : "bg-slate-800/70 hover:bg-slate-800 text-slate-300 border-slate-700/60"
                          }`}
                        >
                          {name}
                        </button>
                      ))
                    )}
                  </div>
                </div>
              )}

              {/* Intelligence */}
              {intelPills.length > 0 && (
                <div className="space-y-1">
                  <div className="text-[10px] font-mono font-bold text-cyan-400 uppercase tracking-wider">Intelligence Lenses</div>
                  <div className="flex flex-wrap gap-1">
                    {intelPills.map((group) =>
                      group.entities.slice(0, 10).map((name) => (
                        <button
                          key={name}
                          onClick={() => setSelectedEntityFilter(selectedEntityFilter === name ? null : name)}
                          className={`tactile-btn text-[10px] font-mono px-2 py-0.5 rounded border transition-colors ${
                            selectedEntityFilter === name
                              ? "bg-cyan-500 text-slate-950 font-bold border-cyan-400"
                              : "bg-cyan-950/30 text-cyan-300 border-cyan-800/50 hover:bg-cyan-900/40"
                          }`}
                        >
                          {name}
                        </button>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Control Bar: Search & View Mode Switcher with Framer Motion layoutId */}
      <div className="space-y-2">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          {/* View Mode Toggle */}
          <div className="bg-slate-900 border border-slate-800 p-0.5 rounded-lg flex items-center space-x-1 shadow-sm w-fit">
            {[
              { id: "split", label: "SPLIT VIEW" },
              { id: "relationships", label: `TRIPLETS (${filteredRelationships.length})` },
              { id: "transcript", label: `TRANSCRIPT (${filteredSegments.length})` }
            ].map((mode) => {
              const isSelected = activeViewMode === mode.id;
              return (
                <button
                  key={mode.id}
                  onClick={() => setActiveViewMode(mode.id)}
                  className={`tactile-btn relative px-2.5 py-1 rounded-md text-[11px] font-mono font-semibold transition-colors ${
                    isSelected ? "text-slate-950" : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {isSelected && (
                    <motion.div
                      layoutId="playerViewModeIndicator"
                      className="absolute inset-0 bg-cyan-400 rounded-md -z-10"
                      transition={{ type: "spring", stiffness: 100, damping: 20 }}
                    />
                  )}
                  {mode.label}
                </button>
              );
            })}
          </div>

          {/* Active Filter Pill */}
          {selectedEntityFilter && (
            <div className="flex items-center space-x-1 px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/40 text-cyan-300 text-[10px] font-mono font-bold">
              <span>FILTER: {selectedEntityFilter}</span>
              <button onClick={() => setSelectedEntityFilter(null)} className="hover:text-white ml-1">
                <X className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>

        {/* Search Bar */}
        <div className="flex items-center space-x-2 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800">
          <Search className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search relationships, concepts, or transcript words..."
            className="w-full bg-transparent text-xs text-white placeholder-slate-500 font-mono focus:outline-none"
          />
          {searchQuery && (
            <button onClick={() => setSearchQuery("")} className="text-slate-400 hover:text-white text-xs font-mono mr-1">
              CLEAR
            </button>
          )}
        </div>

        {/* Relation Type Horizontal Filters */}
        {activeViewMode !== "transcript" && relationTypes.length > 2 && (
          <div className="flex items-center space-x-1 overflow-x-auto pb-1 no-scrollbar pt-0.5">
            {relationTypes.slice(0, 10).map((rel) => (
              <button
                key={rel}
                onClick={() => setSelectedRelation(rel)}
                className={`tactile-btn px-2 py-0.5 rounded text-[10px] font-mono font-medium whitespace-nowrap transition-colors border ${
                  selectedRelation === rel
                    ? "bg-cyan-950/60 text-cyan-300 border-cyan-700/60 font-bold"
                    : "bg-slate-900 text-slate-400 border-slate-800 hover:border-slate-750 hover:text-slate-200"
                }`}
              >
                {rel}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Main Content Area */}
      {loading ? (
        <div className="py-16 text-center text-slate-400 text-xs font-mono flex flex-col items-center space-y-2">
          <Workflow className="w-6 h-6 animate-spin text-cyan-400" />
          <span>Loading relationships and transcript semantics...</span>
        </div>
      ) : (
        <div className={`gap-3 ${activeViewMode === "split" ? "grid grid-cols-1 lg:grid-cols-2" : "space-y-3"}`}>
          {/* 1. Relationships Column / View */}
          {(activeViewMode === "split" || activeViewMode === "relationships") && (
            <div className="space-y-2">
              <div className="flex items-center justify-between px-1">
                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
                  <Workflow className="w-3.5 h-3.5 text-cyan-400" />
                  <span>KNOWLEDGE TRIPLETS ({filteredRelationships.length})</span>
                </h3>
                <span className="text-[10px] font-mono text-slate-500">Tap time to jump</span>
              </div>

              <div className="space-y-1.5 max-h-[550px] overflow-y-auto pr-1">
                {filteredRelationships.length > 0 ? (
                  filteredRelationships.map((r, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 rounded-lg bg-slate-900/80 hover:bg-slate-850 border border-slate-800/80 transition-all group"
                    >
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <div className="flex items-center space-x-1.5 flex-wrap gap-y-1">
                          <span 
                            onClick={() => setSelectedEntityFilter(r.subject)}
                            className="text-xs font-bold text-white hover:text-cyan-300 cursor-pointer transition-colors"
                          >
                            {r.subject}
                          </span>
                          <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700/50">
                            {r.subject_type || "Concept"}
                          </span>
                        </div>

                        {r.source_time && (
                          <button
                            onClick={() => scrollToTimestamp(r.source_time)}
                            className="tactile-btn px-1.5 py-0.5 rounded bg-cyan-950/40 text-cyan-400 hover:bg-cyan-900/50 border border-cyan-800/40 text-[10px] font-mono font-bold transition-colors shrink-0 flex items-center space-x-1"
                            title="Jump to transcript segment"
                          >
                            <Clock className="w-2.5 h-2.5" />
                            <span>[{r.source_time}]</span>
                          </button>
                        )}
                      </div>

                      {/* Relationship Arrow & Object */}
                      <div className="flex items-center space-x-1.5 pl-2 border-l-2 border-cyan-500/40 mt-1.5">
                        <span className="text-[9px] font-mono uppercase font-bold tracking-wider px-1.5 py-0.2 rounded bg-cyan-950/60 text-cyan-300 border border-cyan-800/40">
                          {r.relation}
                        </span>
                        <ArrowRight className="w-2.5 h-2.5 text-slate-500 shrink-0" />
                        <span 
                          onClick={() => setSelectedEntityFilter(r.object)}
                          className="text-xs font-medium text-slate-200 hover:text-cyan-300 cursor-pointer transition-colors"
                        >
                          {r.object}
                        </span>
                        <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-slate-800/80 text-slate-500">
                          {r.object_type || "Concept"}
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="py-8 text-center text-slate-500 text-xs font-mono bg-slate-900/40 rounded-lg border border-slate-800">
                    No relationships match current filters.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 2. Transcript Semantics Column / View */}
          {(activeViewMode === "split" || activeViewMode === "transcript") && (
            <div className="space-y-2">
              <div className="flex items-center justify-between px-1">
                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
                  <Clock className="w-3.5 h-3.5 text-cyan-400" />
                  <span>TIME-ALIGNED TRANSCRIPT ({filteredSegments.length})</span>
                </h3>
                <span className="text-[10px] font-mono text-slate-500">Tagged per moment</span>
              </div>

              <div ref={transcriptListRef} className="space-y-1.5 max-h-[550px] overflow-y-auto pr-1">
                {filteredSegments.length > 0 ? (
                  filteredSegments.map((seg, idx) => {
                    const isTarget = highlightedTime === seg.timestamp;
                    return (
                      <div
                        key={idx}
                        id={`seg-${seg.timestamp.replace(":", "-")}`}
                        className={`p-2.5 rounded-lg border transition-colors ${
                          isTarget
                            ? "bg-cyan-950/30 border-cyan-500/70 shadow-sm"
                            : "bg-slate-900/80 hover:bg-slate-850 border-slate-800/80"
                        }`}
                      >
                        <div className="flex items-start space-x-2">
                          <span className="px-1.5 py-0.2 rounded bg-slate-800 text-cyan-400 border border-slate-700/60 text-[10px] font-mono font-bold shrink-0 mt-0.5">
                            {seg.timestamp}
                          </span>
                          <div className="space-y-1 flex-1">
                            <p className="text-xs text-slate-300 leading-relaxed">
                              {highlightMatch(seg.text, searchQuery)}
                            </p>

                            {/* Detected Semantics Tags */}
                            {seg.detected_entities && seg.detected_entities.length > 0 && (
                              <div className="flex flex-wrap gap-1 pt-0.5">
                                {seg.detected_entities.map((ent) => (
                                  <button
                                    key={ent}
                                    onClick={() => setSelectedEntityFilter(ent)}
                                    className="tactile-btn text-[9px] font-mono px-1 py-0.2 rounded bg-slate-800 hover:bg-cyan-950/60 text-cyan-300 border border-slate-700/60 transition-colors"
                                  >
                                    #{ent}
                                  </button>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="py-8 text-center text-slate-500 text-xs font-mono bg-slate-900/40 rounded-lg border border-slate-800">
                    No transcript segments match your query.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

