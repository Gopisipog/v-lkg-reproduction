import React, { useState, useEffect } from "react";
import { X, Database, CheckCircle2, AlertTriangle, RefreshCw, Server, ArrowRight, ShieldCheck, HardDrive } from "lucide-react";
import { getDatabaseStatus, connectDatabase, syncDataToAura } from "../services/api";

export default function DatabaseModal({ isOpen, onClose }) {
  const [dbStatus, setDbStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [feedback, setFeedback] = useState(null);

  // Form state
  const [uri, setUri] = useState("");
  const [username, setUsername] = useState("neo4j");
  const [password, setPassword] = useState("");

  const loadStatus = async () => {
    setLoading(true);
    try {
      const data = await getDatabaseStatus();
      setDbStatus(data);
      if (data?.uri) setUri(data.uri);
      if (data?.user) setUsername(data.user);
    } catch (e) {
      console.warn("Failed to load database status", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadStatus();
      setFeedback(null);
    }
  }, [isOpen]);

  const handleConnect = async (e) => {
    e.preventDefault();
    setLoading(true);
    setFeedback(null);
    try {
      const res = await connectDatabase({ uri, username, password });
      if (res.connected) {
        setFeedback({ type: "success", text: res.message || "Connected to Neo4j successfully!" });
        await loadStatus();
      } else {
        setFeedback({ 
          type: "error", 
          text: res.error || "Connection failed. LocalGraphStore remains active." 
        });
      }
    } catch (err) {
      setFeedback({ type: "error", text: err.message || "Network error connecting to database." });
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    setFeedback(null);
    try {
      const res = await syncDataToAura();
      setFeedback({ type: "success", text: res.message || "Synced graph to Neo4j Aura DB!" });
      await loadStatus();
    } catch (err) {
      setFeedback({ 
        type: "error", 
        text: err.message || "Aura DB unreachable. Using LocalGraphStore JSON storage." 
      });
    } finally {
      setSyncing(false);
    }
  };

  if (!isOpen) return null;

  const isAuraConnected = dbStatus?.is_connected_to_aura || dbStatus?.status === "connected";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div 
        className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Database className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-100 flex items-center space-x-2">
                <span>Knowledge Graph Data Store</span>
              </h2>
              <p className="text-[11px] text-slate-400 font-mono">Neo4j AuraDB & LocalGraphStore</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Scrollable Body */}
        <div className="p-5 space-y-4 overflow-y-auto flex-1 text-xs">

          {/* Feedback banner */}
          {feedback && (
            <div className={`p-3 rounded-xl border flex items-start space-x-2.5 ${
              feedback.type === "success" 
                ? "bg-emerald-950/50 border-emerald-700/60 text-emerald-300" 
                : "bg-amber-950/50 border-amber-700/60 text-amber-300"
            }`}>
              {feedback.type === "success" ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              )}
              <div className="text-xs leading-relaxed">{feedback.text}</div>
            </div>
          )}

          {/* Active Store Card */}
          <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Active Storage Layer</span>
              <div className={`flex items-center space-x-1.5 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold ${
                isAuraConnected 
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30" 
                  : "bg-sky-500/10 text-sky-400 border border-sky-500/30"
              }`}>
                <span className={`w-1.5 h-1.5 rounded-full ${isAuraConnected ? "bg-emerald-400 animate-pulse" : "bg-sky-400"}`}></span>
                <span>{isAuraConnected ? "AURA CLOUD CONNECTED" : "LOCAL GRAPH STORE ACTIVE"}</span>
              </div>
            </div>

            <div className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
              {isAuraConnected ? (
                <Server className="w-4 h-4 text-emerald-400" />
              ) : (
                <HardDrive className="w-4 h-4 text-sky-400" />
              )}
              <span>{dbStatus?.active_store || "LocalGraphStore (JSON Storage)"}</span>
            </div>

            {/* Local Repository Stats */}
            {dbStatus?.repository_stats && (
              <div className="grid grid-cols-3 gap-2 pt-1 border-t border-slate-850">
                <div className="p-2 rounded bg-slate-900/60 text-center">
                  <div className="text-slate-400 text-[10px] font-mono uppercase">Triplets</div>
                  <div className="text-cyan-400 font-bold font-mono text-sm mt-0.5">{dbStatus.repository_stats.triplets_count}</div>
                </div>
                <div className="p-2 rounded bg-slate-900/60 text-center">
                  <div className="text-slate-400 text-[10px] font-mono uppercase">Entities</div>
                  <div className="text-emerald-400 font-bold font-mono text-sm mt-0.5">{dbStatus.repository_stats.entities_count}</div>
                </div>
                <div className="p-2 rounded bg-slate-900/60 text-center">
                  <div className="text-slate-400 text-[10px] font-mono uppercase">Videos</div>
                  <div className="text-purple-400 font-bold font-mono text-sm mt-0.5">{dbStatus.repository_stats.videos_count}</div>
                </div>
              </div>
            )}
          </div>

          {/* Connect Form */}
          <form onSubmit={handleConnect} className="space-y-3 bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono text-slate-300 font-bold">Connect Neo4j Instance</span>
              <span className="text-[10px] font-mono text-slate-500">Aura or Local bolt</span>
            </div>

            <div>
              <label className="block text-[11px] font-mono text-slate-400 mb-1">Neo4j URI</label>
              <input
                type="text"
                value={uri}
                onChange={(e) => setUri(e.target.value)}
                placeholder="neo4j+s://xxxx.databases.neo4j.io or bolt://localhost:7687"
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 font-mono focus:border-cyan-500 outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="neo4j"
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 font-mono focus:border-cyan-500 outline-none"
                />
              </div>
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Instance password"
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 font-mono focus:border-cyan-500 outline-none"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-100 font-bold text-xs transition-colors flex items-center justify-center space-x-2 border border-slate-700"
            >
              {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin text-cyan-400" /> : <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />}
              <span>{loading ? "Testing Connection..." : "Test & Connect to Neo4j"}</span>
            </button>
          </form>

          {/* Sync Action */}
          <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between">
            <div className="space-y-0.5">
              <div className="text-xs font-bold text-slate-200">Push Local Data to Aura</div>
              <div className="text-[11px] text-slate-400">Sync all {dbStatus?.repository_stats?.triplets_count || 648} triplets & entities to cloud DB</div>
            </div>
            <button
              type="button"
              onClick={handleSync}
              disabled={syncing}
              className="px-3 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition-colors flex items-center space-x-1.5 shadow-sm shadow-emerald-600/20"
            >
              {syncing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Database className="w-3.5 h-3.5" />}
              <span>{syncing ? "Syncing..." : "Sync to Aura"}</span>
            </button>
          </div>

          <div className="text-[11px] text-slate-500 leading-normal">
            💡 <strong>Offline Guarantee:</strong> When Neo4j Aura is paused or unreachable, V-LKG seamlessly operates on the integrated local JSON graph store with zero interruption.
          </div>
        </div>
      </div>
    </div>
  );
}
