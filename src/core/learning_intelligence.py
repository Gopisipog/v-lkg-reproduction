import os
import json
from openai import OpenAI


class LearningIntelligenceEngine:
    """L&D Intelligence — AI Learning Assistant for CLOs and L&D Directors.
    Analyzes skills gaps, recommends learning paths, and tracks competency development."""

    def __init__(self, db_client=None):
        self.db = db_client
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def analyze_skills_gap(self, target_role, current_competencies):
        if not self.client:
            return self._default_skills_gap(target_role)

        comps_str = ", ".join(current_competencies) if current_competencies else "None specified"
        prompt = f"""
You are an L&D Intelligence analyst. Analyze the skills gap for someone targeting the role of "{target_role}".

Current competencies: {comps_str}

Based on leadership development best practices, identify:
1. Missing critical competencies
2. Recommended learning path with milestones
3. Estimated time to proficiency
4. Key resources and practice areas

Return JSON:
{{
    "target_role": "{target_role}",
    "current_competencies": {json.dumps(current_competencies)},
    "gap_analysis": ["gap1", "gap2", "gap3"],
    "learning_path": [{{"step": 1, "competency": "...", "resources": ["..."], "timeline": "..."}}],
    "estimated_time": "...",
    "priority_areas": ["area1", "area2"],
    "cross_video_connections": ["Relevant leadership video topics to watch"]
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an L&D Intelligence analyst. Output ONLY valid JSON."},
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
            print(f"Skills gap analysis error: {e}")
            return self._default_skills_gap(target_role)

    def _default_skills_gap(self, target_role):
        return {
            "target_role": target_role,
            "gap_analysis": ["Leadership fundamentals", "Strategic thinking", "Communication"],
            "learning_path": [
                {"step": 1, "competency": "Core Leadership", "resources": ["TED talks", "Leadership courses"], "timeline": "1-2 months"},
                {"step": 2, "competency": "Strategic Vision", "resources": ["Case studies", "Mentorship"], "timeline": "3-6 months"},
            ],
            "estimated_time": "6-12 months",
            "priority_areas": ["Emotional intelligence", "Decision-making", "Team building"],
        }

    def get_video_recommendations(self, competency):
        if not self.db or not self.db.driver:
            return {"videos": [], "message": "Neo4j not connected"}
        try:
            nodes = self.db.execute_read(
                "MATCH (n) WHERE n.name CONTAINS $keyword RETURN n.name AS name, labels(n)[0] AS type LIMIT 10",
                {"keyword": competency},
            ) or []
            return {"videos": nodes, "count": len(nodes)}
        except Exception as e:
            return {"videos": [], "error": str(e)}

    def extract_from_corpus(self, corpus_data, registry_data, video_id=None):
        """Auto-extract L&D intelligence insights from ingested video corpus.

        If `video_id` is provided, analysis is scoped to that single video.
        Otherwise analyzes across all ingested content.
        """
        if not corpus_data:
            return {"status": "no_data", "message": "No corpus data available."}

        # Filter to specific video if requested
        if video_id:
            corpus_data = [s for s in corpus_data if s.get("video_id") == video_id]
            registry_data = [v for v in (registry_data or []) if v.get("video_id") == video_id]
            if not corpus_data:
                return {"status": "no_data", "message": f"No data for video: {video_id}"}

        if not self.client:
            return self._default_corpus_extraction(corpus_data, registry_data, video_id)

        # Prepare context from registry
        video_titles = [v.get("title", "Untitled") for v in (registry_data or [])]
        titles_text = "\n".join(f"- {t}" for t in video_titles) or "No videos ingested"

        # Sample up to ~3000 chars of transcript
        full_text = " ".join(
            s.get("transcript", "") for s in corpus_data[:50]
        )[:3000]

        scope_hint = f" (scoped to video: {video_id})" if video_id else ""
        prompt = f"""
You are an L&D Intelligence analyst. Analyze the following ingested video knowledge base and extract learning & development insights{scope_hint}.

Video Titles:
{titles_text}

Transcript Excerpts:
{full_text}

Extract:
1. Key competencies discussed across the content
2. Identified skills gaps (what leaders need vs. what's covered)
3. Recommended learning paths derived from the content
4. Priority development areas
5. Cross-video connections (themes that appear in multiple videos)
6. Estimated time to proficiency for key roles

Return JSON:
{{
    "video_count": {len(registry_data or [])},
    "segment_count": {len(corpus_data)},
    "scope": "global" if not {'"'+video_id+'"' if video_id else 'None'} else "per-video",
    "video_id": '{video_id if video_id else "all"}',
    "key_competencies": ["comp1", "comp2"],
    "skills_gaps": [{{"gap": "...", "severity": "high|medium|low", "videos_addressing_it": ["..."]}}],
    "learning_paths": [{{"step": 1, "competency": "...", "source_videos": ["..."], "rationale": "..."}}],
    "priority_areas": ["area1", "area2"],
    "cross_video_themes": [{{"theme": "...", "video_count": 0, "description": "..."}}],
    "estimated_proficiency": {{"role": "emerging leader", "timeline": "6-12 months"}}
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an L&D Intelligence analyst. Output ONLY valid JSON."},
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
            print(f"Corpus L&D extraction error: {e}")
            return self._default_corpus_extraction(corpus_data, registry_data, video_id)

    def _default_corpus_extraction(self, corpus_data, registry_data, video_id=None):
        all_text = " ".join(s.get("transcript", "") for s in corpus_data[:30]).lower()
        detected_comps = []
        for comp in ["communication", "strategic planning", "emotional intelligence", 
                       "decision making", "team building", "conflict resolution",
                       "coaching", "mentoring", "delegation", "vision"]:
            if comp in all_text:
                detected_comps.append(comp.title())
        vid_label = video_id or "all"
        return {
            "video_count": len(registry_data or []),
            "segment_count": len(corpus_data),
            "scope": "per-video" if video_id else "global",
            "video_id": vid_label,
            "key_competencies": detected_comps[:8] or ["Communication", "Strategic Thinking", "Team Leadership"],
            "skills_gaps": [
                {"gap": "Advanced strategic execution", "severity": "medium", "videos_addressing_it": ["See Strategy Map tab"]}
            ],
            "learning_paths": [
                {"step": 1, "competency": "Core Leadership", "source_videos": [], "rationale": "Foundation for all leadership roles"}
            ],
            "priority_areas": detected_comps[:5] or ["Communication", "Emotional Intelligence", "Decision Making"],
            "cross_video_themes": [{"theme": "Leadership fundamentals", "video_count": len(registry_data or []), "description": "Core concepts appearing across multiple videos"}],
            "estimated_proficiency": {"role": "emerging leader", "timeline": "6-12 months"},
        }
