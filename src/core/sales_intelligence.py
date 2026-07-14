import os
import json
from openai import OpenAI


class SalesIntelligenceEngine:
    """Sales Intelligence — Sales Knowledge Engine for VP Sales and RevOps.
    Provides deal insights, objection handling, and buyer signal detection."""

    def __init__(self, db_client=None):
        self.db = db_client
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def analyze_deal(self, deal_context, buyer_persona):
        if not self.client:
            return self._default_deal_analysis(deal_context)

        prompt = f"""
You are a Sales Intelligence analyst. Analyze this sales deal and provide actionable insights.

Deal context: {deal_context[:500]}
Buyer persona: {buyer_persona}

Provide:
1. Deal health assessment
2. Key buyer signals and pain points
3. Recommended messaging and positioning
4. Objection handling strategies
5. Next best actions with timeline
6. Competitive positioning advice

Return JSON:
{{
    "deal_health": "strong|moderate|at_risk",
    "buyer_signals": [{{"signal": "...", "strength": "high|medium|low"}}],
    "recommended_messaging": ["message1", "message2"],
    "objection_handlers": [{{"objection": "...", "response": "...", "evidence": "..."}}],
    "next_actions": [{{"action": "...", "priority": "high|medium|low", "timeline": "..."}}],
    "competitive_positioning": "How to position against alternatives"
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Sales Intelligence analyst. Output ONLY valid JSON."},
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
            print(f"Deal analysis error: {e}")
            return self._default_deal_analysis(deal_context)

    def _default_deal_analysis(self, deal_context):
        return {
            "deal_health": "moderate",
            "buyer_signals": [
                {"signal": "Active research phase", "strength": "medium"},
                {"signal": "Budget discussion initiated", "strength": "high"},
            ],
            "recommended_messaging": ["Focus on ROI and business outcomes", "Address specific pain points"],
            "objection_handlers": [
                {"objection": "Too expensive", "response": "Show ROI calculation and payback period", "evidence": "Case studies"},
            ],
            "next_actions": [
                {"action": "Schedule demo with decision makers", "priority": "high", "timeline": "This week"},
            ],
            "competitive_positioning": "Position against status quo and alternative solutions",
        }

    def extract_buyer_signals(self, transcript_segments):
        signals = []
        for seg in transcript_segments:
            text = seg.get("transcript", "").lower()
            if any(w in text for w in ["budget", "pricing", "cost", "roi", "invest"]):
                signals.append({"signal": "Budget/pricing discussion", "segment": text[:100], "timestamp": seg.get("start_time", 0)})
            elif any(w in text for w in ["competitor", "alternative", "comparing", "vs"]):
                signals.append({"signal": "Competitive evaluation", "segment": text[:100], "timestamp": seg.get("start_time", 0)})
            elif any(w in text for w in ["urgent", "deadline", "asap", "priority", "critical"]):
                signals.append({"signal": "Urgency/priority signal", "segment": text[:100], "timestamp": seg.get("start_time", 0)})
        return signals

    def extract_from_corpus(self, corpus_data, registry_data, video_id=None):
        """Auto-extract sales intelligence insights. Scoped per-video if video_id is provided."""
        if not corpus_data:
            return {"status": "no_data", "message": "No corpus data available."}

        if video_id:
            corpus_data = [s for s in corpus_data if s.get("video_id") == video_id]
            registry_data = [v for v in (registry_data or []) if v.get("video_id") == video_id]
            if not corpus_data:
                return {"status": "no_data", "message": f"No data for video: {video_id}"}

        all_signals = self.extract_buyer_signals([
            {"transcript": s.get("transcript", ""), "start_time": s.get("start_time", 0)}
            for s in corpus_data
        ])

        if not self.client:
            return self._default_corpus_extraction(corpus_data, registry_data, video_id, all_signals)

        video_titles = [v.get("title", "Untitled") for v in (registry_data or [])]
        titles_text = "\n".join(f"- {t}" for t in video_titles) or "No videos ingested"
        full_text = " ".join(s.get("transcript", "") for s in corpus_data[:50])[:3000]
        scope_hint = f" (scoped to video: {video_id})" if video_id else ""

        prompt = f"""
You are a Sales Intelligence analyst. Analyze the following ingested video content for sales insights{scope_hint}.

Video Titles:
{titles_text}

Transcript Excerpts:
{full_text}

Buyer signals detected ({len(all_signals)}): {json.dumps([s['signal'] for s in all_signals[:5]])}

Extract:
1. Deal-relevant themes and buyer pain points discussed
2. Effective messaging and positioning strategies implied
3. Objection handling approaches referenced
4. Next best actions for sales teams based on content
5. Competitive positioning insights

Return JSON:
{{
    "video_count": {len(registry_data or [])},
    "segment_count": {len(corpus_data)},
    "scope": "per-video" if {"'"+video_id+"'" if video_id else "None"} else "global",
    "video_id": '{video_id if video_id else "all"}',
    "buyer_signals": [{{"signal": "...", "strength": "high|medium|low", "count": 0}}],
    "deal_themes": [{{"theme": "...", "relevance": "high|medium|low", "source_videos": ["..."]}}],
    "recommended_messaging": ["message1", "message2"],
    "objection_handlers": [{{"objection": "...", "response": "..."}}],
    "next_actions": [{{"action": "...", "priority": "high|medium|low"}}],
    "competitive_positioning": "Key positioning derived from content"
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Sales Intelligence analyst. Output ONLY valid JSON."},
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
            print(f"Corpus sales extraction error: {e}")
            return self._default_corpus_extraction(corpus_data, registry_data, video_id, all_signals)

    def _default_corpus_extraction(self, corpus_data, registry_data, video_id=None, signals=None):
        return {
            "video_count": len(registry_data or []),
            "segment_count": len(corpus_data),
            "scope": "per-video" if video_id else "global",
            "video_id": video_id or "all",
            "buyer_signals": [{"signal": s["signal"], "strength": "medium", "count": 1} for s in (signals or [])[:5]] or [{"signal": "General leadership interest", "strength": "medium", "count": 1}],
            "deal_themes": [{"theme": "Leadership development", "relevance": "high", "source_videos": []}],
            "recommended_messaging": ["Focus on actionable leadership insights", "Emphasize practical frameworks"],
            "objection_handlers": [{"objection": "Too busy for training", "response": "Show ROI and time-efficient methods"}],
            "next_actions": [{"action": "Share relevant video clips with prospects", "priority": "high"}],
            "competitive_positioning": "Deep leadership expertise vs. generic training alternatives",
        }
