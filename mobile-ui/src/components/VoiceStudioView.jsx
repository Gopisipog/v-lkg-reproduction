import React, { useState, useEffect, useRef } from "react";
import { 
  Mic, Square, Sparkles, Brain, Check, RefreshCw, Upload, 
  CheckCircle2, ArrowRight, PlayCircle, Volume2, Radio, Activity
} from "lucide-react";
import { motion } from "framer-motion";
import { liveExtractEntities, processVoiceRecording } from "../services/api";

const PRESET_INTELLIGENCE_LENSES = [
  { id: "executive", name: "Executive", color: "#0ea5e9" },
  { id: "sales", name: "Sales", color: "#10b981" },
  { id: "learning", name: "Learning", color: "#f59e0b" },
  { id: "engineering", name: "R&D/AI", color: "#38bdf8" },
  { id: "thought_leadership", name: "Leadership", color: "#06b6d4" }
];

export default function VoiceStudioView({ 
  activeApp, 
  onRecordingSaved 
}) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [transcript, setTranscript] = useState("");
  const [liveEntities, setLiveEntities] = useState([]);
  const [title, setTitle] = useState("");
  const [selectedLenses, setSelectedLenses] = useState(["executive", "thought_leadership", "learning"]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const recognitionRef = useRef(null);
  const timerRef = useRef(null);
  const lastExtractTextRef = useRef("");

  // Speech Recognition Setup
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = "en-US";

      recognition.onresult = (event) => {
        let currentText = "";
        for (let i = 0; i < event.results.length; i++) {
          currentText += event.results[i][0].transcript + " ";
        }
        setTranscript(currentText);

        // Trigger live entity extraction on new text
        if (currentText.length - lastExtractTextRef.current.length > 15) {
          lastExtractTextRef.current = currentText;
          extractLive(currentText);
        }
      };

      recognition.onerror = (event) => {
        console.warn("Speech recognition notice:", event.error);
      };

      recognitionRef.current = recognition;
    }
  }, []);

  const extractLive = async (text) => {
    try {
      const existingNames = liveEntities.map((e) => e.name);
      const newDiscovered = await liveExtractEntities(text, existingNames);
      if (newDiscovered && newDiscovered.length > 0) {
        setLiveEntities((prev) => [...prev, ...newDiscovered]);
      }
    } catch (err) {
      console.error("Live extraction error:", err);
    }
  };

  const startRecording = () => {
    setIsRecording(true);
    setSaveSuccess(false);
    setTranscript("");
    setLiveEntities([]);
    setRecordingTime(0);
    lastExtractTextRef.current = "";

    if (recognitionRef.current) {
      try {
        recognitionRef.current.start();
      } catch (e) {
        console.warn(e);
      }
    }

    timerRef.current = setInterval(() => {
      setRecordingTime((t) => t + 1);
    }, 1000);
  };

  const stopRecording = () => {
    setIsRecording(false);
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {
        console.warn(e);
      }
    }
    if (timerRef.current) clearInterval(timerRef.current);

    // Final entity sweep
    if (transcript) {
      extractLive(transcript);
    }
  };

  const handleSimulateSpeech = () => {
    // Simulation button for testing
    const sampleSpeech = "Effective executive leadership requires active listening, clear boundary setting, and time blocking. When we implement rapid feedback loops, team alignment improves and revenue growth follows.";
    setTranscript(sampleSpeech);
    extractLive(sampleSpeech);
  };

  const toggleLens = (lensId) => {
    if (selectedLenses.includes(lensId)) {
      if (selectedLenses.length > 1) {
        setSelectedLenses(selectedLenses.filter((l) => l !== lensId));
      }
    } else {
      setSelectedLenses([...selectedLenses, lensId]);
    }
  };

  const handleSaveToGraph = async () => {
    if (!transcript.trim()) {
      alert("Please record or speak some content first.");
      return;
    }

    setIsProcessing(true);
    try {
      const segments = [
        { start: 0, end: Math.max(recordingTime, 15), text: transcript.trim() }
      ];

      const res = await processVoiceRecording(
        title.trim() || `Voice Note - ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`,
        segments,
        activeApp?.id,
        selectedLenses
      );

      setSaveSuccess(true);
      if (onRecordingSaved) onRecordingSaved(res);
    } catch (err) {
      alert(err.message || "Failed to process voice recording");
    } finally {
      setIsProcessing(false);
    }
  };

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="p-3.5 space-y-3 pb-32 max-w-2xl mx-auto">
      {/* Cockpit Studio Telemetry Header */}
      <div className="rounded-xl bg-slate-900/90 border border-slate-800 p-4 shadow-xl">
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center space-x-2 text-rose-400 text-[10px] font-mono uppercase tracking-wider font-semibold">
            <Radio className="w-3.5 h-3.5 animate-pulse text-rose-400" />
            <span>Telemetry Voice Capture</span>
          </div>
          <span className="font-mono text-[10px] text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700/60">
            {activeApp?.name || "Global Scope"}
          </span>
        </div>
        <h2 className="text-sm font-semibold tracking-tight text-white">Live Voice & Entity Extraction</h2>
        <p className="text-[11px] text-slate-400 mt-0.5 leading-relaxed">
          Real-time spoken semantic parsing. Entities and relationships stream directly into the knowledge graph.
        </p>
      </div>

      {/* Main Recording Console */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-lg flex flex-col items-center justify-center space-y-3">
        {/* Monospace Timer */}
        <div className="text-2xl font-mono font-bold text-white tracking-widest tabular-nums">
          {formatTime(recordingTime)}
        </div>

        {/* Dynamic Waveform Visualizer */}
        <div className="flex items-center space-x-1.5 h-10">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className={`w-1 rounded-full transition-all duration-150 ${
                isRecording 
                  ? "bg-gradient-to-t from-rose-500 to-rose-400 animate-pulse" 
                  : "bg-slate-800 h-1.5"
              }`}
              style={{
                height: isRecording ? `${Math.max(6, Math.sin(i + recordingTime * 2) * 28 + 10)}px` : '4px'
              }}
            />
          ))}
        </div>

        {/* Record / Stop Button */}
        <div className="flex items-center space-x-3 pt-1">
          {!isRecording ? (
            <motion.button
              whileTap={{ scale: 0.95 }}
              transition={{ type: "spring", stiffness: 400, damping: 25 }}
              onClick={startRecording}
              className="flex items-center space-x-2 px-5 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs shadow-md shadow-rose-600/20 transition-all tactile-btn"
            >
              <Mic className="w-4 h-4" />
              <span>Start Recording</span>
            </motion.button>
          ) : (
            <motion.button
              whileTap={{ scale: 0.95 }}
              transition={{ type: "spring", stiffness: 400, damping: 25 }}
              onClick={stopRecording}
              className="flex items-center space-x-2 px-5 py-2 rounded-lg bg-slate-800 hover:bg-slate-750 text-rose-400 border border-rose-500/40 font-semibold text-xs shadow-md transition-all tactile-btn"
            >
              <Square className="w-3.5 h-3.5 fill-rose-400" />
              <span>Stop Recording</span>
            </motion.button>
          )}

          <motion.button
            whileTap={{ scale: 0.95 }}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
            onClick={handleSimulateSpeech}
            className="px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-800 text-slate-400 hover:text-white text-[11px] font-mono border border-slate-700/80 transition-colors tactile-btn"
            title="Load sample speech"
          >
            Simulate Input
          </motion.button>
        </div>
      </div>

      {/* Real-time Streaming Transcript */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <h4 className="text-[10px] font-mono uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
            <Volume2 className="w-3.5 h-3.5 text-sky-400" />
            <span>Telemetry Transcript Stream</span>
          </h4>
          <span className="text-[10px] font-mono text-slate-500">
            {transcript ? `${transcript.split(/\s+/).filter(Boolean).length} words` : "idle"}
          </span>
        </div>
        <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 min-h-[75px] text-xs text-slate-300 leading-relaxed font-sans">
          {transcript || (
            <span className="text-slate-500 italic text-[11px]">
              Audio waveform input will be decoded here in real-time...
            </span>
          )}
        </div>
      </div>

      {/* LIVE ENTITY EXTRACTION FEED */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h4 className="text-[10px] font-mono uppercase tracking-wider text-rose-400 flex items-center space-x-1.5">
            <Sparkles className="w-3.5 h-3.5 text-rose-400 animate-spin" />
            <span>Live Entity Stream ({liveEntities.length})</span>
          </h4>
          <span className="text-[10px] font-mono text-slate-500">streaming</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {liveEntities.length > 0 ? (
            liveEntities.map((ent, idx) => (
              <div
                key={idx}
                className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm flex flex-col justify-between space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <span
                    className="text-[9px] font-mono px-1.5 py-0.5 rounded uppercase font-semibold border"
                    style={{ 
                      backgroundColor: `${ent.color}15`, 
                      color: ent.color,
                      borderColor: `${ent.color}35`
                    }}
                  >
                    {ent.type}
                  </span>
                  <span className="text-[9px] font-mono text-slate-500">{ent.detected_at}</span>
                </div>
                <h5 className="text-xs font-semibold text-white truncate">{ent.name}</h5>
                <div className="flex flex-wrap gap-1">
                  {ent.intelligences?.slice(0, 2).map((dom) => (
                    <span key={dom} className="text-[8px] font-mono text-slate-400 bg-slate-800/80 px-1 py-0.2 rounded border border-slate-700/50">
                      {dom}
                    </span>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-full py-6 text-center text-slate-500 text-xs font-mono border border-dashed border-slate-800 rounded-xl bg-slate-900/30">
              Entities discovered while speaking stream here in real time
            </div>
          )}
        </div>
      </div>

      {/* Ingestion & Save Section */}
      {transcript && (
        <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3 shadow-lg">
          <h4 className="text-[10px] font-mono uppercase tracking-wider text-sky-400">
            Commit Spoken Content to Knowledge Graph
          </h4>

          <div>
            <label className="block text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1">Recording Identifier / Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Executive 1-on-1 Feedback Session..."
              className="w-full px-3 py-2 bg-slate-800/80 border border-slate-700 rounded-lg text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
            />
          </div>

          <div>
            <label className="block text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">Intelligence Lenses</label>
            <div className="flex flex-wrap gap-1.5">
              {PRESET_INTELLIGENCE_LENSES.map((lens) => {
                const active = selectedLenses.includes(lens.id);
                return (
                  <button
                    key={lens.id}
                    onClick={() => toggleLens(lens.id)}
                    className={`px-2.5 py-1 rounded-lg text-[10px] font-mono uppercase tracking-wider border transition-all tactile-btn ${
                      active ? "bg-sky-600/20 text-sky-300 border-sky-500/60 font-semibold" : "bg-slate-800/60 text-slate-400 border-slate-700/60"
                    }`}
                  >
                    {lens.name}
                  </button>
                );
              })}
            </div>
          </div>

          <motion.button
            whileTap={{ scale: 0.98 }}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
            onClick={handleSaveToGraph}
            disabled={isProcessing}
            className="w-full py-2.5 px-4 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold shadow-md shadow-sky-600/25 transition-all flex items-center justify-center space-x-2 tactile-btn disabled:opacity-50"
          >
            {isProcessing ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : saveSuccess ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-300" />
                <span className="font-mono text-[11px]">Ingested & Committed to {activeApp?.name}!</span>
              </>
            ) : (
              <>
                <Brain className="w-3.5 h-3.5" />
                <span className="font-mono text-[11px]">Process & Commit to {activeApp?.name}</span>
              </>
            )}
          </motion.button>
        </div>
      )}
    </div>
  );
}
