"""Standalone FastAPI Application for CineGraph Studio.

Provides an independent REST API and interactive Web Dashboard for the
Google Cloud Agentic Cinema Hackathon.
"""

import os
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from cinegraph_studio.orchestrator import CineGraphOrchestrator
from cinegraph_studio.mcp.tools import STUDIO_MCP_TOOLS
from cinegraph_studio.config import HOST, PORT, PROJECT_NAME, HACKATHON_TRACK

app = FastAPI(
    title=PROJECT_NAME,
    description="Autonomous Multi-Agent Cinema Production Platform powered by Google Cloud Gemini and Parallel Web Systems.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = CineGraphOrchestrator()


# ── Pydantic Request Models ──────────────────────────────────────────

class AnalyzeSceneRequest(BaseModel):
    video_id: str
    scene_title: str
    transcript_text: str
    start_time: Optional[float] = 0.0
    end_time: Optional[float] = 60.0
    period_setting: Optional[str] = "Contemporary"
    genre: Optional[str] = "Drama"


class CompsRequest(BaseModel):
    genre: str
    logline: str


class PeriodVerifyRequest(BaseModel):
    claim: str
    period: str


class ClearanceRequest(BaseModel):
    entity_name: str
    entity_type: Optional[str] = "Brand"


class CopilotRequest(BaseModel):
    query: str
    scene_context: Optional[str] = None


# ── REST API Endpoints ───────────────────────────────────────────────

@app.get("/api/status")
def get_status():
    """System health check verifying Google Cloud Gemini & Parallel Web Systems."""
    return orchestrator.get_status()


@app.post("/api/analyze-scene")
def analyze_scene(req: AnalyzeSceneRequest):
    """Execute complete multi-agent scene analysis and dossier generation."""
    return orchestrator.produce_scene_dossier(
        video_id=req.video_id,
        scene_title=req.scene_title,
        transcript_text=req.transcript_text,
        start_time=req.start_time or 0.0,
        end_time=req.end_time or 60.0,
        period_setting=req.period_setting or "Contemporary",
        genre=req.genre or "Drama"
    )


@app.post("/api/comps")
def get_comps(req: CompsRequest):
    """Fetch box office comparables and audience retention metrics via Parallel Search."""
    return orchestrator.producer.evaluate_budget_and_comps(req.genre, req.logline)


@app.post("/api/verify-period")
def verify_period(req: PeriodVerifyRequest):
    """Fact-check period dialogue against open-web archival records via Parallel Search."""
    return orchestrator.parallel.verify_period_authenticity(req.claim, req.period)


@app.post("/api/clearance")
def check_clearance(req: ClearanceRequest):
    """Scan trademark and copyright clearance status via Parallel Search."""
    return orchestrator.producer.check_rights_and_clearances(req.entity_name, req.entity_type or "Brand")


@app.post("/api/copilot")
def ask_copilot(req: CopilotRequest):
    """Consult the CineGraph Studio Co-Pilot, grounded by Parallel Web Systems."""
    return orchestrator.ask_copilot(req.query, req.scene_context)


@app.get("/api/mcp/tools")
def list_mcp_tools():
    """List available managed MCP tools for enterprise agent networks."""
    return [
        {"name": t["name"], "description": t["description"]}
        for t in STUDIO_MCP_TOOLS
    ]


# ── Serve Standalone Cinematic Web Cockpit ───────────────────────────

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    @app.get("/")
    def serve_dashboard():
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "CineGraph Studio API is running."}


def start_server():
    import uvicorn
    uvicorn.run("cinegraph_studio.server:app", host=HOST, port=PORT, reload=False)


if __name__ == "__main__":
    start_server()
