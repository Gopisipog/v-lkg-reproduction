import json
import os
import traceback
import datetime
import streamlit as st
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

if db.driver:
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

# ── Tabs ────────────────────────────────────────────────────────────────────
tab_search, tab_knowledge, tab_strategy, tab_proactive, tab_perspectives, tab_interview = st.tabs(
    [
        "Search",
        "Ingested Knowledge",
        "Strategy Map",
        "Proactive Learning",
        "YouTube Perspectives",
        "Interview Intelligence",
    ]
)

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

    TYPE_COLORS = {
        "Competency": "#2196F3",
        "Concept": "#4CAF50",
        "Outcome": "#FF9800",
        "Personality": "#9C27B0",
        "Strategy": "#FF5722",
        "Tactic": "#E91E63",
        "Path": "#00BCD4",
    }

    def pill(name, color):
        return (
            f"<span style='background:{color};color:white;padding:2px 10px;"
            f"border-radius:12px;font-size:0.82em;margin:2px;display:inline-block'>"
            f"{name}</span>"
        )

    # ── Load registry & corpus ──────────────────────────────────────────────
    registry = []
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)

    corpus = []
    if os.path.exists(CORPUS_PATH):
        with open(CORPUS_PATH, "r", encoding="utf-8") as f:
            corpus = json.load(f)

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
                        st.image(vid["thumbnail_url"], use_container_width=True)
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

                    if vid_nodes:
                        EXTRACTED_TYPES = {"Competency", "Concept"}
                        ENRICHED_TYPES = {
                            "Strategy",
                            "Tactic",
                            "Path",
                            "Outcome",
                            "Personality",
                        }

                        extracted_groups: dict = {}
                        enriched_groups: dict = {}

                        for row in vid_nodes:
                            for ntype, name in [
                                (row["from_type"], row["from_name"]),
                                (row["to_type"], row["to_name"]),
                            ]:
                                if name.startswith("http://") or name.startswith(
                                    "https://"
                                ):
                                    continue
                                if ntype in EXTRACTED_TYPES:
                                    extracted_groups.setdefault(ntype, set()).add(name)
                                elif ntype in ENRICHED_TYPES:
                                    enriched_groups.setdefault(ntype, set()).add(name)

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
                                time_str = f"{r['time']:.1f}s" if r.get("time") else "—"
                                rel_rows.append(
                                    {
                                        "From": f"{r['from_name']} ({r['from_type']})",
                                        "Relation": r["relation"],
                                        "To": f"{r['to_name']} ({r['to_type']})",
                                        "Timestamp": time_str,
                                    }
                                )
                            st.dataframe(
                                rel_rows, use_container_width=True, hide_index=True
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

    if not db.driver:
        st.error("Neo4j not connected.")
    else:
        # ── Fetch all competencies that have at least one strategy ──────────
        comp_query = """
        MATCH (c)-[:HAS_STRATEGY|HAS_ALTERNATIVE]->(:Strategy)
        WHERE c.name IS NOT NULL
        RETURN DISTINCT c.name AS name, labels(c)[0] AS label
        ORDER BY c.name
        """
        competencies = db.execute_read(comp_query) or []

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
                                use_container_width=True,
                                hide_index=True,
                            )

# ── Tab 4: Proactive Learning ───────────────────────────────────────────────
with tab_proactive:
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
    if not db.driver:
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

# ── Detect running environment ──────────────────────────────────────────────
_IS_CLOUD = os.environ.get("STREAMLIT_CLOUD", False) or os.path.exists("/mount/src")

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
    video_url = st.sidebar.text_input("YouTube Video URL")
    if st.sidebar.button("Run V-LKG Pipeline"):
        if video_url:
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
        else:
            st.sidebar.warning("Please enter a valid URL.")

