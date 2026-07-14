import os
import json
from openai import OpenAI


class ThoughtLeadershipEngine:
    """Thought Leadership — Industry Pulse for analysts and consultants.
    Tracks industry trends, analyst views, and market shifts."""

    def __init__(self, db_client=None):
        self.db = db_client
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def analyze_industry_pulse(self, industry, signals=None):
        if not self.client:
            return self._default_pulse_analysis(industry)

        sigs = ", ".join(signals) if signals else "Current industry developments"
        prompt = f"""
You are a Thought Leadership analyst. Analyze the current industry pulse for "{industry}".

Key signals and developments: {sigs}

Provide:
1. Current industry sentiment and momentum
2. Emerging narratives and themes
3. Key voices and thought leaders to follow
4. Content and perspective gaps to fill
5. Recommended thought leadership angles
6. Potential contrarian viewpoints worth exploring

Return JSON:
{{
    "industry": "{industry}",
    "industry_momentum": "rising|stable|declining|transforming",
    "key_narratives": [{{"narrative": "...", "strength": "dominant|emerging|fringe", "proponents": ["..."]}}],
    "thought_leaders": [{{"name": "...", "expertise": "...", "influence": "high|medium|low"}}],
    "content_gaps": [{{"gap": "...", "opportunity": "...", "audience_demand": "high|medium|low"}}],
    "recommended_angles": [{{"angle": "...", "rationale": "...", "format": "article|video|podcast|report"}}],
    "contrarian_viewpoints": [{{"viewpoint": "...", "evidence": "...", "risk_level": "high|medium|low"}}]
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Thought Leadership analyst. Output ONLY valid JSON."},
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
            print(f"Industry pulse error: {e}")
            return self._default_pulse_analysis(industry)

    def _default_pulse_analysis(self, industry):
        return {
            "industry": industry,
            "industry_momentum": "transforming",
            "key_narratives": [
                {"narrative": "Digital transformation accelerating", "strength": "dominant", "proponents": ["Industry analysts", "Technology leaders"]},
                {"narrative": "People-first leadership gaining traction", "strength": "emerging", "proponents": ["HR thought leaders", "Culture experts"]},
            ],
            "thought_leaders": [
                {"name": "Industry analysts", "expertise": "Market trends and forecasts", "influence": "high"},
            ],
            "content_gaps": [
                {"gap": "Practical implementation guides", "opportunity": "High demand for actionable content", "audience_demand": "high"},
            ],
            "recommended_angles": [
                {"angle": "Bridge theory and practice", "rationale": "Audiences want actionable insights", "format": "article"},
            ],
            "contrarian_viewpoints": [
                {"viewpoint": "Counter-consensus perspective on industry direction", "evidence": "Emerging data points", "risk_level": "medium"},
            ],
        }

    def extract_leadership_insights(self, transcript_segments):
        insights = []
        for seg in transcript_segments:
            text = seg.get("transcript", "")
            if len(text) > 50 and any(w in text.lower() for w in ["future", "trend", "shift", "emerging", "next", "transform", "disrupt"]):
                insights.append({
                    "insight": text[:200],
                    "timestamp": seg.get("start_time", 0),
                    "signal_type": "future_trend" if any(w in text.lower() for w in ["future", "trend", "shift"]) else "transformation",
                })
        return insights[:10]

    def extract_from_corpus(self, corpus_data, registry_data, video_id=None):
        """Auto-extract thought leadership insights. Scoped per-video if video_id provided."""
        if not corpus_data:
            return {"status": "no_data", "message": "No corpus data available."}

        if video_id:
            corpus_data = [s for s in corpus_data if s.get("video_id") == video_id]
            registry_data = [v for v in (registry_data or []) if v.get("video_id") == video_id]
            if not corpus_data:
                return {"status": "no_data", "message": f"No data for video: {video_id}"}

        if not self.client:
            return self._default_corpus_extraction(corpus_data, registry_data, video_id)

        all_insights = self.extract_leadership_insights(corpus_data)

        video_titles = [v.get("title", "Untitled") for v in (registry_data or [])]
        titles_text = "\n".join(f"- {t}" for t in video_titles) or "No videos ingested"
        full_text = " ".join(s.get("transcript", "") for s in corpus_data[:50])[:3000]
        scope_hint = f" (scoped to video: {video_id})" if video_id else ""

        prompt = f"""
You are a Thought Leadership analyst. Analyze the following ingested video content for thought leadership insights{scope_hint}.

Video Titles:
{titles_text}

Transcript Excerpts:
{full_text}

Signal insights detected ({len(all_insights)}): {json.dumps([s['signal_type'] for s in all_insights[:5]])}

Extract:
1. Current industry sentiment and momentum from the content
2. Emerging narratives and key themes discussed
3. Key voices and thought leaders referenced
4. Content and perspective gaps (what's missing)
5. Recommended thought leadership angles based on what's covered
6. Potential contrarian viewpoints worth exploring

Return JSON:
{{
    "video_count": {len(registry_data or [])},
    "segment_count": {len(corpus_data)},
    "scope": "per-video" if {"'"+video_id+"'" if video_id else "None"} else "global",
    "video_id": '{video_id if video_id else "all"}',
    "signal_count": {len(all_insights)},
    "industry_momentum": "rising|stable|declining|transforming",
    "key_narratives": [{{"narrative": "...", "strength": "dominant|emerging|fringe", "proponents": ["..."]}}],
    "thought_leaders": [{{"name": "...", "expertise": "...", "influence": "high|medium|low"}}],
    "content_gaps": [{{"gap": "...", "opportunity": "...", "audience_demand": "high|medium|low"}}],
    "recommended_angles": [{{"angle": "...", "rationale": "...", "format": "article|video|podcast|report"}}],
    "contrarian_viewpoints": [{{"viewpoint": "...", "evidence": "...", "risk_level": "high|medium|low"}}]
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Thought Leadership analyst. Output ONLY valid JSON."},
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
            print(f"Corpus thought leadership extraction error: {e}")
            return self._default_corpus_extraction(corpus_data, registry_data, video_id)

    def _default_corpus_extraction(self, corpus_data, registry_data, video_id=None):
        all_text = " ".join(s.get("transcript", "") for s in corpus_data[:30]).lower()
        narratives = []
        for n in ["leadership", "innovation", "digital transformation", "culture",
                   "future of work", "ai", "strategy", "change"]:
            if n in all_text:
                narratives.append(n.title())
        return {
            "video_count": len(registry_data or []),
            "segment_count": len(corpus_data),
            "scope": "per-video" if video_id else "global",
            "video_id": video_id or "all",
            "signal_count": 0,
            "industry_momentum": "transforming",
            "key_narratives": [
                {"narrative": n, "strength": "emerging", "proponents": ["Content creators"]}
                for n in narratives[:5]
            ] or [{"narrative": "Leadership development", "strength": "emerging", "proponents": ["Industry thought leaders"]}],
            "thought_leaders": [{"name": "Featured speakers", "expertise": "Leadership and management", "influence": "high"}],
            "content_gaps": [{"gap": "Deep-dive industry analysis", "opportunity": "Expand beyond general leadership", "audience_demand": "high"}],
            "recommended_angles": [{"angle": "Apply leadership frameworks to emerging trends", "rationale": "High audience interest", "format": "article"}],
            "contrarian_viewpoints": [{"viewpoint": "Challenge conventional leadership wisdom", "evidence": "Emerging research and practice", "risk_level": "medium"}],
        }
