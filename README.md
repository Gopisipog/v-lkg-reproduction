# V-LKG: Video Knowledge Graph Agent

[![All Things Agentic Hackathon](https://img.shields.io/badge/Hackathon-All%20Things%20Agentic-blue)](HACKATHON_SUBMISSION.md)
**Participating Tracks**:
- ⚙️ **Track 1: The Taskmaster** (Autonomous background video ingestion, multimodal ASR/OCR, & knowledge extraction)
- 🤝 **Track 2: The Collaborative Partner** (Interactive AI co-pilot, visual graph queries, timestamp links, & MCP protocol support)

A multimodal agentic pipeline that transforms unstructured YouTube leadership and educational content into a structured, queryable Neo4j Knowledge Graph.

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

V-LKG can be easily deployed as a serverless container on **Google Cloud Run** using the provided `Dockerfile`.

### Option A: Continuous Deployment via GitHub (Recommended)
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Navigate to **Cloud Run** and click **Create Service**.
3. Select **"Continuously deploy new revisions from a source repository"** and select your repository `Gopisipog/v-lkg-reproduction`.
4. Select the `main` branch.
5. In the Build Configuration, choose **Dockerfile** (it will use the root `Dockerfile` to build the image via Cloud Build).
6. Under **Variables & Secrets**, add your environment variables:
   - `GEMINI_API_KEY` (from Google AI Studio)
   - `GOOGLE_CLOUD_PROJECT` (your GCP project ID)
7. Click **Create** to deploy.

### Option B: Deploy via gcloud CLI
If you have the Google Cloud SDK installed locally, run:
```bash
gcloud run deploy v-lkg --source . --port 8080 --allow-unauthenticated
```
