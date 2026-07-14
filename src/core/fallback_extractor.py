"""Rule-based fallback extractor for when LLM APIs are unavailable.

Extracts leadership-domain entities from transcript text using keyword
dictionaries, pattern matching, and co-occurrence heuristics.  No external
API calls — runs entirely locally.
"""

import re
from typing import List, Dict

# ── domain keyword dictionaries ────────────────────────────────────────────
# Maps entity name (lowercased) -> entity type

_COMPETENCIES: Dict[str, str] = {
    # communication & presentations
    "active listening": "Competency",
    "communication": "Competency",
    "public speaking": "Competency",
    "presentation": "Competency",
    "storytelling": "Competency",
    "storyteller": "Competency",
    "persuasion": "Competency",
    "influence": "Competency",
    "engagement": "Competency",
    "audience engagement": "Competency",
    # emotional & interpersonal
    "empathy": "Competency",
    "vulnerability": "Competency",
    "self-awareness": "Competency",
    "emotional intelligence": "Competency",
    "emotional regulation": "Competency",
    "resilience": "Competency",
    "courage": "Competency",
    "confidence": "Competency",
    "authenticity": "Competency",
    "active listening": "Competency",
    "feedback": "Competency",
    "negotiation": "Competency",
    "conflict resolution": "Competency",
    "boundary setting": "Competency",
    "boundaries": "Competency",
    "setting boundaries": "Competency",
    # leadership & management
    "decision making": "Competency",
    "delegation": "Competency",
    "coaching": "Competency",
    "mentoring": "Competency",
    "team building": "Competency",
    "motivation": "Competency",
    "accountability": "Competency",
    "trust": "Competency",
    "strategic thinking": "Competency",
    "problem solving": "Competency",
    "critical thinking": "Competency",
    "creativity": "Competency",
    "innovation": "Competency",
    "adaptability": "Competency",
    "time management": "Competency",
    "execution": "Competency",
    "leadership": "Competency",
    "self-regulation": "Competency",
    "mindfulness": "Competency",
    "self-care": "Competency",
    "self esteem": "Competency",
    "self-worth": "Competency",
    "personal growth": "Competency",
    "growth": "Competency",
    "learning": "Competency",
    "curiosity": "Competency",
    "observation": "Competency",
    "pattern recognition": "Competency",
    "data analysis": "Competency",
    "research": "Competency",
    "writing": "Competency",
    "reading": "Competency",
    "networking": "Competency",
    "collaboration": "Competency",
}

_CONCEPTS: Dict[str, str] = {
    "vulnerability": "Concept",
    "psychological safety": "Concept",
    "belonging": "Concept",
    "connection": "Concept",
    "love": "Concept",
    "shame": "Concept",
    "guilt": "Concept",
    "fear": "Concept",
    "toxic behavior": "Concept",
    "toxic people": "Concept",
    "manipulation": "Concept",
    "gaslighting": "Concept",
    "codependency": "Concept",
    "people pleasing": "Concept",
    "boundaries": "Concept",
    "trust": "Concept",
    "authenticity": "Concept",
    "integrity": "Concept",
    "purpose": "Concept",
    "meaning": "Concept",
    "values": "Concept",
    "growth mindset": "Concept",
    "fixed mindset": "Concept",
    "servant leadership": "Concept",
    "transformational leadership": "Concept",
    "situational leadership": "Concept",
    "authentic leadership": "Concept",
    "emotional intelligence": "Concept",
    "organizational culture": "Concept",
    "culture": "Concept",
    "diversity": "Concept",
    "inclusion": "Concept",
    "equity": "Concept",
    "employee engagement": "Concept",
    "employee retention": "Concept",
    "team performance": "Concept",
    "problem solving": "Concept",
    "education": "Concept",
    "systemic thinking": "Concept",
    "first principles": "Concept",
    "first principles thinking": "Concept",
    "scientific method": "Concept",
    "learning": "Concept",
    "teaching": "Concept",
    "knowledge": "Concept",
    "wisdom": "Concept",
    "self-awareness": "Concept",
    "self-reflection": "Concept",
    "resilience": "Concept",
    "mindset": "Concept",
    "neuroscience": "Concept",
    "positive psychology": "Concept",
    "behavioral psychology": "Concept",
    "digital marketing": "Concept",
    "content marketing": "Concept",
    "seo": "Concept",
    "search engine optimization": "Concept",
    "brand building": "Concept",
    "customer experience": "Concept",
    "go-to-market": "Concept",
    "gtm engineering": "Concept",
    "market research": "Concept",
    "competitive analysis": "Concept",
    "data-driven decision making": "Concept",
    "metrics": "Concept",
    "analytics": "Concept",
    "conversion": "Concept",
    "engagement": "Concept",
    "audience": "Concept",
}

