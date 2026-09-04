import React, { useState, useEffect, useRef } from "react";
import { 
  Mic, Square, Sparkles, Brain, Check, RefreshCw, Upload, 
  CheckCircle2, ArrowRight, PlayCircle, Volume2
} from "lucide-react";
import { liveExtractEntities, processVoiceRecording } from "../services/api";

const PRESET_INTELLIGENCE_LENSES = [
  { id: "executive", name: "Executive", color: "#6366f1" },
  { id: "sales", name: "Sales", color: "#10b981" },
  { id: "learning", name: "Learning", color: "#f59e0b" },
  { id: "engineering", name: "R&D/AI", color: "#3b82f6" },
  { id: "thought_leadership", name: "Leadership", color: "#14b8a6" }
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
    // Helpful simulation button for demonstration/testing
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
    <div className="p-4 space-y-5 pb-40 max-w-2xl mx-auto animate-fade-in">
      {/* Studio Header */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-rose-950/80 via-slate-900 to-indigo-950/60 border border-rose-500/30 p-5 shadow-2xl">
        <div className="flex items-center space-x-2 text-rose-400 text-xs font-bold uppercase tracking-wider mb-1">
          <Mic className="w-4 h-4 animate-pulse" />
          <span>Live Voice & Entity Extraction Studio</span>
        </div>
        <h2 className="text-lg font-black text-white">Record Speech & Stream Live Entities</h2>
        <p className="text-xs text-slate-300 mt-1">
          Speak your insights. Discovered entities, competencies, and concepts appear in real-time and ingest directly into <strong className="text-white">{activeApp?.name}</strong>.
        </p>
      </div>

      {/* Main Recording Console */}
      <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl flex flex-col items-center justify-center space-y-4">
        {/* Timer */}
        <div className="text-3xl font-mono font-bold text-white tracking-widest">
          {formatTime(recordingTime)}
        </div>

        {/* Dynamic Waveform Visualizer */}
        <div className="flex items-center space-x-1.5 h-12">
          {[...Array(16)].map((_, i) => (
            <div
              key={i}
              className={`w-1.5 rounded-full transition-all duration-150 ${
                isRecording 
                  ? "bg-gradient-to-t from-rose-500 to-pink-400 animate-pulse" 
                  : "bg-slate-800 h-2"
              }`}
              style={{
                height: isRecording ? `${Math.max(8, Math.sin(i + recordingTime * 2) * 36 + 12)}px` : '6px'
              }}
            />
          ))}
        </div>

        {/* Record / Stop Button */}
        <div className="flex items-center space-x-4 pt-2">
          {!isRecording ? (
            <button
              onClick={startRecording}
              className="flex items-center space-x-2 px-6 py-3 rounded-full bg-gradient-to-r from-rose-500 to-pink-600 hover:from-rose-600 hover:to-pink-700 text-white font-bold text-sm shadow-lg shadow-rose-500/30 transition-all active:scale-95"
            >
              <Mic className="w-5 h-5" />
              <span>Start Recording</span>
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="flex items-center space-x-2 px-6 py-3 rounded-full bg-slate-800 hover:bg-slate-750 text-rose-400 border border-rose-500/40 font-bold text-sm shadow-lg transition-all active:scale-95"
            >
              <Square className="w-4 h-4 fill-rose-400" />
              <span>Stop Recording</span>
            </button>
          )}

          <button
            onClick={handleSimulateSpeech}
            className="px-3.5 py-2 rounded-2xl bg-slate-800 hover:bg-slate-750 text-slate-400 hover:text-white text-xs font-semibold border border-slate-700 transition-colors"
            title="Load sample leadership speech"
          >
            Simulate Speech
          </button>
        </div>
      </div>

      {/* Real-time Streaming Transcript */}
      <div className="space-y-2">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
          <Volume2 className="w-3.5 h-3.5 text-indigo-400" />
          <span>Real-Time Live Transcript</span>
        </h4>
        <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 min-h-[90px] text-xs text-slate-200 leading-relaxed">
          {transcript || (
            <span className="text-slate-500 italic">
              Spoken words will appear here in real-time as you record...
            </span>
          )}
        </div>
      </div>

      {/* LIVE ENTITY EXTRACTION FEED */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center space-x-1.5">
            <Sparkles className="w-4 h-4 text-rose-400 animate-spin" />
            <span>Live Entity Extraction ({liveEntities.length})</span>
          </h4>
          <span className="text-[10px] text-slate-500">Discovered in real-time</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {liveEntities.length > 0 ? (
            liveEntities.map((ent, idx) => (
              <div
                key={idx}
                className="p-3 rounded-2xl bg-slate-850 border border-slate-700/80 shadow-md animate-fade-in flex flex-col justify-between space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <span
                    className="text-[9px] px-1.5 py-0.2 rounded font-bold uppercase"
                    style={{ backgroundColor: `${ent.color}25`, color: ent.color }}
                  >
                    {ent.type}
                  </span>
                  <span className="text-[9px] text-slate-400">{ent.detected_at}</span>
                </div>
                <h5 className="text-xs font-bold text-white truncate">{ent.name}</h5>
                <div className="flex flex-wrap gap-1">
                  {ent.intelligences?.slice(0, 2).map((dom) => (
                    <span key={dom} className="text-[8px] text-slate-400 bg-slate-800 px-1 py-0.2 rounded">
                      {dom}
                    </span>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-full py-6 text-center text-slate-500 text-xs border border-dashed border-slate-800 rounded-2xl">
              Entities discovered while speaking will pop up here dynamically!
            </div>
          )}
        </div>
      </div>

      {/* Ingestion & Save Section */}
      {transcript && (
        <div className="p-4 rounded-3xl bg-slate-900 border border-slate-800 space-y-3.5 animate-slide-up">
          <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-400">
            Ingest into Linear Words & Entities
          </h4>

          <div>
            <label className="block text-[11px] font-semibold text-slate-400 mb-1">Recording Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Executive 1-on-1 Feedback Session..."
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-400 mb-1.5">Intelligence Lenses</label>
            <div className="flex flex-wrap gap-1.5">
              {PRESET_INTELLIGENCE_LENSES.map((lens) => {
                const active = selectedLenses.includes(lens.id);
                return (
                  <button
                    key={lens.id}
                    onClick={() => toggleLens(lens.id)}
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
            onClick={handleSaveToGraph}
            disabled={isProcessing}
            className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white text-xs font-bold shadow-lg shadow-indigo-500/25 transition-all flex items-center justify-center space-x-2"
          >
            {isProcessing ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : saveSuccess ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Ingested & Assigned to {activeApp?.name}!</span>
              </>
            ) : (
              <>
                <Brain className="w-4 h-4" />
                <span>Process & Ingest into {activeApp?.name}</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
