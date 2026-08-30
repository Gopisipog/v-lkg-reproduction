"""Shared Google Cloud / Gemini client for V-LKG.

This module provides a single, reusable client that:
  - Connects to Google Gemini (via google-genai SDK) as the primary LLM
  - Falls back to OpenAI-compatible clients if GEMINI_API_KEY is not set
  - Wraps the call interface so every intelligence engine just calls
    ``GeminiClient().chat(prompt)`` with no provider-specific boilerplate.

Environment variables (any of these is sufficient):
    GEMINI_API_KEY       — Google AI Studio key  (preferred)
    GOOGLE_API_KEY       — alias for GEMINI_API_KEY
    GOOGLE_CLOUD_PROJECT — GCP project ID (for Vertex AI / Cloud services)
    GOOGLE_CLOUD_LOCATION — GCP region (default: us-central1)
    OPENAI_API_KEY       — fallback if Gemini unavailable
    DEEPSEEK_API_KEY     — fallback if both Gemini and OpenAI unavailable
"""

from __future__ import annotations

import json
import os
import re
from typing import Any


# ── Model defaults ────────────────────────────────────────────────────────────

GEMINI_MODEL   = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
OPENAI_MODEL   = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
DEEPSEEK_MODEL = "deepseek-chat"


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
        self._fallback = None          # OpenAI-compatible fallback client
        self._fallback_model: str = ""

        gemini_key = (
            os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
        )

        if gemini_key:
            try:
                from google import genai  # type: ignore
                self._client = genai.Client(api_key=gemini_key)
                print(f"[GCP] Gemini client initialised (model={model}).")
            except ImportError:
                print("[GCP] google-genai not installed; falling back to OpenAI.")

        if self._client is None:
            # Try OpenAI → DeepSeek fallbacks
            from openai import OpenAI  # type: ignore
            deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
            openai_key   = os.environ.get("OPENAI_API_KEY")
            if deepseek_key:
                self._fallback = OpenAI(
                    api_key=deepseek_key,
                    base_url="https://api.deepseek.com",
                )
                self._fallback_model = DEEPSEEK_MODEL
                print("[GCP] Using DeepSeek fallback.")
            elif openai_key:
                self._fallback = OpenAI(api_key=openai_key)
                self._fallback_model = OPENAI_MODEL
                print("[GCP] Using OpenAI fallback.")
            else:
                print("[GCP] WARNING: No LLM API key found. Calls will return empty strings.")

    @property
    def available(self) -> bool:
        return self._client is not None or self._fallback is not None

    def chat(self, prompt: str, system: str = "") -> str:
        """Send a prompt and return the plain-text response."""
        if not self.available:
            return ""

        try:
            if self._client is not None:
                full_prompt = f"{system}\n\n{prompt}".strip() if system else prompt
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                )
                return response.text.strip()
            else:
                messages = []
                if system:
                    messages.append({"role": "system", "content": system})
                messages.append({"role": "user", "content": prompt})
                response = self._fallback.chat.completions.create(
                    model=self._fallback_model,
                    messages=messages,
                    temperature=0.3,
                )
                return response.choices[0].message.content.strip()
        except Exception as exc:
            print(f"[GCP] LLM call failed: {exc}")
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