_STRATEGIES: Dict[str, str] = {
    "transformational leadership": "Strategy",
    "servant leadership": "Strategy",
    "situational leadership": "Strategy",
    "authentic leadership": "Strategy",
    "coaching": "Strategy",
    "mentoring": "Strategy",
    "reverse mentoring": "Strategy",
    "peer coaching": "Strategy",
    "action learning": "Strategy",
    "360-degree feedback": "Strategy",
    "strengths-based leadership": "Strategy",
    "purpose-driven leadership": "Strategy",
    "inclusive leadership": "Strategy",
    "adaptive leadership": "Strategy",
    "design thinking": "Strategy",
    "lean management": "Strategy",
    "first principles thinking": "Strategy",
    "systems thinking": "Strategy",
    "scenario planning": "Strategy",
    "okrs": "Strategy",
    "goal setting": "Strategy",
    "content strategy": "Strategy",
    "seo strategy": "Strategy",
    "keyword research": "Strategy",
    "a/b testing": "Strategy",
    "funnel optimization": "Strategy",
    "storytelling": "Strategy",
    "narrative framing": "Strategy",
    "boundary setting": "Strategy",
    "radical candor": "Strategy",
    "difficult conversations": "Strategy",
    "power dynamics": "Strategy",
    "stakeholder engagement": "Strategy",
    "conflict resolution": "Strategy",
    "negotiation": "Strategy",
    "assertive communication": "Strategy",
    "active listening": "Strategy",
}

_TACTICS: Dict[str, str] = {
    "one-on-one": "Tactic",
    "one-on-one meetings": "Tactic",
    "stand-up": "Tactic",
    "daily stand-up": "Tactic",
    "standup meeting": "Tactic",
    "weekly sync": "Tactic",
    "team huddle": "Tactic",
    "all-hands meeting": "Tactic",
    "town hall": "Tactic",
    "skip-level meeting": "Tactic",
    "brainstorming": "Tactic",
    "mind mapping": "Tactic",
    "swot analysis": "Tactic",
    "retrospective": "Tactic",
    "after-action review": "Tactic",
    "peer feedback": "Tactic",
    "360 review": "Tactic",
    "360 feedback": "Tactic",
    "smart goals": "Tactic",
    "okr setting": "Tactic",
    "journaling": "Tactic",
    "self-reflection": "Tactic",
    "reflection": "Tactic",
    "meditation": "Tactic",
    "mindfulness practice": "Tactic",
    "stretch assignment": "Tactic",
    "job rotation": "Tactic",
    "cross-training": "Tactic",
    "pair programming": "Tactic",
    "lunch and learn": "Tactic",
    "book club": "Tactic",
    "community of practice": "Tactic",
    "shadowing": "Tactic",
    "buddy system": "Tactic",
    "onboarding checklist": "Tactic",
    "feedback sandwich": "Tactic",
    "sbi feedback": "Tactic",
    "coaching conversation": "Tactic",
    "grow model": "Tactic",
    "oscar model": "Tactic",
    "fireside chat": "Tactic",
    "ask me anything": "Tactic",
    "blog post": "Tactic",
    "blog": "Tactic",
    "video content": "Tactic",
    "social media": "Tactic",
    "email marketing": "Tactic",
    "podcast": "Tactic",
    "webinar": "Tactic",
    "lead magnet": "Tactic",
    "case study": "Tactic",
    "white paper": "Tactic",
    "infographic": "Tactic",
    "newsletter": "Tactic",
    "youtube": "Tactic",
    "facebook ads": "Tactic",
    "google ads": "Tactic",
    "linkedin": "Tactic",
    "twitter": "Tactic",
    "google search console": "Tactic",
    "looker studio": "Tactic",
    "api": "Tactic",
    "claude code": "Tactic",
    "chatgpt": "Tactic",
    "prompt engineering": "Tactic",
    "automation": "Tactic",
    "workflow automation": "Tactic",
    "data pipeline": "Tactic",
    "knowledge graph": "Tactic",
    "mcp": "Tactic",
    "model context protocol": "Tactic",
}

