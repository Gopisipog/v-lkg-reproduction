"""The Technical Producer Agent.

Corresponds to Hackathon Theme 2: Enterprise Data & Context Infrastructure.
Manages production intelligence pipelines, integrating open-web archival facts,
box office comparables, and intellectual property data via Parallel Web Systems.
"""

from typing import Dict, Any, List, Optional
from cinegraph_studio.integrations.parallel_client import ParallelStudioClient


class TechnicalProducerAgent:
    """The Producer Agent: Builds context packages, performs clearance checks, and sources comps."""

    def __init__(self, parallel_client: Optional[ParallelStudioClient] = None):
        self.parallel = parallel_client or ParallelStudioClient()

    def build_scene_intelligence_context(
        self,
        scene_title: str,
        transcript_text: str,
        period_setting: str = "Contemporary",
        genre: str = "Drama"
    ) -> Dict[str, Any]:
        """Assemble a complete external intelligence context package for a scene."""
        # 1. Period authenticity verification via Parallel Search
        sample_claim = transcript_text[:120].strip() or scene_title
        fact_check = self.parallel.verify_period_authenticity(sample_claim, period_setting)

        # 2. Box office and audience retention comparables via Parallel Search
        comps = self.parallel.fetch_boxoffice_comps(genre, scene_title)

        # 3. Scan potential brand or trademark entities in the transcript
        detected_entities = [w.strip(".,!?\"'") for w in transcript_text.split() if w.istitle() and len(w) > 4][:3]
        clearance_reports = []
        for ent in detected_entities:
            clearance_reports.append(self.parallel.ip_and_rights_clearance(ent, "Brand/Entity"))

        return {
            "producer_status": "READY",
            "scene_title": scene_title,
            "period_setting": period_setting,
            "genre": genre,
            "fact_checking": fact_check,
            "boxoffice_comps": comps,
            "clearance_reports": clearance_reports,
            "pipeline_source": "Parallel Web Systems (parallel-web SDK v0.4.2)"
        }

    def evaluate_budget_and_comps(self, genre: str, logline: str) -> Dict[str, Any]:
        """Query real-world box office precedent and commercial viability."""
        return self.parallel.fetch_boxoffice_comps(genre, logline)

    def check_rights_and_clearances(self, entity_name: str, entity_type: str = "Brand") -> Dict[str, Any]:
        """Scan copyright, brand usage, and trademark clearance."""
        return self.parallel.ip_and_rights_clearance(entity_name, entity_type)
