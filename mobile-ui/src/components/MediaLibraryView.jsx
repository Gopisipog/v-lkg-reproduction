import React, { useState, useEffect } from "react";
import { 
  Film, Plus, Link, Clock, Brain, Check, RefreshCw, 
  PlayCircle, Mic, CheckCircle2, ExternalLink, Search, X, Workflow, Tag
} from "lucide-react";
import { ingestYouTubeVideo, updateVideoIntelligences, searchTranscripts } from "../services/api";

const INTELLIGENCE_LENSES = [
  { id: "executive", name: "Executive", color: "#6366f1" },
  { id: "sales", name: "Sales", color: "#10b981" },
  { id: "learning", name: "Learning", color: "#f59e0b" },
  { id: "engineering", name: "R&D/AI", color: "#3b82f6" },
  { id: "compliance", name: "Governance", color: "#ef4444" },
  { id: "customer", name: "Customer", color: "#ec4899" },
  { id: "competitive", name: "Competitive", color: "#8b5cf6" },
  { id: "thought_leadership", name: "Leadership", color: "#14b8a6" }
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
        <mark key={i} className="bg-amber-400/30 text-amber-200 px-1 py-0.5 rounded font-bold">
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
    <div className="p-4 space-y-5 pb-40 max-w-3xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center space-x-2">
            <Film className="w-5 h-5 text-indigo-400" />
            <span>Multimedia Library ({allVideos.length})</span>
          </h2>
          <p className="text-xs text-slate-400">
            Global catalog of ingested YouTube videos & Voice recordings
          </p>
        </div>

        <button
          onClick={() => setShowIngestModal(true)}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all active:scale-95 shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Ingest YouTube</span>
        </button>
      </div>

      {/* Ingest YouTube Modal */}
      {showIngestModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-md bg-slate-900 border border-slate-700 rounded-3xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <Link className="w-4 h-4 text-indigo-400" />
                <span>Ingest New YouTube Video</span>
              </h3>
              <button
                onClick={() => setShowIngestModal(false)}
                className="text-slate-400 hover:text-white text-xs font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleIngest} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  YouTube Video URL
                </label>
                <input
                  type="url"
                  required
                  value={ingestUrl}
                  onChange={(e) => setIngestUrl(e.target.value)}
                  placeholder="https://www.youtube.com/watch?v=..."
                  className="w-full px-3.5 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Assign to Child App
                </label>
                <select
                  value={targetAppId}
                  onChange={(e) => setTargetAppId(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Global Library Only (No Specific Child App)</option>
                  {apps.map((app) => (
                    <option key={app.id} value={app.id}>
                      {app.name}
                    </option>
                  ))}
                </select>
                <p className="text-[10px] text-slate-400 mt-1">
                  Extracted linear words and entities will be scoped to this child app.
                </p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Select Intelligence Lenses to Apply
                </label>
                <div className="flex flex-wrap gap-1.5">
                  {INTELLIGENCE_LENSES.map((lens) => {
                    const active = selectedLensesForIngest.includes(lens.id);
                    return (
                      <button
                        key={lens.id}
                        type="button"
                        onClick={() => toggleLensForIngest(lens.id)}
                        className={`px-2.5 py-1 rounded-xl text-[10px] font-semibold border transition-all ${
                          active ? "bg-indigo-600 text-white border-indigo-500" : "bg-slate-800 text-slate-400 border-slate-700"
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
                className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center space-x-2"
              >
                {isIngesting ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : ingestSuccess ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
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
      <div className="rounded-3xl bg-gradient-to-br from-indigo-950/70 via-slate-900 to-slate-900 border border-indigo-500/30 p-4 shadow-xl space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-indigo-300">
            <Search className="w-3.5 h-3.5 text-indigo-400" />
            <span>Search All Video Transcripts (3,180+ Segments)</span>
          </div>
          {transcriptQuery && (
            <span className="text-[11px] text-slate-400">
              {searching ? "Searching..." : `Found ${searchResults.length} matches`}
            </span>
          )}
        </div>

        <div className="flex items-center space-x-2 bg-slate-950/80 p-2.5 rounded-2xl border border-slate-700/80 focus-within:border-indigo-500 transition-colors">
          <Search className="w-4 h-4 text-slate-400 ml-1 shrink-0" />
          <input
            type="text"
            value={transcriptQuery}
            onChange={(e) => setTranscriptQuery(e.target.value)}
            placeholder="Search words across all analysed video transcripts (e.g. 'vulnerability', 'toxic', 'Feynman', 'strategy')..."
            className="w-full bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none"
          />
          {transcriptQuery && (
            <button
              onClick={() => setTranscriptQuery("")}
              className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white text-xs mr-1"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Global Search Results Stream */}
        {transcriptQuery.trim().length >= 2 && (
          <div className="space-y-2 max-h-96 overflow-y-auto pr-1 pt-1 border-t border-slate-800/80 animate-fade-in">
            {searching ? (
              <div className="py-6 text-center text-slate-400 text-xs flex items-center justify-center space-x-2">
                <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
                <span>Searching all video transcripts...</span>
              </div>
            ) : searchResults.length > 0 ? (
              searchResults.map((res, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-2xl bg-slate-900/90 hover:bg-slate-850 border border-slate-800 hover:border-indigo-500/40 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 group"
                >
                  <div className="space-y-1 flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-[11px] font-bold text-white group-hover:text-indigo-300 transition-colors">
                        {res.video_title}
                      </span>
                      <span className="px-2 py-0.2 rounded bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 text-[10px] font-mono font-bold">
                        {res.timestamp}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      {highlightMatch(res.text, transcriptQuery)}
                    </p>
                  </div>

                  <button
                    onClick={() => onJumpToVideo(res.video_id, res.timestamp)}
                    className="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition-all shrink-0 active:scale-95 shadow-md shadow-indigo-600/20"
                  >
                    <Workflow className="w-3.5 h-3.5" />
                    <span>View in Semantics</span>
                  </button>
                </div>
              ))
            ) : (
              <div className="py-6 text-center text-slate-500 text-xs">
                No transcript segments found matching "{transcriptQuery}".
              </div>
            )}
          </div>
        )}
      </div>

      {/* Videos List */}
      <div className="space-y-3.5">
        {allVideos.map((v) => {
          const isVoice = v.is_voice_recording || v.video_id.startsWith("voice_") || v.video_id.startsWith("live_");
          const lenses = v.selected_intelligences || ["executive", "thought_leadership"];

          return (
            <div
              key={v.video_id}
              className="p-4 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-3"
            >
              <div className="flex items-start space-x-3.5">
                <div className="relative w-20 h-14 rounded-2xl bg-slate-800 shrink-0 overflow-hidden border border-slate-700">
                  {isVoice ? (
                    <div className="w-full h-full flex flex-col items-center justify-center bg-gradient-to-tr from-rose-900/60 to-pink-900/40 text-rose-300">
                      <Mic className="w-5 h-5" />
                      <span className="text-[9px] font-bold mt-0.5">VOICE</span>
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
                  <p className="text-[11px] text-slate-400">{v.channel}</p>
                  <div className="flex items-center space-x-2 text-[10px] text-slate-500 mt-1">
                    <span className="flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{Math.round(v.duration_sec / 60)}m</span>
                    </span>
                    <span>·</span>
                    <span>{v.segment_count || 0} segments</span>
                    <span>·</span>
                    <span className="text-indigo-400 font-medium">{v.triplet_count || 0} triplets</span>
                  </div>
                </div>

                <button
                  onClick={() => onJumpToVideo(v.video_id, "00:00")}
                  className="px-3 py-1.5 rounded-xl bg-indigo-600/20 hover:bg-indigo-600 text-indigo-400 hover:text-white border border-indigo-500/30 text-xs font-semibold flex items-center space-x-1.5 transition-all shrink-0 active:scale-95"
                  title="Explore Semantics & Transcripts"
                >
                  <Workflow className="w-3.5 h-3.5" />
                  <span>Semantics</span>
                </button>
              </div>

              {/* Summary */}
              {v.summary && (
                <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed bg-slate-850/60 p-2.5 rounded-2xl border border-slate-800">
                  {v.summary}
                </p>
              )}

              {/* Per-Video Intelligence Lenses */}
              <div className="pt-2 border-t border-slate-800/80">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 flex items-center space-x-1">
                    <Brain className="w-3 h-3 text-indigo-400" />
                    <span>Active Intelligence Lenses</span>
                  </span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {INTELLIGENCE_LENSES.map((lens) => {
                    const active = lenses.includes(lens.id);
                    return (
                      <button
                        key={lens.id}
                        onClick={() => toggleVideoLens(v.video_id, lens.id, lenses)}
                        className={`px-2 py-0.5 rounded-lg text-[10px] font-medium border transition-all ${
                          active 
                            ? "bg-slate-800 border-indigo-500 text-white" 
                            : "bg-slate-900 border-slate-800 text-slate-500 hover:text-slate-300"
                        }`}
                      >
                        <span style={{ color: active ? lens.color : undefined }}>● </span>
                        {lens.name}
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
