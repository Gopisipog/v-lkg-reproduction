# V-LKG: Video Knowledge Graph Construction

A multimodal pipeline that transforms unstructured YouTube leadership content into a structured, queryable Neo4j Knowledge Graph specifically optimized for leadership education.

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
