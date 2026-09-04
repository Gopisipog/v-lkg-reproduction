import React, { useState, useEffect } from "react";
import { X, Film, Clock, Brain, PlusCircle, CheckCircle2 } from "lucide-react";
import { updateVideoIntelligences } from "../services/api";

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

export default function VideoManagerModal({ 
  isOpen, 
  onClose, 
  activeApp, 
  allVideos, 
  onSaveAssignedVideos,
  onRefreshVideos
}) {
  const [selectedVideoIds, setSelectedVideoIds] = useState([]);
  const [videoLenses, setVideoLenses] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (activeApp && isOpen) {
      setSelectedVideoIds(activeApp.video_ids || []);
      const lensMap = {};
      allVideos.forEach(v => {
        lensMap[v.video_id] = v.selected_intelligences || ["executive", "thought_leadership"];
      });
      setVideoLenses(lensMap);
    }
  }, [activeApp, allVideos, isOpen]);

  if (!isOpen || !activeApp) return null;

  const toggleVideo = (videoId) => {
    if (selectedVideoIds.includes(videoId)) {
      setSelectedVideoIds(selectedVideoIds.filter(id => id !== videoId));
    } else {
      setSelectedVideoIds([...selectedVideoIds, videoId]);
    }
  };

  const toggleLensForVideo = async (videoId, lensId) => {
    const current = videoLenses[videoId] || ["executive", "thought_leadership"];
    const updated = current.includes(lensId)
      ? current.filter(l => l !== lensId)
      : [...current, lensId];
      
    if (updated.length === 0) return;

    setVideoLenses({ ...videoLenses, [videoId]: updated });
    try {
      await updateVideoIntelligences(videoId, updated);
      if (onRefreshVideos) onRefreshVideos();
    } catch (err) {
      console.error("Failed to update video intelligence:", err);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSaveAssignedVideos(activeApp.id, selectedVideoIds);
      onClose();
    } catch (err) {
      alert(err.message || "Failed to assign videos");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-xl bg-slate-900 border border-slate-700/80 rounded-t-3xl sm:rounded-3xl shadow-2xl max-h-[90vh] flex flex-col overflow-hidden animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div 
              className="w-8 h-8 rounded-xl flex items-center justify-center text-white"
              style={{ backgroundColor: activeApp.theme_color || "#6366f1" }}
            >
              <Film className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">
                Assign Videos & Select Intelligences
              </h3>
              <p className="text-xs text-slate-400">
                Scoped to <span className="text-white font-medium">{activeApp.name}</span> ({selectedVideoIds.length} active)
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 rounded-full bg-slate-800 hover:bg-slate-750 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Video List */}
        <div className="p-6 overflow-y-auto space-y-4">
          <p className="text-xs text-slate-300">
            Select YouTube videos and voice recordings for this child app. Toggle domain <strong>Intelligence Lenses</strong> to specify what types of entities are extracted:
          </p>

          <div className="space-y-3">
            {allVideos.map((video) => {
              const isAssigned = selectedVideoIds.includes(video.video_id);
              const lenses = videoLenses[video.video_id] || video.selected_intelligences || [];
              const isVoice = video.is_voice_recording || video.video_id.startsWith("voice_") || video.video_id.startsWith("live_");

              return (
                <div 
                  key={video.video_id}
                  className={`p-3.5 rounded-2xl border transition-all ${
                    isAssigned 
                      ? "bg-slate-850/90 border-indigo-500/80 shadow-md ring-1 ring-indigo-500/20" 
                      : "bg-slate-900/60 border-slate-800/80 opacity-75 hover:opacity-100"
                  }`}
                >
                  <div className="flex items-start justify-between space-x-3">
                    <div className="relative w-16 h-12 rounded-xl bg-slate-800 shrink-0 overflow-hidden border border-slate-700">
                      {isVoice ? (
                        <div className="w-full h-full flex flex-col items-center justify-center bg-gradient-to-tr from-rose-900/60 to-pink-900/40 text-rose-300">
                          <span className="text-[10px] font-bold">VOICE</span>
                        </div>
                      ) : (
                        <img 
                          src={video.thumbnail_url} 
                          alt={video.title} 
                          className="w-full h-full object-cover"
                          onError={(e) => { e.target.style.display = 'none'; }}
                        />
                      )}
                    </div>

                    <div className="flex-1 min-w-0">
                      <h4 className="text-xs font-semibold text-white line-clamp-1">{video.title}</h4>
                      <p className="text-[11px] text-slate-400 truncate">{video.channel}</p>
                      <div className="flex items-center space-x-2 mt-1 text-[10px] text-slate-500">
                        <span className="flex items-center space-x-1">
                          <Clock className="w-3 h-3" />
                          <span>{Math.round(video.duration_sec / 60)}m</span>
                        </span>
                        <span>·</span>
                        <span>{video.segment_count || 0} segments</span>
                        <span>·</span>
                        <span className="text-indigo-400 font-medium">{video.triplet_count || 0} triplets</span>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => toggleVideo(video.video_id)}
                      className={`p-2 rounded-xl transition-all ${
                        isAssigned 
                          ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30" 
                          : "bg-slate-800 text-slate-400 hover:text-white"
                      }`}
                    >
                      {isAssigned ? <CheckCircle2 className="w-4 h-4" /> : <PlusCircle className="w-4 h-4" />}
                    </button>
                  </div>

                  {/* Selectable Intelligence Lenses */}
                  <div className="mt-3 pt-2.5 border-t border-slate-800/80">
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 flex items-center space-x-1">
                        <Brain className="w-3 h-3 text-indigo-400" />
                        <span>Active Intelligence Lenses ({lenses.length})</span>
                      </span>
                    </div>

                    <div className="flex flex-wrap gap-1.5">
                      {INTELLIGENCE_LENSES.map((lens) => {
                        const active = lenses.includes(lens.id);
                        return (
                          <button
                            key={lens.id}
                            type="button"
                            onClick={() => toggleLensForVideo(video.video_id, lens.id)}
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

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/90 flex items-center justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-slate-300 hover:text-white text-xs font-semibold transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition-all active:scale-95 disabled:opacity-50"
          >
            {saving ? "Saving..." : `Apply to ${activeApp.name}`}
          </button>
        </div>
      </div>
    </div>
  );
}
