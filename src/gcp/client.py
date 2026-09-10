"""Shared Google Cloud / Gemini client for CineGraph / V-LKG.

This module provides a single, reusable client strictly powered by
Google Cloud Gemini (via the google-genai SDK) to ensure full compliance
with Google Cloud Hackathon requirements.

Environment variables:
    GEMINI_API_KEY        — Google AI Studio key (preferred)
    GOOGLE_API_KEY        — alias for GEMINI_API_KEY
    GOOGLE_CLOUD_PROJECT  — GCP project ID (for Vertex AI / Cloud services)
    GOOGLE_CLOUD_LOCATION — GCP region (default: us-central1)
"""

from __future__ import annotations

import json
import os
import re
from typing import Any


# ── Model defaults ────────────────────────────────────────────────────────────

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _strip_fences(text: str) -> str:
    """Strip markdown code fences that LLMs sometimes wrap JSON in."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def _safe_json(text: str) -> Any:
    """Parse JSON from LLM text, tolerating fences and common errors."""
    cleaned = _strip_fences(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find a JSON object/array substring
        for start, end in [("{", "}"), ("[", "]")]:
            si = cleaned.find(start)
            ei = cleaned.rfind(end)
            if si != -1 and ei > si:
                try:
                    return json.loads(cleaned[si: ei + 1])
                except json.JSONDecodeError:
                    pass
    return None


# ── Primary client: Google Gemini ─────────────────────────────────────────────

class GeminiClient:
    """Thin wrapper around the Google GenAI SDK.

    Usage::

        client = GeminiClient()
        text   = client.chat("Explain servant leadership in 3 bullet points.")
        obj    = client.chat_json("Return a JSON list of leadership traits.")
    """

    def __init__(self, model: str = GEMINI_MODEL):
        self.model = model
        self._client = None

        gemini_key = (
            os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
        )

        if gemini_key:
            try:
                from google import genai  # type: ignore
                self._client = genai.Client(api_key=gemini_key)
                print(f"[GCP] Gemini client initialised (model={model}).")
            except Exception as exc:
                print(f"[GCP] Failed to initialize google-genai client: {exc}")
        else:
            # Check for GCP Application Default Credentials
            try:
                from google import genai  # type: ignore
                project = os.environ.get("GOOGLE_CLOUD_PROJECT")
                location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
                if project:
                    self._client = genai.Client(vertexai=True, project=project, location=location)
                    print(f"[GCP] Vertex AI Gemini client initialised (project={project}, location={location}).")
            except Exception:
                pass

        if self._client is None:
            print("[GCP] INFO: GEMINI_API_KEY / GOOGLE_CLOUD_PROJECT not configured. Running in offline/mock mode.")

    @property
    def available(self) -> bool:
        return self._client is not None

    def chat(self, prompt: str, system: str = "") -> str:
        """Send a prompt to Google Gemini and return the plain-text response."""
        if not self.available:
            return ""

        try:
            full_prompt = f"{system}\n\n{prompt}".strip() if system else prompt
            response = self._client.models.generate_content(
                model=self.model,
                contents=full_prompt,
            )
            return response.text.strip()
        except Exception as exc:
            print(f"[GCP] Gemini API call failed: {exc}")
            return ""

    def chat_json(self, prompt: str, system: str = "Output ONLY valid JSON.") -> Any:
        """Send a prompt and parse the response as JSON. Returns None on failure."""
        raw = self.chat(prompt, system=system)
        if not raw:
            return None
        result = _safe_json(raw)
        if result is None:
            print(f"[GCP] JSON parse failed. Raw response: {raw[:200]}")
        return result


# ── Singleton helper ──────────────────────────────────────────────────────────

_default_client: GeminiClient | None = None


def get_client(model: str = GEMINI_MODEL) -> GeminiClient:
    """Return a module-level singleton GeminiClient (lazy-initialised)."""
    global _default_client
    if _default_client is None or _default_client.model != model:
        _default_client = GeminiClient(model=model)
    return _default_client
