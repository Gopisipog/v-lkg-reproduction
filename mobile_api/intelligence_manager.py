"""
Intelligence Manager — Manages 8 specialized intelligence lenses for YouTube videos and child apps.
Lenses: Executive, Sales, Learning & Dev, R&D / Engineering, Compliance, Customer, Competitive, Thought Leadership.
"""

from typing import List, Dict, Any, Set
import re

INTELLIGENCE_DOMAINS = {
    "executive": {
        "id": "executive",
        "name": "Executive Intelligence",
        "icon": "Briefcase",
        "color": "#6366f1",
        "badge": "bg-indigo-500/20 text-indigo-400 border-indigo-500/30",
        "description": "Strategic decision-making, C-suite frameworks, resource allocation, and organizational alignment.",
        "keywords": [
            "strategy", "strategic", "clarity", "execution", "velocity", "leadership", "executive", "vision", "decision", "governance", "organization",
            "scale", "board", "alignment", "culture", "management", "delegation", "priority", "roi",
            "capital", "kpi", "okr", "transformation", "leverage", "operating"
        ]
    },
    "sales": {
        "id": "sales",
        "name": "Sales & Revenue",
        "icon": "TrendingUp",
        "color": "#10b981",
        "badge": "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
        "description": "Objection handling, conversion funnels, pitch positioning, value proposition, and closing.",
        "keywords": [
            "sales", "revenue", "pitch", "deal", "pricing", "closing", "prospect", "customer", "conversion",
            "pipeline", "objection", "negotiation", "value proposition", "gtm", "funnel", "offer", "discount",
            "upsell", "b2b", "quota", "lead"
        ]
    },
    "learning": {
        "id": "learning",
        "name": "Learning & Mastery",
        "icon": "GraduationCap",
        "color": "#f59e0b",
        "badge": "bg-amber-500/20 text-amber-400 border-amber-500/30",
        "description": "Skill acquisition, deliberate practice, habit formation, retention, and coaching ladders.",
        "keywords": [
            "skill", "practice", "learning", "habit", "coaching", "mindset", "feedback", "mastery",
            "discipline", "routine", "exercise", "training", "retention", "reflection", "improvement",
            "mentor", "repetition", "framework", "workbook"
        ]
    },
    "engineering": {
        "id": "engineering",
        "name": "R&D & Engineering",
        "icon": "Cpu",
        "color": "#3b82f6",
        "badge": "bg-blue-500/20 text-blue-400 border-blue-500/30",
        "description": "Technical systems, AI workflows, tooling, automation, product architecture, and engineering execution.",
        "keywords": [
            "engineering", "architecture", "ai", "llm", "claude", "tool", "code", "automation", "api",
            "system", "software", "infrastructure", "pipeline", "technical", "r&d", "developer", "prompt",
            "workflow", "agent", "data"
        ]
    },
    "compliance": {
        "id": "compliance",
        "name": "Risk & Governance",
        "icon": "ShieldCheck",
        "color": "#ef4444",
        "badge": "bg-red-500/20 text-red-400 border-red-500/30",
        "description": "Risk mitigation, regulatory guardrails, ethical boundaries, security, and quality assurance.",
        "keywords": [
            "compliance", "risk", "security", "policy", "legal", "regulation", "guardrail", "audit",
            "privacy", "governance", "standard", "safety", "boundary", "mitigation", "threat", "liability"
        ]
    },
    "customer": {
        "id": "customer",
        "name": "Customer Success",
        "icon": "Users",
        "color": "#ec4899",
        "badge": "bg-pink-500/20 text-pink-400 border-pink-500/30",
        "description": "User empathy, active listening, retention, churn prevention, and relationship building.",
        "keywords": [
            "customer", "client", "retention", "churn", "empathy", "listening", "satisfaction",
            "relationship", "support", "trust", "experience", "nps", "onboarding", "rapport", "connection"
        ]
    },
    "competitive": {
        "id": "competitive",
        "name": "Competitive Intelligence",
        "icon": "Crosshair",
        "color": "#8b5cf6",
        "badge": "bg-purple-500/20 text-purple-400 border-purple-500/30",
        "description": "Market moats, differentiation, competitive analysis, category creation, and positioning.",
        "keywords": [
            "competitor", "competition", "moat", "differentiation", "market", "advantage", "positioning",
            "barrier", "rival", "pricing power", "benchmark", "monopoly", "category", "niche"
        ]
    },
    "thought_leadership": {
        "id": "thought_leadership",
        "name": "Thought Leadership",
        "icon": "Sparkles",
        "color": "#14b8a6",
        "badge": "bg-teal-500/20 text-teal-400 border-teal-500/30",
        "description": "Presentation devices, storytelling frameworks, rhetorical devices, and viral communication.",
        "keywords": [
            "presentation", "storytelling", "communication", "device", "rhetorical", "contrast", "hook",
            "metaphor", "analogy", "speaker", "influence", "persuasion", "narrative", "audience", "message"
        ]
    }
}


def classify_entity_intelligences(name: str, entity_type: str = "", context: str = "") -> List[str]:
    """Classifies an entity into matching intelligence domains based on keywords and semantics."""
    text = f"{name} {entity_type} {context}".lower()
    matched = set()
    
    for domain_id, meta in INTELLIGENCE_DOMAINS.items():
        for kw in meta["keywords"]:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, text):
                matched.add(domain_id)
                break
                
    if not matched:
        matched.add("thought_leadership")
        matched.add("executive")
        
    return list(matched)


def classify_triplet_intelligences(triplet: Dict[str, Any]) -> List[str]:
    """Classifies a triplet into matching intelligence domains."""
    sub = triplet.get("subject", "")
    rel = triplet.get("relation", "")
    obj = triplet.get("object", "")
    text = f"{sub} {rel} {obj}".lower()
    
    matched = set()
    for domain_id, meta in INTELLIGENCE_DOMAINS.items():
        for kw in meta["keywords"]:
            if kw in text:
                matched.add(domain_id)
                break
                
    if not matched:
        matched.add("thought_leadership")
        matched.add("executive")
    return list(matched)
