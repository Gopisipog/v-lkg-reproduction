"""Standalone test suite for CineGraph Studio.

Validates:
1. Google Cloud Gemini Enterprise compliance (Rule 7.B)
2. Parallel Web Systems (parallel-web SDK) partner integration
3. Three-agent network (Director, Producer, Studio Head)
4. Managed MCP tool definitions
5. Standalone FastAPI REST endpoints
"""

import pytest
from fastapi.testclient import TestClient

from cinegraph_studio.integrations.parallel_client import ParallelStudioClient
from cinegraph_studio.agents.director import VisionaryDirectorAgent
from cinegraph_studio.agents.producer import TechnicalProducerAgent
from cinegraph_studio.agents.studio_head import StudioHeadAgent
from cinegraph_studio.orchestrator import CineGraphOrchestrator
from cinegraph_studio.mcp.tools import (
    STUDIO_MCP_TOOLS,
    tool_analyze_scene,
    tool_search_boxoffice_comps,
    tool_verify_period_authenticity,
    tool_clearance_scan,
    tool_studio_head_audit
)
from cinegraph_studio.server import app


# ── 1. Google Cloud Compliance (Rule 7.B) ────────────────────────────

def test_pure_google_ai_compliance():
    """Verify strictly zero imports or fallbacks to OpenAI, Anthropic, or DeepSeek."""
    import inspect
    import cinegraph_studio.agents.director as dir_mod
    import cinegraph_studio.orchestrator as orch_mod
    import cinegraph_studio.config as cfg_mod

    combined_source = (
        inspect.getsource(dir_mod) +
        inspect.getsource(orch_mod) +
        inspect.getsource(cfg_mod)
    ).lower()

    assert "openai" not in combined_source
    assert "anthropic" not in combined_source
    assert "deepseek" not in combined_source


# ── 2. Parallel Web Systems Integration ──────────────────────────────

def test_parallel_client_search():
    client = ParallelStudioClient()
    res = client.search_live("theatrical box office trends 2026", max_results=2)
    assert "results" in res
    assert len(res["results"]) > 0


def test_parallel_verify_period_authenticity():
    client = ParallelStudioClient()
    res = client.verify_period_authenticity(
        scene_claim="We need to deploy automated continuous deployment pipelines",
        period_setting="1920s Prohibition Era"
    )
    assert res["verified"] is True
    assert "authenticity_score" in res
    assert "sources" in res


def test_parallel_boxoffice_comps():
    client = ParallelStudioClient()
    res = client.fetch_boxoffice_comps("Sci-Fi Thriller", "A team of researchers trapped in an undersea habitat.")
    assert "comps" in res
    assert len(res["comps"]) >= 2
    assert "budget" in res["comps"][0]


def test_parallel_ip_clearance():
    client = ParallelStudioClient()
    # Test high risk brand
    res_risky = client.ip_and_rights_clearance("Ferrari 488 Pista", "Automotive Brand")
    assert res_risky["risk_level"] == "HIGH"
    assert res_risky["clearance_status"] == "FLAGGED_FOR_LEGAL_REVIEW"

    # Test generic public domain term
    res_safe = client.ip_and_rights_clearance("Vintage Pocket Watch", "Prop")
    assert res_safe["risk_level"] == "LOW"
    assert res_safe["clearance_status"] == "APPROVED_PUBLIC_USE"


# ── 3. Multi-Agent Personas ──────────────────────────────────────────

def test_director_agent_beat_detection():
    director = VisionaryDirectorAgent()
    breakdown = director.analyze_scene_beats(
        scene_title="Climactic Confrontation",
        transcript_text="Dr. Vance: The reactor core is destabilizing. Marcus: Then stabilize it, or none of us leave.",
        start_time=120.0,
        end_time=185.0
    )
    assert breakdown["scene_title"] == "Climactic Confrontation"
    assert "dramatic_beats" in breakdown
    assert len(breakdown["dramatic_beats"]) >= 2
    assert "characters" in breakdown
    assert "staging_notes" in breakdown


def test_producer_agent_pipeline():
    producer = TechnicalProducerAgent()
    context = producer.build_scene_intelligence_context(
        scene_title="Hangar Briefing",
        transcript_text="The stealth prototype utilizes carbon-nanotube composite plating.",
        period_setting="Near-Future 2030",
        genre="Military Action"
    )
    assert context["producer_status"] == "READY"
    assert "fact_checking" in context
    assert "boxoffice_comps" in context
    assert "clearance_reports" in context


