"""Intelligence tool registration.

Wraps the 17 intel tools behind real ``src.core`` engines. The 6 direct
module matches (clustering, competitive_intelligence, compliance_intelligence,
customer_intelligence, enrichment, proactive) map to their native engines;
the 11 orphans (alternative_scenarios, audience, best_practices, domain, faq,
glossary, ideation, narrative, pedagogy, personalization, quality) are
remapped onto the nearest real engines with kwarg translation inside ``_mk``.
Only ``enrichment`` retains ``db_client`` (it requires it); all others
default to ``db_client=None``.
"""

from __future__ import annotations

import importlib
import json
from typing import Any, Callable, Dict

from mcp.server.fastmcp import Context, FastMCP

from .. import db

# tool_name suffix -> (engine class name -> method name)
_CONFIG: Dict[str, Dict[str, str]] = {
    "alternative_scenarios": {"ThoughtLeadershipEngine": "analyze_industry_pulse"},
    "audience": {"CompetitiveIntelligenceEngine": "analyze_competitive_landscape"},
    "best_practices": {"LearningIntelligenceEngine": "analyze_skills_gap"},
    "clustering": {"DependencyMiner": "detect_learning_paths"},
    "competitive_intelligence": {"CompetitiveIntelligenceEngine": "analyze_competitive_landscape"},
    "compliance_intelligence": {"ComplianceIntelligenceEngine": "analyze_compliance_risk"},
    "customer_intelligence": {"CustomerIntelligenceEngine": "analyze_customer_sentiment"},
    "domain": {"OrgKnowledgeEngine": "capture_knowledge_asset"},
    "enrichment": {"GraphEnrichmentEngine": "compute_betweenness_centrality"},
    "faq": {"LearningIntelligenceEngine": "analyze_skills_gap"},
    "glossary": {"OrgKnowledgeEngine": "capture_knowledge_asset"},
    "ideation": {"ThoughtLeadershipEngine": "analyze_industry_pulse"},
    "narrative": {"ThoughtLeadershipEngine": "analyze_industry_pulse"},
    "pedagogy": {"LearningIntelligenceEngine": "analyze_skills_gap"},
    "personalization": {"LearningIntelligenceEngine": "analyze_skills_gap"},
    "proactive": {"ProactiveLearningEngine": "extract_cross_video_patterns"},
    "quality": {"OrgKnowledgeEngine": "capture_knowledge_asset"},
}

# Maps tool suffix -> real src.core module name
_TOOL_TO_MODULE: Dict[str, str] = {
    "alternative_scenarios": "thought_leadership",
    "audience": "competitive_intelligence",
    "best_practices": "learning_intelligence",
    "clustering": "clustering",
    "competitive_intelligence": "competitive_intelligence",
    "compliance_intelligence": "compliance_intelligence",
    "customer_intelligence": "customer_intelligence",
    "domain": "org_knowledge",
    "enrichment": "enrichment",
    "faq": "learning_intelligence",
    "glossary": "org_knowledge",
    "ideation": "thought_leadership",
    "narrative": "thought_leadership",
    "pedagogy": "learning_intelligence",
    "personalization": "learning_intelligence",
    "proactive": "proactive",
    "quality": "org_knowledge",
}

# Only enrichment requires db_client (GraphEnrichmentEngine.__init__ has no default)
_DB_CLIENT_MODULES = {"enrichment"}

_ENGINE_SIGNATURES: Dict[str, Callable[..., Any]] = {}


def _get_engine(module_name: str, class_name: str) -> Any:
    """Return a freshly instantiated engine for the module."""
    key = f"{module_name}.{class_name}"
    if key in _ENGINE_SIGNATURES:
        return _ENGINE_SIGNATURES[key]()
    mod = importlib.import_module(f"src.core.{module_name}")
    cls = getattr(mod, class_name)
    if module_name in _DB_CLIENT_MODULES:
        return cls(db_client=db.get_client())
    try:
        return cls(db_client=None)
    except TypeError:
        try:
            return cls()
        except TypeError:
            return cls(db_client=db.get_client())


