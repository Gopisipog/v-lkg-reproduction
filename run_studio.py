"""CineGraph Studio Standalone Launcher.

Run this script to start the CineGraph Studio autonomous cinema backlot platform:
    python run_studio.py

Built for the Google Cloud Agentic Cinema Hackathon (Parallel Web Systems Track).
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cinegraph_studio.config import HOST, PORT, PROJECT_NAME, HACKATHON_NAME, HACKATHON_TRACK
from cinegraph_studio.server import start_server


def main():
    print("=" * 70)
    print(f"🎬 {PROJECT_NAME.upper()} — AUTONOMOUS CINEMA BACKLOT")
    print("=" * 70)
    print(f"🌟 Hackathon: {HACKATHON_NAME}")
    print(f"🤝 Partner Track: {HACKATHON_TRACK}")
    print(f"🤖 Primary AI: Google Cloud Gemini 2.5 Flash (google-genai)")
    print(f"🌐 Web Intelligence: Parallel Web Systems (parallel-web SDK)")
    print(f"🚀 Studio Dashboard: http://localhost:{PORT}")
    print("=" * 70)
    print(f"Starting server on http://{HOST}:{PORT} ... (Press Ctrl+C to stop)")
    start_server()


if __name__ == "__main__":
    main()
