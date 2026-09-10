"""The Visionary Director Agent.

Corresponds to Hackathon Theme 1: Agent Architecture & Workflow Automation.
Orchestrates creative workflows: scene continuity, beat detection, character objectives,
and staging instructions using Google Cloud Gemini 2.5 Flash.
"""

import json
import os
from typing import Dict, Any, List, Optional
from cinegraph_studio.config import GEMINI_API_KEY, GEMINI_MODEL


class VisionaryDirectorAgent:
    """The Director Agent: Breaks down scenes into dramatic beats, emotional arcs, and staging."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = GEMINI_MODEL
        self._genai_client = None

        if self.api_key:
            try:
                from google import genai
                self._genai_client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[CineGraph:Director] Gemini client notice: {e}")
                self._genai_client = None

    def analyze_scene_beats(
        self,
        scene_title: str,
        transcript_text: str,
        start_time: float = 0.0,
        end_time: float = 60.0
    ) -> Dict[str, Any]:
        """Analyze scene dialogue and extract dramatic beats, pacing, and visual staging."""
        prompt = f"""
You are the Visionary Director on an elite Hollywood film production lot.
Break down this scene transcript into cinematic beats, character objectives, emotional tension, and staging.

Scene: {scene_title} ({start_time:.1f}s - {end_time:.1f}s)
Transcript:
\"\"\"{transcript_text}\"\"\"

Return ONLY a valid JSON object matching this schema:
{{
    "scene_title": "{scene_title}",
    "duration_seconds": {end_time - start_time},
    "pacing": "Deliberate / Escalating / High-Energy",
    "emotional_climax_timestamp": "MM:SS",
    "dramatic_beats": [
        {{
            "beat_number": 1,
            "beat_type": "Inciting Action / Reversal / Confrontation",
            "timecode": "MM:SS",
            "description": "Short explanation",
            "subtext": "What is unsaid beneath the dialogue"
        }}
    ],
    "characters": [
        {{
            "name": "Character Name",
            "objective": "What they desperately want in this moment",
            "obstacle": "What prevents them from getting it",
            "emotional_state": "Vulnerable / Defiant / Calculating"
        }}
    ],
    "staging_notes": {{
        "camera_movement": "Steadicam push-in / Handheld medium close-up",
        "lighting_palette": "High-contrast chiaroscuro / Amber tungsten",
        "sound_design": "Subtle low drone / Sudden silence"
    }}
}}
"""
        if self._genai_client:
            try:
                response = self._genai_client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                txt = response.text.strip()
                if "```json" in txt:
                    txt = txt.split("```json")[1].split("```")[0].strip()
                elif "```" in txt:
                    txt = txt.split("```")[1].split("```")[0].strip()
                return json.loads(txt)
            except Exception as e:
                return self._fallback_beats(scene_title, transcript_text, start_time, end_time, f"Gemini fallback: {e}")

        return self._fallback_beats(scene_title, transcript_text, start_time, end_time, "Running in deterministic studio director mode")

    def _fallback_beats(self, title: str, transcript: str, st: float, et: float, reason: str) -> Dict[str, Any]:
        """Deterministic director scene breakdown for offline/mock test execution."""
        words = transcript.split()
        char_a = words[0].title() if words else "Lead"
        char_b = words[1].title() if len(words) > 1 else "Counterpart"
        
        m_st = int(st // 60)
        s_st = int(st % 60)
        mid = (st + et) / 2
        m_mid = int(mid // 60)
        s_mid = int(mid % 60)

        return {
            "scene_title": title,
            "duration_seconds": et - st,
            "pacing": "Escalating",
            "emotional_climax_timestamp": f"{m_mid:02d}:{s_mid:02d}",
            "dramatic_beats": [
                {
                    "beat_number": 1,
                    "beat_type": "Inciting Question",
                    "timecode": f"{m_st:02d}:{s_st:02d}",
                    "description": f"Initial confrontation established over {title.lower()}.",
                    "subtext": "Testing boundaries and establishing unspoken hierarchy."
                },
                {
                    "beat_number": 2,
                    "beat_type": "Dramatic Reversal",
                    "timecode": f"{m_mid:02d}:{s_mid:02d}",
                    "description": "Underlying conflict surfaces as hidden intentions are voiced.",
                    "subtext": "Fear of losing control in high-stakes environment."
                }
            ],
            "characters": [
                {
                    "name": char_a,
                    "objective": "Establish moral and strategic dominance.",
                    "obstacle": "Reluctance of counterpart to commit.",
                    "emotional_state": "Focused and calculating"
                },
                {
                    "name": char_b,
                    "objective": "Preserve independence without triggering open conflict.",
                    "obstacle": "Aggressive probing from the lead.",
                    "emotional_state": "Defiant and guarded"
                }
            ],
            "staging_notes": {
                "camera_movement": "Slow 35mm Steadicam track revolving around subject",
                "lighting_palette": "Deep teal backlighting with warm key light on facial contours",
                "sound_design": "Subtle room tone that drops away at the moment of confrontation"
            },
            "director_notice": reason
        }
