import json
import os
import traceback
import datetime
import tempfile
import streamlit as st
import streamlit.components.v1 as components
from src.database.neo4j_client import Neo4jClient
from dotenv import load_dotenv
import shutil

# Ensure ffmpeg is available for yt-dlp and Whisper
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    pass

if not shutil.which("ffmpeg"):
    st.warning("ffmpeg not found in PATH. Install it via packages.txt.")

# Load environment variables (local .env file OR Streamlit Cloud secrets)
load_dotenv()

# In Streamlit Cloud, secrets are injected as env vars
if hasattr(st, 'secrets') and st.secrets:
    for key in st.secrets:
        if key not in os.environ:
            os.environ[key] = st.secrets[key]

st.set_page_config(page_title="V-LKG Query Engine", layout="wide")

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
    </style>
""",
    unsafe_allow_html=True,
)


st.title("Leadership Knowledge Graph (V-LKG)")
st.markdown(
    "Search across semantic nodes (Competencies, Outcomes, Concepts) to receive precise video timestamp links."
)

# Sidebar stats
st.sidebar.header("Graph Statistics")
db = Neo4jClient()
node_count = 0
rel_count = 0
avg_degree = 0.0

# Use local store stats if available, otherwise try Neo4j
if db._local_fallback:
    stats = db._local_fallback.get_stats()
    node_count = stats.get("node_count", 0)
    rel_count = stats.get("rel_count", 0)
    avg_degree = stats.get("avg_degree", 0.0)
elif db.driver:
    try:
        nodes = db.execute_read("MATCH (n) RETURN count(n) as count")
        node_count = nodes[0]["count"] if nodes else 0
        rels = db.execute_read("MATCH ()-[r]->() RETURN count(r) as count")
        rel_count = rels[0]["count"] if rels else 0
        degrees = db.execute_read(
            "MATCH (n) WITH n, COUNT { (n)--() } as degree RETURN avg(degree) as avg"
        )
        avg_degree = degrees[0]["avg"] if degrees and degrees[0]["avg"] else 0.0
    except Exception as e:
        st.sidebar.error(f"DB Stat Error: {e}")

st.sidebar.metric("Nodes", f"{node_count}")
st.sidebar.metric("Relationships", f"{rel_count}")
st.sidebar.metric("Avg Degree Centrality", f"{avg_degree:.2f}")

st.sidebar.divider()

# ── Intelligence Pipeline Runner ─────────────────────────────────────────────
st.sidebar.header("🧠 Intelligence Pipeline")
st.sidebar.caption("Auto-extract insights from ingested videos across all intelligence domains.")

# Load corpus & registry for pipeline
_side_corpus = []
_side_registry = []
if os.path.exists("data/processed/corpus.json"):
    try:
        with open("data/processed/corpus.json", "r", encoding="utf-8") as f:
            _side_corpus = json.load(f)
    except Exception:
        pass
if os.path.exists("data/processed/videos_registry.json"):
    try:
        with open("data/processed/videos_registry.json", "r", encoding="utf-8") as f:
            _side_registry = json.load(f)
    except Exception:
        pass

st.sidebar.metric("Videos", len(_side_registry))
st.sidebar.metric("Segments", len(_side_corpus))

if "intel_cache" not in st.session_state:
    st.session_state.intel_cache = {}

def _load_intel_cache():
    """Load pre-computed insights from video_insights.json into session state."""
    insights_path = "data/processed/video_insights.json"
    if os.path.exists(insights_path):
        try:
            with open(insights_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
            st.session_state.intel_cache = cache.get("videos", {})
        except Exception:
            st.session_state.intel_cache = {}
    if not st.session_state.intel_cache:
        st.session_state.intel_cache = {}

_load_intel_cache()

def _save_intel_cache():
    """Persist intelligence cache to disk."""
    insights_path = "data/processed/video_insights.json"
    os.makedirs(os.path.dirname(insights_path), exist_ok=True)
    payload = {
        "videos": st.session_state.intel_cache,
        "cross_video_themes": st.session_state.intel_cache.get("_cross_video_themes", []),
        "expert_patterns": [],
        "last_updated": datetime.datetime.utcnow().isoformat() + "Z",
        "video_count": len(_side_registry),
        "segment_count": len(_side_corpus),
    }
    with open(insights_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)

def run_intelligence_pipeline():
    """Run all intelligence engines on the ingested corpus and cache results.
    Extracts both global (all videos) and per-video insights."""
    if not _side_corpus:
        st.sidebar.warning("No ingested data. Run the video pipeline first.")
        return

    st.sidebar.info("Extracting intelligence across all domains...")
    engines = {}
    try:
        from src.core.learning_intelligence import LearningIntelligenceEngine
        from src.core.competitive_intelligence import CompetitiveIntelligenceEngine
        from src.core.sales_intelligence import SalesIntelligenceEngine
        from src.core.compliance_intelligence import ComplianceIntelligenceEngine
        from src.core.rd_intelligence import RDIntelligenceEngine
        from src.core.customer_intelligence import CustomerIntelligenceEngine
        from src.core.executive_intelligence import ExecutiveIntelligenceEngine
        from src.core.org_knowledge import OrgKnowledgeEngine
        from src.core.thought_leadership import ThoughtLeadershipEngine
    except Exception as e:
        st.sidebar.error(f"Engine import error: {e}")
        return

    # Build engine instances
    engines["learning"] = LearningIntelligenceEngine(db_client=db)
    engines["competitive"] = CompetitiveIntelligenceEngine(db_client=db)
    engines["sales"] = SalesIntelligenceEngine(db_client=db)
    engines["compliance"] = ComplianceIntelligenceEngine(db_client=db)
    engines["rd"] = RDIntelligenceEngine(db_client=db)
    engines["customer"] = CustomerIntelligenceEngine(db_client=db)
    engines["executive"] = ExecutiveIntelligenceEngine(db_client=db)
    engines["orgknowledge"] = OrgKnowledgeEngine(db_client=db)
    engines["thoughtleadership"] = ThoughtLeadershipEngine(db_client=db)

    # Collect unique video IDs for per-video extraction
    all_video_ids = set()
    for s in _side_corpus:
        vid = s.get("video_id")
        if vid:
            all_video_ids.add(vid)
    video_ids = sorted(all_video_ids)

    total_extractions = (len(engines) * (1 + len(video_ids)))  # global + per-video
    processed = 0

    with st.sidebar.status(f"Running intelligence extraction ({total_extractions} jobs)...", expanded=False) as status:
        # ── Global extraction (all videos) ────────────────────────────────
        for name, engine in engines.items():
            if hasattr(engine, "extract_from_corpus"):
                status.write(f"📊 [global] {name.title()}...")
                try:
                    result = engine.extract_from_corpus(_side_corpus, _side_registry, video_id=None)
                    st.session_state.intel_cache[f"{name}_global"] = result
                except Exception as e:
                    st.sidebar.error(f"[global] {name} failed: {e}")
                    st.session_state.intel_cache[f"{name}_global"] = {"error": str(e), "status": "failed"}
                processed += 1

        # ── Per-video extraction ──────────────────────────────────────────
        for vid in video_ids:
            # Find video title for display
            video_title = vid
            for v in (_side_registry or []):
                if v.get("video_id") == vid:
                    video_title = v.get("title", vid)[:40]
                    break
            status.write(f"🎬 [per-video] {video_title}...")
            for name, engine in engines.items():
                if hasattr(engine, "extract_from_corpus"):
                    try:
                        result = engine.extract_from_corpus(_side_corpus, _side_registry, video_id=vid)
                        st.session_state.intel_cache[f"{name}_vid_{vid}"] = result
                    except Exception as e:
                        print(f"[per-video] {name}/{vid} failed: {e}")
                        st.session_state.intel_cache[f"{name}_vid_{vid}"] = {"status": "failed", "error": str(e)}
                    processed += 1
                    if processed % 10 == 0:
                        status.write(f"  ... {processed}/{total_extractions}")

        # Cross-video theme extraction (aggregate)
        status.write("🔄 Aggregating cross-video themes...")
        st.session_state.intel_cache["_cross_video_themes"] = _aggregate_themes()
        _save_intel_cache()
        # Persist intelligence results as knowledge graph triplets
        status.write("🔗 Persisting to knowledge graph...")
        _persist_intelligence_to_graph(engines, video_ids)
        status.update(label=f"✅ Intelligence extraction complete! ({processed} jobs)", state="complete")

    st.sidebar.success(f"Extracted insights: {len(engines)} domains x {len(video_ids)+1} scopes")
    st.rerun()


def _persist_intelligence_to_graph(engines, video_ids):
    """Insert intelligence-derived knowledge as triplets into the knowledge graph.
    This makes intelligence results visible in the 'Ingested Knowledge' tab and Strategy Map.
    Persists both global and per-video intelligence with video provenance."""
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    inserted = 0

    def _insert_entity(name, entity_type, relation, target_name, target_type, vid_id, engine_title):
        """Helper to insert a single intelligence entity with video_id."""
        if not name or not name.strip():
            return 0
        db.insert_triplet(name, entity_type, relation, target_name, target_type,
                          source_time=timestamp, video_id=vid_id)
        return 1

    def _insert_domain_entities(result, name, vid_id, engine_title):
        """Insert all entities from a result dict for a specific video scope."""
        n = 0
        if name == "learning":
            for c in result.get("key_competencies", []):
                n += _insert_entity(c, "Competency", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
            for g in result.get("skills_gaps", []):
                n += _insert_entity(g.get("gap", ""), "SkillGap", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
        elif name == "competitive":
            for t in result.get("competitive_topics", []):
                n += _insert_entity(t.get("topic", ""), "CompetitiveTopic", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
            for t in result.get("competitive_threats", []):
                n += _insert_entity(t.get("threat", ""), "Threat", "FROM", t.get("competitor", "Unknown"), "Competitor", vid_id, engine_title)
            for o in result.get("market_opportunities", []):
                n += _insert_entity(o.get("opportunity", ""), "MarketOpportunity", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
        elif name == "sales":
            for s in result.get("buyer_signals", []):
                n += _insert_entity(s.get("signal", ""), "BuyerSignal", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
            for t in result.get("deal_themes", []):
                n += _insert_entity(t.get("theme", ""), "DealTheme", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
        elif name == "compliance":
            for t in result.get("policy_topics_discussed", []):
                n += _insert_entity(t.get("topic", ""), "PolicyTopic", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
            for r in result.get("risk_assessment", []):
                n += _insert_entity(r.get("risk", ""), "Risk", "MITIGATED_BY", r.get("mitigation", ""), "Control", vid_id, engine_title)
        elif name == "rd":
            for t in result.get("emerging_trends", []):
                n += _insert_entity(t.get("trend", ""), "EmergingTrend", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
            for o in result.get("innovation_opportunities", []):
                n += _insert_entity(o.get("opportunity", ""), "Innovation", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
        elif name == "customer":
            for t in result.get("key_themes", []):
                n += _insert_entity(t.get("theme", ""), "CustomerTheme", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
            for p in result.get("pain_points", []):
                n += _insert_entity(p.get("pain_point", ""), "PainPoint", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
        elif name == "executive":
            for t in result.get("key_themes", []):
                n += _insert_entity(t, "ExecutiveTheme", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
            for d in result.get("recommended_decisions", []):
                n += _insert_entity(d.get("decision", ""), "Decision", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
        elif name == "orgknowledge":
            for cc in result.get("core_concepts", []):
                n += _insert_entity(cc.get("concept", ""), "KnowledgeConcept", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
            for bp in result.get("best_practices", []):
                n += _insert_entity(bp, "BestPractice", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
            for g in result.get("knowledge_gaps", []):
                n += _insert_entity(g.get("gap", ""), "KnowledgeGap", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
        elif name == "thoughtleadership":
            for n_item in result.get("key_narratives", []):
                n += _insert_entity(n_item.get("narrative", ""), "Narrative", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
            for l_item in result.get("thought_leaders", []):
                n += _insert_entity(l_item.get("name", ""), "ThoughtLeader", "HAS_EXPERTISE", l_item.get("expertise", ""), "Expertise", vid_id, engine_title)
            for a in result.get("content_gaps", []):
                n += _insert_entity(a.get("gap", ""), "ContentGap", "EXTRACTED_BY", engine_title, "IntelligenceDomain", vid_id, engine_title)
        return n

    for name in engines:
        engine_title = name.capitalize()

        # Mark domain node
        db.insert_triplet(engine_title, "IntelligenceDomain", "DOMAIN_FOR", "Leadership Knowledge", "KnowledgeBase",
                          source_time=timestamp, video_id="all")

        # ── Global extraction results ─────────────────────────────────────
        cache_key = f"{name}_global"
        result = st.session_state.intel_cache.get(cache_key, {})
        if isinstance(result, dict) and result.get("status") != "failed":
            inserted += _insert_domain_entities(result, name, "all", engine_title)

        # ── Per-video extraction results ──────────────────────────────────
        for vid_id in video_ids:
            vid_cache_key = f"{name}_vid_{vid_id}"
            vid_result = st.session_state.intel_cache.get(vid_cache_key, {})
            if isinstance(vid_result, dict) and vid_result.get("status") != "failed":
                inserted += _insert_domain_entities(vid_result, name, vid_id, engine_title)

    print(f"Persisted {inserted} intelligence triplets to knowledge graph")


def _aggregate_themes():
    """Aggregate themes from all intelligence engine results."""
    themes = []
    seen = set()
    for engine_name, data in st.session_state.intel_cache.items():
        if engine_name.startswith("_") or not isinstance(data, dict):
            continue
        for theme_key in ["key_themes", "key_narratives", "deal_themes",
                           "policy_topics_discussed", "research_directions",
                           "cross_video_themes"]:
            items = data.get(theme_key, [])
            for item in items:
                if isinstance(item, dict):
                    name = item.get("theme") or item.get("topic") or item.get("narrative") or item.get("direction") or str(item)
                else:
                    name = str(item)
                if name and name not in seen:
                    seen.add(name)
                    themes.append({
                        "theme": name,
                        "source_engine": engine_name,
                        "frequency": "medium"
                    })
    return themes[:20]

if st.sidebar.button("🚀 Run Intelligence Pipeline", type="primary", use_container_width=True):
    run_intelligence_pipeline()

if st.session_state.intel_cache:
    st.sidebar.caption(f"✅ Insights cached for {len(st.session_state.intel_cache)} domains")

# ── Helper: video selector widget ────────────────────────────────────────────
def _video_selector_widget(key_prefix: str = "intel"):
    """Render a per-video selector. Returns selected video_id or None for 'All Videos'."""
    registry = []
    if os.path.exists("data/processed/videos_registry.json"):
        try:
            with open("data/processed/videos_registry.json", "r") as f:
                registry = json.load(f)
        except Exception:
            registry = []
    options = [{"video_id": None, "label": "📊 All Videos (Global)"}]
    for v in registry:
        vid = v.get("video_id", "")
        title = v.get("title", "Untitled")[:50]
        options.append({"video_id": vid, "label": f"🎬 {title} ({vid})"})

    selected = st.selectbox(
        "🎯 Scope intelligence to a specific video:",
        options=[o["label"] for o in options],
        key=f"{key_prefix}_video_selector",
        index=0,
    )
    for o in options:
        if o["label"] == selected:
            return o["video_id"]
    return None

# ── Parent Tabs ─────────────────────────────────────────────────────────────
pt_kb, pt_media, pt_intel = st.tabs([
    "📚 Knowledge Base",
    "🎬 Learning & Media",
    "🧠 Leadership Intelligence",
])

with pt_kb:
    tab_search, tab_knowledge, tab_strategy = st.tabs([
        "Search",
        "Ingested Knowledge",
        "Strategy Map",
    ])

with pt_media:
    tab_proactive, tab_perspectives, tab_interview, tab_recording = st.tabs([
        "Proactive Learning",
        "YouTube Perspectives",
        "Interview Intelligence",
        "🎙️ Record",
    ])

with pt_intel:
    tab_learning, tab_competitive, tab_sales, tab_compliance, tab_rd, tab_customer, tab_executive, tab_orgknow, tab_thought = st.tabs([
        "L&D Intelligence",
        "Competitive Intel",
        "Sales Intelligence",
        "Compliance & Policy",
        "R&D Intelligence",
        "Customer Intel",
        "Executive Intel",
        "Org Knowledge",
        "Thought Leadership",
    ])


# ── Helper: render intelligence entities with video provenance ──────────────
def _render_intel_entities(domain_name, registry=None):
    """Query and display intelligence entities for a domain with video provenance.

    Args:
        domain_name: The IntelligenceDomain name (e.g. 'Learning', 'Competitive')
        registry: Optional video registry list for resolving video_id -> title
    """
    entities = db.get_entities_by_domain(domain_name)
    if not entities:
        return

    # Build video_id -> title lookup
    vid_map = {}
    if registry:
        for v in registry:
            vid_map[v.get("video_id", "")] = v.get("title", "Unknown")

    st.markdown(f"#### Derived Graph Entities")

    # Group by type
    by_type = {}
    for e in entities:
        t = e.get("type", "Entity")
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(e)

    cols = st.columns(min(len(by_type), 4))
    for idx, (etype, items) in enumerate(sorted(by_type.items())):
        col = cols[idx % len(cols)]
        with col:
            color = TYPE_COLORS.get(etype, "#607D8B")
            st.metric(etype, len(items))
            for item in items:
                name = item.get("name", "")
                video_ids = item.get("video_ids", ["all"])
                # Resolve video titles
                vid_labels = []
                for vid in video_ids:
                    if vid == "all":
                        vid_labels.append("All videos")
                    elif vid in vid_map:
                        vid_labels.append(vid_map[vid][:40])
                    else:
                        vid_labels.append(vid[:12])
                vid_text = " | ".join(vid_labels)
                st.markdown(
                    f"<div style='margin:4px 0'>"
                    f"<span style='background:{color};color:white;padding:3px 10px;"
                    f"border-radius:12px;font-size:0.82em;display:inline-block'>"
                    f"{name}</span>"
                    f"<br><small style='color:#666;margin-left:8px'>via {vid_text}</small>"
                    f"</div>",
                    unsafe_allow_html=True,
                )


def _render_metric_row(metrics):
    """Render a row of metric cards. metrics: list of (label, value, delta_or_none)."""
    cols = st.columns(len(metrics))
    for col, (label, value, delta) in zip(cols, metrics):
        with col:
            st.metric(label, value, delta=delta)


def _severity_icon(sev):
    """Return an emoji for a severity level."""
    return {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(sev, "⚪")


def _strength_badge(strength):
    """Return styled HTML for a strength indicator."""
    colors = {"dominant": "#d32f2f", "strong": "#f57c00", "emerging": "#fbc02d",
              "weak": "#81c784", "high": "#d32f2f", "medium": "#f57c00", "low": "#81c784"}
    c = colors.get(strength, "#757575")
    return (f"<span style='background:{c};color:white;padding:1px 8px;"
            f"border-radius:8px;font-size:0.72em;margin-left:6px'>{strength}</span>")

# ── Tab 1: Search ────────────────────────────────────────────────────────────
with tab_search:
    query = st.text_input("Search for a concept (e.g., 'Conflict Resolution'):")

    if st.button("Search Knowledge Graph"):
        if query:
            st.info(f"Querying Neo4j Graph for **{query}**...")

            if db.driver:
                search_query = """
                MATCH (n)
                WHERE n.name CONTAINS $keyword OR labels(n)[0] CONTAINS $keyword
                MATCH (n)-[r]-(m)
                RETURN n.name as node, labels(n)[0] as type, r.source_time as time, m.name as related
                LIMIT 5
                """
                results = db.execute_read(search_query, {"keyword": query})

                if results:
                    st.success(f"Found {len(results)} matches!")
                    for res in results:
                        with st.expander(f"{res['node']} ({res['type']})"):
                            st.write(f"**Related to:** {res['related']}")
                            if res["time"]:
                                st.markdown(f"**Timestamp:** {res['time']:.2f}s")
                                st.markdown(
                                    f"[Jump to Video Position](https://youtube.com/watch?v=sample&t={int(res['time'])})"
                                )
                else:
                    st.warning("No matches found in the Knowledge Graph yet.")
            else:
                st.error("Neo4j not connected. Please start the database.")
        else:
            st.warning("Please enter a query.")

# ── Tab 2: Ingested Knowledge ────────────────────────────────────────────────
with tab_knowledge:
    REGISTRY_PATH = "data/processed/videos_registry.json"
    CORPUS_PATH = "data/processed/corpus.json"

    # Canonical entity colors — single source of truth shared by ingestion,
    # enrichment, and every intelligence engine (src/core/entity_registry.py).
    from src.core.entity_registry import ENTITY_COLORS as TYPE_COLORS

    def pill(name, color):
        return (
            f"<span style='background:{color};color:white;padding:2px 10px;"
            f"border-radius:12px;font-size:0.82em;margin:2px;display:inline-block'>"
            f"{name}</span>"
        )

    def render_knowledge_layer(exclude_types=None, heading="🔎 Shared Knowledge Entities (color-coded)"):
        """Surface the shared, extracted + enriched, color-coded entity layer.

        Reads every entity persisted in the knowledge graph (ingestion
        extraction + enrichment + all intelligence domains) so the same
        cross-domain entity set is available inside every intelligence
        tab. Colors come from the persisted `color` property (falling
        back to the canonical map).
        """
        entities = db.get_knowledge_entities(exclude_types=(exclude_types or ["IntelligenceDomain"]))
        if not entities:
            return
        # group by type, preserving a stable type order
        by_type: dict = {}
        order: list = []
        for e in entities:
            t = e.get("type", "Entity")
            if t not in by_type:
                by_type[t] = []
                order.append(t)
            by_type[t].append(e)
        st.markdown(f"**{heading}**")
        for t in order:
            color = by_type[t][0].get("color") or TYPE_COLORS.get(t, "#607D8B")
            names = sorted({e.get("name", "") for e in by_type[t] if e.get("name")})
            if not names:
                continue
            html = "".join(pill(n, color) for n in names)
            st.markdown(html, unsafe_allow_html=True)
        # legend
        legend = " &nbsp; ".join(
            pill(t, by_type[t][0].get("color") or TYPE_COLORS.get(t, "#607D8B"))
            for t in order
        )
        st.markdown(f"<small>{legend}</small>", unsafe_allow_html=True)

    # ── Load registry & corpus ──────────────────────────────────────────────
    registry = []
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)

    corpus = []
    if os.path.exists(CORPUS_PATH):
        try:
            with open(CORPUS_PATH, "r", encoding="utf-8") as f:
                corpus = json.load(f)
        except json.JSONDecodeError:
            st.warning("Corpus file is corrupted or truncated. Some data may not display.")
            corpus = []

    if not registry:
        st.info("No videos ingested yet. Use the sidebar to run the pipeline.")
    else:
        st.markdown(f"### {len(registry)} Video(s) Ingested")

        for vid in registry:
            vid_id = vid["video_id"]
            segs = [s for s in corpus if s.get("video_id") == vid_id]
            duration = vid.get("duration_sec", 0)
            mins, secs = divmod(int(duration), 60)
            ingested = vid.get("ingested_at", "")[:10]

            with st.container(border=True):
                # ── Header row ──────────────────────────────────────────────
                thumb_col, info_col = st.columns([1, 3])
                with thumb_col:
                    if vid.get("thumbnail_url"):
                        st.image(vid["thumbnail_url"], width="stretch")
                with info_col:
                    st.markdown(f"#### [{vid['title']}]({vid['url']})")
                    st.caption(
                        f"📺 {vid.get('channel', '—')}  &nbsp;|&nbsp;  "
                        f"⏱ {mins}m {secs}s  &nbsp;|&nbsp;  "
                        f"📅 Ingested {ingested}  &nbsp;|&nbsp;  "
                        f"🆔 `{vid_id}`"
                    )
                    st.markdown(f"> {vid.get('summary', '')}")

                # ── Per-video metrics ────────────────────────────────────────
                m1, m2, m3 = st.columns(3)
                m1.metric("Transcript Segments", len(segs))
                m2.metric("Duration", f"{mins}m {secs}s")
                m3.metric(
                    "Visual Text Segments", sum(1 for s in segs if s.get("visual_text"))
                )

                # ── Extracted knowledge for this video ───────────────────────
                is_local_db = hasattr(db, '_local_fallback') and db._local_fallback is not None
                vid_nodes = []
                if db.driver:
                    vid_nodes = (
                        db.execute_read(
                            """
                        MATCH (a)-[r]->(b)
                        WHERE r.video_id = $vid_id
                          AND a.name IS NOT NULL AND b.name IS NOT NULL
                        RETURN labels(a)[0] AS from_type, a.name AS from_name,
                               type(r)      AS relation,
                               labels(b)[0] AS to_type,  b.name AS to_name,
                               r.source_time AS time
                        ORDER BY r.source_time
                        """,
                            {"vid_id": vid_id},
                        )
                        or []
                    )
                elif is_local_db:
                    local = db._local_fallback
                    for t in local.get_triplets(video_id=vid_id):
                        vid_nodes.append({
                            "from_type": t.get("subject_type", "Entity"),
                            "from_name": t["subject"],
                            "relation": t["relation"],
                            "to_type": t.get("object_type", "Entity"),
                            "to_name": t["object"],
                            "time": t.get("source_time", ""),
                        })
                    # Also add intelligence-derived nodes tagged with this vid
                    for cache_key, data in st.session_state.intel_cache.items():
                        if not isinstance(data, dict) or data.get("status") == "failed":
                            continue
                        # Check if this cache entry is per-video for this vid
                        if f"_vid_{vid_id}" not in cache_key:
                            continue
                        engine_name = cache_key.replace(f"_vid_{vid_id}", "")
                        # Add engine domain node
                        vid_nodes.append({
                            "from_type": "IntelligenceDomain",
                            "from_name": engine_name.capitalize(),
                            "relation": "ANALYZED",
                            "to_type": "Video",
                            "to_name": vid_id,
                            "time": "",
                        })

                if vid_nodes:
                    EXTRACTED_TYPES = {"Competency", "Concept"}
                    ENRICHED_TYPES = {
                        "Strategy", "Tactic", "Path", "Outcome", "Personality",
                    }
                    INTEL_TYPES = {
                        "CompetitiveTopic", "Threat", "MarketOpportunity",
                        "BuyerSignal", "DealTheme", "PolicyTopic", "Risk",
                        "EmergingTrend", "Innovation", "CustomerTheme",
                        "PainPoint", "ExecutiveTheme", "Decision",
                        "KnowledgeConcept", "BestPractice", "KnowledgeGap",
                        "Narrative", "ThoughtLeader", "ContentGap",
                        "SkillGap", "IntelligenceDomain",
                    }

                    extracted_groups: dict = {}
                    enriched_groups: dict = {}
                    intel_groups: dict = {}

                    for row in vid_nodes:
                        for ntype, name in [
                            (row["from_type"], row["from_name"]),
                            (row["to_type"], row["to_name"]),
                        ]:
                            if not name or name.startswith("http://") or name.startswith("https://"):
                                continue
                            if ntype in EXTRACTED_TYPES:
                                extracted_groups.setdefault(ntype, set()).add(name)
                            elif ntype in ENRICHED_TYPES:
                                enriched_groups.setdefault(ntype, set()).add(name)
                            elif ntype in INTEL_TYPES:
                                intel_groups.setdefault(ntype, set()).add(name)

                    # ── Extracted pills ──────────────────────────────────
                    if extracted_groups:
                        st.markdown("**Extracted from Video**")
                        html = "".join(
                            pill(name, TYPE_COLORS.get(ntype, "#607D8B"))
                            for ntype in sorted(extracted_groups)
                            for name in sorted(extracted_groups[ntype])
                        )
                        st.markdown(html, unsafe_allow_html=True)
                        legend = " &nbsp; ".join(
                            pill(t, TYPE_COLORS.get(t, "#607D8B"))
                            for t in sorted(extracted_groups)
                        )
                        st.markdown(
                            f"<small>{legend}</small>", unsafe_allow_html=True
                        )

                    # ── Intelligence pills ───────────────────────────────
                    if intel_groups:
                        st.markdown("**Intelligence Analysis**")
                        intel_html = "".join(
                            pill(name, "#7C4DFF")  # purple for intel
                            for ntype in sorted(intel_groups)
                            for name in sorted(intel_groups[ntype])
                        )
                        st.markdown(intel_html, unsafe_allow_html=True)
                        intel_types_shown = " &nbsp; ".join(
                            pill(t, "#7C4DFF") for t in sorted(intel_groups)
                        )
                        st.markdown(
                            f"<small>{intel_types_shown}</small>",
                            unsafe_allow_html=True,
                        )

                        # ── Enriched pills ───────────────────────────────────
                        if enriched_groups:
                            st.markdown("**Enriched Knowledge**")
                            html = "".join(
                                pill(name, TYPE_COLORS.get(ntype, "#607D8B"))
                                for ntype in sorted(enriched_groups)
                                for name in sorted(enriched_groups[ntype])
                            )
                            st.markdown(html, unsafe_allow_html=True)
                            legend = " &nbsp; ".join(
                                pill(t, TYPE_COLORS.get(t, "#607D8B"))
                                for t in sorted(enriched_groups)
                            )
                            st.markdown(
                                f"<small>{legend}</small>", unsafe_allow_html=True
                            )

                        # Relationships table
                        with st.expander(f"View {len(vid_nodes)} Relationships"):
                            rel_rows = []
                            for r in vid_nodes:
                                time_val = r.get("time", 0)
                                try:
                                    time_str = f"{float(time_val):.1f}s"
                                except (ValueError, TypeError):
                                    time_str = str(time_val) if time_val else "—"
                                rel_rows.append(
                                    {
                                        "From": f"{r['from_name']} ({r['from_type']})",
                                        "Relation": r["relation"],
                                        "To": f"{r['to_name']} ({r['to_type']})",
                                        "Timestamp": time_str,
                                    }
                                )
                            st.dataframe(
                                rel_rows, width="stretch", hide_index=True
                            )
                    else:
                        st.info("No graph nodes attributed to this video yet.")

                # ── Transcript ───────────────────────────────────────────────
                with st.expander(f"View {len(segs)} Transcript Segments"):
                    for seg in segs:
                        ts = int(seg["start_time"])
                        m_s, s_s = divmod(ts, 60)
                        text = seg["transcript"]
                        line = f"`{m_s}:{s_s:02d}`  {text}"
                        if seg.get("visual_text"):
                            line += f"  _(visual: {seg['visual_text'][:60]})_"
                        st.markdown(f"- {line}")

# ── Tab 3: Strategy Map ──────────────────────────────────────────────────────
with tab_strategy:
    st.markdown("### Strategy Map")
    st.caption(
        "Visualises every competency's strategies, their tactics, "
        "alternative approaches, prequels (what to learn first), and sequels (what comes next)."
    )

    STYPE_COLORS = {
        "Competency": "#2196F3",
        "Concept": "#4CAF50",
        "Strategy": "#FF5722",
        "Tactic": "#9C27B0",
        "Path": "#00BCD4",
        "Outcome": "#FF9800",
        "Personality": "#795548",
    }

    def tag(text, color, size="0.82em"):
        return (
            f"<span style='background:{color};color:white;padding:3px 10px;"
            f"border-radius:12px;font-size:{size};margin:2px;display:inline-block'>"
            f"{text}</span>"
        )

    is_local = db._local_fallback is not None if hasattr(db, '_local_fallback') else False
    use_neo4j = db.driver is not None

    if not use_neo4j and not is_local:
        st.error("No graph database connected.")
    else:
        # ── Fetch all competencies ─────────────────────────────────────────
        if is_local:
            local = db._local_fallback
            all_triplets = local.get_triplets()
            comp_names = set()
            for t in all_triplets:
                if t["relation"] in ("HAS_STRATEGY", "HAS_ALTERNATIVE", "IS_PREQUEL_TO", "LEADS_TO"):
                    comp_names.add(t["subject"])
            competencies = [{"name": c, "label": "Competency"} for c in sorted(comp_names)]
        else:
            comp_query = """
            MATCH (c)-[:HAS_STRATEGY|HAS_ALTERNATIVE]->(:Strategy)
            WHERE c.name IS NOT NULL
            RETURN DISTINCT c.name AS name, labels(c)[0] AS label
            ORDER BY c.name
            """
            raw_comps = db.execute_read(comp_query) or []
            competencies = [{"name": c["name"], "label": c.get("label", "Competency")} for c in raw_comps]

        if not competencies:
            st.info(
                "No strategy data yet. Run the pipeline on a YouTube video to populate the graph."
            )
        else:
            for comp_rec in competencies:
                comp_name = comp_rec["name"]
                comp_label = comp_rec["label"] or "Competency"
                comp_color = STYPE_COLORS.get(comp_label, "#607D8B")

                with st.container(border=True):
                    st.markdown(
                        tag(comp_label.upper(), comp_color, "0.75em")
                        + f"&nbsp;<b style='font-size:1.1em'>{comp_name}</b>",
                        unsafe_allow_html=True,
                    )

                    # ── Prequels ────────────────────────────────────────────
                    prequel_q = """
                    MATCH (pre)-[:IS_PREQUEL_TO]->(c {name: $name})
                    RETURN collect(pre.name) AS prequels
                    """
                    preq_res = db.execute_read(prequel_q, {"name": comp_name}) or []
                    prequels = preq_res[0]["prequels"] if preq_res else []
                    if prequels:
                        preq_html = " ".join(tag(p, "#607D8B") for p in prequels)
                        st.markdown(
                            f"<small><b>Learn first:</b> {preq_html}</small>",
                            unsafe_allow_html=True,
                        )

                    # ── Outcomes (LEADS_TO) ─────────────────────────────────
                    outcome_q = """
                    MATCH (c {name: $name})-[:LEADS_TO]->(o)
                    WHERE o.name IS NOT NULL
                    RETURN collect(o.name) AS outcomes
                    """
                    out_res = db.execute_read(outcome_q, {"name": comp_name}) or []
                    outcomes = out_res[0]["outcomes"] if out_res else []
                    if outcomes:
                        out_html = " ".join(
                            tag(o, STYPE_COLORS.get("Outcome", "#FF9800"))
                            for o in outcomes
                        )
                        st.markdown(
                            f"<small><b>Leads to:</b> {out_html}</small>",
                            unsafe_allow_html=True,
                        )

                    st.divider()

                    # ── Strategies (primary + alternatives side-by-side) ────
                    strat_q = """
                    MATCH (c {name: $comp})-[rel:HAS_STRATEGY|HAS_ALTERNATIVE]->(s:Strategy)
                    OPTIONAL MATCH (s)-[:HAS_TACTIC]->(t:Tactic)
                    OPTIONAL MATCH (s)-[:PRECEDED_BY]->(prereq)
                    RETURN s.name AS strategy,
                           type(rel) AS rel_type,
                           collect(DISTINCT t.name) AS tactics,
                           collect(DISTINCT prereq.name) AS strategy_prequels
                    ORDER BY rel_type
                    """
                    strat_rows = db.execute_read(strat_q, {"comp": comp_name}) or []

                    if not strat_rows:
                        st.caption("No strategies extracted yet for this competency.")
                    else:
                        cols = st.columns(max(len(strat_rows), 1))
                        for col, row in zip(cols, strat_rows):
                            s_name = row["strategy"]
                            rel_type = row["rel_type"]
                            tactics = [t for t in row["tactics"] if t]
                            s_preqs = [p for p in row["strategy_prequels"] if p]

                            is_alt = rel_type == "HAS_ALTERNATIVE"
                            border_color = "#FF5722" if not is_alt else "#9E9E9E"
                            badge = "ALTERNATIVE" if is_alt else "STRATEGY"
                            badge_color = "#9E9E9E" if is_alt else "#FF5722"

                            with col:
                                st.markdown(
                                    f"<div style='border-left:4px solid {border_color};"
                                    f"padding:8px 12px;margin-bottom:6px'>"
                                    f"{tag(badge, badge_color, '0.7em')}"
                                    f"<br><b>{s_name}</b></div>",
                                    unsafe_allow_html=True,
                                )

                                # Strategy prequels
                                if s_preqs:
                                    sp_html = " ".join(
                                        tag(p, "#607D8B") for p in s_preqs
                                    )
                                    st.markdown(
                                        f"<small>Requires: {sp_html}</small>",
                                        unsafe_allow_html=True,
                                    )

                                # Tactics — rich cards with replies, intent, difficulty, sequel
                                if tactics:
                                    st.markdown(
                                        tag("TACTICS", "#9C27B0", "0.7em"),
                                        unsafe_allow_html=True,
                                    )
                                    for tactic in tactics:
                                        tactic_detail_q = """
                                        MATCH (t:Tactic {name: $name})
                                        OPTIONAL MATCH (t)-[:REPLIES_TO]->(ctx)
                                        OPTIONAL MATCH (t)-[:INTENDS_TO]->(intent_node)
                                        OPTIONAL MATCH (t)-[:FOLLOWED_BY]->(nxt)
                                        RETURN t.difficulty   AS difficulty,
                                               t.applies_when AS applies_when,
                                               collect(DISTINCT ctx.name)[0]         AS replies_to,
                                               collect(DISTINCT intent_node.name)[0] AS intends_to,
                                               collect(DISTINCT nxt.name)[0]         AS sequel
                                        """
                                        td = (
                                            db.execute_read(
                                                tactic_detail_q, {"name": tactic}
                                            )
                                            or [{}]
                                        )[0]

                                        difficulty = td.get("difficulty")
                                        applies_when = td.get("applies_when")
                                        replies_to = td.get("replies_to")
                                        intends_to = td.get("intends_to")
                                        sequel = td.get("sequel")

                                        DIFF_COLOR = {
                                            "Beginner": "#4CAF50",
                                            "Intermediate": "#FF9800",
                                            "Advanced": "#F44336",
                                        }
                                        diff_badge = (
                                            tag(
                                                difficulty,
                                                DIFF_COLOR.get(difficulty, "#607D8B"),
                                                "0.65em",
                                            )
                                            if difficulty
                                            else ""
                                        )

                                        card = (
                                            f"<div style='border:1px solid #e0e0e0;border-radius:8px;"
                                            f"padding:8px 10px;margin:5px 0;background:#fafafa'>"
                                            f"<b style='font-size:0.9em'>{tactic}</b> {diff_badge}<br>"
                                        )
                                        if replies_to:
                                            card += (
                                                f"<span style='font-size:0.78em;color:#555'>"
                                                f"<b>Replies to:</b> {replies_to}</span><br>"
                                            )
                                        if intends_to:
                                            card += (
                                                f"<span style='font-size:0.78em;color:#555'>"
                                                f"<b>Intent:</b> {intends_to}</span><br>"
                                            )
                                        if applies_when:
                                            card += (
                                                f"<span style='font-size:0.75em;color:#777;font-style:italic'>"
                                                f"{applies_when}</span><br>"
                                            )
                                        if sequel:
                                            card += (
                                                f"<span style='font-size:0.75em;color:#9C27B0'>"
                                                f"Next: {sequel}</span>"
                                            )
                                        card += "</div>"
                                        st.markdown(card, unsafe_allow_html=True)
                                else:
                                    st.caption("No tactics yet.")

                    # ── Full relationship table (expandable) ─────────────────
                    all_rels_q = """
                    MATCH (c {name: $comp})-[r]-(other)
                    WHERE other.name IS NOT NULL
                    RETURN type(r) AS relation, other.name AS node,
                           labels(other)[0] AS node_type
                    ORDER BY type(r), other.name
                    """
                    all_rels = db.execute_read(all_rels_q, {"comp": comp_name}) or []
                    if all_rels:
                        with st.expander(
                            f"All {len(all_rels)} relationships for {comp_name}"
                        ):
                            st.dataframe(
                                [
                                    {
                                        "Relation": r["relation"],
                                        "Node": r["node"],
                                        "Type": r["node_type"],
                                    }
                                    for r in all_rels
                                ],
                                width="stretch",
                                hide_index=True,
                            )

# ── Tab 4: Proactive Learning ───────────────────────────────────────────────
with tab_proactive:
    render_knowledge_layer(exclude_types=["IntelligenceDomain"])
    st.markdown("### Proactive Learning")
    st.caption(
        "Answer these questions to receive personalized action items based on your leadership journey."
    )

    # Initialize session state
    if "proactive_initialized" not in st.session_state:
        st.session_state.proactive_initialized = False
        st.session_state.questions = []
        st.session_state.answers = {}
        st.session_state.action_items = []
        st.session_state.show_results = False

    # Load knowledge graph data
    is_local = db._local_fallback is not None if hasattr(db, '_local_fallback') else False
    if not db.driver and not is_local:
        st.error("Neo4j not connected. Please start the database.")
    else:
        # Fetch nodes and relationships
        nodes = (
            db.execute_read(
                "MATCH (n) WHERE n.name IS NOT NULL RETURN labels(n)[0] AS type, n.name AS name"
            )
            or []
        )
        relationships = (
            db.execute_read(
                "MATCH (a)-[r]->(b) WHERE a.name IS NOT NULL AND b.name IS NOT NULL RETURN a.name AS from_node, type(r) AS relation, b.name AS to_node"
            )
            or []
        )

        if not nodes:
            st.warning(
                "No knowledge graph data available. Run the pipeline to populate the graph first."
            )
        else:
            # Load corpus for video-specific content
            corpus_segments = []
            if os.path.exists("data/processed/corpus.json"):
                with open("data/processed/corpus.json", "r") as f:
                    corpus_segments = json.load(f)

            # Lazy import for Proactive Learning Engine (avoids heavy deps at startup)
            from src.core.proactive import ProactiveLearningEngine
            engine = ProactiveLearningEngine()

            # Video cross-reference stats
            stats = engine.get_video_stats()
            st.info(
                f"**Cross-Video Insights:** Questions connect this video to patterns from other YouTube leadership content"
            )

            # Generate questions button
            if st.button("Generate Questions from This Video", type="primary"):
                with st.spinner(
                    "Generating questions connecting this video to other YouTube leadership content..."
                ):
                    questions = engine.generate_questions(
                        nodes, relationships, corpus_segments, num_questions=5
                    )
                    st.session_state.questions = questions
                    st.session_state.answers = {}
                    st.session_state.show_results = False
                    st.session_state.proactive_initialized = True
                    st.rerun()

            # Display questions
            if st.session_state.questions:
                st.markdown("---")
                st.subheader("Video-Specific Reflection Questions")
                st.caption(
                    "Questions generated from THIS video's content, with insights from OTHER YouTube leadership content for cross-referencing."
                )

                for q in st.session_state.questions:
                    q_id = f"q_{q['id']}"

                    # Video reference card
                    with st.container(border=True):
                        st.markdown(f"**Q{q['id']}. {q['question']}**")

                        # Video context
                        if q.get("video_reference"):
                            st.markdown(
                                f'<small>:movie_camera: *"{q["video_reference"][:100]}..."*</small>',
                                unsafe_allow_html=True,
                            )

                        # Cross-video connection
                        if q.get("cross_video_connection"):
                            with st.expander("Other YouTube Content"):
                                st.markdown(
                                    f"<small>:link: **What other YouTube leaders say:** {q['cross_video_connection']}</small>",
                                    unsafe_allow_html=True,
                                )

                        # Alternative perspective
                        if q.get("alternative_perspective"):
                            st.info(
                                f":bulb: **Alternative view:** {q['alternative_perspective']}"
                            )

                        # Explanation
                        if q.get("explanation"):
                            st.markdown(f"_{q['explanation']}_")

                        # Radio buttons for options
                        options = q.get("options", ["Yes", "No", "Maybe", "Not sure"])
                        selected = st.radio(
                            f"Select your answer",
                            options,
                            index=None,
                            key=q_id,
                            horizontal=True,
                        )

                        if selected:
                            st.session_state.answers[q_id] = {
                                "question_id": q["id"],
                                "question": q["question"],
                                "answer": selected,
                                "selected_option": selected,
                            }

                        # Cross-video insight
                        if q.get("cross_video_connection"):
                            st.markdown(
                                f"<small>:link: Cross-reference: {q['cross_video_connection'][:80]}...</small>",
                                unsafe_allow_html=True,
                            )

                st.markdown("")

                # Generate action items button
                if st.button("Get My Personalized Action Items", type="primary"):
                    if len(st.session_state.answers) < len(st.session_state.questions):
                        st.warning(
                            f"Please answer all questions ({len(st.session_state.answers)}/{len(st.session_state.questions)} answered)"
                        )
                    else:
                        with st.spinner(
                            "Generating action items from this video and cross-referencing other YouTube content..."
                        ):
                            action_items = engine.generate_action_items(
                                st.session_state.questions,
                                list(st.session_state.answers.values()),
                                corpus_segments,
                            )
                            st.session_state.action_items = action_items
                            st.session_state.show_results = True
                            st.rerun()

                # Display action items
                if st.session_state.show_results and st.session_state.action_items:
                    st.markdown("---")
                    st.subheader("Your Personalized Action Items")
                    st.success(
                        "Based on your answers AND insights from other learners who watched this video:"
                    )

                    for item in st.session_state.action_items:
                        with st.container(border=True):
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.markdown(f"**{item['id']}. {item['action']}**")
                                if item.get("video_connection"):
                                    st.markdown(
                                        f"<small>:movie_camera: **This video:** {item['video_connection'][:80]}...</small>",
                                        unsafe_allow_html=True,
                                    )

                                # Cross-video support
                                if item.get("cross_video_support"):
                                    st.markdown(
                                        f"<small>:link: **Other YouTube content:** {item['cross_video_support'][:80]}...</small>",
                                        unsafe_allow_html=True,
                                    )

                                # Alternative approach
                                if item.get("alternative_approach"):
                                    st.info(
                                        f":bulb: **Other perspective:** {item['alternative_approach']}"
                                    )

                                # Balanced perspective
                                if item.get("balanced_perspective"):
                                    st.markdown(f"_{item['balanced_perspective']}_")

                            with col2:
                                st.markdown(
                                    f"**Timeline:** {item.get('timeline', 'This week')}"
                                )
                                st.caption(
                                    f"Success: {item.get('success_metric', 'Complete the action')}"
                                )

                            # Mark as complete checkbox
                            complete_key = f"complete_{item['id']}"
                            if complete_key not in st.session_state:
                                st.session_state[complete_key] = False

                            st.checkbox(
                                "I completed this action",
                                key=complete_key,
                                value=st.session_state.get(complete_key, False),
                            )

                    # Progress summary
                    completed = sum(
                        1
                        for item in st.session_state.action_items
                        if st.session_state.get(f"complete_{item['id']}", False)
                    )
                    total = len(st.session_state.action_items)
                    st.markdown("---")
                    st.progress(completed / total if total > 0 else 0)
                    st.markdown(f"**Progress:** {completed}/{total} actions completed")

                    # Share/Copy button
                    if st.button("Copy Action Items"):
                        action_text = "\n".join(
                            [
                                f"{i + 1}. {item['action']} ({item.get('timeline', 'This week')})"
                                for i, item in enumerate(st.session_state.action_items)
                            ]
                        )
                        st.text_area(
                            "Copy from here:",
                            value=action_text,
                            height=150,
                            key="copy_area",
                        )
                        st.caption("Select all and copy (Ctrl+A, Ctrl+C)")

            elif (
                not st.session_state.questions
                and st.session_state.proactive_initialized
            ):
                st.info(
                    "Click **'Generate Questions from This Video'** to start your personalized learning journey."
                )

# ── Tab 5: YouTube Perspectives ─────────────────────────────────────────────
with tab_perspectives:
    render_knowledge_layer(exclude_types=["IntelligenceDomain"])
    st.markdown("### Ask Any Question, Get YouTube Leader Perspectives")
    st.caption(
        "Enter any leadership/development question and see how famous YouTube leaders would answer it - with actionable insights from each perspective."
    )

    # Initialize session state
    if "perspectives_initialized" not in st.session_state:
        st.session_state.perspectives_initialized = False
        st.session_state.question_results = []
        st.session_state.current_question = ""

    # Lazy import for YouTube Perspectives Engine (avoids heavy deps at startup)
    from src.core.perspectives import YouTubePerspectivesEngine
    engine = YouTubePerspectivesEngine(db)

    # Show video knowledge stats
    video_stats = engine.get_video_stats()
    if video_stats["videos_ingested"] > 0:
        st.success(
            f"📺 Using knowledge from {video_stats['videos_ingested']} ingested video(s) | {video_stats['total_nodes']} concepts | {video_stats['total_relationships']} relationships"
        )
    else:
        st.info(
            "💡 Tip: Ingest YouTube videos to get personalized insights from your own knowledge graph!"
        )

    st.markdown("#### Available YouTube Leaders:")
    youtuber_cols = st.columns(4)
    youtuber_list = list(engine.YOUTUBERS.keys())
    for i, col in enumerate(youtuber_cols):
        if i < len(youtuber_list):
            with col:
                st.markdown(f"**{youtuber_list[i]}**")
                st.caption(
                    f"_{engine.YOUTUBERS[youtuber_list[i]]['expertise'][:40]}..._"
                )

    st.markdown("---")

    # Question input
    st.markdown("#### Ask Your Question:")
    user_question = st.text_input(
        "Enter any leadership or personal development question:",
        placeholder="e.g., How do I become a better leader? How do I build confidence?",
        key="youtuber_question",
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        topic_context = st.text_area(
            "Optional: Add context from the video (optional):",
            placeholder="Paste transcript excerpt or notes here for more specific answers...",
            height=80,
            key="topic_context",
        )
    with col2:
        num_perspectives = st.selectbox(
            "Number of perspectives:", [3, 5, 8], index=0, key="num_perspectives"
        )

    if st.button("Get Perspectives from YouTube Leaders", type="primary"):
        if user_question:
            with st.spinner(
                "Getting perspectives from YouTube leaders and your video knowledge..."
            ):
                st.session_state.current_question = user_question
                st.session_state.question_results = engine.generate_all_perspectives(
                    user_question,
                    db_client=db,
                    num_perspectives=num_perspectives,
                )
                st.session_state.perspectives_initialized = True
                st.rerun()
        else:
            st.warning("Please enter a question first.")

    # Display results
    if st.session_state.question_results and st.session_state.perspectives_initialized:
        st.markdown("---")
        st.markdown(
            f'#### How YouTube Leaders Answer: *"{st.session_state.current_question}"*'
        )

        # Display each perspective
        for i, result in enumerate(st.session_state.question_results):
            is_video_knowledge = result.get("is_video_knowledge", False)

            # Use different styling for video knowledge
            if is_video_knowledge:
                st.markdown("#### 📺 From Your Ingested Videos")
                st.markdown(f"_{result.get('answer', '')}_")

                # Show relevant concepts
                if result.get("relevant_nodes"):
                    st.markdown("**Relevant Concepts from Your Videos:**")
                    for node in result["relevant_nodes"]:
                        st.markdown(f"- {node}")

                # Show transcript excerpt
                if result.get("transcript_excerpt"):
                    with st.expander("Transcript Reference"):
                        st.markdown(f"_{result['transcript_excerpt']}..._")

                # Action Item
                if result.get("action_item"):
                    st.success(f"**ACTION ITEM:** {result.get('action_item')}")

                st.markdown("---")
            else:
                with st.container(border=True):
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.markdown(f"### {i}")
                        st.markdown(f"**{result.get('youtuber', 'YouTuber')}**")
                    with col2:
                        # Answer
                        st.markdown(f"**Answer:** {result.get('answer', '')}")

                        # Video connection
                        if (
                            result.get("video_connection")
                            and result.get("video_connection") != "N/A"
                        ):
                            st.markdown(
                                f"<small>:movie_camera: **Video Insight:** {result.get('video_connection')}</small>",
                                unsafe_allow_html=True,
                            )

                        # Quote
                        if result.get("quote"):
                            st.markdown(
                                f'<small>:speech_balloon: *"{result.get("quote")}"*</small>',
                                unsafe_allow_html=True,
                            )

                        st.markdown("---")

                        # Action Item (highlighted)
                        if result.get("action_item"):
                            st.success(
                                f"**:backhand_index_pointing_right: ACTION ITEM: {result.get('action_item')}"
                            )

                        # Key Insight
                    if result.get("key_insight"):
                        st.info(f":bulb: **Key Insight:** {result.get('key_insight')}")

        st.markdown("---")

        # Generate consolidated action plan
        st.markdown("#### Consolidated Action Plan")
        st.caption(
            "Combining insights from all YouTube leaders into one actionable plan"
        )

        if st.button("Generate Combined Action Plan", type="primary"):
            with st.spinner(
                "Creating your personalized action plan from YouTube leaders and your video knowledge..."
            ):
                action_plan = engine.generate_consensus_action_plan(
                    st.session_state.question_results, db_client=db
                )

                with st.container(border=True):
                    st.markdown(
                        f"**Primary Action:** {action_plan.get('primary_action', '')}"
                    )
                    st.markdown(
                        f"**Mindset Shift:** {action_plan.get('mindset_shift', '')}"
                    )
                    st.markdown(
                        f"**Daily Habit:** {action_plan.get('daily_habit', '')}"
                    )
                    st.markdown(
                        f"**Measurement:** {action_plan.get('measurement', '')}"
                    )
                    st.markdown(f"\n\n_{action_plan.get('perspective_summary', '')}_")

        # Reset button
        if st.button("Ask Another Question"):
            st.session_state.question_results = []
            st.session_state.current_question = ""
            st.rerun()

# ── Tab 6: Interview Intelligence ──────────────────────────────────────────
with tab_interview:
    render_knowledge_layer(exclude_types=["IntelligenceDomain"])
    st.markdown("### Interview Intelligence")
    st.caption(
        "Analyze interview-style content: find similar terms across the knowledge graph, "
        "detect Q&A patterns, and extract key concepts from transcripts."
    )

    if "interview_initialized" not in st.session_state:
        st.session_state.interview_initialized = False
        st.session_state.similar_terms_results = None
        st.session_state.qa_results = []
        st.session_state.insights_results = None
        st.session_state.expanded_terms = []
        st.session_state.extracted_terms = []
        st.session_state.xref_results = []

    from src.core.interview_intelligence import InterviewIntelligenceEngine
    iie = InterviewIntelligenceEngine(db_client=db)

    sim_tab, qa_tab, extract_tab = st.tabs(
        ["🔍 On Similar Terms", "🎙 Q&A Detection", "📋 Term Extraction"]
    )

    # ── Similar Terms Tab ────────────────────────────────────────────────
    with sim_tab:
        st.markdown("#### On Similar Terms")
        st.caption(
            "Enter a concept or term to find semantically similar terms "
            "across your ingested video knowledge graph."
        )

        sim_query = st.text_input(
            "Search for similar terms:",
            placeholder="e.g., 'Conflict Resolution', 'Trust', 'Innovation'",
            key="sim_terms_query",
        )

        col_sim1, col_sim2 = st.columns([1, 1])
        with col_sim1:
            sim_top_k = st.slider("Max results", 5, 25, 10, key="sim_top_k")
        with col_sim2:
            sim_min_sim = st.slider("Min similarity", 0.1, 0.9, 0.3, 0.05, key="sim_min_sim")

        if st.button("Find Similar Terms", type="primary", key="find_sim_terms"):
            if sim_query:
                with st.spinner("Computing semantic similarity across knowledge graph..."):
                    result = iie.find_similar_terms(
                        sim_query, top_k=sim_top_k, min_similarity=sim_min_sim
                    )
                    st.session_state.similar_terms_results = result
                    st.session_state.interview_initialized = True
                    st.rerun()
            else:
                st.warning("Please enter a term to search for.")

        if st.session_state.similar_terms_results:
            result = st.session_state.similar_terms_results

            if "error" in result:
                st.info(result["error"])
            else:
                st.success(
                    f"Found **{result['matches']}** similar terms for "
                    f"*\"{result['query']}\"* across {result['total_nodes']} graph nodes"
                )

                if result["results"]:
                    st.markdown("#### Ranked Similar Terms")
                    for i, r in enumerate(result["results"]):
                        sim_pct = int(r["similarity"] * 100)
                        color = "#4CAF50" if sim_pct >= 70 else "#FF9800" if sim_pct >= 50 else "#2196F3"
                        with st.container(border=True):
                            cols = st.columns([3, 1, 1])
                            with cols[0]:
                                st.markdown(f"**{r['term']}**")
                                st.caption(f"Type: {r['type']}")
                            with cols[1]:
                                st.markdown(
                                    f"<span style='color:{color};font-size:1.2em;font-weight:bold;'>"
                                    f"{sim_pct}%</span>",
                                    unsafe_allow_html=True,
                                )
                            with cols[2]:
                                st.markdown(f"<small>rank #{i+1}</small>", unsafe_allow_html=True)

                            if r.get("relationships"):
                                with st.expander(f"Relationships ({len(r['relationships'])})"):
                                    for rel in r["relationships"]:
                                        st.markdown(
                                            f"- **{rel['relation']}** → {rel['target']} "
                                            f"<small>({rel['target_type']})</small>",
                                            unsafe_allow_html=True,
                                        )

                    # Expand button
                    seed = [r["term"] for r in result["results"][:3]]
                    if st.button("Expand Related Terms", key="expand_terms_btn"):
                        with st.spinner("Expanding with second-degree similarity..."):
                            expanded = iie.expand_terms(seed, max_terms=15)
                            st.session_state.expanded_terms = expanded
                            st.rerun()

                    if st.session_state.expanded_terms:
                        st.markdown("#### Expanded Related Terms")
                        st.caption("Second-degree similarity expansion from top results")
                        for et in st.session_state.expanded_terms:
                            sim_pct = int(et["similarity"] * 100)
                            st.markdown(
                                f"- **{et['term']}** ({et.get('type', '?')}) — "
                                f"<span style='color:{color};'>{sim_pct}% similar</span>",
                                unsafe_allow_html=True,
                            )
                else:
                    st.warning("No terms met the minimum similarity threshold.")

    # ── Q&A Detection Tab ────────────────────────────────────────────────
    with qa_tab:
        st.markdown("#### Interview Q&A Detection")
        st.caption(
            "Detect question-answer patterns in ingested video transcripts "
            "and analyze interview styles."
        )

        if st.button("Analyze Transcripts for Q&A", type="primary", key="detect_qa"):
            with st.spinner("Scanning transcripts for Q&A patterns..."):
                corpus = iie.get_video_corpus()
                if not corpus:
                    st.warning("No transcript data found. Ingest videos first.")
                else:
                    qa_pairs = iie.detect_qa_pairs(corpus)
                    st.session_state.qa_results = qa_pairs
                    st.session_state.interview_initialized = True
                    st.rerun()

        if st.session_state.qa_results:
            qa_pairs = st.session_state.qa_results
            st.success(f"Detected **{len(qa_pairs)}** Q&A pairs across transcripts")

            # Stats
            analysis = iie.analyze_interview_style(qa_pairs)
            if analysis:
                st.markdown("#### Interview Style Analysis")
                mqa1, mqa2, mqa3 = st.columns(3)
                mqa1.metric("Total Q&A Pairs", analysis.get("total_qa_pairs", 0))
                mqa2.metric("Avg Q Length", f"{analysis.get('avg_question_length_words', 0)} words")
                mqa3.metric("Avg A Length", f"{analysis.get('avg_answer_length_words', 0)} words")

                q_types = analysis.get("question_types", {})
                st.markdown("**Question Type Breakdown:**")
                qtype_cols = st.columns(4)
                qtype_labels = [("Open", "open", "#4CAF50"), ("Closed", "closed", "#2196F3"),
                                ("Hypothetical", "hypothetical", "#FF9800"), ("Leading", "leading", "#9C27B0")]
                for col, (label, key, clr) in zip(qtype_cols, qtype_labels):
                    with col:
                        st.markdown(
                            f"<span style='background:{clr};color:white;padding:4px 12px;"
                            f"border-radius:8px;font-size:0.85em;display:block;text-align:center'>"
                            f"{label}: {q_types.get(key, 0)}</span>",
                            unsafe_allow_html=True,
                        )

            # Q&A pairs list
            st.markdown("#### Detected Q&A Pairs")
            for i, qa in enumerate(qa_pairs[:10]):
                with st.container(border=True):
                    st.markdown(f"**Q{i+1}:** {qa['question'][:200]}")
                    st.markdown(f"*A:* {qa['answer'][:300]}")
                    if qa.get("timestamp"):
                        st.caption(f"⏱ {qa['timestamp']:.1f}s — Video: `{qa.get('video_id', '?')}`")

            if len(qa_pairs) > 10:
                st.caption(f"... and {len(qa_pairs) - 10} more Q&A pairs")

            # Generate insights
            if st.button("Generate Interview Insights", key="gen_insights"):
                with st.spinner("Generating intelligence from Q&A patterns..."):
                    similar = None
                    if st.session_state.similar_terms_results:
                        similar = st.session_state.similar_terms_results.get("results", [])
                    insights = iie.generate_interview_insights(qa_pairs, similar)
                    st.session_state.insights_results = insights
                    st.rerun()

            if st.session_state.insights_results:
                ins = st.session_state.insights_results
                st.markdown("#### Interview Intelligence Insights")
                with st.container(border=True):
                    st.markdown(f"**Topic:** {ins.get('interview_topic', 'N/A')}")
                    st.markdown("**Key Insights:**")
                    for ki in ins.get("key_insights", []):
                        st.markdown(f"- {ki}")
                    st.markdown(f"**Interviewer Approach:** {ins.get('interviewer_approach', 'N/A')}")
                    if ins.get("notable_quotes"):
                        st.markdown("**Notable Quotes:**")
                        for nq in ins["notable_quotes"]:
                            st.markdown(f"> *\"{nq}\"*")
                    if ins.get("related_concepts"):
                        st.markdown("**Related Concepts:**")
                        st.markdown(", ".join(f"`{c}`" for c in ins["related_concepts"]))

    # ── Term Extraction Tab ──────────────────────────────────────────────
    with extract_tab:
        st.markdown("#### Key Term Extraction")
        st.caption(
            "Extract leadership terms from interview transcripts "
            "and cross-reference them against the knowledge graph."
        )

        extract_method = st.radio("Extraction method:", ["Heuristic", "LLM (Deep)"], horizontal=True, key="extract_method")

        if st.button("Extract Terms from Transcripts", type="primary", key="extract_terms"):
            with st.spinner("Extracting key terms..."):
                corpus = iie.get_video_corpus()
                if not corpus:
                    st.warning("No transcript data found.")
                else:
                    all_text = " ".join(s.get("transcript", "") for s in corpus)
                    use_llm = extract_method == "LLM (Deep)"
                    terms = iie.extract_key_terms(all_text, use_llm=use_llm)

                    if terms:
                        st.success(f"Extracted **{len(terms)}** key terms")
                        st.session_state.extracted_terms = terms
                        st.rerun()
                    else:
                        st.info("No leadership terms found in transcripts.")

        if st.session_state.get("extracted_terms"):
            terms = st.session_state.extracted_terms
            st.markdown("#### Extracted Leadership Terms")

            if isinstance(terms, list) and isinstance(terms[0], dict) and "term" in terms[0]:
                for t in terms:
                    cat = t.get("category", "")
                    st.markdown(f"- **{t['term']}**  <small>{cat}</small>", unsafe_allow_html=True)
            elif isinstance(terms, list) and isinstance(terms[0], dict) and "count" in terms[0]:
                total = sum(t["count"] for t in terms)
                for t in terms[:20]:
                    pct = int(t["count"] / total * 100) if total else 0
                    st.markdown(
                        f"- **{t['term']}** — {t['count']} mentions "
                        f"<span style='color:#888;'>({pct}%)</span>",
                        unsafe_allow_html=True,
                    )
                if len(terms) > 20:
                    st.caption(f"... and {len(terms) - 20} more terms")

            # Cross-reference with knowledge graph
            if st.button("Cross-Reference with Knowledge Graph", key="xref_terms"):
                with st.spinner("Cross-referencing terms with knowledge graph..."):
                    term_names = [t["term"] if isinstance(t, dict) and "term" in t else t for t in terms[:10]]
                    similar_all = iie.expand_terms(term_names, max_terms=20)
                    st.session_state.xref_results = similar_all
                    st.rerun()

            if st.session_state.get("xref_results"):
                st.markdown("#### Knowledge Graph Cross-References")
                st.caption("Terms that exist in your knowledge graph:")
                xref = st.session_state.xref_results
                found_count = sum(1 for r in xref if r.get("similarity", 0) > 0.5)
                st.info(f"{found_count} of {len(xref)} related terms found in the knowledge graph")
                for r in xref[:15]:
                    st.markdown(
                        f"- **{r['term']}** ({r.get('type', '?')}) "
                        f"— sim: {int(r['similarity']*100)}%",
                        unsafe_allow_html=True,
                    )

# ── Tab 7: Recording ────────────────────────────────────────────────────────
with tab_recording:
    st.markdown("### Record & Transcribe")
    st.caption(
        "Record audio, video, or your screen directly in the browser. "
        "Transcribe recordings and add them to the knowledge graph."
    )

    # Initialize recording session state
    if "rec_segments" not in st.session_state:
        st.session_state.rec_segments = []
        st.session_state.rec_id = None
        st.session_state.rec_processing = False
        st.session_state.rec_saved = False

    rec_col1, rec_col2 = st.columns([3, 2])

    with rec_col1:
        st.markdown("#### 🎬 Recorder")

        # Embed the browser-based recorder
        from src.recording.recorder_component import RECORDER_HTML
        components.html(RECORDER_HTML, height=520, scrolling=False)

        st.markdown(
            "<small style='color:#888;'>After recording, click <b>Download</b> "
            "in the recorder above, then upload the file below to transcribe.</small>",
            unsafe_allow_html=True,
        )

    with rec_col2:
        st.markdown("#### 📤 Upload & Process")

        uploaded_rec = st.file_uploader(
            "Upload a recording to transcribe:",
            type=["webm", "mp4", "wav", "mp3", "ogg", "m4a", "flac"],
            key="rec_file_upload",
            help="Supported formats: WebM, MP4, WAV, MP3, OGG, M4A, FLAC",
        )

        rec_title = st.text_input(
            "Recording title (optional):",
            placeholder="e.g., Team meeting, Leadership lecture",
            key="rec_title",
        )

        rec_source = st.selectbox(
            "Source type:",
            ["Recording", "Meeting", "Lecture", "Interview", "Presentation", "Other"],
            key="rec_source",
        )

        # Transcription method
        has_openai_key = bool(os.environ.get("OPENAI_API_KEY"))
        transcription_options = []
        if has_openai_key:
            transcription_options.append("OpenAI Whisper API (cloud, fast)")
        transcription_options.append("Local Whisper (on-device)")

        if len(transcription_options) > 1:
            transcription_method = st.radio(
                "Transcription method:",
                transcription_options,
                horizontal=True,
                key="rec_method",
            )
        elif transcription_options:
            transcription_method = transcription_options[0]
        else:
            transcription_method = "Local Whisper (on-device)"

        if "Local" in transcription_method:
            whisper_model = st.selectbox(
                "Whisper model size:",
                ["tiny", "base", "small", "medium"],
                index=1,
                key="rec_whisper_model",
                help="Larger models are more accurate but slower",
            )
        else:
            whisper_model = "base"

        # Process button
        if uploaded_rec and st.button("🎯 Transcribe & Add to Knowledge Graph", type="primary", key="rec_process"):
            from src.recording.processor import (
                generate_recording_id,
                transcribe_recording,
                transcribe_recording_openai,
                save_to_corpus,
            )

            with st.spinner("Processing recording..."):
                try:
                    # Save uploaded file to temp
                    file_bytes = uploaded_rec.read()
                    rec_id = generate_recording_id(file_bytes)

                    suffix = os.path.splitext(uploaded_rec.name)[1] or ".webm"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(file_bytes)
                        tmp_path = tmp.name

                    # Transcribe
                    st.info("🔊 Transcribing audio...")
                    if "OpenAI" in transcription_method:
                        segments = transcribe_recording_openai(tmp_path)
                    else:
                        segments = transcribe_recording(tmp_path, model_size=whisper_model)

                    # Clean up temp file
                    os.unlink(tmp_path)

                    if not segments:
                        st.warning("No speech detected in the recording.")
                    else:
                        # Calculate duration
                        duration = max(s["end"] for s in segments) if segments else 0

                        # Save to corpus
                        title = rec_title or uploaded_rec.name
                        count = save_to_corpus(
                            recording_id=rec_id,
                            segments=segments,
                            title=title,
                            duration_sec=duration,
                            source=rec_source,
                        )

                        st.session_state.rec_segments = segments
                        st.session_state.rec_id = rec_id
                        st.session_state.rec_saved = True

                        st.success(
                            f"✅ Transcribed **{count} segments** "
                            f"({duration:.0f}s) and added to the knowledge graph!"
                        )
                        st.balloons()

                except Exception as e:
                    st.error(f"Error processing recording: {e}")
                    st.code(traceback.format_exc(), language="text")

    # Show transcription results
    if st.session_state.rec_segments:
        st.markdown("---")
        st.markdown("#### 📝 Transcription Results")

        segments = st.session_state.rec_segments

        # Stats
        mc1, mc2, mc3 = st.columns(3)
        total_duration = max(s["end"] for s in segments) if segments else 0
        total_words = sum(len(s["text"].split()) for s in segments)
        mc1.metric("Segments", len(segments))
        mc2.metric("Duration", f"{int(total_duration // 60)}m {int(total_duration % 60)}s")
        mc3.metric("Words", total_words)

        # Full transcript
        with st.expander("View Full Transcript", expanded=True):
            for seg in segments:
                ts = int(seg["start"])
                m, s = divmod(ts, 60)
                st.markdown(f"`{m}:{s:02d}` {seg['text']}")

        # Download transcript
        transcript_text = "\n".join(
            f"[{int(s['start'] // 60)}:{int(s['start'] % 60):02d}] {s['text']}"
            for s in segments
        )
        st.download_button(
            "📥 Download Transcript (.txt)",
            data=transcript_text,
            file_name=f"transcript-{st.session_state.rec_id or 'recording'}.txt",
            mime="text/plain",
        )

        # Download as JSON
        transcript_json = json.dumps(segments, indent=2, ensure_ascii=False)
        st.download_button(
            "📥 Download Transcript (.json)",
            data=transcript_json,
            file_name=f"transcript-{st.session_state.rec_id or 'recording'}.json",
            mime="application/json",
        )

        if st.session_state.rec_saved:
            st.info(
                "💡 **Next steps:** Go to the **Ingested Knowledge** tab to see your recording, "
                "or use the sidebar pipeline to extract entities into the knowledge graph."
            )

        # Clear button
        if st.button("🗑️ Clear Transcription", key="rec_clear"):
            st.session_state.rec_segments = []
            st.session_state.rec_id = None
            st.session_state.rec_saved = False
            st.rerun()

# ── Tab 8: L&D Intelligence ─────────────────────────────────────────────────
with tab_learning:
    st.markdown("### 📚 L&D Intelligence")
    st.caption("Analyze skills gaps, build learning paths, and track competency development across your video knowledge base.")

    if "ld_initialized" not in st.session_state:
        st.session_state.ld_initialized = False
        st.session_state.ld_results = None
        st.session_state.ld_video_recs = None

    from src.core.learning_intelligence import LearningIntelligenceEngine
    ld_engine = LearningIntelligenceEngine(db_client=db)

    corpus_data = []
    registry_data = []
    if os.path.exists("data/processed/corpus.json"):
        with open("data/processed/corpus.json", "r") as f:
            corpus_data = json.load(f)
    if os.path.exists("data/processed/videos_registry.json"):
        with open("data/processed/videos_registry.json", "r") as f:
            registry_data = json.load(f)

    ld_video_id = _video_selector_widget(key_prefix="ld")
    ld_cache_key = f"learning_vid_{ld_video_id}" if ld_video_id else "learning_global"
    ld_cache = st.session_state.intel_cache.get(ld_cache_key, {})

    if ld_cache and ld_cache.get("status") != "failed" and "error" not in ld_cache:
        # ── Top metrics ───────────────────────────────────────────────────
        _render_metric_row([
            ("Videos Analyzed", ld_cache.get("video_count", len(registry_data)), None),
            ("Competencies Found", len(ld_cache.get("key_competencies", [])), None),
            ("Skills Gaps", len(ld_cache.get("skills_gaps", [])), None),
            ("Learning Paths", len(ld_cache.get("learning_paths", [])), None),
        ])

        # ── Competencies ──────────────────────────────────────────────────
        if ld_cache.get("key_competencies"):
            st.markdown("#### Key Competencies Identified")
            st.markdown(" ".join(
                f"<span style='background:#1976D2;color:white;padding:4px 12px;"
                f"border-radius:14px;font-size:0.85em;margin:3px;display:inline-block'>"
                f"{c}</span>"
                for c in ld_cache["key_competencies"]
            ), unsafe_allow_html=True)

        # ── Skills gaps + Learning paths side by side ─────────────────────
        gap_col, path_col = st.columns(2)
        with gap_col:
            st.markdown("#### 🎯 Skills Gaps")
            if ld_cache.get("skills_gaps"):
                for gap in ld_cache["skills_gaps"]:
                    sev = gap.get("severity", "medium")
                    st.markdown(
                        f"{_severity_icon(sev)} **{gap['gap']}**"
                        f"{_strength_badge(sev)}"
                        f"<br><small style='color:#666'>Addressed in: {', '.join(gap.get('videos_addressing_it', [])) or 'N/A'}</small>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No skills gaps detected.")

        with path_col:
            st.markdown("#### 🛤️ Suggested Learning Paths")
            if ld_cache.get("learning_paths"):
                for path in ld_cache["learning_paths"]:
                    st.markdown(
                        f"**Step {path['step']}:** {path['competency']}"
                        f"<br><small style='color:#666'>{path.get('rationale', '')}</small>"
                        f"<br><small style='color:#888'>Sources: {', '.join(path.get('source_videos', [])) or 'Multiple'}</small>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No learning paths generated.")

        # ── Cross-video themes + Priority areas ───────────────────────────
        if ld_cache.get("cross_video_themes"):
            st.markdown("#### 🔄 Cross-Video Themes")
            for theme in ld_cache["cross_video_themes"]:
                st.markdown(
                    f"**{theme['theme']}** — appears in {theme.get('video_count', '?')} videos"
                    f"<br><small style='color:#666'>{theme.get('description', '')}</small>",
                    unsafe_allow_html=True,
                )

        if ld_cache.get("priority_areas"):
            st.markdown("#### 🏆 Priority Development Areas")
            for pa in ld_cache["priority_areas"]:
                st.markdown(f"- 🔥 {pa}")

        if ld_cache.get("estimated_proficiency"):
            ep = ld_cache["estimated_proficiency"]
            st.info(f"⏱️ Estimated time to proficiency for **{ep.get('role', 'leader')}**: {ep.get('timeline', 'N/A')}")

        _render_intel_entities("Learning", registry_data)
    else:
        st.info("💡 Run the **Intelligence Pipeline** from the sidebar to auto-extract L&D insights from your entire corpus.")

    st.divider()

    # ── Interactive Skills Gap Analysis ─────────────────────────────────────
    st.markdown("#### 🔍 Interactive Skills Gap Analysis")
    col_ld1, col_ld2 = st.columns(2)
    with col_ld1:
        target_role = st.text_input("Target role:", placeholder="e.g., VP of Engineering, Team Lead", key="ld_role")
    with col_ld2:
        current_competencies = st.text_area("Current competencies (comma-separated):", placeholder="e.g., Communication, Strategic Planning", key="ld_competencies", height=68)

    if st.button("Analyze Skills Gap", type="primary", key="ld_analyze"):
        if target_role:
            with st.spinner("Analyzing skills gap against ingested knowledge..."):
                comp_list = [c.strip() for c in current_competencies.split(",") if c.strip()]
                result = ld_engine.analyze_skills_gap(target_role, comp_list)
                st.session_state.ld_results = result
                st.session_state.ld_initialized = True
                st.rerun()
        else:
            st.warning("Please enter a target role.")

    if st.session_state.ld_results:
        r = st.session_state.ld_results
        st.success(f"Skills gap analysis for **{r.get('target_role', 'N/A')}**")

        st.markdown("#### Priority Areas")
        for pa in r.get("priority_areas", []):
            st.markdown(f"- {pa}")

        if r.get("gap_analysis"):
            st.markdown("#### Gap Analysis")
            for ga in r["gap_analysis"]:
                st.markdown(f"- {ga}")

        if r.get("learning_path"):
            st.markdown("#### Recommended Learning Path")
            for step in r["learning_path"]:
                with st.container(border=True):
                    st.markdown(f"**Step {step['step']}:** {step['competency']}")
                    st.markdown(f"*Timeline: {step.get('timeline', 'N/A')}*")
                    if step.get("resources"):
                        st.caption("Resources: " + ", ".join(step["resources"]))

        st.markdown(f"**Estimated time:** {r.get('estimated_time', 'N/A')}")

    # Video recommendations by competency
    st.markdown("---")
    st.markdown("#### Video Recommendations by Competency")
    comp_search = st.text_input(
        "Enter a competency to find related videos:",
        placeholder="e.g., Leadership, Communication",
        key="ld_comp_search",
    )
    if st.button("Find Videos", key="ld_find_videos"):
        if comp_search:
            with st.spinner("Searching ingested video corpus..."):
                vids = ld_engine.get_video_recommendations(comp_search)
                st.session_state.ld_video_recs = vids
                st.rerun()

    if st.session_state.ld_video_recs:
        vids = st.session_state.ld_video_recs
        if vids.get("videos"):
            st.success(f"Found **{vids.get('count', 0)}** related videos")
            for v in vids["videos"]:
                st.markdown(f"- {v}")
        else:
            st.info(vids.get("message", "No videos found."))

# ── Tab 9: Competitive Intel ────────────────────────────────────────────────
with tab_competitive:
    st.markdown("### 🏢 Competitive Intelligence")
    st.caption("Analyze competitive landscapes, identify market opportunities, and track threats from your video knowledge base.")

    if "ci_initialized" not in st.session_state:
        st.session_state.ci_initialized = False
        st.session_state.ci_results = None

    from src.core.competitive_intelligence import CompetitiveIntelligenceEngine
    ci_engine = CompetitiveIntelligenceEngine(db_client=db)

    corpus_data = []
    if os.path.exists("data/processed/corpus.json"):
        with open("data/processed/corpus.json", "r") as f:
            corpus_data = json.load(f)
    registry_data = []
    if os.path.exists("data/processed/videos_registry.json"):
        with open("data/processed/videos_registry.json", "r") as f:
            registry_data = json.load(f)

    ci_video_id = _video_selector_widget(key_prefix="ci")
    ci_cache_key = f"competitive_vid_{ci_video_id}" if ci_video_id else "competitive_global"
    ci_cache = st.session_state.intel_cache.get(ci_cache_key, {})

    if ci_cache and ci_cache.get("status") != "failed" and "error" not in ci_cache:
        _render_metric_row([
            ("Videos Analyzed", ci_cache.get("video_count", len(registry_data)), None),
            ("Competitive Topics", len(ci_cache.get("competitive_topics", [])), None),
            ("Threats Detected", len(ci_cache.get("competitive_threats", [])), None),
            ("Opportunities", len(ci_cache.get("market_opportunities", [])), None),
        ])

        # ── Threats + Opportunities side by side ──────────────────────────
        threat_col, opp_col = st.columns(2)
        with threat_col:
            st.markdown("#### 🔴 Competitive Threats")
            if ci_cache.get("competitive_threats"):
                for t in ci_cache["competitive_threats"]:
                    sev = t.get("severity", "medium")
                    st.markdown(
                        f"{_severity_icon(sev)} **{t['threat']}**"
                        f"{_strength_badge(sev)}"
                        f"<br><small style='color:#666'>Competitor: {t.get('competitor', 'N/A')}</small>"
                        f"<br><small style='color:#888'>Source: {', '.join(t.get('videos', [])) or 'N/A'}</small>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No threats detected.")

        with opp_col:
            st.markdown("#### 🟢 Market Opportunities")
            if ci_cache.get("market_opportunities"):
                for o in ci_cache["market_opportunities"]:
                    st.markdown(
                        f"**{o['opportunity']}**"
                        f"<br><small style='color:#666'>Potential: {o.get('potential', 'N/A')} | Timeframe: {o.get('timeframe', 'N/A')}</small>"
                        f"<br><small style='color:#888'>Videos: {', '.join(o.get('videos', [])) or 'N/A'}</small>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No opportunities identified.")

        if ci_cache.get("strategic_recommendations"):
            st.markdown("#### 🎯 Strategic Recommendations")
            for rec in ci_cache["strategic_recommendations"]:
                st.markdown(f"- 💡 {rec}")

        if ci_cache.get("key_monitoring_signals"):
            with st.expander("📡 Key Monitoring Signals"):
                for s in ci_cache["key_monitoring_signals"]:
                    st.markdown(f"- {s}")

        _render_intel_entities("Competitive", registry_data)
    else:
        st.info("💡 Run the **Intelligence Pipeline** from the sidebar to auto-extract competitive insights.")

    st.divider()
    st.markdown("#### 🔍 Interactive Competitive Analysis")
    domain = st.text_input("Industry / domain:", placeholder="e.g., SaaS, AI, EdTech", key="ci_domain")
    competitors = st.text_area("Competitors (optional, one per line):", placeholder="e.g., Competitor A\nCompetitor B", key="ci_competitors", height=68)

    if st.button("Analyze Competitive Landscape", type="primary", key="ci_analyze"):
        if domain:
            with st.spinner("Analyzing competitive landscape..."):
                comp_list = [c.strip() for c in competitors.split("\n") if c.strip()] or None
                result = ci_engine.analyze_competitive_landscape(domain, competitors=comp_list)
                st.session_state.ci_results = result
                st.session_state.ci_initialized = True
                st.rerun()
        else:
            st.warning("Please enter a domain.")

    if st.session_state.ci_results:
        r = st.session_state.ci_results

        st.markdown("#### Competitive Threats")
        for t in r.get("competitive_threats", []):
            sev = t.get("severity", "medium")
            icon = "🔴" if sev == "high" else "🟡" if sev == "medium" else "🟢"
            st.markdown(f"{icon} **{t['threat']}** — {t.get('competitor', 'N/A')}")

        st.markdown("#### Market Opportunities")
        for o in r.get("market_opportunities", []):
            with st.container(border=True):
                st.markdown(f"**{o['opportunity']}**")
                st.caption(f"Potential: {o.get('potential', 'N/A')} | Timeframe: {o.get('timeframe', 'N/A')}")

        st.markdown("#### Strategic Recommendations")
        for rec in r.get("strategic_recommendations", []):
            st.markdown(f"- {rec}")

        if r.get("key_monitoring_signals"):
            with st.expander("Key Monitoring Signals"):
                for s in r["key_monitoring_signals"]:
                    st.markdown(f"- {s}")

# ── Tab 10: Sales Intelligence ──────────────────────────────────────────────
with tab_sales:
    st.markdown("### 💼 Sales Intelligence")
    st.caption("Analyze deals, extract buyer signals, and get recommended messaging from your ingested knowledge.")

    if "si_initialized" not in st.session_state:
        st.session_state.si_initialized = False
        st.session_state.si_results = None
        st.session_state.si_signals = None

    from src.core.sales_intelligence import SalesIntelligenceEngine
    si_engine = SalesIntelligenceEngine(db_client=db)

    corpus_data = []
    if os.path.exists("data/processed/corpus.json"):
        with open("data/processed/corpus.json", "r") as f:
            corpus_data = json.load(f)
    registry_data = []
    if os.path.exists("data/processed/videos_registry.json"):
        with open("data/processed/videos_registry.json", "r") as f:
            registry_data = json.load(f)

    si_video_id = _video_selector_widget(key_prefix="si")
    si_cache_key = f"sales_vid_{si_video_id}" if si_video_id else "sales_global"
    si_cache = st.session_state.intel_cache.get(si_cache_key, {})

    if si_cache and si_cache.get("status") != "failed" and "error" not in si_cache:
        _render_metric_row([
            ("Videos Analyzed", si_cache.get("video_count", len(registry_data)), None),
            ("Buyer Signals", len(si_cache.get("buyer_signals", [])), None),
            ("Deal Themes", len(si_cache.get("deal_themes", [])), None),
            ("Objection Handlers", len(si_cache.get("objection_handlers", [])), None),
        ])

        # ── Buyer Signals + Messaging side by side ────────────────────────
        sig_col, msg_col = st.columns(2)
        with sig_col:
            st.markdown("#### 📡 Buyer Signals")
            if si_cache.get("buyer_signals"):
                for bs in si_cache["buyer_signals"]:
                    strength = bs.get("strength", "medium")
                    st.markdown(
                        f"{_severity_icon(strength)} **{bs['signal']}**"
                        f"{_strength_badge(strength)}"
                        f"<br><small style='color:#666'>Mentioned {bs.get('count', 1)}x in content</small>"
                        f"<br><small style='color:#888'>Videos: {', '.join(bs.get('videos', [])) or 'N/A'}</small>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No buyer signals detected.")

        with msg_col:
            st.markdown("#### 💬 Recommended Messaging")
            if si_cache.get("recommended_messaging"):
                for msg in si_cache["recommended_messaging"]:
                    st.markdown(f"- ✅ {msg}")
            else:
                st.caption("No messaging recommendations.")

        # ── Objection Handlers + Next Actions ─────────────────────────────
        if si_cache.get("objection_handlers"):
            st.markdown("#### 🛡️ Objection Handlers")
            for oh in si_cache["objection_handlers"]:
                st.markdown(
                    f"**❌ {oh['objection']}**"
                    f"<br>→ ✅ {oh.get('response', '')}"
                    f"<br><small style='color:#888'>Source: {', '.join(oh.get('videos', [])) or 'N/A'}</small>",
                    unsafe_allow_html=True,
                )

        if si_cache.get("next_actions"):
            st.markdown("#### 🎯 Next Actions")
            for na in si_cache["next_actions"]:
                pri = na.get("priority", "medium")
                st.markdown(
                    f"{_severity_icon(pri)} **{na['action']}**"
                    f"{_strength_badge(pri)}",
                    unsafe_allow_html=True,
                )

        _render_intel_entities("Sales", registry_data)
    else:
        st.info("💡 Run the **Intelligence Pipeline** from the sidebar to auto-extract sales insights.")

    st.divider()
    deal_tab, signal_tab = st.tabs(["💼 Deal Analysis", "📡 Extract Signals"])

    with deal_tab:
        col_si1, col_si2 = st.columns(2)
        with col_si1:
            deal_context = st.text_area("Deal context:", placeholder="Describe the deal, stage, key stakeholders...", key="si_context", height=100)
        with col_si2:
            buyer_persona = st.text_input("Buyer persona:", placeholder="e.g., CTO, VP Marketing", key="si_persona")

        if st.button("Analyze Deal", type="primary", key="si_analyze"):
            if deal_context:
                with st.spinner("Analyzing deal against ingested knowledge..."):
                    result = si_engine.analyze_deal(deal_context, buyer_persona)
                    st.session_state.si_results = result
                    st.session_state.si_initialized = True
                    st.rerun()
            else:
                st.warning("Please enter deal context.")

    with signal_tab:
        if st.button("Extract Buyer Signals from Transcripts", type="primary", key="si_extract"):
            with st.spinner("Scanning transcripts for buyer signals..."):
                segments = [{"text": s.get("transcript", ""), "start": s.get("start_time", 0)}
                           for s in corpus_data if s.get("transcript")]
                signals = si_engine.extract_buyer_signals(segments)
                st.session_state.si_signals = signals
                st.rerun()

        if st.session_state.si_signals:
            signals = st.session_state.si_signals
            st.success(f"Found **{len(signals)}** buyer signals")
            for s in signals[:20]:
                st.markdown(f"- **{s['signal']}** — *\"{s['segment'][:80]}...\"*")

# ── Tab 11: Compliance & Policy ─────────────────────────────────────────────
with tab_compliance:
    st.markdown("### ⚖️ Compliance & Policy Intelligence")
    st.caption("Analyze compliance risks, scan transcripts for policy keywords, and get recommended controls.")

    if "comp_initialized" not in st.session_state:
        st.session_state.comp_initialized = False
        st.session_state.comp_results = None
        st.session_state.comp_scans = None

    from src.core.compliance_intelligence import ComplianceIntelligenceEngine
    comp_engine = ComplianceIntelligenceEngine(db_client=db)

    corpus_data = []
    if os.path.exists("data/processed/corpus.json"):
        with open("data/processed/corpus.json", "r") as f:
            corpus_data = json.load(f)
    registry_data = []
    if os.path.exists("data/processed/videos_registry.json"):
        with open("data/processed/videos_registry.json", "r") as f:
            registry_data = json.load(f)

    comp_video_id = _video_selector_widget(key_prefix="comp")
    comp_cache_key = f"compliance_vid_{comp_video_id}" if comp_video_id else "compliance_global"
    comp_cache = st.session_state.intel_cache.get(comp_cache_key, {})

    if comp_cache and comp_cache.get("status") != "failed" and "error" not in comp_cache:
        _render_metric_row([
            ("Videos Analyzed", comp_cache.get("video_count", len(registry_data)), None),
            ("Policy Topics", len(comp_cache.get("policy_topics_discussed", [])), None),
            ("Risks Found", len(comp_cache.get("risk_assessment", [])), None),
            ("Keyword Matches", comp_cache.get("keyword_findings_count", 0), None),
        ])

        # ── Risks + Controls side by side ─────────────────────────────────
        risk_col, ctrl_col = st.columns(2)
        with risk_col:
            st.markdown("#### ⚠️ Risk Assessment")
            if comp_cache.get("risk_assessment"):
                for ra in comp_cache["risk_assessment"]:
                    sev = ra.get("severity", "medium")
                    st.markdown(
                        f"{_severity_icon(sev)} **{ra['risk']}**"
                        f"{_strength_badge(sev)}"
                        f"<br>→ Mitigation: {ra.get('mitigation', 'N/A')}"
                        f"<br><small style='color:#888'>Videos: {', '.join(ra.get('videos', [])) or 'N/A'}</small>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No risks identified.")

        with ctrl_col:
            st.markdown("#### 🛡️ Recommended Controls")
            if comp_cache.get("recommended_controls"):
                for ctrl in comp_cache["recommended_controls"]:
                    st.markdown(f"- ✅ {ctrl}")
            else:
                st.caption("No controls recommended.")

        if comp_cache.get("policy_topics_discussed"):
            st.markdown("#### 📋 Policy Topics Discussed")
            for pt in comp_cache["policy_topics_discussed"]:
                sev = pt.get("severity", "medium")
                st.markdown(
                    f"{_severity_icon(sev)} **{pt['topic']}** — {pt.get('mentions', 0)} mentions"
                    f"<br><small style='color:#888'>Videos: {', '.join(pt.get('videos', [])) or 'N/A'}</small>",
                    unsafe_allow_html=True,
                )

        if comp_cache.get("monitoring_plan"):
            mp = comp_cache["monitoring_plan"]
            st.info(f"📋 **Monitoring:** {mp.get('frequency', 'N/A')} via {mp.get('method', 'N/A')}")

        _render_intel_entities("Compliance", registry_data)
    else:
        st.info("💡 Run the **Intelligence Pipeline** from the sidebar to auto-extract compliance insights.")

    st.divider()
    risk_tab, scan_tab = st.tabs(["⚠️ Risk Analysis", "🔍 Transcript Scan"])

    with risk_tab:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            policy_area = st.text_input("Policy area:", placeholder="e.g., Data Privacy, AI Ethics, GDPR", key="comp_policy")
        with col_c2:
            context = st.text_area("Context:", placeholder="Describe your compliance context...", key="comp_context", height=68)

        if st.button("Analyze Compliance Risk", type="primary", key="comp_analyze"):
            if policy_area:
                with st.spinner("Analyzing compliance risks..."):
                    result = comp_engine.analyze_compliance_risk(policy_area, context)
                    st.session_state.comp_results = result
                    st.session_state.comp_initialized = True
                    st.rerun()
            else:
                st.warning("Please enter a policy area.")

    with scan_tab:
        policy_keywords = st.text_input("Policy keywords to scan (comma-separated):", placeholder="e.g., privacy, compliance, regulation", key="comp_keywords")
        if st.button("Scan Transcripts", type="primary", key="comp_scan"):
            if policy_keywords:
                with st.spinner("Scanning transcripts for policy keywords..."):
                    keywords = [k.strip() for k in policy_keywords.split(",") if k.strip()]
                    segs = [{"text": s.get("transcript", ""), "start": s.get("start_time", 0), "video_id": s.get("video_id", "")}
                           for s in corpus_data if s.get("transcript")]
                    results = comp_engine.scan_transcript_for_compliance(segs, keywords)
                    st.session_state.comp_scans = results
                    st.rerun()
            else:
                st.warning("Please enter policy keywords.")

        if st.session_state.comp_scans:
            scans = st.session_state.comp_scans
            st.success(f"Found **{len(scans)}** compliance-related segments")
            for s in scans[:15]:
                st.markdown(f"- **{s['keyword']}** — *\"{s['context'][:100]}...\"*")

# ── Tab 12: R&D Intelligence ────────────────────────────────────────────────
with tab_rd:
    st.markdown("### 🔬 R&D Intelligence")
    st.caption("Discover emerging trends, innovation opportunities, and convergence patterns from your knowledge base.")

    if "rd_initialized" not in st.session_state:
        st.session_state.rd_initialized = False
        st.session_state.rd_results = None
        st.session_state.rd_related = None

    from src.core.rd_intelligence import RDIntelligenceEngine
    rd_engine = RDIntelligenceEngine(db_client=db)

    corpus_data = []
    if os.path.exists("data/processed/corpus.json"):
        with open("data/processed/corpus.json", "r") as f:
            corpus_data = json.load(f)
    registry_data = []
    if os.path.exists("data/processed/videos_registry.json"):
        with open("data/processed/videos_registry.json", "r") as f:
            registry_data = json.load(f)

    rd_video_id = _video_selector_widget(key_prefix="rd")
    rd_cache_key = f"rd_vid_{rd_video_id}" if rd_video_id else "rd_global"
    rd_cache = st.session_state.intel_cache.get(rd_cache_key, {})

    if rd_cache and rd_cache.get("status") != "failed" and "error" not in rd_cache:
        _render_metric_row([
            ("Videos Analyzed", rd_cache.get("video_count", len(registry_data)), None),
            ("Emerging Trends", len(rd_cache.get("emerging_trends", [])), None),
            ("Innovation Opportunities", len(rd_cache.get("innovation_opportunities", [])), None),
            ("Research Directions", len(rd_cache.get("research_directions", [])), None),
        ])

        # ── Trends + Opportunities side by side ───────────────────────────
        trend_col, inn_col = st.columns(2)
        with trend_col:
            st.markdown("#### 📈 Emerging Trends")
            if rd_cache.get("emerging_trends"):
                for t in rd_cache["emerging_trends"]:
                    impact = t.get("impact", "medium")
                    maturity = t.get("maturity", "N/A")
                    st.markdown(
                        f"{_severity_icon(impact)} **{t['trend']}**"
                        f"{_strength_badge(impact)}"
                        f"<br><small style='color:#666'>Maturity: {maturity}</small>"
                        f"<br><small style='color:#888'>Videos: {', '.join(t.get('videos', [])) or 'N/A'}</small>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No trends identified.")

        with inn_col:
            st.markdown("#### 💡 Innovation Opportunities")
            if rd_cache.get("innovation_opportunities"):
                for o in rd_cache["innovation_opportunities"]:
                    st.markdown(
                        f"**{o['opportunity']}**"
                        f"<br><small style='color:#666'>Effort: {o.get('effort', 'N/A')} | Potential: {o.get('potential', 'N/A')}</small>"
                        f"<br><small style='color:#888'>Videos: {', '.join(o.get('videos', [])) or 'N/A'}</small>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No opportunities found.")

        if rd_cache.get("research_directions"):
            st.markdown("#### 🔭 Research Directions")
            for rd_dir in rd_cache["research_directions"]:
                st.markdown(
                    f"- 🎯 **{rd_dir['direction']}** — {rd_dir.get('rationale', '')} ({rd_dir.get('timeframe', 'N/A')})",
                )

        if rd_cache.get("convergence_patterns"):
            with st.expander("🔗 Convergence Patterns"):
                for cp in rd_cache["convergence_patterns"]:
                    domains = ", ".join(cp.get("domains", []))
                    st.markdown(f"- **{domains}**: {cp.get('description', '')}")

        if rd_cache.get("potential_disruptions"):
            with st.expander("⚡ Potential Disruptions"):
                for d in rd_cache["potential_disruptions"]:
                    st.markdown(f"- {d}")

        _render_intel_entities("Rd", registry_data)
    else:
        st.info("💡 Run the **Intelligence Pipeline** from the sidebar to auto-extract R&D insights.")

    st.divider()
    st.markdown("#### 🔍 Interactive Innovation Analysis")
    col_rd1, col_rd2 = st.columns(2)
    with col_rd1:
        rd_domain = st.text_input("Domain:", placeholder="e.g., AI, Blockchain, Biotech", key="rd_domain")
    with col_rd2:
        rd_signals = st.text_area("Signals (optional, one per line):", placeholder="e.g., Rising GPU demand\nOpen source LLM adoption", key="rd_signals", height=68)

    if st.button("Analyze Innovation Trends", type="primary", key="rd_analyze"):
        if rd_domain:
            with st.spinner("Analyzing innovation trends..."):
                signals_list = [s.strip() for s in rd_signals.split("\n") if s.strip()] or None
                result = rd_engine.analyze_innovation_trends(rd_domain, signals=signals_list)
                st.session_state.rd_results = result
                st.session_state.rd_initialized = True
                st.rerun()
        else:
            st.warning("Please enter a domain.")

    if st.session_state.rd_results:
        r = st.session_state.rd_results
        st.markdown("#### Emerging Trends")
        for t in r.get("emerging_trends", []):
            mat = t.get("maturity", "")
            icon = "🌱" if mat == "emerging" else "📈" if mat == "growing" else "🌳"
            st.markdown(f"{icon} **{t['trend']}** — {mat} (impact: {t.get('impact', 'N/A')})")

        st.markdown("#### Innovation Opportunities")
        for o in r.get("innovation_opportunities", []):
            with st.container(border=True):
                st.markdown(f"**{o['opportunity']}**")
                st.caption(f"Effort: {o.get('effort', 'N/A')} | Potential: {o.get('potential', 'N/A')}")

        st.markdown("#### Research Directions")
        for d in r.get("research_directions", []):
            st.markdown(f"- **{d['direction']}** — {d.get('rationale', '')} ({d.get('timeframe', 'N/A')})")

        if r.get("convergence_patterns"):
            with st.expander("Convergence Patterns"):
                for cp in r["convergence_patterns"]:
                    st.markdown(f"- **{' + '.join(cp.get('domains', []))}**: {cp.get('description', '')}")

# ── Tab 13: Customer Intel ──────────────────────────────────────────────────
with tab_customer:
    st.markdown("### 👥 Customer Intelligence")
    st.caption("Analyze customer sentiment, extract pain points, and identify desired outcomes from ingested content.")

    if "cust_initialized" not in st.session_state:
        st.session_state.cust_initialized = False
        st.session_state.cust_results = None
        st.session_state.cust_needs = None

    from src.core.customer_intelligence import CustomerIntelligenceEngine
    cust_engine = CustomerIntelligenceEngine(db_client=db)

    corpus_data = []
    if os.path.exists("data/processed/corpus.json"):
        with open("data/processed/corpus.json", "r") as f:
            corpus_data = json.load(f)
    registry_data = []
    if os.path.exists("data/processed/videos_registry.json"):
        with open("data/processed/videos_registry.json", "r") as f:
            registry_data = json.load(f)

    cust_video_id = _video_selector_widget(key_prefix="cust")
    cust_cache_key = f"customer_vid_{cust_video_id}" if cust_video_id else "customer_global"
    cust_cache = st.session_state.intel_cache.get(cust_cache_key, {})

    if cust_cache and cust_cache.get("status") != "failed" and "error" not in cust_cache:
        # Sentiment headline
        sent = cust_cache.get("overall_sentiment", "neutral")
        sent_icon = "🟢" if sent == "positive" else "🔴" if sent == "negative" else "🔵"

        _render_metric_row([
            ("Overall Sentiment", f"{sent_icon} {sent.title()}", None),
            ("Videos Analyzed", cust_cache.get("video_count", len(registry_data)), None),
            ("Pain Points", len(cust_cache.get("pain_points", [])), None),
            ("Desired Outcomes", len(cust_cache.get("desired_outcomes", [])), None),
        ])

        # Sentiment breakdown
        if cust_cache.get("sentiment_breakdown"):
            sb = cust_cache["sentiment_breakdown"]
            cols = st.columns(3)
            cols[0].metric("Positive", sb.get("positive", 0))
            cols[1].metric("Negative", sb.get("negative", 0))
            cols[2].metric("Neutral", sb.get("neutral", 0))

        # ── Pain Points + Outcomes side by side ───────────────────────────
        pain_col, out_col = st.columns(2)
        with pain_col:
            st.markdown("#### 😟 Pain Points")
            if cust_cache.get("pain_points"):
                for pp in cust_cache["pain_points"]:
                    sev = pp.get("severity", "medium")
                    st.markdown(
                        f"{_severity_icon(sev)} **{pp['pain_point']}**"
                        f"{_strength_badge(sev)}"
                        f"<br><small style='color:#888'>Videos: {', '.join(pp.get('videos', [])) or 'N/A'}</small>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No pain points detected.")

        with out_col:
            st.markdown("#### 🎯 Desired Outcomes")
            if cust_cache.get("desired_outcomes"):
                for out in cust_cache["desired_outcomes"]:
                    pri = out.get("priority", "medium")
                    st.markdown(
                        f"{_severity_icon(pri)} **{out['outcome']}**"
                        f"{_strength_badge(pri)}",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No outcomes identified.")

        if cust_cache.get("key_themes"):
            st.markdown("#### 🔑 Key Themes")
            for t in cust_cache["key_themes"]:
                st.markdown(f"- **{t['theme']}** — sentiment: {t.get('sentiment', 'N/A')}")

        if cust_cache.get("recommendations"):
            st.markdown("#### 💡 Recommendations")
            for rec in cust_cache["recommendations"]:
                st.markdown(f"- {rec}")

        _render_intel_entities("Customer", registry_data)
    else:
        st.info("💡 Run the **Intelligence Pipeline** from the sidebar to auto-extract customer insights.")

    st.divider()
    col_cust1, col_cust2 = st.columns(2)
    with col_cust1:
        cust_topic = st.text_input("Topic / theme:", placeholder="e.g., Product experience, Support quality", key="cust_topic")
    with col_cust2:
        st.metric("Available Segments", len(corpus_data))

    if st.button("Analyze Customer Sentiment", type="primary", key="cust_analyze"):
        if cust_topic:
            with st.spinner("Analyzing customer sentiment from transcripts..."):
                segs = [{"text": s.get("transcript", ""), "start": s.get("start_time", 0)}
                       for s in corpus_data if s.get("transcript")]
                result = cust_engine.analyze_customer_sentiment(segs, topic=cust_topic)
                st.session_state.cust_results = result
                st.session_state.cust_initialized = True
                st.rerun()
        else:
            st.warning("Please enter a topic.")

    # Extract customer needs from text
    st.markdown("---")
    st.markdown("#### 📝 Extract Customer Needs from Text")
    cust_text = st.text_area("Paste a transcript excerpt or customer feedback:", placeholder="Paste text here to extract customer needs...", key="cust_text", height=80)
    if st.button("Extract Needs", key="cust_extract"):
        if cust_text:
            with st.spinner("Extracting customer needs..."):
                needs = cust_engine.extract_customer_needs(cust_text)
                st.session_state.cust_needs = needs
                st.rerun()

    if st.session_state.cust_needs:
        st.success(f"Extracted **{len(st.session_state.cust_needs)}** customer need signals")
        for n in st.session_state.cust_needs:
            st.markdown(f"- **{n['category']}**: {n['signal']}")

# ── Tab 14: Executive Intel ─────────────────────────────────────────────────
with tab_executive:
    st.markdown("### 📊 Executive Intelligence")
    st.caption("Generate executive briefs and strategic insights synthesized from your video content.")

    if "exec_initialized" not in st.session_state:
        st.session_state.exec_initialized = False
        st.session_state.exec_results = None
        st.session_state.exec_synthesis = None

    from src.core.executive_intelligence import ExecutiveIntelligenceEngine
    exec_engine = ExecutiveIntelligenceEngine(db_client=db)

    corpus_data = []
    registry_data = []
    if os.path.exists("data/processed/corpus.json"):
        with open("data/processed/corpus.json", "r") as f:
            corpus_data = json.load(f)
    if os.path.exists("data/processed/videos_registry.json"):
        with open("data/processed/videos_registry.json", "r") as f:
            registry_data = json.load(f)

    exec_video_id = _video_selector_widget(key_prefix="exec")
    exec_cache_key = f"executive_vid_{exec_video_id}" if exec_video_id else "executive_global"
    exec_cache = st.session_state.intel_cache.get(exec_cache_key, {})

    if exec_cache and exec_cache.get("status") != "failed" and "error" not in exec_cache:
        _render_metric_row([
            ("Videos Analyzed", exec_cache.get("video_count", len(registry_data)), None),
            ("Key Themes", len(exec_cache.get("key_themes", [])), None),
            ("Strategic Implications", len(exec_cache.get("strategic_implications", [])), None),
            ("Recommended Decisions", len(exec_cache.get("recommended_decisions", [])), None),
        ])

        # Executive summary
        if exec_cache.get("executive_summary"):
            st.markdown("#### 📋 Executive Summary")
            st.info(exec_cache["executive_summary"])

        # ── Implications + Decisions side by side ─────────────────────────
        impl_col, dec_col = st.columns(2)
        with impl_col:
            st.markdown("#### ⚡ Strategic Implications")
            if exec_cache.get("strategic_implications"):
                for si in exec_cache["strategic_implications"]:
                    urg = si.get("urgency", "medium")
                    st.markdown(
                        f"{_severity_icon(urg)} **{si['topic']}**"
                        f"{_strength_badge(urg)}"
                        f"<br>{si['implication']}",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No implications identified.")

        with dec_col:
            st.markdown("#### 🎯 Recommended Decisions")
            if exec_cache.get("recommended_decisions"):
                for rd in exec_cache["recommended_decisions"]:
                    st.markdown(
                        f"- **{rd['decision']}**"
                        f"<br><small style='color:#666'>{rd.get('rationale', '')}</small>"
                        f"<br><small style='color:#888'>Videos: {', '.join(rd.get('videos', [])) or 'N/A'}</small>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No decisions recommended.")

        if exec_cache.get("key_metrics"):
            with st.expander("📈 Key Metrics"):
                for km in exec_cache["key_metrics"]:
                    st.markdown(f"- **{km['metric']}**: {km.get('current_state', 'N/A')} → {km.get('target', 'N/A')} ({km.get('trend', 'N/A')})")

        if exec_cache.get("cross_domain_connections"):
            with st.expander("🔗 Cross-Domain Connections"):
                for cd in exec_cache["cross_domain_connections"]:
                    domains = ", ".join(cd.get("domains", []))
                    st.markdown(f"- **{domains}**: {cd.get('insight', '')}")

        _render_intel_entities("Executive", registry_data)
    else:
        st.info("💡 Run the **Intelligence Pipeline** from the sidebar to auto-extract executive insights.")

    st.divider()
    brief_tab, synth_tab = st.tabs(["📋 Executive Brief", "🧩 Video Synthesis"])

    with brief_tab:
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            exec_topics = st.text_area("Topics (one per line):", placeholder="e.g., AI Strategy\nTalent Retention", key="exec_topics", height=80)
        with col_ex2:
            exec_context = st.text_area("Optional context:", placeholder="Recent developments, priorities...", key="exec_context", height=80)

        if st.button("Generate Executive Brief", type="primary", key="exec_generate"):
            topics = [t.strip() for t in exec_topics.split("\n") if t.strip()]
            if topics:
                with st.spinner("Generating executive brief from ingested knowledge..."):
                    result = exec_engine.generate_executive_brief(topics, context=exec_context or None)
                    st.session_state.exec_results = result
                    st.session_state.exec_initialized = True
                    st.rerun()
            else:
                st.warning("Please enter at least one topic.")

    with synth_tab:
        if st.button("Synthesize All Video Insights", type="primary", key="exec_synthesize"):
            with st.spinner("Synthesizing insights from all ingested videos..."):
                video_data = {
                    "corpus": corpus_data,
                    "registry": registry_data,
                }
                result = exec_engine.synthesize_video_insights(video_data)
                st.session_state.exec_synthesis = result
                st.rerun()

        if st.session_state.exec_synthesis:
            s = st.session_state.exec_synthesis
            st.success("Video insights synthesized")
            st.markdown("#### Key Themes")
            for theme in s.get("key_themes", []):
                st.markdown(f"- {theme}")
            st.markdown("#### Actionable Insights")
            for ai in s.get("actionable_insights", []):
                st.markdown(f"- {ai}")
            if s.get("knowledge_gaps"):
                with st.expander("Knowledge Gaps"):
                    for g in s["knowledge_gaps"]:
                        st.markdown(f"- {g}")

# ── Tab 15: Org Knowledge ───────────────────────────────────────────────────
with tab_orgknow:
    st.markdown("### 📚 Organizational Knowledge")
    st.caption("Capture and organize knowledge assets, identify gaps, and cross-reference across your content.")

    if "org_initialized" not in st.session_state:
        st.session_state.org_initialized = False
        st.session_state.org_results = None
        st.session_state.org_gaps = None

    from src.core.org_knowledge import OrgKnowledgeEngine
    org_engine = OrgKnowledgeEngine(db_client=db)

    corpus_data = []
    registry_data = []
    if os.path.exists("data/processed/corpus.json"):
        with open("data/processed/corpus.json", "r") as f:
            corpus_data = json.load(f)
    if os.path.exists("data/processed/videos_registry.json"):
        with open("data/processed/videos_registry.json", "r") as f:
            registry_data = json.load(f)

    org_video_id = _video_selector_widget(key_prefix="org")
    org_cache_key = f"orgknowledge_vid_{org_video_id}" if org_video_id else "orgknowledge_global"
    org_cache = st.session_state.intel_cache.get(org_cache_key, {})

    if org_cache and org_cache.get("status") != "failed" and "error" not in org_cache:
        _render_metric_row([
            ("Videos Analyzed", org_cache.get("video_count", len(registry_data)), None),
            ("Core Concepts", len(org_cache.get("core_concepts", [])), None),
            ("Knowledge Gaps", len(org_cache.get("knowledge_gaps", [])), None),
            ("Expertise Level", org_cache.get("expertise_level", "N/A").title(), None),
        ])

        # ── Concepts + Gaps side by side ──────────────────────────────────
        conc_col, gap_col = st.columns(2)
        with conc_col:
            st.markdown("#### 🧠 Core Concepts")
            if org_cache.get("core_concepts"):
                for cc in org_cache["core_concepts"]:
                    st.markdown(f"- **{cc['concept']}**: {cc.get('definition', '')}")
            else:
                st.caption("No concepts identified.")

        with gap_col:
            st.markdown("#### ⚠️ Knowledge Gaps")
            if org_cache.get("knowledge_gaps"):
                for kg in org_cache["knowledge_gaps"]:
                    imp = kg.get("importance", "medium")
                    st.markdown(
                        f"{_severity_icon(imp)} **{kg['gap']}**"
                        f"{_strength_badge(imp)}",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No gaps identified.")

        if org_cache.get("key_principles"):
            st.markdown("#### 📐 Key Principles")
            for kp in org_cache["key_principles"]:
                st.markdown(f"- **{kp['principle']}**: {kp.get('explanation', '')}")

        if org_cache.get("best_practices"):
            with st.expander("✅ Best Practices"):
                for bp in org_cache["best_practices"]:
                    st.markdown(f"- {bp}")

        if org_cache.get("common_pitfalls"):
            with st.expander("❌ Common Pitfalls"):
                for cp in org_cache["common_pitfalls"]:
                    st.markdown(f"- **{cp['pitfall']}** → {cp.get('prevention', '')}")

        _render_intel_entities("Orgknowledge", registry_data)
    else:
        st.info("💡 Run the **Intelligence Pipeline** from the sidebar to auto-extract organizational knowledge.")

    st.divider()
    cap_tab, gap_tab = st.tabs(["📝 Knowledge Capture", "🔍 Gap Analysis"])

    with cap_tab:
        col_o1, col_o2 = st.columns(2)
        with col_o1:
            org_topic = st.text_input("Knowledge topic:", placeholder="e.g., Agile Methodology, OKR Framework", key="org_topic")
        with col_o2:
            org_source = st.text_input("Source (optional):", placeholder="e.g., Video ID, Book, Workshop", key="org_source")
        org_content = st.text_area("Content / notes:", placeholder="Paste knowledge content or transcript excerpt...", key="org_content", height=100)

        if st.button("Capture Knowledge Asset", type="primary", key="org_capture"):
            if org_topic and org_content:
                with st.spinner("Processing knowledge asset..."):
                    result = org_engine.capture_knowledge_asset(org_topic, org_content, source=org_source or None)
                    st.session_state.org_results = result
                    st.session_state.org_initialized = True
                    st.rerun()
            else:
                st.warning("Please enter both topic and content.")

    with gap_tab:
        if st.button("Find Knowledge Gaps", type="primary", key="org_find_gaps"):
            with st.spinner("Analyzing knowledge gaps across ingested content..."):
                if db.driver:
                    nodes = db.execute_read("MATCH (n) WHERE n.name IS NOT NULL RETURN n.name AS name, labels(n)[0] AS type")
                else:
                    nodes = []
                result = org_engine.find_knowledge_gaps(nodes)
                st.session_state.org_gaps = result
                st.rerun()

        if st.session_state.org_gaps:
            r = st.session_state.org_gaps
            if r.get("gaps"):
                st.warning(f"Found **{len(r['gaps'])}** knowledge gaps")
                for g in r["gaps"]:
                    st.markdown(f"- {g}")
            else:
                st.success(r.get("message", "No gaps identified."))

# ── Tab 16: Thought Leadership ──────────────────────────────────────────────
with tab_thought:
    st.markdown("### 💡 Thought Leadership")
    st.caption("Analyze industry pulse, identify key narratives, and discover content opportunities from your knowledge.")

    if "tl_initialized" not in st.session_state:
        st.session_state.tl_initialized = False
        st.session_state.tl_results = None
        st.session_state.tl_insights = None

    from src.core.thought_leadership import ThoughtLeadershipEngine
    tl_engine = ThoughtLeadershipEngine(db_client=db)

    corpus_data = []
    registry_data = []
    if os.path.exists("data/processed/corpus.json"):
        with open("data/processed/corpus.json", "r") as f:
            corpus_data = json.load(f)
    if os.path.exists("data/processed/videos_registry.json"):
        with open("data/processed/videos_registry.json", "r") as f:
            registry_data = json.load(f)

    tl_video_id = _video_selector_widget(key_prefix="tl")
    tl_cache_key = f"thoughtleadership_vid_{tl_video_id}" if tl_video_id else "thoughtleadership_global"
    tl_cache = st.session_state.intel_cache.get(tl_cache_key, {})

    if tl_cache and tl_cache.get("status") != "failed" and "error" not in tl_cache:
        momentum = tl_cache.get("industry_momentum", "stable")
        momentum_icon = "📈" if momentum == "rising" else "📉" if momentum == "declining" else "📊"

        _render_metric_row([
            ("Industry Momentum", f"{momentum_icon} {momentum.title()}", None),
            ("Videos Analyzed", tl_cache.get("video_count", len(registry_data)), None),
            ("Key Narratives", len(tl_cache.get("key_narratives", [])), None),
            ("Content Gaps", len(tl_cache.get("content_gaps", [])), None),
        ])

        # ── Narratives + Opportunities side by side ───────────────────────
        narr_col, gap_col = st.columns(2)
        with narr_col:
            st.markdown("#### 📢 Key Narratives")
            if tl_cache.get("key_narratives"):
                for kn in tl_cache["key_narratives"]:
                    strength = kn.get("strength", "emerging")
                    st.markdown(
                        f"{_severity_icon(strength)} **{kn['narrative']}**"
                        f"{_strength_badge(strength)}"
                        f"<br><small style='color:#666'>Proponents: {', '.join(kn.get('proponents', [])) or 'N/A'}</small>"
                        f"<br><small style='color:#888'>Videos: {', '.join(kn.get('videos', [])) or 'N/A'}</small>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No narratives identified.")

        with gap_col:
            st.markdown("#### 🎯 Content Gaps & Opportunities")
            if tl_cache.get("content_gaps"):
                for cg in tl_cache["content_gaps"]:
                    st.markdown(
                        f"**{cg['gap']}**"
                        f"<br><small style='color:#666'>Demand: {cg.get('audience_demand', 'N/A')}</small>"
                        f"<br><small style='color:#888'>Videos: {', '.join(cg.get('videos', [])) or 'N/A'}</small>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No gaps identified.")

        if tl_cache.get("recommended_angles"):
            st.markdown("#### ✍️ Recommended Thought Leadership Angles")
            for ra in tl_cache["recommended_angles"]:
                st.markdown(
                    f"- **{ra['angle']}** — {ra.get('rationale', '')} (format: {ra.get('format', 'N/A')})",
                )

        if tl_cache.get("thought_leaders"):
            with st.expander("👤 Thought Leaders Referenced"):
                for tl_ref in tl_cache["thought_leaders"]:
                    st.markdown(f"- **{tl_ref['name']}** — {tl_ref.get('expertise', '')}")

        if tl_cache.get("contrarian_viewpoints"):
            with st.expander("🔄 Contrarian Viewpoints"):
                for cv in tl_cache["contrarian_viewpoints"]:
                    st.markdown(f"- **{cv['viewpoint']}** — {cv.get('evidence', '')} (risk: {cv.get('risk_level', 'N/A')})")

        _render_intel_entities("Thoughtleadership", registry_data)
    else:
        st.info("💡 Run the **Intelligence Pipeline** from the sidebar to auto-extract thought leadership insights.")

    st.divider()
    pulse_tab, insight_tab = st.tabs(["🌐 Industry Pulse", "💡 Insight Extraction"])

    with pulse_tab:
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            tl_industry = st.text_input("Industry:", placeholder="e.g., SaaS, AI, Healthcare", key="tl_industry")
        with col_t2:
            tl_signals = st.text_area("Market signals (optional):", placeholder="e.g., Remote work shift\nAI regulation", key="tl_signals", height=68)

        if st.button("Analyze Industry Pulse", type="primary", key="tl_analyze"):
            if tl_industry:
                with st.spinner("Analyzing industry pulse from ingested content..."):
                    signals = [s.strip() for s in tl_signals.split("\n") if s.strip()] or None
                    result = tl_engine.analyze_industry_pulse(tl_industry, signals=signals)
                    st.session_state.tl_results = result
                    st.session_state.tl_initialized = True
                    st.rerun()
            else:
                st.warning("Please enter an industry.")

    with insight_tab:
        if st.button("Extract Leadership Insights", type="primary", key="tl_extract"):
            with st.spinner("Extracting leadership insights from transcripts..."):
                segs = [{"text": s.get("transcript", ""), "start": s.get("start_time", 0)}
                       for s in corpus_data if s.get("transcript")]
                insights = tl_engine.extract_leadership_insights(segs[:50])
                st.session_state.tl_insights = insights
                st.rerun()

        if st.session_state.tl_insights:
            insights = st.session_state.tl_insights
            st.success(f"Extracted **{len(insights)}** leadership insights")
            for ins in insights[:15]:
                st.markdown(f"- *\"{ins['insight'][:120]}...\"* — type: {ins.get('signal_type', 'N/A')}")

# ── Detect running environment ──────────────────────────────────────────────
_IS_CLOUD = os.environ.get("STREAMLIT_CLOUD", False) or os.path.exists("/mount/src")
print(f"DBG_IS_CLOUD={_IS_CLOUD}", flush=True)

# ── Sidebar: Ingest ──────────────────────────────────────────────────────────

st.sidebar.divider()
st.sidebar.header("Ingest New Leadership Content")

if _IS_CLOUD:
    # ── Cloud mode — YouTube downloads blocked, use uploads ───────────────
    st.sidebar.info(
        "🧠 **YouTube block detected.** Cloud servers can't download YouTube videos. "
        "Please run the pipeline on your **local computer** and upload the results here, "
        "or upload a transcript file below."
    )

    # Download launcher
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⬇️ Download Local Launcher")

    with open("setup_and_run.bat", "r", encoding="utf-8") as f:
        batch_content = f.read()
    st.sidebar.download_button(
        label="📥 Download setup_and_run.bat",
        data=batch_content,
        file_name="setup_and_run.bat",
        mime="text/bat",
        help="Download this batch file, run it on your Windows PC to set up and launch V-LKG locally"
    )

    st.sidebar.markdown(
        "<small>Run the downloaded file on Windows. It will:<br>"
        "1. Install Python if missing<br>"
        "2. Download latest code from GitHub<br>"
        "3. Install dependencies (pip)<br>"
        "4. Launch the app at localhost:8501</small>",
        unsafe_allow_html=True,
    )

    # Upload processed data files
    uploaded_transcript = st.sidebar.file_uploader(
        "Upload transcript (JSON, VTT, or SRT):",
        type=["json", "vtt", "srt", "txt"],
        key="transcript_upload"
    )
    uploaded_video_url = st.sidebar.text_input(
        "YouTube Video URL (required for upload):",
        key="cloud_video_url"
    )

    if uploaded_transcript and uploaded_video_url and st.sidebar.button("Process Uploaded Transcript"):
        import re
        import json as json_mod

        # Extract video ID
        vid_id = None
        for pattern in [r"(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})",
                        r"(?:embed/)([a-zA-Z0-9_-]{11})",
                        r"(?:shorts/)([a-zA-Z0-9_-]{11})"]:
            match = re.search(pattern, uploaded_video_url)
            if match:
                vid_id = match.group(1)
                break

        if not vid_id:
            st.sidebar.error("Could not extract video ID from URL")
        else:
            # Parse transcript
            content = uploaded_transcript.read().decode("utf-8")
            segments = []
            fname = uploaded_transcript.name.lower()

            try:
                if fname.endswith(".json"):
                    data = json_mod.loads(content)
                    # Handle various JSON formats
                    if isinstance(data, list):
                        segments = data
                    elif isinstance(data, dict):
                        segments = data.get("segments", data.get("events", [data]))
                elif fname.endswith(".vtt"):
                    import re as re_mod
                    lines = content.split("\n")
                    i = 0
                    while i < len(lines):
                        line = lines[i].strip()
                        if "-->" in line:
                            parts = line.split("-->")
                            start_str = parts[0].strip().replace(",", ".")
                            end_str = parts[1].strip().replace(",", ".")
                            start = sum(float(x) * 60 ** (2 - j) for j, x in enumerate(start_str.split(":")))
                            end = sum(float(x) * 60 ** (2 - j) for j, x in enumerate(end_str.split(":")))
                            text_parts = []
                            i += 1
                            while i < len(lines) and lines[i].strip():
                                text_parts.append(lines[i].strip())
                                i += 1
                            text = " ".join(text_parts)
                            if text.strip():
                                segments.append({"start": start, "end": end, "text": text.strip()})
                        i += 1
                elif fname.endswith(".srt"):
                    blocks = content.strip().split("\n\n")
                    for block in blocks:
                        blines = block.strip().split("\n")
                        if len(blines) >= 3 and "-->" in blines[1]:
                            parts = blines[1].split("-->")
                            start_str = parts[0].strip().replace(",", ".")
                            end_str = parts[1].strip().replace(",", ".")
                            start = sum(float(x) * 60 ** (2 - j) for j, x in enumerate(start_str.split(":")))
                            end = sum(float(x) * 60 ** (2 - j) for j, x in enumerate(end_str.split(":")))
                            text = " ".join(blines[2:]).strip()
                            if text:
                                segments.append({"start": start, "end": end, "text": text})
                else:
                    # Treat as plain text - one big segment
                    segments.append({"start": 0, "end": 60, "text": content.strip()[:5000]})

                if segments:
                    # Save to corpus
                    os.makedirs("data/processed", exist_ok=True)
                    corpus = []
                    if os.path.exists("data/processed/corpus.json"):
                        with open("data/processed/corpus.json", "r") as f:
                            corpus = json_mod.load(f)
                    corpus = [s for s in corpus if s.get("video_id") != vid_id]
                    new_segs = [{
                        "video_id": vid_id,
                        "start_time": s.get("start", s.get("start_time", 0)),
                        "end_time": s.get("end", s.get("end_time", 0)),
                        "transcript": s.get("text", s.get("transcript", "")),
                        "visual_text": ""
                    } for s in segments]
                    corpus.extend(new_segs)
                    with open("data/processed/corpus.json", "w") as f:
                        json_mod.dump(corpus, f, indent=4)

                    # Save to registry
                    registry = []
                    if os.path.exists("data/processed/videos_registry.json"):
                        with open("data/processed/videos_registry.json", "r") as f:
                            registry = json_mod.load(f)
                    registry = [v for v in registry if v.get("video_id") != vid_id]
                    registry.append({
                        "video_id": vid_id,
                        "title": f"Uploaded: {uploaded_transcript.name}",
                        "url": uploaded_video_url,
                        "channel": "Manual Upload",
                        "duration_sec": 0,
                        "thumbnail_url": "",
                        "summary": "",
                        "ingested_at": str(datetime.datetime.now())
                    })
                    with open("data/processed/videos_registry.json", "w") as f:
                        json_mod.dump(registry, f, indent=4)

                    st.sidebar.success(f"✅ Uploaded {len(new_segs)} transcript segments!")
                    st.rerun()
                else:
                    st.sidebar.error("Could not parse any segments from the uploaded file")
            except Exception as e:
                st.sidebar.error(f"Error processing upload: {e}")
else:
    # ── Local mode — YouTube downloads work ────────────────────────────────
    video_url = st.sidebar.text_input("YouTube Video URL", key="video_url_input")
    # Guard: only run pipeline on explicit button click, never on initial render
    if "pipeline_armed" not in st.session_state:
        st.session_state.pipeline_armed = False
    if st.sidebar.button("Run V-LKG Pipeline"):
        st.session_state.pipeline_armed = True
    if st.session_state.pipeline_armed and video_url:
        st.session_state.pipeline_armed = False  # fire once
        # Lazy import for pipeline (heavy deps only needed on local machine)
        from main import run_pipeline

        sb_progress = st.sidebar.progress(0.0)
        sb_label = st.sidebar.empty()
        sb_label.caption("0%")

        with st.status("Executing Multimodal Pipeline...", expanded=True) as status:

            def _on_progress(frac, label):
                sb_progress.progress(min(frac, 1.0))
                sb_label.caption(f"{int(frac * 100)}%")
                status.update(label=label)
                st.write(f"`{int(frac * 100):3d}%` {label}")

            try:
                run_pipeline(video_url, progress_cb=_on_progress)
                sb_progress.progress(1.0)
                sb_label.caption("100%")
                status.update(
                    label="Pipeline Complete!", state="complete", expanded=False
                )
                st.sidebar.success("Knowledge Graph extracted successfully!")
                st.rerun()
            except Exception as e:
                status.update(label="Pipeline Failed", state="error")
                sb_label.caption("Failed")
                st.sidebar.error(f"Error: {e}")
                st.error(f"**{type(e).__name__}:** {e}")
                st.code(traceback.format_exc(), language="text")
    elif video_url:
        st.sidebar.warning("Pipeline not triggered. Click the button to start.")