def test_studio_head_governance():
    studio_head = StudioHeadAgent()
    director_packet = {"pacing": "Escalating"}
    producer_packet = {
        "fact_checking": {"authenticity_score": 0.95},
        "clearance_reports": [
            {"entity": "Generic Sedan", "risk_level": "LOW"}
        ]
    }
    decision = studio_head.audit_and_greenlight(director_packet, producer_packet)
    assert decision["studio_head_decision"] == "GREENLIT"
    assert decision["governance_status"] == "COMPLIANT_APPROVED"
    assert decision["iam_security_verification"]["least_privilege_enforced"] is True


# ── 4. Central Orchestrator ──────────────────────────────────────────

def test_orchestrator_produce_dossier():
    orchestrator = CineGraphOrchestrator()
    dossier = orchestrator.produce_scene_dossier(
        video_id="scene_001",
        scene_title="The Midnight Pitch",
        transcript_text="CEO: I am pulling the funding. Founder: You can't. We already launched the node network.",
        start_time=0.0,
        end_time=45.0,
        period_setting="Contemporary",
        genre="Drama"
    )
    assert dossier["video_id"] == "scene_001"
    assert "director_breakdown" in dossier
    assert "producer_intelligence" in dossier
    assert "studio_head_governance" in dossier
    assert dossier["production_ready"] is True


def test_orchestrator_copilot():
    orchestrator = CineGraphOrchestrator()
    copilot_res = orchestrator.ask_copilot(
        query="How should we light this scene to emphasize moral ambiguity?",
        scene_context="Dimly lit underground poker room"
    )
    assert "advice" in copilot_res
    assert "parallel_grounding" in copilot_res
    assert len(copilot_res["advice"]) > 30


# ── 5. Managed MCP Tools ─────────────────────────────────────────────

def test_mcp_tools_surface():
    assert len(STUDIO_MCP_TOOLS) == 5
    tool_names = [t["name"] for t in STUDIO_MCP_TOOLS]
    assert "studio_analyze_scene" in tool_names
    assert "studio_search_boxoffice_comps" in tool_names
    assert "studio_verify_period_authenticity" in tool_names
    assert "studio_clearance_scan" in tool_names
    assert "studio_head_audit" in tool_names


def test_mcp_tool_execution():
    res = tool_verify_period_authenticity("The telegraph arrived yesterday", "1885 Victorian Era")
    assert res["verified"] is True

    comps = tool_search_boxoffice_comps("Neo-Noir", "A detective uncovers a conspiracy in New Orleans")
    assert len(comps["comps"]) >= 2

    clearance = tool_clearance_scan("Coca-Cola bottle on the desk")
    assert clearance["risk_level"] == "HIGH"


# ── 6. Standalone FastAPI REST Endpoints ─────────────────────────────

@pytest.fixture
def client():
    return TestClient(app)


def test_endpoint_status(client):
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "Google Cloud" in data["primary_ai_model"]
    assert "Parallel" in data["hackathon_track"]


def test_endpoint_analyze_scene(client):
    payload = {
        "video_id": "test_vid_123",
        "scene_title": "Final Examination",
        "transcript_text": "Professor: Time is up. Put your pencils down. Student: Just give me thirty seconds.",
        "start_time": 10.0,
        "end_time": 70.0,
        "period_setting": "Contemporary",
        "genre": "Drama"
    }
    res = client.post("/api/analyze-scene", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["video_id"] == "test_vid_123"
    assert "director_breakdown" in data
    assert "studio_head_governance" in data


def test_endpoint_comps(client):
    res = client.post("/api/comps", json={"genre": "Heist", "logline": "A crew robs a diamond vault in Antwerp."})
    assert res.status_code == 200
    assert len(res.json()["comps"]) >= 2


def test_endpoint_verify_period(client):
    res = client.post("/api/verify-period", json={"claim": "We will dispatch the message by carrier pigeon", "period": "Ancient Rome"})
    assert res.status_code == 200
    assert res.json()["verified"] is True


def test_endpoint_clearance(client):
    res = client.post("/api/clearance", json={"entity_name": "Disney World Magic Kingdom", "entity_type": "Theme Park"})
    assert res.status_code == 200
    assert res.json()["risk_level"] == "HIGH"


def test_endpoint_copilot(client):
    res = client.post("/api/copilot", json={"query": "What lens focal length should we use for intense two-shots?"})
    assert res.status_code == 200
    assert "advice" in res.json()


def test_endpoint_mcp_tools(client):
    res = client.get("/api/mcp/tools")
    assert res.status_code == 200
    tools = res.json()
    assert len(tools) == 5
