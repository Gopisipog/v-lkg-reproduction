"""Managed MCP (Model Context Protocol) tools for CineGraph Studio.

Exposes cinematic intelligence tools to agent networks and enterprise data pipelines.
"""

from typing import Dict, Any, List, Optional
from cinegraph_studio.orchestrator import CineGraphOrchestrator

_global_orchestrator: Optional[CineGraphOrchestrator] = None


def get_orchestrator() -> CineGraphOrchestrator:
    global _global_orchestrator
    if _global_orchestrator is None:
        _global_orchestrator = CineGraphOrchestrator()
    return _global_orchestrator


def tool_analyze_scene(
    video_id: str,
    scene_title: str,
    transcript_text: str,
    period_setting: str = "Contemporary",
    genre: str = "Drama"
) -> Dict[str, Any]:
    """MCP Tool: Complete multi-agent scene analysis and dossier production."""
    orchestrator = get_orchestrator()
    return orchestrator.produce_scene_dossier(
        video_id=video_id,
        scene_title=scene_title,
        transcript_text=transcript_text,
        period_setting=period_setting,
        genre=genre
    )


def tool_search_boxoffice_comps(genre: str, logline: str) -> Dict[str, Any]:
    """MCP Tool: Fetch real-world box office comps and audience metrics via Parallel Search."""
    orchestrator = get_orchestrator()
    return orchestrator.producer.evaluate_budget_and_comps(genre, logline)


def tool_verify_period_authenticity(claim: str, period: str) -> Dict[str, Any]:
    """MCP Tool: Fact-check historical claims and dialogue accuracy via Parallel Search."""
    orchestrator = get_orchestrator()
    return orchestrator.parallel.verify_period_authenticity(claim, period)


def tool_clearance_scan(entity_name: str, entity_type: str = "Brand") -> Dict[str, Any]:
    """MCP Tool: Scan trademark and copyright clearance via Parallel Search."""
    orchestrator = get_orchestrator()
    return orchestrator.producer.check_rights_and_clearances(entity_name, entity_type)


def tool_studio_head_audit(scene_title: str, transcript_text: str) -> Dict[str, Any]:
    """MCP Tool: Perform governance audit and grant production greenlight."""
    orchestrator = get_orchestrator()
    dossier = orchestrator.produce_scene_dossier(
        video_id="audit_check",
        scene_title=scene_title,
        transcript_text=transcript_text
    )
    return dossier.get("studio_head_governance", {})


STUDIO_MCP_TOOLS = [
    {
        "name": "studio_analyze_scene",
        "description": "Multi-agent breakdown of dramatic beats, character objectives, and Parallel comps.",
        "function": tool_analyze_scene
    },
    {
        "name": "studio_search_boxoffice_comps",
        "description": "Retrieve box office comparables and audience retention metrics using Parallel Web Systems.",
        "function": tool_search_boxoffice_comps
    },
    {
        "name": "studio_verify_period_authenticity",
        "description": "Fact-check screenplay dialogue against open-web archival records using Parallel Web Systems.",
        "function": tool_verify_period_authenticity
    },
    {
        "name": "studio_clearance_scan",
        "description": "Check trademark, brand, and IP clearance status using Parallel Web Systems.",
        "function": tool_clearance_scan
    },
    {
        "name": "studio_head_audit",
        "description": "Conduct enterprise governance audit and greenlight review.",
        "function": tool_studio_head_audit
    }
]