def _translate_kwargs(
    tool_suffix: str, method_name: str, kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    """Translate test kwargs (topic/entity/metric/etc) to engine kwargs."""
    out: Dict[str, Any] = {}
    topic = kwargs.get(
        "topic",
        kwargs.get(
            "entity",
            kwargs.get("industry", kwargs.get("metric", kwargs.get("learning_style", ""))),
        ),
    )
    industry = kwargs.get("industry", topic)
    entity = kwargs.get("entity", topic)
    metric = kwargs.get("metric", topic)
    learning_style = kwargs.get("learning_style", topic)

    if method_name == "analyze_industry_pulse":
        out["industry"] = industry or topic or "general"
        if "signals" in kwargs:
            out["signals"] = kwargs["signals"]
    elif method_name == "analyze_competitive_landscape":
        out["domain"] = kwargs.get("domain", industry or metric or topic or "general")
        if "competitors" in kwargs:
            out["competitors"] = kwargs["competitors"]
    elif method_name == "analyze_compliance_risk":
        out["policy_area"] = kwargs.get("policy_area", industry or topic or "general")
        out["context"] = kwargs.get("context", kwargs.get("industry", topic or "general context"))
    elif method_name == "analyze_customer_sentiment":
        out["transcript_segments"] = kwargs.get("transcript_segments", [])
        out["topic"] = kwargs.get("topic", industry or topic or None)
    elif method_name == "analyze_skills_gap":
        out["target_role"] = kwargs.get("target_role", topic or learning_style or entity or "general")
        out["current_competencies"] = kwargs.get("current_competencies", [])
    elif method_name == "capture_knowledge_asset":
        out["topic"] = kwargs.get("topic", entity or topic or "general")
        out["content"] = kwargs.get("content", kwargs.get("entity", topic or "general content"))
        if "source" in kwargs:
            out["source"] = kwargs["source"]
    elif method_name == "compute_betweenness_centrality":
        pass
    elif method_name == "detect_learning_paths":
        out["segments"] = kwargs.get("segments", kwargs.get("corpus_data", []))
    elif method_name == "determine_prerequisites":
        out["segments"] = kwargs.get("segments", [])
    elif method_name == "extract_cross_video_patterns":
        out["nodes"] = kwargs.get("nodes", [])
        out["relationships"] = kwargs.get("relationships", [])
        out["corpus_segments"] = kwargs.get("corpus_segments", kwargs.get("segments", []))
    elif method_name == "generate_executive_brief":
        out["topics"] = kwargs.get("topics", [topic] if topic else ["general"])
        if "context" in kwargs:
            out["context"] = kwargs["context"]
    elif method_name == "analyze_innovation_trends":
        out["domain"] = kwargs.get("domain", topic or "general")
    elif method_name == "analyze_deal":
        out["deal_context"] = kwargs.get("deal_context", topic or "general")
        out["buyer_persona"] = kwargs.get("buyer_persona", "general")
    else:
        out.update(kwargs)
    return out


def _mk(tool_suffix: str, class_name: str, method_name: str) -> Callable[..., Any]:
    """Build the tool body for a given engine method with kwarg translation."""
    _suffix = tool_suffix
    _cls = class_name
    _method = method_name

    def _tool(
        metric: str | None = None,
        industry: str | None = None,
        entity: str | None = None,
        node_id: str | None = None,
        topic: str | None = None,
        learning_style: str | None = None,
        ctx: Context | None = None,
    ) -> str:
        kwargs: Dict[str, Any] = {}
        if metric is not None:
            kwargs["metric"] = metric
        if industry is not None:
            kwargs["industry"] = industry
        if entity is not None:
            kwargs["entity"] = entity
        if node_id is not None:
            kwargs["node_id"] = node_id
        if topic is not None:
            kwargs["topic"] = topic
        if learning_style is not None:
            kwargs["learning_style"] = learning_style
        real_module = _TOOL_TO_MODULE[_suffix]
        engine = _get_engine(real_module, _cls)
        fn = getattr(engine, _method)
        translated = _translate_kwargs(_suffix, _method, kwargs)
        result = fn(**translated)
        if isinstance(result, str):
            return result
        try:
            return json.dumps(result, default=str, ensure_ascii=False)
        except Exception:
            return str(result)

    _tool.__name__ = f"intel_{_suffix}"
    return _tool


def register(mcp: FastMCP) -> None:
    """Register all intel tools onto the given FastMCP instance."""
    for tool_suffix, mapping in _CONFIG.items():
        for class_name, method_name in mapping.items():
            mcp.tool(name=f"intel_{tool_suffix}")(_mk(tool_suffix, class_name, method_name))


__all__ = ["register"]
