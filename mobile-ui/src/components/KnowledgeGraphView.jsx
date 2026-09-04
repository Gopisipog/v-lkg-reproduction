import React, { useState, useEffect, useRef } from "react";
import { 
  Search, ZoomIn, ZoomOut, RotateCcw, Filter, 
  ExternalLink, PlayCircle, X, Sparkles, Brain
} from "lucide-react";
import { getAppGraph } from "../services/api";

const INTELLIGENCE_FILTERS = [
  { id: "all", label: "All Intelligence", color: "#6366f1" },
  { id: "executive", label: "Executive", color: "#6366f1" },
  { id: "sales", label: "Sales & Revenue", color: "#10b981" },
  { id: "learning", label: "Learning & Dev", color: "#f59e0b" },
  { id: "engineering", label: "R&D / AI", color: "#3b82f6" },
  { id: "compliance", label: "Governance", color: "#ef4444" },
  { id: "customer", label: "Customer", color: "#ec4899" },
  { id: "competitive", label: "Competitive", color: "#8b5cf6" },
  { id: "thought_leadership", label: "Leadership", color: "#14b8a6" }
];

export default function KnowledgeGraphView({ 
  activeApp, 
  onJumpToVideo 
}) {
  const canvasRef = useRef(null);
  const [graphData, setGraphData] = useState({ nodes: [], links: [], stats: {} });
  const [selectedLens, setSelectedLens] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedNode, setSelectedNode] = useState(null);
  const [loading, setLoading] = useState(true);

  // Canvas transform state
  const [transform, setTransform] = useState({ x: 0, y: 0, k: 1 });
  const isDragging = useRef(false);
  const dragStart = useRef({ x: 0, y: 0 });
  const nodePositions = useRef(new Map());

  // Load graph data
  useEffect(() => {
    if (!activeApp) return;
    setLoading(true);
    getAppGraph(activeApp.id, selectedLens)
      .then((data) => {
        setGraphData(data);
        initLayout(data.nodes, data.links);
      })
      .catch((err) => console.error("Graph load error:", err))
      .finally(() => setLoading(false));
  }, [activeApp, selectedLens]);

  // Initial circular/force-like layout simulation
  const initLayout = (nodes, links) => {
    const width = 600;
    const height = 500;
    const pos = new Map();
    const count = nodes.length || 1;

    nodes.forEach((node, i) => {
      const angle = (i / count) * 2 * Math.PI;
      const radius = 120 + (i % 3) * 60;
      pos.set(node.id, {
        x: width / 2 + Math.cos(angle) * radius + (Math.random() - 0.5) * 40,
        y: height / 2 + Math.sin(angle) * radius + (Math.random() - 0.5) * 40,
        vx: 0,
        vy: 0,
        radius: Math.max(14, Math.min(28, (node.centrality || 20) / 3))
      });
    });

    nodePositions.current = pos;
    setTransform({ x: 0, y: 0, k: 1 });
  };

  // Render loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let animationFrameId;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.save();
      ctx.translate(transform.x, transform.y);
      ctx.scale(transform.k, transform.k);

      const pos = nodePositions.current;

      // Draw Links
      ctx.lineWidth = 1.2;
      graphData.links.forEach((link) => {
        const sourcePos = pos.get(link.source);
        const targetPos = pos.get(link.target);
        if (sourcePos && targetPos) {
          ctx.beginPath();
          ctx.moveTo(sourcePos.x, sourcePos.y);
          ctx.lineTo(targetPos.x, targetPos.y);
          ctx.strokeStyle = "rgba(71, 85, 105, 0.4)";
          ctx.stroke();

          // Relation label
          const midX = (sourcePos.x + targetPos.x) / 2;
          const midY = (sourcePos.y + targetPos.y) / 2;
          ctx.font = "9px sans-serif";
          ctx.fillStyle = "rgba(148, 163, 184, 0.7)";
          ctx.textAlign = "center";
          ctx.fillText(link.relation, midX, midY - 3);
        }
      });

      // Draw Nodes
      graphData.nodes.forEach((node) => {
        const p = pos.get(node.id);
        if (!p) return;

        const isMatch = searchQuery && node.label.toLowerCase().includes(searchQuery.toLowerCase());
        const isSelected = selectedNode?.id === node.id;
        const nodeRadius = p.radius || 18;

        // Glow ring if selected or matching search
        if (isSelected || isMatch) {
          ctx.beginPath();
          ctx.arc(p.x, p.y, nodeRadius + 6, 0, 2 * Math.PI);
          ctx.fillStyle = isSelected ? "rgba(99, 102, 241, 0.35)" : "rgba(234, 179, 8, 0.3)";
          ctx.fill();
        }

        // Main circle
        ctx.beginPath();
        ctx.arc(p.x, p.y, nodeRadius, 0, 2 * Math.PI);
        ctx.fillStyle = node.color || "#6366f1";
        ctx.fill();
        ctx.lineWidth = isSelected ? 3 : 1.5;
        ctx.strokeStyle = isSelected ? "#ffffff" : "rgba(255, 255, 255, 0.6)";
        ctx.stroke();

        // Node Label
        ctx.font = `bold ${Math.max(10, 11 / transform.k)}px sans-serif`;
        ctx.fillStyle = "#f8fafc";
        ctx.textAlign = "center";
        ctx.shadowColor = "rgba(0,0,0,0.8)";
        ctx.shadowBlur = 4;
        ctx.fillText(node.label, p.x, p.y + nodeRadius + 14);
        ctx.shadowBlur = 0;
      });

      ctx.restore();
      animationFrameId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(animationFrameId);
  }, [graphData, transform, selectedNode, searchQuery]);

  // Touch and mouse events
  const handlePointerDown = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const clientY = e.clientY || (e.touches && e.touches[0].clientY);

    const mouseX = (clientX - rect.left - transform.x) / transform.k;
    const mouseY = (clientY - rect.top - transform.y) / transform.k;

    // Check hit test on nodes
    let clickedNode = null;
    nodePositions.current.forEach((p, nodeId) => {
      const dist = Math.hypot(p.x - mouseX, p.y - mouseY);
      if (dist <= (p.radius || 18)) {
        clickedNode = graphData.nodes.find((n) => n.id === nodeId);
      }
    });

    if (clickedNode) {
      setSelectedNode(clickedNode);
    } else {
      isDragging.current = true;
      dragStart.current = { x: clientX - transform.x, y: clientY - transform.y };
    }
  };

  const handlePointerMove = (e) => {
    if (!isDragging.current) return;
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const clientY = e.clientY || (e.touches && e.touches[0].clientY);
    setTransform((prev) => ({
      ...prev,
      x: clientX - dragStart.current.x,
      y: clientY - dragStart.current.y
    }));
  };

  const handlePointerUp = () => {
    isDragging.current = false;
  };

  const zoom = (factor) => {
    setTransform((prev) => ({
      ...prev,
      k: Math.max(0.4, Math.min(3, prev.k * factor))
    }));
  };

  return (
    <div className="relative w-full h-[calc(100vh-120px)] bg-slate-950 flex flex-col overflow-hidden animate-fade-in">
      {/* Top Filter Bar */}
      <div className="absolute top-3 left-3 right-3 z-20 space-y-2">
        {/* Search & Stats Header */}
        <div className="flex items-center space-x-2 bg-slate-900/90 backdrop-blur-md p-2 rounded-2xl border border-slate-800 shadow-lg">
          <Search className="w-4 h-4 text-slate-400 ml-1 shrink-0" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search entities (e.g. Active Listening, GTM)..."
            className="w-full bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none"
          />
          {searchQuery && (
            <button onClick={() => setSearchQuery("")} className="text-slate-400 p-1">
              <X className="w-3.5 h-3.5" />
            </button>
          )}
          <div className="text-[10px] bg-slate-800 text-slate-300 px-2.5 py-1 rounded-xl font-semibold shrink-0 border border-slate-700">
            {graphData.nodes.length} Nodes
          </div>
        </div>

        {/* Intelligence Lens Pills */}
        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 no-scrollbar">
          {INTELLIGENCE_FILTERS.map((filter) => {
            const isSelected = selectedLens === filter.id;
            return (
              <button
                key={filter.id}
                onClick={() => setSelectedLens(filter.id)}
                className={`px-3 py-1 rounded-xl text-xs font-semibold whitespace-nowrap transition-all border shrink-0 ${
                  isSelected
                    ? "bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/30"
                    : "bg-slate-900/80 text-slate-400 border-slate-800 hover:text-white"
                }`}
              >
                {filter.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Floating Canvas Controls */}
      <div className="absolute right-4 bottom-24 z-20 flex flex-col space-y-2">
        <button
          onClick={() => zoom(1.25)}
          className="p-2.5 rounded-2xl bg-slate-900/90 text-slate-300 hover:text-white border border-slate-800 shadow-lg transition-transform active:scale-90"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => zoom(0.8)}
          className="p-2.5 rounded-2xl bg-slate-900/90 text-slate-300 hover:text-white border border-slate-800 shadow-lg transition-transform active:scale-90"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={() => setTransform({ x: 0, y: 0, k: 1 })}
          className="p-2.5 rounded-2xl bg-slate-900/90 text-slate-300 hover:text-white border border-slate-800 shadow-lg transition-transform active:scale-90"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* Canvas */}
      <div className="w-full h-full cursor-grab active:cursor-grabbing">
        {loading ? (
          <div className="w-full h-full flex flex-col items-center justify-center space-y-3">
            <div className="w-8 h-8 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-xs text-slate-400">Loading scoped knowledge graph...</p>
          </div>
        ) : (
          <canvas
            ref={canvasRef}
            width={window.innerWidth > 640 ? 700 : window.innerWidth}
            height={window.innerHeight - 140}
            onMouseDown={handlePointerDown}
            onMouseMove={handlePointerMove}
            onMouseUp={handlePointerUp}
            onTouchStart={handlePointerDown}
            onTouchMove={handlePointerMove}
            onTouchEnd={handlePointerUp}
            className="w-full h-full block"
          />
        )}
      </div>

      {/* Node Inspector Bottom Sheet */}
      {selectedNode && (
        <div className="absolute bottom-16 left-3 right-3 z-30 bg-slate-900/95 backdrop-blur-md border border-slate-700/90 rounded-3xl p-4 shadow-2xl animate-slide-up">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <div
                className="w-8 h-8 rounded-xl flex items-center justify-center text-white font-bold text-xs"
                style={{ backgroundColor: selectedNode.color || "#6366f1" }}
              >
                {selectedNode.type?.[0] || "C"}
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">{selectedNode.label}</h4>
                <div className="flex items-center space-x-2 text-[11px] text-slate-400">
                  <span>Type: <strong className="text-slate-200">{selectedNode.type}</strong></span>
                  <span>·</span>
                  <span>Centrality: <strong className="text-indigo-400">{selectedNode.centrality}%</strong></span>
                </div>
              </div>
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="p-1 rounded-full bg-slate-800 text-slate-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Timestamps & Video Citations */}
          <div className="mt-3 pt-2.5 border-t border-slate-800">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5 block">
              Observed Video Timestamps ({selectedNode.timestamps?.length || 0})
            </span>
            <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
              {selectedNode.timestamps?.map((ts, idx) => (
                <button
                  key={idx}
                  onClick={() => onJumpToVideo(ts.video_id, ts.time)}
                  className="flex items-center space-x-1.5 px-2.5 py-1 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs font-semibold transition-all active:scale-95"
                >
                  <PlayCircle className="w-3 h-3 text-indigo-400" />
                  <span>Jump [{ts.time}]</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
