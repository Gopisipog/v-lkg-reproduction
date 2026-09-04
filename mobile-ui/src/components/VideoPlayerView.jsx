import React, { useState, useEffect, useRef } from "react";
import { 
  Workflow, Tag, Clock, Search, ExternalLink, Sparkles, Film, Mic, 
  ArrowRight, ChevronDown, ChevronUp, Filter, X, Layers, Brain, Check,
  Share2, Compass, PlayCircle
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
        <mark key={i} className="bg-amber-400/30 text-amber-200 px-1 py-0.5 rounded font-bold">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  const currentVideo = displayVideos.find((v) => v.video_id === currentVideoId) || semanticsData?.metadata;
  const isVoice = currentVideo?.is_voice_recording || currentVideoId?.startsWith("voice_") || currentVideoId?.startsWith("live_");

  const relationships = semanticsData?.relationships || [];
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
    <div className="p-4 space-y-4 pb-40 max-w-4xl mx-auto animate-fade-in">
      {/* Video Carousel Selector */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1 no-scrollbar">
        {displayVideos.map((v) => {
          const isSelected = v.video_id === currentVideoId;
          const isV = v.is_voice_recording || v.video_id.startsWith("voice_");
          return (
            <button
              key={v.video_id}
              onClick={() => setCurrentVideoId(v.video_id)}
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-2xl border text-xs font-semibold whitespace-nowrap transition-all shrink-0 ${
                isSelected
                  ? "bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/25"
                  : "bg-slate-900 text-slate-400 border-slate-800 hover:text-white"
              }`}
            >
              {isV ? <Mic className="w-3.5 h-3.5 text-rose-400" /> : <Film className="w-3.5 h-3.5 text-indigo-400" />}
              <span className="truncate max-w-[150px]">{v.title}</span>
            </button>
          );
        })}
      </div>

      {/* Main Video Semantics & Knowledge Header (Replaces video iframe) */}
      <div className="rounded-3xl overflow-hidden bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950/40 border border-slate-800 shadow-2xl p-5 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-[11px] font-bold">
                <Workflow className="w-3 h-3 text-indigo-400" />
                <span>Recorded VLKG Knowledge & Transcript Semantics</span>
              </span>
              <span className="text-[11px] text-slate-500 font-mono">ID: {currentVideoId}</span>
            </div>

            <h2 className="text-base sm:text-lg font-black text-white tracking-tight leading-snug">
              {currentVideo?.title || `Video Archive [${currentVideoId}]`}
            </h2>

            <div className="flex items-center space-x-2 text-xs text-slate-400">
              <span>{currentVideo?.channel || "Leadership Series"}</span>
              <span>·</span>
              <span>{durationMin > 0 ? `${durationMin} mins duration` : "Ingested Recording"}</span>
              {currentVideo?.url && (
                <>
                  <span>·</span>
                  <a 
                    href={currentVideo.url} 
                    target="_blank" 
                    rel="noreferrer"
                    className="text-indigo-400 hover:text-indigo-300 inline-flex items-center space-x-0.5 font-medium underline"
                  >
                    <span>YouTube source</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </>
              )}
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="flex items-center gap-2 shrink-0">
            <div className="px-3 py-2 rounded-2xl bg-slate-850/80 border border-slate-800 text-center">
              <div className="text-sm font-black text-indigo-400">{relationships.length}</div>
              <div className="text-[10px] text-slate-400 font-medium">Relationships</div>
            </div>
            <div className="px-3 py-2 rounded-2xl bg-slate-850/80 border border-slate-800 text-center">
              <div className="text-sm font-black text-purple-400">{segments.length}</div>
              <div className="text-[10px] text-slate-400 font-medium">Segments</div>
            </div>
            <div className="px-3 py-2 rounded-2xl bg-slate-850/80 border border-slate-800 text-center">
              <div className="text-sm font-black text-emerald-400">{intelPills.length}</div>
              <div className="text-[10px] text-slate-400 font-medium">Lenses</div>
            </div>
          </div>
        </div>

        {/* Video Summary if available */}
        {currentVideo?.summary && (
          <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded-2xl border border-slate-800/80">
            <strong className="text-slate-200">Summary: </strong>{currentVideo.summary}
          </p>
        )}

        {/* Expandable VLKG Recorded Knowledge Badges */}
        <div className="pt-2 border-t border-slate-800/80 space-y-2">
          <button
            onClick={() => setShowPillsSection(!showPillsSection)}
            className="w-full flex items-center justify-between text-xs font-bold text-slate-300 hover:text-white transition-colors"
          >
            <div className="flex items-center space-x-2">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>Explore Recorded Entity & Intelligence Pills ({extractedPills.length + enrichedPills.length + intelPills.length} Categories)</span>
            </div>
            {showPillsSection ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
          </button>

          {showPillsSection && (
            <div className="space-y-3 pt-2 animate-fade-in">
              {/* Extracted */}
              {extractedPills.length > 0 && (
                <div className="space-y-1">
                  <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Extracted from Video</div>
                  <div className="flex flex-wrap gap-1.5">
                    {extractedPills.map((group) =>
                      group.entities.slice(0, 15).map((name) => (
                        <button
                          key={name}
                          onClick={() => setSelectedEntityFilter(selectedEntityFilter === name ? null : name)}
                          className={`text-[11px] px-2.5 py-0.5 rounded-full border transition-all ${
                            selectedEntityFilter === name
                              ? "ring-2 ring-white text-white font-bold"
                              : "text-slate-200 hover:opacity-80"
                          }`}
                          style={{ backgroundColor: `${group.color}25`, borderColor: group.color }}
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
                  <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Enriched Pathways</div>
                  <div className="flex flex-wrap gap-1.5">
                    {enrichedPills.map((group) =>
                      group.entities.slice(0, 15).map((name) => (
                        <button
                          key={name}
                          onClick={() => setSelectedEntityFilter(selectedEntityFilter === name ? null : name)}
                          className={`text-[11px] px-2.5 py-0.5 rounded-full border transition-all ${
                            selectedEntityFilter === name
                              ? "ring-2 ring-white text-white font-bold"
                              : "text-slate-200 hover:opacity-80"
                          }`}
                          style={{ backgroundColor: `${group.color}25`, borderColor: group.color }}
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
                  <div className="text-[11px] font-bold text-purple-400 uppercase tracking-wider">Intelligence Lenses</div>
                  <div className="flex flex-wrap gap-1.5">
                    {intelPills.map((group) =>
                      group.entities.slice(0, 10).map((name) => (
                        <button
                          key={name}
                          onClick={() => setSelectedEntityFilter(selectedEntityFilter === name ? null : name)}
                          className={`text-[11px] px-2.5 py-0.5 rounded-full border border-purple-500/40 bg-purple-500/20 text-purple-200 transition-all ${
                            selectedEntityFilter === name ? "ring-2 ring-white font-bold" : "hover:opacity-80"
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

      {/* Control Bar: Search & View Mode */}
      <div className="space-y-2">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          {/* View Mode Toggle */}
          <div className="bg-slate-900 border border-slate-800 p-1 rounded-2xl flex items-center space-x-1 shadow-md w-fit">
            <button
              onClick={() => setActiveViewMode("split")}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                activeViewMode === "split"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Split View
            </button>
            <button
              onClick={() => setActiveViewMode("relationships")}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                activeViewMode === "relationships"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Relationships ({filteredRelationships.length})
            </button>
            <button
              onClick={() => setActiveViewMode("transcript")}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                activeViewMode === "transcript"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Transcript ({filteredSegments.length})
            </button>
          </div>

          {/* Active Filter Pill */}
          {selectedEntityFilter && (
            <div className="flex items-center space-x-1.5 px-3 py-1 rounded-xl bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 text-xs font-semibold">
              <span>Filtered by: <strong>{selectedEntityFilter}</strong></span>
              <button onClick={() => setSelectedEntityFilter(null)} className="hover:text-white ml-1">
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>

        {/* Search Bar */}
        <div className="flex items-center space-x-2 bg-slate-900 p-2.5 rounded-2xl border border-slate-800 shadow-md">
          <Search className="w-4 h-4 text-slate-400 ml-1 shrink-0" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search relationships, concepts, or transcript words..."
            className="w-full bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none"
          />
          {searchQuery && (
            <button onClick={() => setSearchQuery("")} className="text-slate-400 hover:text-white text-xs mr-2">
              Clear
            </button>
          )}
        </div>

        {/* Relation Type Horizontal Filters (when in relationships or split mode) */}
        {activeViewMode !== "transcript" && relationTypes.length > 2 && (
          <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 no-scrollbar pt-1">
            {relationTypes.slice(0, 10).map((rel) => (
              <button
                key={rel}
                onClick={() => setSelectedRelation(rel)}
                className={`px-2.5 py-1 rounded-xl text-[11px] font-semibold whitespace-nowrap transition-all border ${
                  selectedRelation === rel
                    ? "bg-indigo-500/30 text-indigo-300 border-indigo-500/50 shadow-sm"
                    : "bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200"
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
        <div className="py-16 text-center text-slate-400 text-xs flex flex-col items-center space-y-2">
          <Workflow className="w-6 h-6 animate-spin text-indigo-400" />
          <span>Loading relationships and transcript semantics...</span>
        </div>
      ) : (
        <div className={`gap-4 ${activeViewMode === "split" ? "grid grid-cols-1 lg:grid-cols-2" : "space-y-4"}`}>
          {/* 1. Relationships Column / View */}
          {(activeViewMode === "split" || activeViewMode === "relationships") && (
            <div className="space-y-2.5">
              <div className="flex items-center justify-between px-1">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
                  <Workflow className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Knowledge Relationships ({filteredRelationships.length})</span>
                </h3>
                <span className="text-[10px] text-slate-500">Tap timestamp to jump</span>
              </div>

              <div className="space-y-2 max-h-[550px] overflow-y-auto pr-1">
                {filteredRelationships.length > 0 ? (
                  filteredRelationships.map((r, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-2xl bg-slate-900/90 hover:bg-slate-850 border border-slate-800/90 hover:border-indigo-500/40 transition-all shadow-sm group"
                    >
                      <div className="flex items-center justify-between gap-2 mb-1.5">
                        <div className="flex items-center space-x-1.5 flex-wrap gap-y-1">
                          <span 
                            onClick={() => setSelectedEntityFilter(r.subject)}
                            className="text-xs font-bold text-white hover:text-indigo-300 cursor-pointer transition-colors"
                          >
                            {r.subject}
                          </span>
                          <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 font-medium border border-slate-700/50">
                            {r.subject_type || "Concept"}
                          </span>
                        </div>

                        {r.source_time && (
                          <button
                            onClick={() => scrollToTimestamp(r.source_time)}
                            className="px-2 py-0.5 rounded-lg bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600 hover:text-white border border-indigo-500/30 text-[11px] font-bold transition-all shrink-0 flex items-center space-x-1"
                            title="Jump to transcript segment"
                          >
                            <Clock className="w-2.5 h-2.5" />
                            <span>{r.source_time}</span>
                          </button>
                        )}
                      </div>

                      {/* Relationship Arrow & Object */}
                      <div className="flex items-center space-x-2 pl-2 border-l-2 border-indigo-500/40 mt-2">
                        <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-md bg-indigo-950/60 text-indigo-300 border border-indigo-500/30">
                          {r.relation}
                        </span>
                        <ArrowRight className="w-3 h-3 text-slate-500 shrink-0" />
                        <span 
                          onClick={() => setSelectedEntityFilter(r.object)}
                          className="text-xs font-semibold text-slate-200 hover:text-indigo-300 cursor-pointer transition-colors"
                        >
                          {r.object}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800/80 text-slate-400">
                          {r.object_type || "Concept"}
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="py-12 text-center text-slate-500 text-xs bg-slate-900/40 rounded-2xl border border-dashed border-slate-800">
                    No relationships match current filters.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 2. Transcript Semantics Column / View */}
          {(activeViewMode === "split" || activeViewMode === "transcript") && (
            <div className="space-y-2.5">
              <div className="flex items-center justify-between px-1">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
                  <Clock className="w-3.5 h-3.5 text-purple-400" />
                  <span>Time-Aligned Transcript ({filteredSegments.length})</span>
                </h3>
                <span className="text-[10px] text-slate-500">Entities tagged per moment</span>
              </div>

              <div ref={transcriptListRef} className="space-y-2 max-h-[550px] overflow-y-auto pr-1">
                {filteredSegments.length > 0 ? (
                  filteredSegments.map((seg, idx) => {
                    const isTarget = highlightedTime === seg.timestamp;
                    return (
                      <div
                        key={idx}
                        id={`seg-${seg.timestamp.replace(":", "-")}`}
                        className={`p-3 rounded-2xl border transition-all ${
                          isTarget
                            ? "bg-indigo-950/50 border-indigo-500 shadow-md ring-1 ring-indigo-500/30"
                            : "bg-slate-900/80 hover:bg-slate-850 border-slate-800"
                        }`}
                      >
                        <div className="flex items-start space-x-2.5">
                          <span className="px-2 py-0.5 rounded-lg bg-purple-600/20 text-purple-300 border border-purple-500/30 text-[11px] font-mono font-bold shrink-0 mt-0.5">
                            {seg.timestamp}
                          </span>
                          <div className="space-y-1.5 flex-1">
                            <p className="text-xs text-slate-300 leading-relaxed">
                              {highlightMatch(seg.text, searchQuery)}
                            </p>

                            {/* Detected Semantics Tags */}
                            {seg.detected_entities && seg.detected_entities.length > 0 && (
                              <div className="flex flex-wrap gap-1 pt-1">
                                {seg.detected_entities.map((ent) => (
                                  <button
                                    key={ent}
                                    onClick={() => setSelectedEntityFilter(ent)}
                                    className="text-[10px] px-1.5 py-0.2 rounded-md bg-slate-800 hover:bg-indigo-600/30 text-indigo-300 border border-slate-700/60 font-medium transition-colors"
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
                  <div className="py-12 text-center text-slate-500 text-xs bg-slate-900/40 rounded-2xl border border-dashed border-slate-800">
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
