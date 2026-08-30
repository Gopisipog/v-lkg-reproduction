# 🚀 V-LKG: Video Leadership Knowledge Graph Agent
**Submission for All Things Agentic Hackathon**

---

## 📌 Project Overview
**V-LKG (Video Leadership Knowledge Graph Agent)** is an agentic AI system designed to transform massive unstructured video repositories (such as YouTube leadership talks, tutorials, and educational lectures) into a structured, highly queryable Neo4j Knowledge Graph.

Instead of scrubbing through hours of video, V-LKG acts as an autonomous background processor and interactive learning partner—extracting granular concepts, competencies, outcomes, and prerequisite relationships with precise timestamp links back to the source videos.

---

## 🏆 Selected Hackathon Tracks

V-LKG competes in **two key tracks** of the All Things Agentic Hackathon:

### 1. ⚙️ Track 1: The Taskmaster (Autonomous Heavy-Lifting Agent)
* **Background Ingestion & Multimodal OCR/ASR**: Autonomously downloads YouTube video streams, extracts audio transcripts via Whisper, and performs slide/on-screen OCR via EasyOCR.
* **Automated Knowledge Mining**: Asynchronously parses time-aligned content to mine entities, semantic triplets, and concept dependencies.
* **Knowledge Graph Construction**: Auto-enriches and populates a Neo4j Graph DB using centrality and vector similarity metrics without human intervention.

### 2. 🤝 Track 2: The Collaborative Partner (Human-in-the-Loop Co-pilot)
* **Interactive Knowledge Exploration**: Users can visually query the graph, filter by concept competencies or outcomes, and immediately jump to exact video timestamps.
* **Personalized Pathway Generation**: Works alongside educators and learners to generate custom study pathways based on prerequisite concept dependencies.
* **Model Context Protocol (MCP) Integration**: Features a native MCP server (`vlkg_mcp`) allowing external LLMs and desktop agents to query the video knowledge graph directly.

---

## 🏗️ System Architecture

```
                                +---------------------------+
                                |    YouTube / Video Files  |
                                +-------------+-------------+
                                              |
                                              v
                              +---------------+---------------+
                              |   Autonomous Background Agent |
                              |  (Audio ASR + Video Slide OCR)|
                              +---------------+---------------+
                                              |
                                              v
                              +---------------+---------------+
                              | Entity & Triplet Mining Engine|
                              |   (LLM + Semantic Extractor)  |
                              +---------------+---------------+
                                              |
                                              v
                              +---------------+---------------+
                              |    Neo4j Knowledge Graph      |
                              |  (Concepts, Outcomes, Links)  |
                              +-------+---------------+-------+
                                      |               |
                                      v               v
                +---------------------+--+   +--------+------------------+
                | Interactive UI Engine  |   | MCP Server (vlkg_mcp)    |
                | (Streamlit Co-Pilot)   |   | (Tool API for External AI)|
                +------------------------+   +---------------------------+
```

---

## 🤖 Key Agentic Features

1. **Multimodal Time-Aligned Ingestion**: Combines spoken audio context with visual slide text to ensure complete content understanding.
2. **Centrality & Prerequisite Mining**: Infers learning prerequisites automatically by mapping structural dependencies across video modules.
3. **Exact Timestamp Grounding**: Every node in the graph retains exact video URL timestamp links (`?t=XXs`) for verifiable evidence retrieval.
4. **MCP Standard Protocol**: Includes a built-in MCP server supporting tools like `query_knowledge_graph`, `get_prerequisites`, and `search_video_timestamps`.

---

## 🚀 How to Run

### Prerequisites
* Python 3.10+
* Neo4j Database (Local desktop or Neo4j Aura)
* ffmpeg (installed automatically via static-ffmpeg or system PATH)

### 1. Installation
```bash
git clone https://github.com/YourRepo/v-lkg-reproduction.git
cd v-lkg-reproduction
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### 3. Launching the App
Run the interactive Streamlit UI:
```bash
streamlit run app.py
```
*(Or use `START_APP.bat` on Windows)*

---

## 📝 Devpost Submission Checklist & Video Guide
- [x] **Project Name**: V-LKG: Video Knowledge Graph Agent
- [x] **Track Selection**: The Taskmaster & The Collaborative Partner
- [x] **Repository / Codebase**: Open-source Python & Streamlit codebase with MCP integration
- [x] **Demo Video (4 Min Max)**: Highlight background ingestion, knowledge graph expansion, interactive concept search, and exact video timestamp jumping.
