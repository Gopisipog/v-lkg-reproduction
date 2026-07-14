import os
import json
from openai import OpenAI


class RDIntelligenceEngine:
    """R&D Intelligence — R&D Knowledge Graph for Innovation teams.
    Tracks innovation patterns, emerging trends, and technology convergence."""

    def __init__(self, db_client=None):
        self.db = db_client
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def analyze_innovation_trends(self, domain, signals=None):
        if not self.client:
            return self._default_innovation_analysis(domain)

        sigs = ", ".join(signals) if signals else "Emerging patterns in the field"
        prompt = f"""
You are an R&D Intelligence analyst. Analyze innovation trends in "{domain}".

Key signals and patterns: {sigs}

Provide:
1. Emerging technology and methodology trends
2. Innovation opportunities and whitespace
3. Convergence patterns across domains
4. Recommended research directions
5. Potential disruptions on the horizon
6. Collaboration and partnership opportunities

Return JSON:
{{
    "domain": "{domain}",
    "emerging_trends": [{{"trend": "...", "maturity": "emerging|growing|mature", "impact": "high|medium|low"}}],
    "innovation_opportunities": [{{"opportunity": "...", "effort": "low|medium|high", "potential": "..."}}],
    "convergence_patterns": [{{"domains": ["..."], "description": "...", "opportunity": "..."}}],
    "research_directions": [{{"direction": "...", "rationale": "...", "timeframe": "..."}}],
    "potential_disruptions": ["disruption1", "disruption2"],
    "recommended_partnerships": ["partner1", "partner2"]
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an R&D Intelligence analyst. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            return json.loads(content)
        except Exception as e:
            print(f"Innovation analysis error: {e}")
            return self._default_innovation_analysis(domain)

    def _default_innovation_analysis(self, domain):
        return {
            "domain": domain,
            "emerging_trends": [
                {"trend": "AI-powered decision making", "maturity": "growing", "impact": "high"},
                {"trend": "Remote and hybrid collaboration", "maturity": "mature", "impact": "medium"},
            ],
            "innovation_opportunities": [
                {"opportunity": "Integrate AI into core workflows", "effort": "medium", "potential": "High ROI"},
            ],
            "convergence_patterns": [
                {"domains": ["Technology", "Psychology"], "description": "Human-AI interaction design", "opportunity": "New product category"},
            ],
            "research_directions": [
                {"direction": "Explore AI-augmented decision making", "rationale": "Growing demand", "timeframe": "6-12 months"},
            ],
            "potential_disruptions": ["AI democratization", "New collaboration paradigms"],
            "recommended_partnerships": ["Academic institutions", "Technology partners"],
        }

    def find_related_innovations(self, concept, graph_nodes=None):
        if not self.db or not self.db.driver:
            return {"related": [], "message": "Neo4j not connected"}
        try:
            related = self.db.execute_read(
                """MATCH (n)-[r]-(m) WHERE n.name CONTAINS $concept 
                   AND m.name IS NOT NULL RETURN m.name AS name, type(r) AS relation, labels(m)[0] AS type LIMIT 10""",
                {"concept": concept},
            ) or []
            return {"related": related, "count": len(related)}
        except Exception as e:
            return {"related": [], "error": str(e)}

    def extract_from_corpus(self, corpus_data, registry_data, video_id=None):
        """Auto-extract R&D intelligence insights. Scoped per-video if video_id is provided."""
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
You are an R&D Intelligence analyst. Analyze the following ingested video content for innovation and R&D insights{scope_hint}.

Video Titles:
{titles_text}

Transcript Excerpts:
{full_text}

Extract:
1. Emerging trends and methodologies discussed
2. Innovation opportunities identified in the content
3. Convergence patterns across domains
4. Recommended research directions
5. Potential disruptions implied
6. Collaboration opportunities mentioned

Return JSON:
{{
    "video_count": {len(registry_data or [])},
    "segment_count": {len(corpus_data)},
    "scope": "per-video" if {"'"+video_id+"'" if video_id else "None"} else "global",
    "video_id": '{video_id if video_id else "all"}',
    "emerging_trends": [{{"trend": "...", "maturity": "emerging|growing|mature", "impact": "high|medium|low"}}],
    "innovation_opportunities": [{{"opportunity": "...", "effort": "low|medium|high", "potential": "..."}}],
    "convergence_patterns": [{{"domains": ["..."], "description": "...", "opportunity": "..."}}],
    "research_directions": [{{"direction": "...", "rationale": "...", "timeframe": "..."}}],
    "potential_disruptions": ["disruption1", "disruption2"],
    "recommended_partnerships": ["partner1", "partner2"]
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an R&D Intelligence analyst. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            return json.loads(content)
        except Exception as e:
            print(f"Corpus R&D extraction error: {e}")
            return self._default_corpus_extraction(corpus_data, registry_data, video_id)

    def _default_corpus_extraction(self, corpus_data, registry_data, video_id=None):
        all_text = " ".join(s.get("transcript", "") for s in corpus_data[:30]).lower()
        trends_detected = []
        for t in ["artificial intelligence", "machine learning", "innovation", "digital transformation",
                   "collaboration", "agile", "data-driven", "automation", "design thinking", "cloud"]:
            if t in all_text:
                trends_detected.append(t.title())
        return {
            "video_count": len(registry_data or []),
            "segment_count": len(corpus_data),
            "scope": "per-video" if video_id else "global",
            "video_id": video_id or "all",
            "emerging_trends": [{"trend": t, "maturity": "growing", "impact": "high"} for t in trends_detected[:5]] or [
                {"trend": "Leadership innovation", "maturity": "growing", "impact": "high"}
            ],
            "innovation_opportunities": [{"opportunity": "Apply leadership frameworks to R&D", "effort": "medium", "potential": "High impact"}],
            "convergence_patterns": [{"domains": ["Leadership", "Technology"], "description": "Tech-enabled leadership development", "opportunity": "New learning products"}],
            "research_directions": [{"direction": "Explore emerging leadership models", "rationale": "Content suggests evolving paradigms", "timeframe": "3-6 months"}],
            "potential_disruptions": ["New collaboration paradigms", "AI-assisted decision making"],
            "recommended_partnerships": ["Academic institutions", "Learning technology providers"],
        }
