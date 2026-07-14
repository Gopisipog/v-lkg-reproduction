import os
import json
from openai import OpenAI


class CustomerIntelligenceEngine:
    """Customer Intelligence — Voice of Customer Engine for Product/CX teams.
    Analyzes customer feedback, sentiment, and needs from video content."""

    def __init__(self, db_client=None):
        self.db = db_client
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def analyze_customer_sentiment(self, transcript_segments, topic=None):
        if not self.client or not transcript_segments:
            return self._default_sentiment_analysis(topic)

        excerpts = "\n".join(
            f"- [{s.get('start_time', 0):.1f}s] {s['transcript'][:200]}"
            for s in transcript_segments[:8]
        )
        topic_str = topic or "General leadership and development"

        prompt = f"""
You are a Customer Intelligence analyst. Analyze customer sentiment from transcript segments.

Topic: {topic_str}

Transcript excerpts:
{excerpts}

Provide:
1. Overall sentiment analysis (positive/negative/neutral distribution)
2. Key themes and topics discussed
3. Pain points and challenges expressed
4. Desired outcomes and needs
5. Sentiment trend across the conversation
6. Actionable recommendations

Return JSON:
{{
    "topic": "{topic_str}",
    "overall_sentiment": "positive|negative|neutral|mixed",
    "sentiment_breakdown": {{"positive": 0, "negative": 0, "neutral": 0}},
    "key_themes": [{{"theme": "...", "frequency": "high|medium|low", "sentiment": "..."}}],
    "pain_points": [{{"pain_point": "...", "severity": "high|medium|low", "context": "..."}}],
    "desired_outcomes": [{{"outcome": "...", "priority": "high|medium|low"}}],
    "recommendations": ["rec1", "rec2"]
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Customer Intelligence analyst. Output ONLY valid JSON."},
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
            print(f"Sentiment analysis error: {e}")
            return self._default_sentiment_analysis(topic)

    def _default_sentiment_analysis(self, topic):
        return {
            "topic": topic or "General",
            "overall_sentiment": "mixed",
            "sentiment_breakdown": {"positive": 40, "negative": 20, "neutral": 40},
            "key_themes": [
                {"theme": "Leadership challenges", "frequency": "high", "sentiment": "mixed"},
            ],
            "pain_points": [
                {"pain_point": "Difficulty implementing change", "severity": "high", "context": "Common leadership challenge"},
            ],
            "desired_outcomes": [
                {"outcome": "Better team engagement", "priority": "high"},
            ],
            "recommendations": ["Focus on practical implementation strategies", "Provide more case studies and examples"],
        }

    def extract_customer_needs(self, text):
        needs = []
        text_lower = text.lower()
        need_signals = {
            "need": ["need", "require", "must have", "essential"],
            "want": ["want", "would like", "hoping for", "looking for"],
            "problem": ["problem", "issue", "challenge", "difficult", "hard"],
            "goal": ["goal", "aim", "objective", "target", "aspire"],
        }
        for category, signals in need_signals.items():
            for signal in signals:
                if signal in text_lower:
                    needs.append({"category": category, "signal": signal})
        return needs

    def extract_from_corpus(self, corpus_data, registry_data, video_id=None):
        """Auto-extract customer intelligence insights. Scoped per-video if video_id provided."""
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
You are a Customer Intelligence analyst. Analyze the following ingested video content for customer insights{scope_hint}.

Video Titles:
{titles_text}

Transcript Excerpts:
{full_text}

Extract:
1. Overall sentiment of the content (positive/negative/neutral distribution)
2. Key themes and topics discussed
3. Pain points and challenges expressed for leaders
4. Desired outcomes and needs from the audience perspective
5. Actionable recommendations based on content patterns

Return JSON:
{{
    "video_count": {len(registry_data or [])},
    "segment_count": {len(corpus_data)},
    "scope": "per-video" if {"'"+video_id+"'" if video_id else "None"} else "global",
    "video_id": '{video_id if video_id else "all"}',
    "overall_sentiment": "positive|negative|neutral|mixed",
    "sentiment_breakdown": {{"positive": 0, "negative": 0, "neutral": 0}},
    "key_themes": [{{"theme": "...", "frequency": "high|medium|low", "sentiment": "..."}}],
    "pain_points": [{{"pain_point": "...", "severity": "high|medium|low", "context": "..."}}],
    "desired_outcomes": [{{"outcome": "...", "priority": "high|medium|low"}}],
    "recommendations": ["rec1", "rec2"]
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Customer Intelligence analyst. Output ONLY valid JSON."},
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
            print(f"Corpus customer extraction error: {e}")
            return self._default_corpus_extraction(corpus_data, registry_data, video_id)

    def _default_corpus_extraction(self, corpus_data, registry_data, video_id=None):
        return {
            "video_count": len(registry_data or []),
            "segment_count": len(corpus_data),
            "scope": "per-video" if video_id else "global",
            "video_id": video_id or "all",
            "overall_sentiment": "mixed",
            "sentiment_breakdown": {"positive": 40, "negative": 20, "neutral": 40},
            "key_themes": [
                {"theme": "Leadership challenges", "frequency": "high", "sentiment": "mixed"},
                {"theme": "Skill development", "frequency": "high", "sentiment": "positive"},
            ],
            "pain_points": [
                {"pain_point": "Implementing change", "severity": "high", "context": "Common challenge discussed in content"}
            ],
            "desired_outcomes": [
                {"outcome": "Better team engagement", "priority": "high"}
            ],
            "recommendations": ["Focus on practical implementation strategies", "Provide more case studies and examples"],
        }
