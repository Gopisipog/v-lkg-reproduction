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
Create a `.env` file in the root directory with your API keys:
```
OPENAI_API_KEY=your_openai_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

3. **Run the Pipeline**:
```bash
python main.py
```

4. **Launch the UI**:
```bash
streamlit run app.py
```
