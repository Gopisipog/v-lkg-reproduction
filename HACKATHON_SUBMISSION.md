# 🎬 CineGraph Studio Agent
**Submission for Google Cloud Agentic Cinema: The Blockbuster Hackathon**

---

## 📌 Project Overview
**CineGraph Studio Agent** is an autonomous multi-agent studio system designed for **filmmakers, screenwriters, and production crews**. 

In modern film and television production, creative teams drown in unstructured assets: hundreds of hours of raw camera rushes, multiple screenplay revisions, historical continuity disputes, and market research. **CineGraph** transforms this creative chaos into a structured, queryable cinematic knowledge graph with:
- **Multimodal Video Grounding**: Time-aligned scene decomposition using Google Cloud Speech-to-Text and Gemini 2.5 Flash.
- **Autonomous Screenplay Fact-Checking**: Live open-web verification of period dialogue, props, and historical events using the **Parallel Search API (`parallel-web` SDK)**.
- **Box Office Comps & Production Intelligence**: Instant retrieval of commercial precedents, budget comps, and audience retention metrics.
- **IP & Rights Clearance Engine**: Automated legal risk analysis on brand mentions, song lyrics, and public domain status.
- **Interactive Director Co-Pilot**: Multi-turn conversational studio advisor grounded in real-time web intelligence.

---

## 🏆 Chosen Partner Track & Hackathon Themes
- **Partner Track**: **Parallel Web Systems**
- **Runtime SDK**: `parallel-web` (version 0.4+)
- **Architecture**: Decoupled, standalone autonomous multi-agent platform (`cinegraph_studio/`)
  - **Theme 1: The Visionary Director** (`cinegraph_studio.agents.director`)
  - **Theme 2: The Technical Producer** (`cinegraph_studio.agents.producer`)
  - **Theme 3: The Studio Head** (`cinegraph_studio.agents.studio_head`)
- **Standalone Execution**: `python run_studio.py` launches the dedicated Studio Backlot UI on port 8501.
- **Verification**: Actively imported and called in `cinegraph_studio/integrations/parallel_client.py` and `cinegraph_studio/agents/producer.py` via `Parallel(api_key=...).beta.search()`.

---

## 📋 Devpost Submission Form Details

### Project Title
**CineGraph Studio Agent: Autonomous Cinema & Media Intelligence**

### Elevator Pitch
*Transforming screenplay drafts, raw rushes, and studio chaos into a seamless cinematic production with Google Cloud Gemini 2.5 Flash and Parallel Web Systems.*

### Hosted Project URL
[https://v-lkg-826803329504.us-central1.run.app](https://v-lkg-826803329504.us-central1.run.app)

### Open Source Repository URL
[https://github.com/Gopisipog/v-lkg-reproduction](https://github.com/Gopisipog/v-lkg-reproduction)  
*License*: Apache License 2.0 (detectable in root `LICENSE`).

---

### Inspiration
Film sets and writer rooms lose millions of dollars to avoidable continuity errors, inaccurate historical dialogue, and copyright infringement discoveries late in post-production. At the same time, directors and screenwriters lack real-time access to commercial box-office comps and historical archival evidence when pitching or shooting scenes. We asked: *What if an autonomous AI agent network could ingest video rushes and scripts, decompose dramatic beats with Gemini, and ground every creative decision against the live web with Parallel?*

### What It Does
1. **Time-Aligned Video & Scene Ingestion**: Ingests raw video clips, dailies, or YouTube masterclasses, extracting dialogue with millisecond precision and generating instant video jump bookmarks (`?t=XXs`).
2. **Dramatic Beat & Character Arc Breakdown**: Gemini 2.5 Flash analyzes the scene, identifying emotional beats, character objectives, and obstacles.
3. **Screenplay Fact-Checking (Parallel Web Systems)**: The agent identifies factual, historical, or technological claims made in dialogue (e.g., *"Arriflex 35 BL was used during the 1972 Munich Olympics"*) and validates them against live open-web records using Parallel Search.
4. **Commercial Comps & Box Office Precedents**: Parallel retrieves recent commercial comps, production budgets, and box-office outcomes matching the scene tone and logline.
5. **IP & Rights Clearance Engine**: Automatically scans dialogue for trademarked terms, copyrighted song riffs, or real personas, assessing public domain status.
6. **Studio Director Co-Pilot**: Interactive chat where directors can ask technical questions (*"What lenses give authentic 1970s anamorphic flares?"*) and receive Gemini answers backed by clickable Parallel web sources.

### How We Built It
- **AI Core**: 100% powered by **Google Cloud Gemini 2.5 Flash** via `google-genai` and Google Cloud Speech-to-Text. Strictly compliant with Rule 7.B (zero non-GCP AI fallbacks).
- **Partner Integration**: Implemented in `cinegraph_studio/integrations/parallel_client.py` using the official `parallel-web` Python SDK (`client.beta.search(mode="one-shot")`).
- **Backend & APIs**: Built in `cinegraph_studio/server.py` with standalone REST endpoints (`/api/status`, `/api/analyze-scene`, `/api/comps`, `/api/verify-period`, `/api/clearance`, `/api/copilot`, `/api/mcp/tools`).
- **Frontend Experience**: Dedicated CineGraph Studio Backlot Cockpit served from `cinegraph_studio/static/index.html` with real-time Director beat breakdowns, live Parallel box office comps, archival fact-checks, and Studio Head governance audits.
- **Standalone Execution**: Launchable independently via `python run_studio.py`.
- **Hosting**: Containerized with Docker and deployable serverlessly to **Google Cloud Run**.

### Google Cloud & Partner Compliance
- **Google Cloud Services Used**:
  - **Vertex AI / Gemini 2.5 Flash (`google-genai`)**: Primary multimodal reasoning and structured extraction engine.
  - **Cloud Speech-to-Text**: High-fidelity audio transcription with word-level timestamps.
  - **Cloud Storage (GCS)**: Persistent storage for production dossiers and transcripts.
  - **Cloud Run**: Serverless container hosting for the web and API platform.
- **Partner Tooling**:
  - **Parallel Web Systems**: Direct runtime integration in Python code (`from parallel import Parallel`).

### Challenges We Overcame
1. **Rule 7.B AI Isolation**: Completely auditing our legacy code to purge all OpenAI/DeepSeek fallbacks, standardizing 100% on `google-genai` while keeping the system robust and offline-testable.
2. **Deterministic Script Verification**: Structuring Gemini prompts to cleanly extract testable factual claims from dramatic dialogue so Parallel could search for definitive historical citations.
3. **Sub-second Latency**: Optimizing parallel tool execution so screenplay fact-checking, IP clearance, and comps retrieval execute simultaneously.

### Accomplishments We're Proud Of
- Passing all 39 automated tests (11 CineGraph Studio tests + 28 MCP tests).
- Seamlessly fusing Google Cloud Gemini 2.5 Flash with Parallel Web Systems into an intuitive, visually stunning Studio Cockpit.
- Providing clickable, time-aligned video bookmarks that jump directly to source footage.

### What's Next for CineGraph
- Live video stream monitoring directly from camera feeds (SDI / NDI over Cloud Run).
- Integration with Google Cloud Imagen 3 for automatic storyboard generation from screenplay beats.
- Multi-user collaborative script editing rooms for studio writing teams.