import os
import json
from openai import OpenAI


class CompetitiveIntelligenceEngine:
    """Competitive Intelligence — CI Radar for Strategy/Product teams.
    Tracks competitor strategies, identifies market threats and opportunities."""

    def __init__(self, db_client=None):
        self.db = db_client
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def analyze_competitive_landscape(self, domain, competitors=None):
        if not self.client:
            return self._default_landscape(domain)

        comps = ", ".join(competitors) if competitors else "Major players in the space"
        prompt = f"""
You are a Competitive Intelligence analyst. Analyze the competitive landscape for "{domain}".

Key competitors: {comps}

Based on strategic analysis frameworks, provide:
1. Market positioning overview
2. Competitive threats and opportunities
3. Differentiation strategies
4. Emerging trends to watch
5. Recommended strategic moves

Return JSON:
{{
    "domain": "{domain}",
    "competitors_analyzed": {json.dumps(competitors) if competitors else "[]"},
    "competitive_threats": [{{"threat": "...", "severity": "high|medium|low", "competitor": "..."}}],
    "market_opportunities": [{{"opportunity": "...", "potential": "high|medium|low", "timeframe": "..."}}],
    "differentiation_areas": ["area1", "area2"],
    "strategic_recommendations": ["rec1", "rec2"],
    "key_monitoring_signals": ["signal1", "signal2"]
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Competitive Intelligence analyst. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            return json.loads(content)
        except Exception as e:
            print(f"Competitive analysis error: {e}")
            return self._default_landscape(domain)

    def _default_landscape(self, domain):
        return {
            "domain": domain,
            "competitors_analyzed": [],
            "competitive_threats": [
                {"threat": "New entrants with innovative approaches", "severity": "medium", "competitor": "Emerging players"},
                {"threat": "Established competitors expanding features", "severity": "high", "competitor": "Market leaders"},
            ],
            "market_opportunities": [
                {"opportunity": "Underserved niche segments", "potential": "high", "timeframe": "6-12 months"},
            ],
            "differentiation_areas": ["Customer experience", "Innovation speed", "Depth of expertise"],
            "strategic_recommendations": ["Monitor competitor moves quarterly", "Invest in unique capabilities"],
            "key_monitoring_signals": ["Funding rounds", "Product launches", "Talent movements"],
        }

    def extract_from_corpus(self, corpus_data, registry_data, video_id=None):
        """Auto-extract competitive intelligence insights.
        Scoped to a single video if `video_id` is provided."""
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
You are a Competitive Intelligence analyst. Analyze the following ingested video content for competitive insights{scope_hint}.

Video Titles:
{titles_text}

Transcript Excerpts:
{full_text}

Extract:
1. Competitive topics and positioning mentioned
2. Market threats identified in the content
3. Opportunities discussed or implied
4. Differentiation areas mentioned
5. Strategic recommendations based on content themes
6. Key monitoring signals to watch

Return JSON:
{{
    "video_count": {len(registry_data or [])},
    "segment_count": {len(corpus_data)},
    "scope": "per-video" if {"'"+video_id+"'" if video_id else "None"} else "global",
    "video_id": '{video_id if video_id else "all"}',
    "competitive_topics": [{{"topic": "...", "sentiment": "positive|negative|neutral", "frequency": "high|medium|low"}}],
    "competitive_threats": [{{"threat": "...", "severity": "high|medium|low", "competitor": "..."}}],
    "market_opportunities": [{{"opportunity": "...", "potential": "high|medium|low", "timeframe": "..."}}],
    "differentiation_areas": ["area1", "area2"],
    "strategic_recommendations": ["rec1", "rec2"],
    "key_monitoring_signals": ["signal1", "signal2"]
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Competitive Intelligence analyst. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            return json.loads(content)
        except Exception as e:
            print(f"Corpus competitive extraction error: {e}")
            return self._default_corpus_extraction(corpus_data, registry_data, video_id)

    def _default_corpus_extraction(self, corpus_data, registry_data, video_id=None):
        return {
            "video_count": len(registry_data or []),
            "segment_count": len(corpus_data),
            "scope": "per-video" if video_id else "global",
            "video_id": video_id or "all",
            "competitive_topics": [{"topic": "Leadership best practices", "sentiment": "positive", "frequency": "high"}],
            "competitive_threats": [
                {"threat": "Complacency in skill development", "severity": "medium", "competitor": "Industry peers"}
            ],
            "market_opportunities": [
                {"opportunity": "Upskilling programs", "potential": "high", "timeframe": "Ongoing"}
            ],
            "differentiation_areas": ["Leadership depth", "Practical implementation"],
            "strategic_recommendations": ["Invest in continuous learning", "Track industry thought leaders"],
            "key_monitoring_signals": ["Emerging leadership frameworks", "New training methodologies"],
        }
