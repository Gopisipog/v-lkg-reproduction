"""Canonical entity registry for the V-LKG knowledge graph.

Single source of truth for entity TYPE -> color mapping, shared by
ingestion (extractor / enrichment) and every intelligence engine so that
color-coded, extracted + enriched entities are available uniformly across
all intelligence domains.

Both the local JSON store (LocalGraphStore) and Neo4j persist a
`color` property on every node via this registry.
"""

# ── Canonical entity colors ────────────────────────────────────────────────
# Ingestion / knowledge-graph core types
ENTITY_COLORS = {
    # Core knowledge-graph types (extracted at ingestion time)
    "Competency": "#2196F3",
    "Concept": "#4CAF50",
    "Outcome": "#FF9800",
    "Personality": "#9C27B0",
    "Strategy": "#FF5722",
    "Tactic": "#E91E63",
    "Path": "#00BCD4",
    "Object": "#795548",
    # Intelligence domain types (produced by the cross-domain pipeline)
    "IntelligenceDomain": "#7C4DFF",
    "CompetitiveTopic": "#E040FB",
    "Threat": "#FF1744",
    "Competitor": "#C2185B",
    "MarketOpportunity": "#00E676",
    "BuyerSignal": "#FF9100",
    "DealTheme": "#FF6D00",
    "PolicyTopic": "#2979FF",
    "Risk": "#D50000",
    "Control": "#5D4037",
    "EmergingTrend": "#00B8D4",
    "Innovation": "#00E5FF",
    "CustomerTheme": "#FF4081",
    "PainPoint": "#FF1744",
    "ExecutiveTheme": "#651FFF",
    "Decision": "#1DE9B6",
    "KnowledgeConcept": "#00BFA5",
    "BestPractice": "#64DD17",
    "KnowledgeGap": "#FFAB00",
    "Narrative": "#6200EA",
    "ThoughtLeader": "#C51162",
    "Expertise": "#00897B",
    "ContentGap": "#FF9100",
    "SkillGap": "#FF3D00",
    # Perspetives / interview / proactive helper types
    "Perspective": "#FF6E40",
    "Question": "#3D5AFE",
    "KeyTerm": "#00897B",
    "QAPair": "#FBC02D",
    # Fallback
    "Entity": "#607D8B",
    "KnowledgeBase": "#37474F",
}


def canonical_color(entity_type):
    """Return the canonical hex color for an entity type.

    Falls back to a neutral blue for unknown types so every entity
    rendered in any intelligence tab always has a color.
    """
    if not entity_type:
        return ENTITY_COLORS["Entity"]
    return ENTITY_COLORS.get(str(entity_type), ENTITY_COLORS["Entity"])


def register_color(entity_type):
    """Convenience accessor mirroring canonical_color."""
    return canonical_color(entity_type)


def render_pill(name, entity_type=None, color=None):
    """Return an HTML pill span for a color-coded entity."""
    if color is None:
        color = canonical_color(entity_type)
    safe = (name or "").replace("<", "&lt;").replace(">", "&gt;")
    return (
        f"<span style='background:{color};color:white;padding:2px 10px;"
        f"border-radius:12px;font-size:0.82em;margin:2px;display:inline-block'>"
        f"{safe}</span>"
    )
