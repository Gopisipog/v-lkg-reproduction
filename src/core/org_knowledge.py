import os
import json
from openai import OpenAI


class OrgKnowledgeEngine:
    """Org Knowledge Capture — Organizational Memory for HR/Ops teams.
    Captures and preserves organizational knowledge, expertise, and best practices."""

    def __init__(self, db_client=None):
        self.db = db_client
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def capture_knowledge_asset(self, topic, content, source=None):
        if not self.client:
            return self._default_knowledge_capture(topic)

        prompt = f"""
You are an Organizational Knowledge analyst. Capture and structure knowledge about "{topic}".

Source content: {content[:500]}
Source: {source or "Leadership video content"}

Structure this knowledge for organizational memory:
1. Core concepts and definitions
2. Key principles and frameworks
3. Implementation best practices
4. Common pitfalls to avoid
5. Related knowledge areas
6. Expertise level required
7. Cross-reference with existing knowledge

Return JSON:
{{
    "topic": "{topic}",
    "core_concepts": [{{"concept": "...", "definition": "..."}}],
    "key_principles": [{{"principle": "...", "explanation": "..."}}],
    "best_practices": ["practice1", "practice2"],
    "common_pitfalls": [{{"pitfall": "...", "prevention": "..."}}],
    "related_areas": ["area1", "area2"],
    "expertise_level": "beginner|intermediate|advanced",
    "cross_references": [{{"topic": "...", "relationship": "...", "relevance": "high|medium|low"}}]
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an Organizational Knowledge analyst. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            return json.loads(content)
        except Exception as e:
            print(f"Knowledge capture error: {e}")
            return self._default_knowledge_capture(topic)

    def _default_knowledge_capture(self, topic):
        return {
            "topic": topic,
            "core_concepts": [{"concept": topic, "definition": f"Key topic in organizational knowledge about {topic}"}],
            "key_principles": [{"principle": "Continuous learning", "explanation": "Knowledge should be regularly updated"}],
            "best_practices": ["Document decisions and rationale", "Review and update regularly", "Share across teams"],
            "common_pitfalls": [{"pitfall": "Knowledge silos", "prevention": "Cross-team sharing sessions"}],
            "related_areas": ["Leadership development", "Change management"],
            "expertise_level": "intermediate",
            "cross_references": [],
        }

    def find_knowledge_gaps(self, graph_nodes):
        if not graph_nodes:
            return {"gaps": [], "message": "No graph data available"}

        types_present = {}
        for n in graph_nodes:
            t = n.get("type", "Unknown")
            types_present[t] = types_present.get(t, 0) + 1

        gaps = []
        essential_types = ["Competency", "Strategy", "Tactic", "Outcome"]
        for et in essential_types:
            if et not in types_present or types_present[et] < 3:
                gaps.append({"type": et, "status": "insufficient", "count": types_present.get(et, 0), "suggestion": f"Add more {et.lower()} nodes"})

        return {"gaps": gaps, "coverage": types_present, "message": f"Found {len(gaps)} knowledge gaps"}

    def extract_from_corpus(self, corpus_data, registry_data, video_id=None):
        """Auto-extract organizational knowledge. Scoped per-video if video_id provided."""
        if not corpus_data:
            return {"status": "no_data", "message": "No corpus data available."}

        if video_id:
            corpus_data = [s for s in corpus_data if s.get("video_id") == video_id]
            registry_data = [v for v in (registry_data or []) if v.get("video_id") == video_id]
            if not corpus_data:
                return {"status": "no_data", "message": f"No data for video: {video_id}"}

        if not self.client:
            return self._default_corpus_extraction(corpus_data, registry_data, video_id)

        video_titles = [v.get("title", "Untitled") for v in (registry_data or [])]
        titles_text = "\n".join(f"- {t}" for t in video_titles) or "No videos ingested"
        full_text = " ".join(s.get("transcript", "") for s in corpus_data[:50])[:3000]
        scope_hint = f" (scoped to video: {video_id})" if video_id else ""

        prompt = f"""
You are an Organizational Knowledge analyst. Capture and structure knowledge from the following ingested video content{scope_hint}.

Video Titles:
{titles_text}

Transcript Excerpts:
{full_text}

Extract:
1. Core concepts and topics covered across videos
2. Key principles and frameworks discussed
3. Implementation best practices mentioned
4. Common pitfalls or challenges addressed
5. Related knowledge areas and cross-references
6. Expertise level of the content (beginner/intermediate/advanced)
7. Knowledge gaps (what important topics are NOT covered)

Return JSON:
{{
    "video_count": {len(registry_data or [])},
    "segment_count": {len(corpus_data)},
    "scope": "per-video" if {"'"+video_id+"'" if video_id else "None"} else "global",
    "video_id": '{video_id if video_id else "all"}',
    "core_concepts": [{{"concept": "...", "definition": "...", "video_sources": ["..."]}}],
    "key_principles": [{{"principle": "...", "explanation": "..."}}],
    "best_practices": ["practice1", "practice2"],
    "common_pitfalls": [{{"pitfall": "...", "prevention": "..."}}],
    "related_areas": ["area1", "area2"],
    "expertise_level": "beginner|intermediate|advanced|mixed",
    "knowledge_gaps": [{{"gap": "...", "importance": "high|medium|low"}}],
    "cross_references": [{{"topic": "...", "relationship": "...", "relevance": "high|medium|low"}}]
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an Organizational Knowledge analyst. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            return json.loads(content)
        except Exception as e:
            print(f"Corpus knowledge extraction error: {e}")
            return self._default_corpus_extraction(corpus_data, registry_data, video_id)

    def _default_corpus_extraction(self, corpus_data, registry_data, video_id=None):
        all_text = " ".join(s.get("transcript", "") for s in corpus_data[:30]).lower()
        concepts = []
        for c in ["leadership", "communication", "strategy", "culture", "innovation",
                   "change management", "team building", "coaching", "decision making"]:
            if c in all_text:
                concepts.append(c.title())
        return {
            "video_count": len(registry_data or []),
            "segment_count": len(corpus_data),
            "scope": "per-video" if video_id else "global",
            "video_id": video_id or "all",
            "core_concepts": [{"concept": c, "definition": f"Key topic discussed across multiple video segments", "video_sources": []} for c in concepts[:5]],
            "key_principles": [{"principle": "Continuous learning", "explanation": "Regular skill development is essential for leadership"}],
            "best_practices": ["Document key takeaways per video", "Cross-reference concepts across videos", "Apply frameworks in practice"],
            "common_pitfalls": [{"pitfall": "Information overload", "prevention": "Focus on actionable insights"}],
            "related_areas": ["Leadership development", "Change management", "Organizational culture"],
            "expertise_level": "mixed",
            "knowledge_gaps": [{"gap": "Advanced domain-specific knowledge", "importance": "medium"}],
            "cross_references": [],
        }
