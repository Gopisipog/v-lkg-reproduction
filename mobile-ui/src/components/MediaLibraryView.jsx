import React, { useState, useEffect } from "react";
import { 
  Film, Plus, Link, Clock, Brain, Check, RefreshCw, 
  PlayCircle, Mic, CheckCircle2, ExternalLink, Search, X, Workflow, Tag, Radio
} from "lucide-react";
import { ingestYouTubeVideo, updateVideoIntelligences, searchTranscripts } from "../services/api";

const INTELLIGENCE_LENSES = [
  { id: "executive", name: "EXECUTIVE", color: "#0ea5e9" },
  { id: "sales", name: "SALES", color: "#10b981" },
  { id: "learning", name: "MASTERY", color: "#f59e0b" },
  { id: "engineering", name: "AI TOOLS & R&D", color: "#38bdf8" },
  { id: "compliance", name: "GOVERNANCE", color: "#ef4444" },
  { id: "customer", name: "SUCCESS", color: "#ec4899" },
  { id: "thought_leadership", name: "LEADERSHIP", color: "#14b8a6" }
];

export default function MediaLibraryView({ 
  allVideos, 
  apps = [],
  activeApp, 
  onRefreshVideos, 
  onJumpToVideo 
}) {
  const [ingestUrl, setIngestUrl] = useState("");
  const [targetAppId, setTargetAppId] = useState(activeApp?.id || "");
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestSuccess, setIngestSuccess] = useState(false);
  const [selectedLensesForIngest, setSelectedLensesForIngest] = useState(["executive", "thought_leadership"]);
  const [showIngestModal, setShowIngestModal] = useState(false);
  const [transcriptQuery, setTranscriptQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    if (!transcriptQuery.trim() || transcriptQuery.trim().length < 2) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(() => {
      setSearching(true);
      searchTranscripts(transcriptQuery.trim())
        .then((res) => {
          setSearchResults(res.results || []);
        })
        .catch((err) => console.error("Transcript search failed:", err))
        .finally(() => setSearching(false));
    }, 250);
    return () => clearTimeout(timer);
  }, [transcriptQuery]);

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

  useEffect(() => {
    if (activeApp?.id) {
      setTargetAppId(activeApp.id);
    }
  }, [activeApp]);

  const toggleLensForIngest = (id) => {
    if (selectedLensesForIngest.includes(id)) {
      if (selectedLensesForIngest.length > 1) {
        setSelectedLensesForIngest(selectedLensesForIngest.filter(l => l !== id));
      }
    } else {
      setSelectedLensesForIngest([...selectedLensesForIngest, id]);
    }
  };

  const handleIngest = async (e) => {
    e.preventDefault();
    if (!ingestUrl.trim()) return;

    setIsIngesting(true);
    setIngestSuccess(false);

    try {
      await ingestYouTubeVideo(
        ingestUrl.trim(),
        targetAppId || null,
        selectedLensesForIngest
      );
      setIngestSuccess(true);
      setIngestUrl("");
      if (onRefreshVideos) onRefreshVideos();
      setTimeout(() => setShowIngestModal(false), 1500);
    } catch (err) {
      alert(err.message || "Failed to ingest YouTube video");
    } finally {
      setIsIngesting(false);
    }
  };

  const toggleVideoLens = async (videoId, lensId, currentLenses) => {
    const updated = currentLenses.includes(lensId)
      ? currentLenses.filter((l) => l !== lensId)
      : [...currentLenses, lensId];
    if (updated.length === 0) return;

    try {
      await updateVideoIntelligences(videoId, updated);
      if (onRefreshVideos) onRefreshVideos();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-3 sm:p-5 space-y-3.5 pb-48 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm sm:text-base font-bold text-white flex items-center space-x-2">
            <Film className="w-4 h-4 text-cyan-400" />
            <span>MULTIMEDIA LIBRARY ({allVideos.length})</span>
          </h2>
          <p className="text-xs font-mono text-slate-400">
            Global catalog of ingested YouTube videos & Voice recordings
          </p>
        </div>

        <button
          onClick={() => setShowIngestModal(true)}
          className="tactile-btn flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-cyan-400 hover:bg-cyan-300 text-slate-950 text-xs font-mono font-bold transition-all shadow-sm shrink-0"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Ingest YouTube</span>
        </button>
      </div>

      {/* Ingest YouTube Modal */}
      {showIngestModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-2xl space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-mono font-bold text-white flex items-center space-x-2">
                <Link className="w-3.5 h-3.5 text-cyan-400" />
                <span>INGEST NEW YOUTUBE RECORDING</span>
              </h3>
              <button
                onClick={() => setShowIngestModal(false)}
                className="tactile-btn text-slate-400 hover:text-white p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleIngest} className="space-y-3">
              <div>
                <label className="block text-[11px] font-mono font-semibold text-slate-300 mb-1">
                  YOUTUBE VIDEO URL
                </label>
                <input
                  type="url"
                  required
                  value={ingestUrl}
                  onChange={(e) => setIngestUrl(e.target.value)}
                  placeholder="https://www.youtube.com/watch?v=..."
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 font-mono focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono font-semibold text-slate-300 mb-1">
                  ASSIGN TO CHILD APP
                </label>
                <select
                  value={targetAppId}
                  onChange={(e) => setTargetAppId(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white font-mono focus:outline-none focus:border-cyan-500"
                >
                  <option value="">Global Library (No Specific App)</option>
                  {apps.map((app) => (
                    <option key={app.id} value={app.id}>
                      {app.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-mono font-semibold text-slate-300 mb-1">
                  SELECT INTELLIGENCE LENSES
                </label>
                <div className="flex flex-wrap gap-1">
                  {INTELLIGENCE_LENSES.map((lens) => {
                    const active = selectedLensesForIngest.includes(lens.id);
                    return (
                      <button
                        key={lens.id}
                        type="button"
                        onClick={() => toggleLensForIngest(lens.id)}
                        className={`tactile-btn px-2 py-0.5 rounded text-[10px] font-mono font-medium border transition-colors ${
                          active ? "bg-cyan-500 text-slate-950 font-bold border-cyan-400" : "bg-slate-950 text-slate-400 border-slate-800"
                        }`}
                      >
                        {lens.name}
                      </button>
                    );
                  })}
                </div>
              </div>

              <button
                type="submit"
                disabled={isIngesting || !ingestUrl.trim()}
                className="tactile-btn w-full py-2 rounded-lg bg-cyan-400 hover:bg-cyan-300 text-slate-950 text-xs font-mono font-bold transition-all disabled:opacity-50 flex items-center justify-center space-x-1.5"
              >
                {isIngesting ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                ) : ingestSuccess ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-950" />
                    <span>Ingestion Complete!</span>
                  </>
                ) : (
                  <span>Ingest & Extract Linear Entities</span>
                )}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Global Searchable Transcripts Box across all videos */}
      <div className="rounded-xl bg-slate-900 border border-slate-800 p-3.5 space-y-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs font-mono font-bold uppercase tracking-wider text-cyan-400">
            <Search className="w-3.5 h-3.5" />
            <span>Search Transcripts (3,180+ Segments)</span>
          </div>
          {transcriptQuery && (
            <span className="text-[10px] font-mono text-slate-400">
              {searching ? "Searching..." : `Found ${searchResults.length} matches`}
            </span>
          )}
        </div>

        <div className="flex items-center space-x-2 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800">
          <Search className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          <input
            type="text"
            value={transcriptQuery}
            onChange={(e) => setTranscriptQuery(e.target.value)}
            placeholder="Search words across all video transcripts..."
            className="w-full bg-transparent text-xs text-white placeholder-slate-500 font-mono focus:outline-none"
          />
          {transcriptQuery && (
            <button
              onClick={() => setTranscriptQuery("")}
              className="tactile-btn p-0.5 text-slate-400 hover:text-white text-xs"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Global Search Results Stream */}
        {transcriptQuery.trim().length >= 2 && (
          <div className="space-y-1.5 max-h-96 overflow-y-auto pr-1 pt-1 border-t border-slate-800/80">
            {searching ? (
              <div className="py-6 text-center text-slate-400 text-xs font-mono flex items-center justify-center space-x-2">
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                <span>Searching all video transcripts...</span>
              </div>
            ) : searchResults.length > 0 ? (
              searchResults.map((res, idx) => (
                <div
                  key={idx}
                  className="p-2.5 rounded-lg bg-slate-950/80 hover:bg-slate-850 border border-slate-800 hover:border-cyan-800/60 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-2 group"
                >
                  <div className="space-y-0.5 flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-[11px] font-semibold text-white group-hover:text-cyan-300 transition-colors">
                        {res.video_title}
                      </span>
                      <span className="px-1.5 py-0.2 rounded bg-cyan-950/60 text-cyan-300 border border-cyan-800/40 text-[9px] font-mono font-bold">
                        {res.timestamp}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed font-sans">
                      {highlightMatch(res.text, transcriptQuery)}
                    </p>
                  </div>

                  <button
                    onClick={() => onJumpToVideo(res.video_id, res.timestamp)}
                    className="tactile-btn px-2 py-1 rounded bg-cyan-950/40 hover:bg-cyan-900/50 text-cyan-300 border border-cyan-800/40 text-[11px] font-mono font-bold flex items-center space-x-1 shrink-0"
                  >
                    <Workflow className="w-3 h-3 text-cyan-400" />
                    <span>View in Semantics</span>
                  </button>
                </div>
              ))
            ) : (
              <div className="py-6 text-center text-slate-500 text-xs font-mono">
                No transcript segments found matching "{transcriptQuery}".
              </div>
            )}
          </div>
        )}
      </div>

      {/* Videos List */}
      <div className="space-y-2">
        {allVideos.map((v) => {
          const isVoice = v.is_voice_recording || v.video_id.startsWith("voice_") || v.video_id.startsWith("live_");
          const lenses = v.selected_intelligences || ["executive", "thought_leadership"];

          return (
            <div
              key={v.video_id}
              className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-2"
            >
              <div className="flex items-start space-x-3">
                <div className="relative w-16 h-12 rounded-lg bg-slate-800 shrink-0 overflow-hidden border border-slate-700/60">
                  {isVoice ? (
                    <div className="w-full h-full flex flex-col items-center justify-center bg-rose-950/40 text-rose-300">
                      <Mic className="w-4 h-4" />
                      <span className="text-[8px] font-mono font-bold mt-0.5">VOICE</span>
                    </div>
                  ) : (
                    <img 
                      src={v.thumbnail_url} 
                      alt={v.title} 
                      className="w-full h-full object-cover"
                      onError={(e) => { e.target.style.display = 'none'; }}
                    />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <h4 className="text-xs font-bold text-white line-clamp-1">{v.title}</h4>
                  <p className="text-[11px] font-mono text-slate-400">{v.channel}</p>
                  <div className="flex items-center space-x-2 text-[10px] font-mono text-slate-500 mt-0.5">
                    <span className="flex items-center space-x-1">
                      <Clock className="w-2.5 h-2.5" />
                      <span>{Math.round(v.duration_sec / 60)}m</span>
                    </span>
                    <span>·</span>
                    <span>{v.segment_count || 0} seg</span>
                    <span>·</span>
                    <span className="text-cyan-400 font-bold">{v.triplet_count || 0} triplets</span>
                  </div>
                </div>

                <button
                  onClick={() => onJumpToVideo(v.video_id, "00:00")}
                  className="tactile-btn px-2.5 py-1 rounded bg-cyan-950/40 hover:bg-cyan-900/50 text-cyan-300 border border-cyan-800/40 text-[11px] font-mono font-bold flex items-center space-x-1 shrink-0"
                  title="Explore Semantics & Transcripts"
                >
                  <Workflow className="w-3 h-3 text-cyan-400" />
                  <span>Semantics</span>
                </button>
              </div>

              {/* Summary */}
              {v.summary && (
                <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed bg-slate-950/60 p-2 rounded border border-slate-800/80 font-sans">
                  {v.summary}
                </p>
              )}

              {/* Per-Video Intelligence Lenses */}
              <div className="pt-1.5 border-t border-slate-800/80">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[9px] font-mono font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1">
                    <Brain className="w-2.5 h-2.5 text-cyan-400" />
                    <span>Active Lenses</span>
                  </span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {INTELLIGENCE_LENSES.map((lens) => {
                    const active = lenses.includes(lens.id);
                    return (
                      <button
                        key={lens.id}
                        onClick={() => toggleVideoLens(v.video_id, lens.id, lenses)}
                        className={`tactile-btn px-1.5 py-0.2 rounded text-[9px] font-mono border transition-colors flex items-center space-x-1 ${
                          active 
                            ? "bg-slate-800 border-cyan-500/60 text-white" 
                            : "bg-slate-950 border-slate-800 text-slate-500 hover:text-slate-300"
                        }`}
                      >
                        <span 
                          className="w-1.5 h-1.5 rounded-full inline-block"
                          style={{ backgroundColor: active ? lens.color : '#64748b' }}
                        />
                        <span>{lens.name}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

