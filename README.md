# V-LKG: Video Knowledge Graph Agent

[![All Things Agentic Hackathon](https://img.shields.io/badge/Hackathon-All%20Things%20Agentic-blue)](HACKATHON_SUBMISSION.md)
**Participating Tracks**:
- ⚙️ **Track 1: The Taskmaster** (Autonomous background video ingestion, multimodal ASR/OCR, & knowledge extraction)
- 🤝 **Track 2: The Collaborative Partner** (Interactive AI co-pilot, visual graph queries, timestamp links, & MCP protocol support)

A multimodal agentic pipeline that transforms unstructured YouTube leadership and educational content into a structured, queryable Neo4j Knowledge Graph.

---

## 📱 V-LKG Mobile & Linear Words Platform

A mobile web application and FastAPI platform providing:
- **Linear Words & Semantic Pathways**: Replaced complex node graphs with linear prioritized words and semantic knowledge pathways.
- **Child Apps Hub**: Executive Leadership, Sales Accelerator, Communication Mastery, and GTM AI Engineering.
- **Transcripts Explorer**: 3,184 time-aligned transcript segments across 16 videos with real-time text highlighting and instant timestamp navigation.
- **Global Transcript Search**: Cross-video search endpoint `GET /api/transcripts/search?q=...` with instant hit navigation.
- **Live Production URL**: [https://v-lkg-826803329504.us-central1.run.app](https://v-lkg-826803329504.us-central1.run.app)
- **Dedicated GitHub Repository**: [https://github.com/Gopisipog/vlkg-mobile](https://github.com/Gopisipog/vlkg-mobile)

### Quick Start (Mobile App)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the full mobile platform (serves API and built UI at http://localhost:8080)
python -m uvicorn mobile_api.server:app --host 0.0.0.0 --port 8080 --reload
```
Or double-click `START_MOBILE_APP.bat` on Windows.

---

## Architecture

This system consists of four primary technical layers:
1. **Multimodal Processor**: Audio transcription (Whisper) and Video OCR (EasyOCR) to build a time-aligned corpus.
2. **Semantic Entity Recognizer**: LLM-based entity/triplet extraction synced with external knowledge bases.
3. **Relationship & Dependency Miner**: Similarity-based prerequisite determination.
4. **Graph Enrichment Engine**: Centrality-based graph completion.

## Setup Instructions

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Environment Setup**:
Create a `.env` file in the root directory:
```env
# ── Google Cloud (Gemini — primary LLM) ───────────────────────────────────
GEMINI_API_KEY=your_gemini_api_key         # from Google AI Studio (aistudio.google.com)
GOOGLE_API_KEY=your_google_api_key         # alias for GEMINI_API_KEY

# ── Google Cloud Project (Speech-to-Text, Cloud Storage) ──────────────────
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# ── Google Cloud Storage (optional — syncs processed JSON to GCS) ─────────
GCS_BUCKET=vlkg-knowledge-graph

# ── Neo4j Graph Database ───────────────────────────────────────────────────
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# ── OpenAI / DeepSeek (fallback if Gemini key not provided) ───────────────
OPENAI_API_KEY=your_openai_key
DEEPSEEK_API_KEY=your_deepseek_key
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

### 1. Test MCP Server & Tool Surface (`pytest`)
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
