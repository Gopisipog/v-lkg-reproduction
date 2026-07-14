import os
import json
from openai import OpenAI


class ExecutiveIntelligenceEngine:
    """Executive Intelligence — Executive Memory for C-suite and Chiefs of Staff.
    Provides synthesized insights, strategic summaries, and decision support."""

    def __init__(self, db_client=None):
        self.db = db_client
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def generate_executive_brief(self, topics, context=None):
        if not self.client:
            return self._default_brief(topics)

        topics_str = ", ".join(topics) if isinstance(topics, list) else topics
        ctx = context[:500] if context else "General leadership and organizational context"

        prompt = f"""
You are an Executive Intelligence analyst. Generate an executive brief covering these topics: {topics_str}

Context: {ctx}

Provide:
1. Executive summary with key takeaways
2. Strategic implications for each topic
3. Key metrics and indicators to monitor
4. Recommended decisions and actions
5. Risks and mitigation strategies
6. Cross-domain connections and insights

Return JSON:
{{
    "topics": {json.dumps(topics) if isinstance(topics, list) else f'["{topics}"]'},
    "executive_summary": "2-3 sentence overview",
    "strategic_implications": [{{"topic": "...", "implication": "...", "urgency": "high|medium|low"}}],
    "key_metrics": [{{"metric": "...", "current_state": "...", "target": "...", "trend": "improving|declining|stable"}}],
    "recommended_decisions": [{{"decision": "...", "rationale": "...", "timeframe": "..."}}],
    "risks": [{{"risk": "...", "probability": "high|medium|low", "mitigation": "..."}}],
    "cross_domain_connections": [{{"domains": ["..."], "insight": "...", "action": "..."}}]
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an Executive Intelligence analyst. Output ONLY valid JSON."},
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
            print(f"Executive brief error: {e}")
            return self._default_brief(topics)

    def _default_brief(self, topics):
        return {
            "topics": [topics] if isinstance(topics, str) else topics,
            "executive_summary": "Strategic overview of key leadership and organizational topics affecting the business.",
            "strategic_implications": [
                {"topic": topics[0] if isinstance(topics, list) else topics, "implication": "Significant impact on organizational direction", "urgency": "high"},
            ],
            "key_metrics": [
                {"metric": "Organizational health", "current_state": "Monitoring", "target": "Improvement", "trend": "stable"},
            ],
            "recommended_decisions": [
                {"decision": "Prioritize leadership development", "rationale": "Direct impact on organizational performance", "timeframe": "This quarter"},
            ],
            "risks": [
                {"risk": "Change resistance", "probability": "medium", "mitigation": "Structured change management program"},
            ],
            "cross_domain_connections": [
                {"domains": ["Leadership", "Culture", "Strategy"], "insight": "Integrated approach yields better outcomes", "action": "Align initiatives across domains"},
            ],
        }

    def synthesize_video_insights(self, video_data):
        if not self.client or not video_data:
            return {"summary": "No video data available", "key_takeaways": []}

        titles = [v.get("title", "Untitled") for v in video_data[:5]]
        prompt = f"""
Synthesize key executive insights from these leadership video titles:
{chr(10).join('- ' + t for t in titles)}

Provide a concise executive summary of the key themes, patterns, and actionable insights.

Return JSON:
{{
    "key_themes": ["theme1", "theme2"],
    "executive_summary": "Brief synthesis",
    "actionable_insights": ["insight1", "insight2"],
    "knowledge_gaps": ["gap1", "gap2"]
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an Executive Intelligence analyst. Output ONLY valid JSON."},
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
        except Exception:
            return {"key_themes": [], "executive_summary": "Analysis unavailable", "actionable_insights": [], "knowledge_gaps": []}

    def extract_from_corpus(self, corpus_data, registry_data, video_id=None):
        """Auto-extract executive intelligence insights. Scoped per-video if video_id provided."""
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
You are an Executive Intelligence analyst. Synthesize the following ingested video content into an executive brief{scope_hint}.

Video Titles:
{titles_text}

Transcript Excerpts:
{full_text}

Synthesize:
1. Executive summary with key takeaways from all content
2. Strategic implications for leadership and the organization
3. Key metrics and indicators discussed
4. Recommended decisions and actions based on content
5. Risks and mitigation strategies implied
6. Cross-domain connections across videos

Return JSON:
{{
    "video_count": {len(registry_data or [])},
    "segment_count": {len(corpus_data)},
    "scope": "per-video" if {"'"+video_id+"'" if video_id else "None"} else "global",
    "video_id": '{video_id if video_id else "all"}',
    "executive_summary": "2-3 sentence overview of all content",
    "key_themes": ["theme1", "theme2"],
    "strategic_implications": [{{"topic": "...", "implication": "...", "urgency": "high|medium|low"}}],
    "key_metrics": [{{"metric": "...", "current_state": "...", "trend": "improving|declining|stable"}}],
    "recommended_decisions": [{{"decision": "...", "rationale": "...", "timeframe": "..."}}],
    "risks": [{{"risk": "...", "probability": "high|medium|low", "mitigation": "..."}}],
    "cross_domain_connections": [{{"domains": ["..."], "insight": "...", "action": "..."}}]
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an Executive Intelligence analyst. Output ONLY valid JSON."},
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
            print(f"Corpus executive extraction error: {e}")
            return self._default_corpus_extraction(corpus_data, registry_data, video_id)

    def _default_corpus_extraction(self, corpus_data, registry_data, video_id=None):
        all_text = " ".join(s.get("transcript", "") for s in corpus_data[:30]).lower()
        detected_themes = []
        for theme in ["strategy", "culture", "innovation", "change", "growth",
                       "performance", "talent", "communication", "vision", "execution"]:
            if theme in all_text:
                detected_themes.append(theme.title())
        return {
            "video_count": len(registry_data or []),
            "segment_count": len(corpus_data),
            "scope": "per-video" if video_id else "global",
            "video_id": video_id or "all",
            "executive_summary": f"Synthesized insights from {len(registry_data or [])} videos covering leadership development and organizational effectiveness.",
            "key_themes": detected_themes[:6] or ["Leadership", "Strategy", "Culture"],
            "strategic_implications": [
                {"topic": t, "implication": f"Content provides insights on {t.lower()}", "urgency": "medium"}
                for t in detected_themes[:3]
            ] or [{"topic": "Leadership", "implication": "Cross-video themes inform organizational strategy", "urgency": "high"}],
            "key_metrics": [{"metric": "Content coverage", "current_state": f"{len(registry_data or [])} videos", "trend": "improving"}],
            "recommended_decisions": [{"decision": "Review all video insights for strategic alignment", "rationale": "Content spans multiple domains", "timeframe": "This quarter"}],
            "risks": [{"risk": "Knowledge silos", "probability": "medium", "mitigation": "Cross-functional review sessions"}],
            "cross_domain_connections": [{"domains": ["Leadership", "Strategy", "Culture"], "insight": "Integrated approach yields better outcomes", "action": "Align initiatives across domains"}],
        }
