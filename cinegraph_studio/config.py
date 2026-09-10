"""Configuration and environment management for CineGraph Studio.

Strict compliance with Google Cloud Agentic Cinema rules:
- Solely Google Cloud AI (Gemini 2.5 Flash via google-genai)
- Parallel Web Systems (parallel-web SDK) partner integration
"""

import os
from typing import Optional

# Google Cloud & Gemini configuration
GEMINI_API_KEY: Optional[str] = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
GOOGLE_CLOUD_PROJECT: Optional[str] = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT_ID")
GEMINI_MODEL: str = os.environ.get("CINEGRAPH_GEMINI_MODEL", "gemini-2.5-flash")

# Parallel Web Systems partner configuration
PARALLEL_API_KEY: Optional[str] = os.environ.get("PARALLEL_API_KEY")

# Server configuration
HOST: str = os.environ.get("CINEGRAPH_HOST", "0.0.0.0")
PORT: int = int(os.environ.get("CINEGRAPH_PORT", "8501"))

# Studio Metadata
PROJECT_NAME: str = "CineGraph Studio Agent"
HACKATHON_TRACK: str = "Parallel Web Systems (parallel-web SDK)"
HACKATHON_NAME: str = "Google Cloud Agentic Cinema: The Blockbuster Hackathon"