_OUTCOMES: Dict[str, str] = {
    "team performance": "Outcome",
    "employee engagement": "Outcome",
    "employee retention": "Outcome",
    "employee satisfaction": "Outcome",
    "job satisfaction": "Outcome",
    "organizational performance": "Outcome",
    "productivity": "Outcome",
    "innovation output": "Outcome",
    "customer satisfaction": "Outcome",
    "customer retention": "Outcome",
    "revenue growth": "Outcome",
    "profitability": "Outcome",
    "market share": "Outcome",
    "brand reputation": "Outcome",
    "employer brand": "Outcome",
    "talent attraction": "Outcome",
    "talent pipeline": "Outcome",
    "succession readiness": "Outcome",
    "leadership pipeline": "Outcome",
    "organizational agility": "Outcome",
    "change readiness": "Outcome",
    "learning culture": "Outcome",
    "trust index": "Outcome",
    "team cohesion": "Outcome",
    "conflict reduction": "Outcome",
    "decision quality": "Outcome",
    "speed to market": "Outcome",
    "quality improvement": "Outcome",
    "cost reduction": "Outcome",
    "risk mitigation": "Outcome",
    "compliance adherence": "Outcome",
    "employee wellbeing": "Outcome",
    "work-life balance": "Outcome",
    "engagement score": "Outcome",
    "retention rate": "Outcome",
    "conversion rate": "Outcome",
    "traffic": "Outcome",
    "leads": "Outcome",
    "distributions": "Outcome",
    "exit": "Outcome",
    "exit valuation": "Outcome",
    "revenue": "Outcome",
    "first 100k": "Outcome",
    "first $100k": "Outcome",
    "financial independence": "Outcome",
    "audience growth": "Outcome",
    "brand awareness": "Outcome",
    "thought leadership": "Outcome",
    "personal brand": "Outcome",
    "professional development": "Outcome",
    "career growth": "Outcome",
    "life satisfaction": "Outcome",
    "well-being": "Outcome",
    "mental health": "Outcome",
    "self-confidence": "Outcome",
    "self-worth": "Outcome",
    "belonging": "Outcome",
    "connection": "Outcome",
}

# Merge all into a flat lookup
_ALL_KEYWORDS: Dict[str, str] = {}
for _d in [_COMPETENCIES, _CONCEPTS, _STRATEGIES, _TACTICS, _OUTCOMES]:
    for _k, _v in _d.items():
        if _k not in _ALL_KEYWORDS:
            _ALL_KEYWORDS[_k] = _v

# ── co-occurrence relation patterns ────────────────────────────────────────
# When two entity types appear in the same text, this determines the relation.
_RELATION_MAP = {
    # directional
    frozenset(("Competency", "Concept")): "DEVELOPS_SKILL",
    frozenset(("Competency", "Outcome")): "LEADS_TO",
    frozenset(("Concept", "Outcome")): "LEADS_TO",
    frozenset(("Strategy", "Concept")): "HAS_STRATEGY",
    frozenset(("Tactic", "Strategy")): "HAS_TACTIC",
    frozenset(("Strategy", "Outcome")): "ENABLES",
    frozenset(("Tactic", "Outcome")): "ENABLES",
    frozenset(("Competency", "Strategy")): "IS_PART_OF",
    frozenset(("Competency", "Tactic")): "IS_PART_OF",
    frozenset(("Concept", "Strategy")): "IS_PART_OF",
    frozenset(("Concept", "Tactic")): "IS_PART_OF",
    frozenset(("Tactic", "Concept")): "IS_PART_OF",
    # symmetric
    frozenset(("Concept", "Concept")): "SEMANTICALLY_RELATED",
    frozenset(("Competency", "Competency")): "SEMANTICALLY_RELATED",
    frozenset(("Strategy", "Strategy")): "SEMANTICALLY_RELATED",
    frozenset(("Tactic", "Tactic")): "SEMANTICALLY_RELATED",
    frozenset(("Outcome", "Outcome")): "SEMANTICALLY_RELATED",
    frozenset(("Competency", "Tactic")): "IS_PART_OF",
    frozenset(("Competency", "Strategy")): "IS_PART_OF",
}

