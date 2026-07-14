import os
import json
from openai import OpenAI


class ComplianceIntelligenceEngine:
    """Compliance & Policy — Compliance Memory for Legal/HR teams.
    Tracks policy requirements, compliance risk, and regulatory changes."""

    def __init__(self, db_client=None):
        self.db = db_client
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def analyze_compliance_risk(self, policy_area, context):
        if not self.client:
            return self._default_compliance_analysis(policy_area)

        prompt = f"""
You are a Compliance Intelligence analyst. Analyze compliance risks for "{policy_area}".

Context: {context[:500]}

Provide:
1. Key compliance requirements and obligations
2. Risk assessment with severity levels
3. Recommended controls and mitigations
4. Monitoring and reporting cadence
5. Related policy areas to review
6. Update frequency recommendations

Return JSON:
{{
    "policy_area": "{policy_area}",
    "requirements": [{{"requirement": "...", "priority": "critical|high|medium|low", "deadline": "..."}}],
    "risk_assessment": [{{"risk": "...", "severity": "critical|high|medium|low", "mitigation": "..."}}],
    "recommended_controls": ["control1", "control2"],
    "monitoring_plan": {{"frequency": "...", "method": "...", "owner": "..."}},
    "related_policies": ["policy1", "policy2"],
    "update_recommendation": "How often to review and update"
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Compliance Intelligence analyst. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            return json.loads(content)
        except Exception as e:
            print(f"Compliance analysis error: {e}")
            return self._default_compliance_analysis(policy_area)

    def _default_compliance_analysis(self, policy_area):
        return {
            "policy_area": policy_area,
            "requirements": [
                {"requirement": "Document and maintain policy", "priority": "high", "deadline": "Quarterly review"},
                {"requirement": "Staff training and awareness", "priority": "high", "deadline": "Annual"},
            ],
            "risk_assessment": [
                {"risk": "Non-compliance with updated regulations", "severity": "high", "mitigation": "Regular audits and updates"},
            ],
            "recommended_controls": ["Regular compliance audits", "Staff training programs", "Documentation management"],
            "monitoring_plan": {"frequency": "Quarterly", "method": "Automated compliance scanning", "owner": "Compliance officer"},
            "related_policies": ["Data protection", "Code of conduct", "Risk management"],
            "update_recommendation": "Review quarterly or when regulations change",
        }

    def scan_transcript_for_compliance(self, transcript_segments, policy_keywords):
        findings = []
        for seg in transcript_segments:
            text = seg.get("transcript", "").lower()
            for keyword in policy_keywords:
                if keyword.lower() in text:
                    findings.append({
                        "keyword": keyword,
                        "context": text[:150],
                        "timestamp": seg.get("start_time", 0),
                        "video_id": seg.get("video_id"),
                    })
        return findings

    def extract_from_corpus(self, corpus_data, registry_data, video_id=None):
        """Auto-extract compliance & policy intelligence. Scoped per-video if video_id provided."""
        if not corpus_data:
            return {"status": "no_data", "message": "No corpus data available."}

        if video_id:
            corpus_data = [s for s in corpus_data if s.get("video_id") == video_id]
            registry_data = [v for v in (registry_data or []) if v.get("video_id") == video_id]
            if not corpus_data:
                return {"status": "no_data", "message": f"No data for video: {video_id}"}

        policy_keywords = [
            "policy", "compliance", "regulation", "legal", "risk", "governance",
            "standard", "requirement", "audit", "ethics", "code of conduct",
            "data protection", "privacy", "security", "mandate", "obligation",
            "law", "statute", "guideline", "framework", "procedure"
        ]
        all_findings = self.scan_transcript_for_compliance(corpus_data, policy_keywords)

        if not self.client:
            return self._default_corpus_extraction(corpus_data, registry_data, video_id, all_findings)

        video_titles = [v.get("title", "Untitled") for v in (registry_data or [])]
        titles_text = "\n".join(f"- {t}" for t in video_titles) or "No videos ingested"
        full_text = " ".join(s.get("transcript", "") for s in corpus_data[:50])[:3000]
        scope_hint = f" (scoped to video: {video_id})" if video_id else ""

        prompt = f"""
You are a Compliance Intelligence analyst. Analyze the following ingested video content for compliance and policy insights{scope_hint}.

Video Titles:
{titles_text}

Transcript Excerpts:
{full_text}

Policy keywords matched ({len(all_findings)}): {json.dumps(list(set(f['keyword'] for f in all_findings))[:10])}

Extract:
1. Policy areas and compliance topics discussed in the content
2. Risk-related themes and their severity
3. Recommended controls based on content patterns
4. Monitoring cadence suggestions
5. Related policy areas to review
6. Update recommendations

Return JSON:
{{
    "video_count": {len(registry_data or [])},
    "segment_count": {len(corpus_data)},
    "scope": "per-video" if {"'"+video_id+"'" if video_id else "None"} else "global",
    "video_id": '{video_id if video_id else "all"}',
    "keyword_findings_count": {len(all_findings)},
    "policy_topics_discussed": [{{"topic": "...", "mentions": 0, "severity": "critical|high|medium|low"}}],
    "risk_assessment": [{{"risk": "...", "severity": "critical|high|medium|low", "mitigation": "..."}}],
    "recommended_controls": ["control1", "control2"],
    "monitoring_plan": {{"frequency": "...", "method": "..."}},
    "related_policies": ["policy1", "policy2"],
    "update_recommendation": "How often to review based on content"
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Compliance Intelligence analyst. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            return json.loads(content)
        except Exception as e:
            print(f"Corpus compliance extraction error: {e}")
            return self._default_corpus_extraction(corpus_data, registry_data, video_id, all_findings)

    def _default_corpus_extraction(self, corpus_data, registry_data, video_id=None, findings=None):
        return {
            "video_count": len(registry_data or []),
            "segment_count": len(corpus_data),
            "scope": "per-video" if video_id else "global",
            "video_id": video_id or "all",
            "keyword_findings_count": len(findings or []),
            "policy_topics_discussed": [{"topic": "Leadership ethics", "mentions": len(findings or []), "severity": "medium"}],
            "risk_assessment": [
                {"risk": "Inconsistent policy application", "severity": "medium", "mitigation": "Regular training sessions"}
            ],
            "recommended_controls": ["Regular policy reviews", "Staff training on updates"],
            "monitoring_plan": {"frequency": "Quarterly", "method": "Content audit"},
            "related_policies": ["Code of conduct", "Training compliance"],
            "update_recommendation": "Review policy framework annually",
        }
