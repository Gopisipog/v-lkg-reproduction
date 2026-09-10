# 🎬 CineGraph Studio Agent: Autonomous Cinema & Media Intelligence

[![Google Cloud Agentic Cinema Hackathon](https://img.shields.io/badge/Hackathon-Google%20Cloud%20Agentic%20Cinema-amber)](HACKATHON_SUBMISSION.md)
[![Partner Track](https://img.shields.io/badge/Partner%20Track-Parallel%20Web%20Systems-cyan)](https://agentic-cinema.devpost.com/details/parallel-resources)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![GCP Cloud Run](https://img.shields.io/badge/Hosted%20On-GCP%20Cloud%20Run-blue)](https://v-lkg-826803329504.us-central1.run.app)

> **Submission for Google Cloud Agentic Cinema: The Blockbuster Hackathon**  
> **Chosen Track**: **Parallel Web Systems (parallel-web SDK)**  
> **Live Production URL**: [https://v-lkg-826803329504.us-central1.run.app](https://v-lkg-826803329504.us-central1.run.app)

An autonomous multi-agent studio system for **filmmakers, screenwriters, and production crews**. CineGraph transforms raw video rushes, screenplays, and studio dailies into an intelligent cinematic knowledge graph with time-aligned multimodal video grounding, automated scene decomposition, screenplay fact-checking, and live film industry research powered by **Google Cloud Gemini 2.5 Flash** and **Parallel Web Systems**.

---

## 🌟 Core Features for Media & Entertainment

1. **Multimodal Time-Aligned Video Breakdown**: Synchronizes video audio (Google Cloud Speech-to-Text) with visual cues and screenplay transcripts to construct precise timestamped scene bookmarks (`?t=XXs`).
2. **Autonomous Screenplay Fact-Checking (Parallel Web Systems)**: Grounded verification of historical, scientific, or cultural claims in dialogue against the real-time open-web index via the official `parallel-web` Python SDK.
3. **Box Office Comps & Production Intelligence**: Live industry retrieval of commercial precedents, budget comps, and audience retention metrics for screenplay pitches.
4. **IP & Rights Clearance Engine**: Automated legal search for song lyrics, trademarks, brand mentions, and public domain status.
5. **Interactive Studio Director Co-Pilot**: Multi-turn conversational assistant for directors, producers, and writers grounded with Gemini 2.5 Flash and Parallel Search.

---

## 📱 Quick Start (Studio Web & Mobile Platform)

```bash
# 1. Install dependencies (strictly Google Cloud AI + Parallel Web Systems)
pip install -r requirements.txt

# 2. Run the platform (serves REST API and built UI at http://localhost:8080)
python -m uvicorn mobile_api.server:app --host 0.0.0.0 --port 8080 --reload
```
Or double-click `START_MOBILE_APP.bat` on Windows.

---

## ⚙️ Environment Configuration

Create a `.env` file in the root directory:
```env
# ── Google Cloud (Gemini 2.5 Flash — Exclusive AI Engine) ─────────────────
GEMINI_API_KEY=your_gemini_api_key         # from Google AI Studio (aistudio.google.com)
GOOGLE_CLOUD_PROJECT=your-gcp-project-id   # for Vertex AI / Cloud services
GOOGLE_CLOUD_LOCATION=us-central1

# ── Partner Track: Parallel Web Systems ──────────────────────────────────
PARALLEL_API_KEY=your_parallel_api_key     # from platform.parallel.ai

# ── Google Cloud Storage (syncs processed JSON to GCS) ───────────────────
GCS_BUCKET=vlkg-knowledge-graph

# ── Neo4j Graph Database (optional) ───────────────────────────────────────
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

## Google Cloud Services Used

| Service | Purpose |
|---|---|
| **Vertex AI / Gemini 2.5 Flash** | Primary LLM for entity extraction, intelligence engines, QA |
| **Cloud Speech-to-Text** | Managed audio transcription (fallback: local Whisper) |
| **Cloud Storage (GCS)** | Persistent JSON store for corpus, entities, and triplets |


3. **Run the Pipeline**:
```bash
python main.py --url https://www.youtube.com/watch?v=VozV9KmhPTU
```

4. **Launch the UI**:
```bash
streamlit run app.py
```

## 🧪 Reproducible Testing Instructions

To run and verify the test suites and pipeline deterministically:

### 1. Test CineGraph Studio & Parallel Integration (`pytest`)
Run all 11 automated tests verifying Gemini 2.5 Flash compliance, Parallel Web Search tools, screenplay fact-checking, and Studio API endpoints:
```bash
python -m pytest tests/test_cinegraph_studio.py -v
```

### 2. Test MCP Server & Tool Surface (`pytest`)
Run all 28 automated unit tests covering the Model Context Protocol (MCP) server graph tools and intelligence engines:
```bash
python -m pytest mcp_server/tests
```

### 2. Verify Local Knowledge Graph Store Ingestion
Populate and test the offline `LocalGraphStore` fallback without requiring a live Neo4j connection:
```bash
python populate_graph.py
```

### 3. Verify Offline Rule-Based Triplet Extractor & Fallbacks
Test fallback extraction and guard logic:
```bash
python test_fallback.py
python test_guard.py
```

### 4. Verify Entity & Phrase Counts
Verify phrase counts and dataset consistency:
```bash
python verify_phrases.py
```

## ☁️ Deployment to Google Cloud Run

V-LKG can be easily deployed as serverless containers on **Google Cloud Run** using the provided Dockerfiles.

### 1. Deploy the Streamlit Web Application (UI)
The main interactive UI can be deployed directly from the root source:
```bash
gcloud run deploy v-lkg --source . --port 8080 --allow-unauthenticated --region us-central1
```

### 2. Deploy the MCP Server (SSE Transport API)
The MCP server can be deployed as a web service running over Server-Sent Events (SSE). It includes `CORSMiddleware` to allow cross-origin requests from web clients (like the Web MCP Inspector).

To build and deploy the MCP server, run using `Dockerfile.mcp`:
1. Temporarily replace the root `Dockerfile` with `Dockerfile.mcp`:
   ```bash
   cp Dockerfile Dockerfile.bak && cp Dockerfile.mcp Dockerfile
   ```
2. Deploy the service under the name `v-lkg-mcp`:
   ```bash
   gcloud run deploy v-lkg-mcp --source . --port 8080 --allow-unauthenticated --region us-central1
   ```
3. Restore the original Dockerfile:
   ```bash
   mv Dockerfile.bak Dockerfile
   ```

---

## 🤝 Track 2: Collaborative Partner Setup & Usage

Track 2 enables human-in-the-loop interactions via two channels: the **Interactive Streamlit UI** and the **Model Context Protocol (MCP) Server**.

### 1. Streamlit Web App UI
The Streamlit UI offers visual strategy maps, search filters, and an audio recorder.
* **Local Run**: 
  ```bash
  streamlit run app.py
  ```
* **Cloud Run**: Access your deployed `v-lkg` service URL (e.g., `https://v-lkg-cgwpuv3gna-uc.a.run.app`).

### 2. Model Context Protocol (MCP) Server
The MCP server exposes V-LKG's tools and graph queries directly to AI agents.

#### **A. Local Client Connection (stdio transport)**
To connect the MCP server locally to desktop clients (like **Claude Desktop**), add the server command configuration pointing to the local package:
* **Claude Desktop Configuration File** (`%APPDATA%\Claude\claude_desktop_config.json`):
  ```json
  {
    "mcpServers": {
      "v-lkg": {
        "command": "python",
        "args": ["-m", "vlkg_mcp.server"],
        "env": {
          "PYTHONPATH": "/absolute/path/to/v-lkg-reproduction;/absolute/path/to/v-lkg-reproduction/mcp_server/src"
        }
      }
    }
  }
  ```

#### **B. Cloud Client Connection (SSE transport)**
If you deployed `v-lkg-mcp` to Cloud Run, it runs as an SSE service. You can connect it directly in **Cursor** or inspect it via the **Web MCP Inspector**:

* **Cursor Setup**:
  1. Open Cursor Settings > **Models** > **MCP**.
  2. Click **+ Add New MCP Server**.
  3. Set Name to `v-lkg`, Type to `SSE`, and URL to:
     `https://v-lkg-mcp-cgwpuv3gna-uc.a.run.app/sse`
  4. Save. The connection will verify and turn green.

* **Web MCP Inspector Setup**:
  1. Open the official web inspector: **[https://inspector.modelcontextprotocol.io](https://inspector.modelcontextprotocol.io)**.
  2. Choose transport type **SSE**.
  3. Enter the connection URL:
     `https://v-lkg-mcp-cgwpuv3gna-uc.a.run.app/sse`
  4. Click **Connect** to interactively test the knowledge graph tools.
```