_DEFAULT_RELATION = "SEMANTICALLY_RELATED"


def _canonical(name: str) -> str:
    """Capitalise entity name nicely."""
    # handle acronyms
    upper = name.upper()
    if upper in ("API", "SEO", "OKRS", "OKR", "MCP", "GTM", "SWOT", "AMA"):
        return upper
    return name.title() if len(name) > 3 else name.capitalize()


class FallbackExtractor:
    """Extracts leadership-domain entities from text without LLM calls.

    Uses keyword matching + co-occurrence to produce triplets that populate
    the knowledge graph when DeepSeek/OpenAI APIs are unavailable.
    """

    def extract_triplets(self, text_segment: str) -> List[Dict]:
        """Return a list of triplet dicts from *text_segment*."""
        lower = text_segment.lower()

        # ── 1. find all keyword hits ───────────────────────────────────
        hits: Dict[str, str] = {}  # entity_name_lower -> type
        for kw, etype in _ALL_KEYWORDS.items():
            if kw in lower:
                # use the longest matching key to avoid sub-matches
                if kw not in hits or len(kw) > len(hits):
                    hits[kw] = etype

        if len(hits) < 2:
            return []

        # ── 2. promote to canonical names ───────────────────────────────
        entities = []
        seen = set()
        for name_lower, etype in hits.items():
            canonical = _canonical(name_lower)
            if canonical not in seen:
                seen.add(canonical)
                entities.append((canonical, etype))

        # ── 3. generate triplets from co-occurrence ─────────────────────
        triplets = []
        for i, (name_a, type_a) in enumerate(entities):
            for name_b, type_b in entities[i + 1:]:
                pair = frozenset((type_a, type_b))
                relation = _RELATION_MAP.get(pair, _DEFAULT_RELATION)
                triplets.append({
                    "subject": name_a,
                    "subject_type": type_a,
                    "relation": relation,
                    "object": name_b,
                    "object_type": type_b,
                })

        return triplets

    def extract_entities(self, text_segment: str) -> List[Dict]:
        """Return just the entities found in *text_segment*."""
        lower = text_segment.lower()
        entities = []
        seen = set()
        for kw, etype in _ALL_KEYWORDS.items():
            if kw in lower:
                canonical = _canonical(kw)
                if canonical not in seen:
                    seen.add(canonical)
                    entities.append({"name": canonical, "type": etype})
        return entities


# ── batch processing ───────────────────────────────────────────────────────

def batch_extract(corpus: list, *, max_segments: int = 0) -> List[Dict]:
    """Extract triplets from an entire corpus.

    Groups segments by video_id, concatenates, then extracts.
    Returns de-duplicated triplets.
    """
    ext = FallbackExtractor()
    from collections import OrderedDict
    video_texts: "OrderedDict[str, list]" = OrderedDict()
    segments = corpus[:max_segments] if max_segments else corpus
    for seg in segments:
        vid = seg.get("video_id", "__unknown__")
        text = seg.get("transcript", "")
        if text:
            video_texts.setdefault(vid, []).append(text)

    all_triplets = []
    seen = set()
    for vid, texts in video_texts.items():
        full_text = " ".join(texts)
        for t in ext.extract_triplets(full_text):
            key = (t["subject"], t["relation"], t["object"])
            if key not in seen:
                seen.add(key)
                all_triplets.append(t)
    return all_triplets


def batch_extract_entities(corpus: list) -> List[Dict]:
    """Extract all unique entities from the corpus."""
    ext = FallbackExtractor()
    from collections import OrderedDict
    video_texts: "OrderedDict[str, list]" = OrderedDict()
    for seg in corpus:
        vid = seg.get("video_id", "__unknown__")
        text = seg.get("transcript", "")
        if text:
            video_texts.setdefault(vid, []).append(text)

    all_entities = []
    seen = set()
    for texts in video_texts.values():
        full_text = " ".join(texts)
        for e in ext.extract_entities(full_text):
            if e["name"] not in seen:
                seen.add(e["name"])
                all_entities.append(e)
    return all_entities
