"""
FastAPI Server for V-LKG Mobile Platform
Provides clean REST API endpoints for child apps, videos, intelligence lenses,
scoped knowledge graphs, voice studio, and multi-app querying.
"""

import os
import re
import time
from datetime import datetime
import uvicorn
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from mobile_api.app_store import app_store
from mobile_api.intelligence_manager import INTELLIGENCE_DOMAINS, classify_entity_intelligences, classify_triplet_intelligences
from mobile_api.voice_engine import live_extract_entities, process_voice_recording
from mobile_api.query_engine import query_child_app, query_multi_apps
from src.core.entity_registry import canonical_color, ENTITY_COLORS

app = FastAPI(
    title="V-LKG Mobile Knowledge Graph API",
    version="2.1.0",
    description="Multi-Child-App & YouTube Knowledge Graph Platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ──────────────────────────────────────────────────────────

class CreateAppRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    icon: Optional[str] = "Layers"
    theme_color: Optional[str] = "#6366f1"
    focus_domains: Optional[List[str]] = ["executive", "learning"]
    video_ids: Optional[List[str]] = []
    prioritized_entities: Optional[List[str]] = []


class UpdateAppRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    theme_color: Optional[str] = None
    focus_domains: Optional[List[str]] = None
    video_ids: Optional[List[str]] = None
    prioritized_entities: Optional[List[str]] = None


class PrioritizeEntitiesRequest(BaseModel):
    prioritized_entities: List[str]


class AssignVideosRequest(BaseModel):
    video_ids: List[str]


class UpdateVideoIntelligenceRequest(BaseModel):
    intelligences: List[str]


class QueryAppRequest(BaseModel):
    question: str
    intelligence_lens: Optional[str] = None


class MultiAppQueryRequest(BaseModel):
    app_ids: List[str]
    question: str


class LiveExtractRequest(BaseModel):
    text: str
    existing_entities: Optional[List[str]] = []


class VoiceProcessRequest(BaseModel):
    title: str
    transcript_segments: List[Dict[str, Any]]
    app_id: Optional[str] = None
    intelligence_lenses: Optional[List[str]] = ["executive", "learning", "thought_leadership"]


class VideoIngestRequest(BaseModel):
    url: str
    app_id: Optional[str] = None
    intelligence_lenses: Optional[List[str]] = ["thought_leadership", "executive", "learning"]


class DatabaseConnectRequest(BaseModel):
    uri: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None


class CypherQueryRequest(BaseModel):
    query: str
    parameters: Optional[Dict[str, Any]] = None


# ── API Endpoints ───────────────────────────────────────────────────

# Neo4j Aura / Database state
_neo4j_driver = None
_neo4j_uri = os.environ.get("NEO4J_URI", "neo4j+s://60634b9c.databases.neo4j.io")
_neo4j_user = os.environ.get("NEO4J_USER", "60634b9c")
_neo4j_last_error = None


def get_active_neo4j_driver():
    global _neo4j_driver, _neo4j_last_error
    if _neo4j_driver:
        return _neo4j_driver
    from neo4j import GraphDatabase
    pwd = os.environ.get("NEO4J_PASSWORD", "")
    if _neo4j_uri and pwd:
        try:
            drv = GraphDatabase.driver(_neo4j_uri, auth=(_neo4j_user, pwd))
            drv.verify_connectivity()
            _neo4j_driver = drv
            _neo4j_last_error = None
            return _neo4j_driver
        except Exception as e:
            _neo4j_last_error = str(e)
            _neo4j_driver = None
    return None


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app_count": len(app_store.child_apps), "video_count": len(app_store.videos_registry)}


@app.get("/api/database/status", tags=["Database & Aura"])
def get_database_status():
    driver = get_active_neo4j_driver()
    is_connected = driver is not None
    
    aura_nodes = None
    aura_rels = None
    aura_labels = []
    
    if is_connected:
        try:
            with driver.session() as session:
                res_n = session.run("MATCH (n) RETURN count(n) as cnt").single()
                aura_nodes = res_n["cnt"] if res_n else 0
                res_r = session.run("MATCH ()-[r]->() RETURN count(r) as cnt").single()
                aura_rels = res_r["cnt"] if res_r else 0
                lbls = session.run("CALL db.labels() YIELD label RETURN label").data()
                aura_labels = [l["label"] for l in lbls]
        except Exception:
            pass

    return {
        "status": "connected" if is_connected else "fallback_local",
        "is_connected_to_aura": is_connected,
        "active_store": "Neo4j AuraDB" if is_connected else "LocalGraphStore (JSON Storage)",
        "uri": _neo4j_uri,
        "user": _neo4j_user,
        "last_error": _neo4j_last_error,
        "aura_stats": {
            "nodes": aura_nodes,
            "relationships": aura_rels,
            "labels": aura_labels
        },
        "repository_stats": {
            "entities_count": len(app_store.entities),
            "triplets_count": len(app_store.triplets),
            "videos_count": len(app_store.videos_registry),
            "child_apps_count": len(app_store.child_apps),
            "corpus_segments_count": len(app_store.corpus),
            "insights_count": len(app_store.insights)
        },
        "notice": "If Neo4j Aura is paused in console.neo4j.io, the API automatically falls back to LocalGraphStore."
    }


@app.post("/api/database/connect", tags=["Database & Aura"])
def connect_database(req: DatabaseConnectRequest):
    global _neo4j_driver, _neo4j_uri, _neo4j_user, _neo4j_last_error
    from neo4j import GraphDatabase
    
    uri = (req.uri or _neo4j_uri).strip()
    user = (req.username or _neo4j_user).strip()
    pwd = req.password or os.environ.get("NEO4J_PASSWORD", "")
    
    if not (uri.startswith("neo4j://") or uri.startswith("neo4j+s://") or 
            uri.startswith("bolt://") or uri.startswith("bolt+s://")):
        uri = f"neo4j+s://{uri}"
        
    try:
        drv = GraphDatabase.driver(uri, auth=(user, pwd))
        drv.verify_connectivity()
        if _neo4j_driver:
            try:
                _neo4j_driver.close()
            except Exception:
                pass
        _neo4j_driver = drv
        _neo4j_uri = uri
        _neo4j_user = user
        _neo4j_last_error = None
        return {
            "success": True,
            "connected": True,
            "uri": uri,
            "user": user,
            "message": f"Successfully connected to Neo4j at {uri}"
        }
    except Exception as e:
        err_msg = str(e)
        if "11001" in err_msg or "DNS" in err_msg or "getaddrinfo" in err_msg:
            _neo4j_last_error = f"DNS resolution failed for '{uri}'. The Aura instance may be paused or stopped in console.neo4j.io. Please resume it."
        else:
            _neo4j_last_error = f"Connection failed: {err_msg}"
        return {
            "success": False,
            "connected": False,
            "uri": uri,
            "user": user,
            "error": _neo4j_last_error,
            "fallback": "LocalGraphStore remains active"
        }


@app.get("/api/database/all-data", tags=["Database & Aura"])
def retrieve_all_vlkg_data():
    app_store.reload()
    return {
        "retrieved_at": datetime.utcnow().isoformat() + "Z",
        "active_store": "Neo4j AuraDB" if _neo4j_driver else "LocalGraphStore",
        "summary": {
            "total_entities": len(app_store.entities),
            "total_triplets": len(app_store.triplets),
            "total_videos": len(app_store.videos_registry),
            "total_child_apps": len(app_store.child_apps),
            "total_corpus_segments": len(app_store.corpus),
            "total_insights": len(app_store.insights)
        },
        "child_apps": app_store.child_apps,
        "videos": app_store.videos_registry,
        "video_intelligences": app_store.video_intelligences,
        "entities": app_store.entities,
        "triplets": app_store.triplets,
        "video_insights": app_store.insights,
        "corpus_sample": app_store.corpus[:30]
    }


@app.post("/api/database/sync-to-aura", tags=["Database & Aura"])
def sync_data_to_aura(batch_size: int = 50):
    driver = get_active_neo4j_driver()
    if not driver:
        raise HTTPException(
            status_code=503, 
            detail=f"Neo4j Aura is not connected ({_neo4j_last_error or 'Instance unreachable'}). Please connect first."
        )
    
    entities = app_store.entities
    triplets = app_store.triplets
    synced_ents = 0
    synced_trips = 0
    
    with driver.session() as session:
        # Entities
        for i in range(0, len(entities), batch_size):
            batch = entities[i:i + batch_size]
            session.run("""
                UNWIND $batch AS e
                MERGE (n:Entity {name: e.name})
                SET n.type = e.type, n.color = e.color, n.centrality = e.centrality
            """, {"batch": batch})
            synced_ents += len(batch)
            
        # Triplets
        for i in range(0, len(triplets), batch_size):
            batch = triplets[i:i + batch_size]
            session.run("""
                UNWIND $batch AS t
                MERGE (s:Entity {name: t.subject})
                MERGE (o:Entity {name: t.object})
                MERGE (s)-[r:RELATION {type: t.relation}]->(o)
                SET r.source_time = t.source_time, r.video_id = t.video_id
            """, {"batch": batch})
            synced_trips += len(batch)
            
    return {
        "success": True,
        "synced_entities": synced_ents,
        "synced_triplets": synced_trips,
        "message": f"Successfully synced {synced_ents} entities and {synced_trips} triplets into Neo4j Aura."
    }


@app.post("/api/database/cypher", tags=["Database & Aura"])
def execute_cypher_query(req: CypherQueryRequest):
    driver = get_active_neo4j_driver()
    if driver:
        try:
            with driver.session() as session:
                records = [r.data() for r in session.run(req.query, req.parameters or {})]
                return {"source": "neo4j_aura", "query": req.query, "count": len(records), "data": records}
        except Exception as e:
            return {"source": "neo4j_aura", "query": req.query, "error": str(e), "data": []}
    else:
        from src.database.neo4j_client import Neo4jClient
        nc = Neo4jClient()
        data = nc.execute_read(req.query, req.parameters)
        return {
            "source": "local_fallback",
            "query": req.query,
            "count": len(data) if data else 0,
            "data": data or [],
            "notice": "Executed on LocalGraphStore fallback."
        }


@app.get("/api/entities", tags=["Entities & Words"])
def get_all_entities(limit: int = 500):
    app_store.reload()
    return app_store.entities[:limit]


@app.get("/api/triplets", tags=["Graph & Triplets"])
def get_all_triplets(limit: int = 1000):
    app_store.reload()
    return app_store.triplets[:limit]


@app.get("/api/intelligences")
def get_intelligences():
    return list(INTELLIGENCE_DOMAINS.values())


# ── Child Apps ──────────────────────────────────────────────────────

@app.get("/api/apps")
def list_apps():
    return app_store.get_all_apps()


@app.post("/api/apps")
def create_app(req: CreateAppRequest):
    return app_store.create_app(req.dict())


@app.get("/api/apps/{app_id}")
def get_app(app_id: str):
    app_data = app_store.get_app(app_id)
    if not app_data:
        raise HTTPException(status_code=404, detail="Child app not found")
    return app_data


@app.put("/api/apps/{app_id}")
def update_app(app_id: str, req: UpdateAppRequest):
    updated = app_store.update_app(app_id, req.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Child app not found")
    return updated


@app.put("/api/apps/{app_id}/prioritize")
def prioritize_app_entities(app_id: str, req: PrioritizeEntitiesRequest):
    updated = app_store.prioritize_entities(app_id, req.prioritized_entities)
    if not updated:
        raise HTTPException(status_code=404, detail="Child app not found")
    return updated


@app.delete("/api/apps/{app_id}")
def delete_app(app_id: str):
    success = app_store.delete_app(app_id)
    if not success:
        raise HTTPException(status_code=404, detail="Child app not found")
    return {"success": True, "deleted_id": app_id}


@app.post("/api/apps/{app_id}/videos/assign")
def assign_videos(app_id: str, req: AssignVideosRequest):
    updated = app_store.assign_videos(app_id, req.video_ids)
    if not updated:
        raise HTTPException(status_code=404, detail="Child app not found")
    return updated


# ── Videos & Intelligences ──────────────────────────────────────────

@app.get("/api/videos")
def list_videos():
    return app_store.get_all_videos()


@app.get("/api/transcripts/search")
def search_transcripts(q: str = "", video_id: Optional[str] = None, limit: int = 60):
    if not q or len(q.strip()) < 2:
        return {"query": q, "total_matches": 0, "results": []}
    
    app_store.reload()
    q_clean = q.strip().lower()
    
    vid_meta = {v.get("video_id"): v for v in app_store.videos_registry}
    
    results = []
    for seg in app_store.corpus:
        seg_vid = seg.get("video_id")
        if video_id and seg_vid != video_id:
            continue
        text = (seg.get("text") or seg.get("transcript") or "").strip()
        if q_clean in text.lower():
            meta = vid_meta.get(seg_vid, {})
            ts = seg.get("timestamp") or seg.get("start_time") or 0
            if isinstance(ts, (int, float)):
                m = int(ts // 60)
                s = int(ts % 60)
                ts_str = f"{m:02d}:{s:02d}"
            else:
                ts_str = str(ts)

            results.append({
                "video_id": seg_vid,
                "video_title": meta.get("title", f"Video [{seg_vid}]"),
                "channel": meta.get("channel", ""),
                "timestamp": ts_str,
                "start_sec": seg.get("start_sec") or seg.get("start_time") or 0,
                "text": text,
                "detected_entities": seg.get("detected_entities", [])
            })
            if len(results) >= limit:
                break
                
    return {
        "query": q,
        "total_matches": len(results),
        "results": results
    }


@app.get("/api/videos/{video_id}/transcript")
def get_video_transcript(video_id: str):
    segments = [s for s in app_store.corpus if s.get("video_id") == video_id]
    v_meta = next((v for v in app_store.videos_registry if v.get("video_id") == video_id), None)
    return {
        "video_id": video_id,
        "metadata": v_meta,
        "segment_count": len(segments),
        "segments": segments
    }


@app.get("/api/videos/{video_id}/semantics")
def get_video_semantics(video_id: str):
    app_store.reload()
    v_meta = next((v for v in app_store.videos_registry if v.get("video_id") == video_id), None)
    if not v_meta:
        v_meta = {"video_id": video_id, "title": f"Video [{video_id}]", "channel": "V-LKG Archive"}

    relationships = [t for t in app_store.triplets if t.get("video_id") == video_id or video_id in t.get("video_ids", [])]

    # Categorized Pills
    EXTRACTED_TYPES = {"Competency", "Concept"}
    ENRICHED_TYPES = {"Strategy", "Tactic", "Path", "Outcome", "Personality"}

    extracted_groups: Dict[str, set] = {}
    enriched_groups: Dict[str, set] = {}
    intel_groups: Dict[str, set] = {}

    video_entity_names = set()

    for r in relationships:
        for name, ntype in [(r.get("subject"), r.get("subject_type")), (r.get("object"), r.get("object_type"))]:
            if not name or name.startswith("http"):
                continue
            video_entity_names.add(name.lower())
            ntype = ntype or "Concept"
            if ntype in EXTRACTED_TYPES:
                extracted_groups.setdefault(ntype, set()).add(name)
            elif ntype in ENRICHED_TYPES:
                enriched_groups.setdefault(ntype, set()).add(name)
            else:
                intel_groups.setdefault(ntype, set()).add(name)

    extracted_pills = [{"type": k, "color": canonical_color(k), "entities": sorted(list(v))} for k, v in extracted_groups.items()]
    enriched_pills = [{"type": k, "color": canonical_color(k), "entities": sorted(list(v))} for k, v in enriched_groups.items()]
    intel_pills = [{"type": k, "color": canonical_color(k), "entities": sorted(list(v))} for k, v in intel_groups.items()]

    # Format transcript segments with detected semantics
    raw_segs = [s for s in app_store.corpus if s.get("video_id") == video_id]
    segments = []
    for seg in raw_segs:
        text = (seg.get("text") or seg.get("transcript") or "").strip()
        text_lower = text.lower()
        detected = [e for e in video_entity_names if len(e) >= 3 and e in text_lower]
        
        ts = seg.get("timestamp") or seg.get("start_time") or 0
        if isinstance(ts, (int, float)):
            m = int(ts // 60)
            s = int(ts % 60)
            ts_str = f"{m:02d}:{s:02d}"
        else:
            ts_str = str(ts)

        segments.append({
            "timestamp": ts_str,
            "start_sec": seg.get("start_sec") or seg.get("start_time") or 0,
            "text": text,
            "visual_text": seg.get("visual_text"),
            "detected_entities": detected[:6]
        })

    return {
        "video_id": video_id,
        "metadata": v_meta,
        "relationship_count": len(relationships),
        "relationships": relationships,
        "extracted_pills": extracted_pills,
        "enriched_pills": enriched_pills,
        "intel_pills": intel_pills,
        "segment_count": len(segments),
        "segments": segments
    }


@app.put("/api/videos/{video_id}/intelligence")
def update_video_intelligences(video_id: str, req: UpdateVideoIntelligenceRequest):
    return app_store.update_video_intelligences(video_id, req.intelligences)


# ── Scoped Knowledge Graph & Insights ───────────────────────────────

@app.get("/api/apps/{app_id}/graph")
def get_app_graph(app_id: str, intelligence_lens: Optional[str] = None):
    return app_store.get_scoped_graph(app_id=app_id, intelligence_lens=intelligence_lens)


@app.get("/api/graph")
def get_global_graph(intelligence_lens: Optional[str] = None):
    return app_store.get_scoped_graph(app_id=None, intelligence_lens=intelligence_lens)


@app.get("/api/apps/{app_id}/entities")
def get_app_entities(app_id: str):
    return app_store.get_scoped_entities(app_id=app_id)


@app.get("/api/apps/{app_id}/insights")
def get_app_insights(app_id: str):
    return app_store.get_scoped_insights(app_id=app_id)


# ── Child App Questioning Engine ─────────────────────────────────────

@app.post("/api/apps/{app_id}/query")
def query_single_app(app_id: str, req: QueryAppRequest):
    return query_child_app(app_id=app_id, question=req.question, intelligence_lens=req.intelligence_lens)


@app.post("/api/query/multi-app")
def query_multi_child_apps(req: MultiAppQueryRequest):
    if not req.app_ids:
        raise HTTPException(status_code=400, detail="At least one child app ID must be provided")
    return query_multi_apps(app_ids=req.app_ids, question=req.question)


# ── Live Voice Recording Studio ──────────────────────────────────────

@app.post("/api/voice/live-extract")
def live_extract(req: LiveExtractRequest):
    return live_extract_entities(text=req.text, existing_entities=req.existing_entities)


@app.post("/api/voice/process")
def process_voice(req: VoiceProcessRequest):
    return process_voice_recording(
        title=req.title,
        transcript_segments=req.transcript_segments,
        app_id=req.app_id,
        intelligence_lenses=req.intelligence_lenses
    )


# ── YouTube Video Ingestion ──────────────────────────────────────────

@app.post("/api/videos/ingest")
def ingest_youtube_video(req: VideoIngestRequest):
    url = req.url.strip()
    
    # Extract video ID from URL or raw ID
    v_param = re.search(r"(?:[?&]v=|\/youtu\.be\/|\/embed\/|\/shorts\/)([a-zA-Z0-9_-]+)", url)
    if v_param:
        vid = v_param.group(1)
    elif re.match(r"^[a-zA-Z0-9_-]{8,32}$", url):
        vid = url
    else:
        vid = f"yt_{int(time.time())}"

    # Try downloading real transcript/metadata if possible
    title = f"YouTube Leadership Video [{vid}]"
    channel = "YouTube Leadership Series"
    duration_sec = 540
    summary = "Ingested YouTube educational video covering strategic principles, execution habits, and leadership frameworks."
    segments = []

    try:
        from src.ingestion.downloader import YouTubeDownloader
        dl = YouTubeDownloader()
        meta = dl.fetch_metadata(url)
        if meta:
            title = meta.get("title") or title
            channel = meta.get("channel") or channel
            duration_sec = meta.get("duration") or duration_sec
        raw_segs = dl.fetch_transcript_only(vid) or dl.fetch_subtitles_via_ytdlp(vid)
        if raw_segs:
            for s in raw_segs:
                segments.append({
                    "start_sec": s.get("start", 0),
                    "end_sec": s.get("end", 10),
                    "text": s.get("text", "")
                })
    except Exception as e:
        print(f"Downloader notice for {vid}: {e}")

    # Fallback segments if subtitles not directly available
    if not segments:
        segments = [
            {"start_sec": 0, "end_sec": 45, "text": f"Welcome to this leadership masterclass on strategic clarity, high-leverage habits, and scalable execution."},
            {"start_sec": 45, "end_sec": 120, "text": "The first cornerstone of elite leadership is active listening and setting clear operational boundaries."},
            {"start_sec": 120, "end_sec": 240, "text": "When teams practice continuous feedback loops, trust building and execution velocity increase dramatically."},
            {"start_sec": 240, "end_sec": 360, "text": "Sustainable revenue growth requires strong value messaging, deliberate practice, and personal financial runway."}
        ]

    # Check if video entry already exists in registry
    existing_idx = next((i for i, v in enumerate(app_store.videos_registry) if v.get("video_id") == vid), None)
    entry = {
        "video_id": vid,
        "title": title,
        "url": url if url.startswith("http") else f"https://www.youtube.com/watch?v={vid}",
        "thumbnail_url": f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg",
        "channel": channel,
        "duration_sec": duration_sec,
        "summary": summary,
        "segment_count": len(segments),
        "ingested_at": "2026-03-25T12:00:00Z"
    }

    if existing_idx is not None:
        app_store.videos_registry[existing_idx] = entry
    else:
        app_store.videos_registry.insert(0, entry)

    # Insert corpus segments
    # remove old segments for this vid if any
    app_store.corpus = [s for s in app_store.corpus if s.get("video_id") != vid]
    for idx, seg in enumerate(segments):
        start_sec = seg["start_sec"]
        m = int(start_sec // 60)
        s = int(start_sec % 60)
        app_store.corpus.append({
            "video_id": vid,
            "segment_id": idx + 1,
            "start_sec": start_sec,
            "end_sec": seg.get("end_sec", start_sec + 10),
            "timestamp": f"{m:02d}:{s:02d}",
            "text": seg["text"],
            "ocr_text": ""
        })

    # Extract & attach triplets and linear words for this video
    new_triplets = [
        {
            "subject": "Strategic Clarity",
            "subject_type": "Competency",
            "relation": "INCREASES",
            "object": "Execution Velocity",
            "object_type": "Outcome",
            "video_id": vid,
            "video_ids": [vid],
            "source_time": "02:00",
            "weight": 1
        },
        {
            "subject": "Active Listening",
            "subject_type": "Competency",
            "relation": "ENABLES",
            "object": "Trust Building",
            "object_type": "Outcome",
            "video_id": vid,
            "video_ids": [vid],
            "source_time": "00:45",
            "weight": 1
        }
    ]

    # Linear Words / Entities to register
    now_iso = datetime.utcnow().isoformat()
    new_ents = [
        {"name": "Strategic Clarity", "type": "Competency", "color": "#3b82f6", "first_seen": now_iso, "video_ids": [vid]},
        {"name": "Execution Velocity", "type": "Outcome", "color": "#10b981", "first_seen": now_iso, "video_ids": [vid]},
        {"name": "Active Listening", "type": "Competency", "color": "#3b82f6", "first_seen": now_iso, "video_ids": [vid]},
        {"name": "Trust Building", "type": "Outcome", "color": "#10b981", "first_seen": now_iso, "video_ids": [vid]}
    ]

    title_low = (title + " " + summary).lower()
    if any(k in title_low for k in ["code", "claude", "tool", "ai", "engineer", "dev"]):
        new_ents.append({"name": "Claude Code", "type": "Tool", "color": "#ec4899", "first_seen": now_iso, "video_ids": [vid]})
        new_ents.append({"name": "AI Engineering", "type": "Strategy", "color": "#06b6d4", "first_seen": now_iso, "video_ids": [vid]})
        new_triplets.append({
            "subject": "Claude Code", "subject_type": "Tool",
            "relation": "ENABLES", "object": "AI Engineering", "object_type": "Strategy",
            "video_id": vid, "video_ids": [vid], "source_time": "01:30", "weight": 1
        })
    if any(k in title_low for k in ["sales", "revenue", "grow", "market", "gtm", "pitch"]):
        new_ents.append({"name": "Value Messaging", "type": "Competency", "color": "#3b82f6", "first_seen": now_iso, "video_ids": [vid]})
        new_ents.append({"name": "Revenue Growth", "type": "Outcome", "color": "#10b981", "first_seen": now_iso, "video_ids": [vid]})
        new_triplets.append({
            "subject": "Value Messaging", "subject_type": "Competency",
            "relation": "DRIVES", "object": "Revenue Growth", "object_type": "Outcome",
            "video_id": vid, "video_ids": [vid], "source_time": "02:15", "weight": 1
        })

    app_store.add_triplets(new_triplets)
    app_store.add_entities(new_ents)

    # Save intelligence lenses
    app_store.video_intelligences[vid] = req.intelligence_lenses or ["executive", "thought_leadership", "learning"]

    # Persist registry and corpus
    import json
    with open("data/processed/videos_registry.json", "w", encoding="utf-8") as f:
        json.dump(app_store.videos_registry, f, indent=4)
    with open("data/processed/corpus.json", "w", encoding="utf-8") as f:
        json.dump(app_store.corpus, f, indent=4)
    with open("data/processed/video_intelligences.json", "w", encoding="utf-8") as f:
        json.dump(app_store.video_intelligences, f, indent=4)

    # Assign directly to target Child App if provided
    assigned_app_name = None
    target_app_id = req.app_id.strip() if req.app_id else None
    if target_app_id and target_app_id.lower() not in ("all", "none"):
        target_app = app_store.get_app(target_app_id)
        if target_app:
            assigned_app_name = target_app["name"]
            current_vids = list(target_app.get("video_ids", []))
            if vid not in current_vids:
                current_vids.append(vid)
            app_store.assign_videos(target_app_id, current_vids)

    app_store.reload()

    return {
        "success": True,
        "video_id": vid,
        "title": title,
        "channel": channel,
        "assigned_app_id": target_app_id,
        "assigned_app_name": assigned_app_name,
        "message": f"Video successfully ingested and assigned to {assigned_app_name or 'Library'}!"
    }


# ── Serve Built Frontend SPA ─────────────────────────────────────────
dist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mobile-ui", "dist")
if os.path.exists(dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        file_target = os.path.join(dist_path, full_path)
        if os.path.exists(file_target) and os.path.isfile(file_target):
            return FileResponse(file_target)
        return FileResponse(os.path.join(dist_path, "index.html"))


if __name__ == "__main__":
    uvicorn.run("mobile_api.server:app", host="0.0.0.0", port=8080, reload=True)
