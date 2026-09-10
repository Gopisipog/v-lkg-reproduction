# 🎬 CineGraph Studio — Autonomous Cinema Backlot Network

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Google Cloud](https://img.shields.io/badge/Google_Cloud-Gemini_2.5_Flash-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/vertex-ai)
[![Partner Track](https://img.shields.io/badge/Partner_Track-Parallel_Web_Systems-00C4CC)](https://parallel.ai)
[![Hackathon](https://img.shields.io/badge/Hackathon-Agentic_Cinema_Blockbuster-E50914)](https://agentic-cinema.devpost.com/)

**CineGraph Studio** is an autonomous multi-agent film production intelligence backlot built for the **Google Cloud Agentic Cinema: The Blockbuster Hackathon**, competing in the **Parallel Web Systems** partner track.

Implemented as a **standalone, decoupled application**, CineGraph Studio orchestrates three specialized autonomous personas using **Google Cloud Gemini 2.5 Flash** and real-time open-web intelligence from the **Parallel Web Systems SDK (`parallel-web`)**.

---

## 🌟 Hackathon Themes & Multi-Agent Architecture

```
                          ┌──────────────────────────────────────────────┐
                          │   Screenplay / Dailies Dialogue Audio        │
                          └──────────────────────┬───────────────────────┘
                                                 │
                                                 ▼
     ┌────────────────────────────────────────────────────────────────────────────────────────┐
     │                             CineGraph Multi-Agent Orchestrator                         │
     └───────────────┬───────────────────────────┬────────────────────────────┬───────────────┘
                     │                           │                            │
                     ▼                           ▼                            ▼
  ┌─────────────────────────────────┐ ┌──────────────────────────────────┐ ┌──────────────────────────────────┐
  │  1. The Visionary Director      │ │  2. The Technical Producer       │ │  3. The Studio Head              │
  │  (Theme 1: Workflow & Beats)    │ │  (Theme 2: Data & Parallel Intel)│ │  (Theme 3: IAM & Governance)     │
  │  - Google Cloud Gemini 2.5 Flash│ │  - Parallel Web Systems SDK      │ │  - Cloud IAM Security Audits     │
  │  - Dramatic Beat Detection      │ │  - Period Archival Fact-Checking │ │  - Clearance Sign-Off Matrix     │
  │  - Character Objectives         │ │  - Box Office Comps & Metrics    │ │  - Multi-Agent Orchestration Log │
  │  - Staging, Lighting & Audio    │ │  - Trademark & Rights Clearances │ │  - Production Greenlight Verdict │
  └────────────────┬────────────────┘ └────────────────┬─────────────────┘ └────────────────┬─────────────────┘
                   │                                   │                                   │
                   └───────────────────────────────────┼───────────────────────────────────┘
                                                       │
                                                       ▼
                                    ┌─────────────────────────────────────┐
                                    │    CineGraph Production Dossier     │
                                    │  & Standalone Cinematic Cockpit     │
                                    │      (http://localhost:8501)        │
                                    └─────────────────────────────────────┘
```

### 1. The Visionary Director (`cinegraph_studio.agents.director`)
- **Theme 1**: Agent Architecture & Workflow Automation.
- Deconstructs scenes into structured dramatic beats (inciting questions, confrontational reversals, emotional climaxes).
- Generates character objectives and obstacles under high stakes.
- Outputs concrete staging notes: 35mm camera movement, lighting color temperature, and audio design cues.

### 2. The Technical Producer (`cinegraph_studio.agents.producer`)
- **Theme 2**: Enterprise Data & Context Infrastructure.
- Connects autonomous agents to live open-web data pipelines using the **Parallel Web Systems SDK (`parallel-web` v0.4.2)**:
  - **Archival Fact-Checking**: Validates period dialogue and historical accuracy against open-web archival records.
  - **Theatrical Box Office Comps**: Retrieves commercial precedents, budget tiers, and audience retention figures.
  - **IP & Rights Clearance**: Scans brand references, song lyrics, and trademark registries for production legal safety.

### 3. The Studio Head (`cinegraph_studio.agents.studio_head`)
- **Theme 3**: Security, Governance & Multi-Agent Orchestration.
- Enforces Google Cloud IAM least-privilege security policies across multi-agent communication boundaries.
- Cross-references Director beats and Producer clearances to issue an executive **GREENLIT**, **CONDITIONAL**, or **REJECTED** verdict.
- Emits verifiable audit trails for studio legal and production insurance packages.

---

## 🚀 Quickstart (Standalone Execution)

CineGraph Studio is fully independent and does not require running the existing mobile or Streamlit apps.

### 1. Environment Setup
Set your Google Cloud Gemini and Parallel Web Systems API keys:

```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your-gemini-api-key"
$env:PARALLEL_API_KEY="your-parallel-api-key"

# Linux / macOS
export GEMINI_API_KEY="your-gemini-api-key"
export PARALLEL_API_KEY="your-parallel-api-key"
```

*(Note: CineGraph Studio includes built-in deterministic offline fallback modes so the test suite and dashboard run even in air-gapped environments without keys).*

### 2. Launch the Application
Run the standalone launcher:

```bash
python run_studio.py
```

Open your browser to:
👉 **[http://localhost:8501](http://localhost:8501)**

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/status` | System health check verifying Gemini 2.5 Flash and Parallel Web Systems status. |
| `POST` | `/api/analyze-scene` | Runs the full 3-agent pipeline to generate a CineGraph Production Dossier. |
| `POST` | `/api/comps` | Queries live theatrical box-office comps via Parallel Search. |
| `POST` | `/api/verify-period` | Fact-checks screenplay dialogue against archival records via Parallel Search. |
| `POST` | `/api/clearance` | Scans trademark, brand names, and IP clearance via Parallel Search. |
| `POST` | `/api/copilot` | Interactive director consultation grounded by Gemini and Parallel Web Systems. |
| `GET` | `/api/mcp/tools` | Lists registered MCP tools for external agent networks. |

---

## 🔌 Managed Model Context Protocol (MCP) Tools

The `cinegraph_studio.mcp` module provides enterprise agent tools:

```python
from cinegraph_studio.mcp import (
    tool_analyze_scene,
    tool_search_boxoffice_comps,
    tool_verify_period_authenticity,
    tool_clearance_scan,
    tool_studio_head_audit
)

# Example: Run historical screenplay fact-check
result = tool_verify_period_authenticity(
    claim="We will use radar to track the convoy",
    period="World War II 1943"
)
```

---

## 🧪 Automated Testing

Run the dedicated standalone test suite:

```bash
python -m pytest tests/test_cinegraph_studio_standalone.py -v
```
