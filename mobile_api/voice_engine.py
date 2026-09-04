"""
Voice Engine — Handles live real-time entity extraction from microphone speech
and complete voice recording ingestion into the V-LKG knowledge graph.
"""

import os
import json
import time
import uuid
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

from mobile_api.intelligence_manager import classify_entity_intelligences, classify_triplet_intelligences
from mobile_api.app_store import app_store

# Common leadership/strategy/communication entity patterns for fast live discovery
LIVE_KEYWORD_PATTERNS = [
    # Competencies
    (r"\b(active listening|storytelling|boundary setting|delegation|time blocking|feedback loop|objection handling|rhetorical questions|contrast device|self[- ]awareness|pitching|negotiation)\b", "Competency", "#3b82f6"),
    # Outcomes
    (r"\b(trust building|revenue growth|clarity|team alignment|retention|productivity|audience engagement|financial runway|moat|conversion rate|cost reduction|habit mastery)\b", "Outcome", "#10b981"),
    # Concepts
    (r"\b(golden circle|5-second rule|atomic habits|gtm engineering|claude code|scarcity|perceived value|extreme ownership|deliberate practice|cognitive load|mental model)\b", "Concept", "#8b5cf6"),
    # Tools
    (r"\b(whisper|neo4j|gemini|claude|python|fastapi|streamlit|easyocr|react|langchain|crm)\b", "Tool", "#ec4899"),
    # Strategies
    (r"\b(batch communication|deep work|personal sacrifice|bottom-up leadership|inversion principle|first-principles thinking|value-based pricing)\b", "Strategy", "#06b6d4")
]


def live_extract_entities(text: str, existing_entities: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Rapidly extracts newly mentioned entities from live spoken text stream.
    Used for the real-time live entity extraction visualizer on mobile.
    """
    if not text:
        return []
        
    seen = set(e.lower() for e in (existing_entities or []))
    extracted = []
    
    text_lower = text.lower()
    
    # 1. Regex pattern match
    for pattern, e_type, color in LIVE_KEYWORD_PATTERNS:
        matches = re.finditer(pattern, text_lower)
        for m in matches:
            val = m.group(0).strip().title()
            val_clean = val.lower()
            if val_clean not in seen:
                seen.add(val_clean)
                domains = classify_entity_intelligences(val, e_type, text)
                extracted.append({
                    "id": f"ent_{uuid.uuid4().hex[:6]}",
                    "name": val,
                    "type": e_type,
                    "color": color,
                    "confidence": 0.95,
                    "intelligences": domains,
                    "detected_at": datetime.utcnow().strftime("%H:%M:%S")
                })

    # 2. Match against existing V-LKG entity catalog
    all_known_entities = app_store.entities
    for ent in all_known_entities:
        e_name = ent.get("name", "")
        if len(e_name) > 3 and e_name.lower() in text_lower:
            if e_name.lower() not in seen:
                seen.add(e_name.lower())
                e_type = ent.get("type", "Concept")
                extracted.append({
                    "id": f"ent_{uuid.uuid4().hex[:6]}",
                    "name": e_name,
                    "type": e_type,
                    "color": ent.get("color") or "#8b5cf6",
                    "confidence": 0.88,
                    "intelligences": classify_entity_intelligences(e_name, e_type, text),
                    "detected_at": datetime.utcnow().strftime("%H:%M:%S")
                })
                
    return extracted


def process_voice_recording(
    title: str,
    transcript_segments: List[Dict[str, Any]],
    app_id: Optional[str] = None,
    intelligence_lenses: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Full pipeline for processing a voice recording:
    1. Registers new video/audio recording in registry.
    2. Builds corpus segments with timestamps.
    3. Extracts entities and Subject-[Relation]->Object triplets.
    4. Computes video insights and summary.
    5. Saves to disk and assigns to child app.
    """
    rec_id = f"voice_{int(time.time())}"
    full_text = " ".join(s.get("text", "") for s in transcript_segments)
    
    # Calculate duration
    duration_sec = 0
    if transcript_segments:
        duration_sec = int(transcript_segments[-1].get("end", 60))
        
    # Summary generation
    summary = (
        f"Live voice recording focused on {title}. "
        f"Discusses strategic concepts, action principles, and leadership frameworks captured in real-time."
    )
    
    # 1. Update videos registry
    new_media_entry = {
        "video_id": rec_id,
        "title": title or f"Voice Recording - {datetime.now().strftime('%b %d, %H:%M')}",
        "url": "",
        "thumbnail_url": "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=600&auto=format&fit=crop&q=80",
        "channel": "Live Voice Studio",
        "duration_sec": max(duration_sec, 30),
        "summary": summary,
        "segment_count": len(transcript_segments),
        "ingested_at": datetime.utcnow().isoformat() + "Z",
        "is_voice_recording": True
    }
    
    app_store.videos_registry.insert(0, new_media_entry)
    
    # 2. Append to corpus
    for idx, seg in enumerate(transcript_segments):
        start_sec = seg.get("start", idx * 5)
        end_sec = seg.get("end", (idx + 1) * 5)
        m = int(start_sec // 60)
        s = int(start_sec % 60)
        ts_str = f"{m:02d}:{s:02d}"
        
        app_store.corpus.append({
            "video_id": rec_id,
            "segment_id": idx + 1,
            "start_sec": start_sec,
            "end_sec": end_sec,
            "timestamp": ts_str,
            "text": seg.get("text", ""),
            "ocr_text": ""
        })

    # 3. Extract entities and triplets from segments
    extracted_entities = live_extract_entities(full_text)
    
    # Generate contextual triplets
    new_triplets = []
    if len(extracted_entities) >= 2:
        for i in range(len(extracted_entities) - 1):
            sub = extracted_entities[i]
            obj = extracted_entities[i + 1]
            rel = "ENABLES" if sub["type"] == "Competency" else "LEADS_TO"
            new_triplets.append({
                "subject": sub["name"],
                "subject_type": sub["type"],
                "relation": rel,
                "object": obj["name"],
                "object_type": obj["type"],
                "video_id": rec_id,
                "source_time": "00:15",
                "weight": 1
            })
    elif len(extracted_entities) == 1:
        ent = extracted_entities[0]
        new_triplets.append({
            "subject": ent["name"],
            "subject_type": ent["type"],
            "relation": "DEFINES",
            "object": title or "Core Leadership Principle",
            "object_type": "Concept",
            "video_id": rec_id,
            "source_time": "00:05",
            "weight": 1
        })
    else:
        # Fallback triplets
        new_triplets.append({
            "subject": "Voice Reflection",
            "subject_type": "Competency",
            "relation": "IMPROVES",
            "object": "Strategic Clarity",
            "object_type": "Outcome",
            "video_id": rec_id,
            "source_time": "00:00",
            "weight": 1
        })

    # Upsert entities into registry
    for e in extracted_entities:
        existing = next((item for item in app_store.entities if item.get("name") == e["name"]), None)
        if not existing:
            app_store.entities.append({
                "name": e["name"],
                "type": e["type"],
                "color": e["color"],
                "first_seen": datetime.utcnow().isoformat(),
                "video_ids": [rec_id]
            })
        else:
            if rec_id not in existing.get("video_ids", []):
                existing.setdefault("video_ids", []).append(rec_id)

    app_store.triplets.extend(new_triplets)

    # 4. Set intelligence lenses
    default_lenses = intelligence_lenses or ["executive", "learning", "thought_leadership"]
    app_store.video_intelligences[rec_id] = default_lenses

    # 5. Persist all updated files
    with open("data/processed/videos_registry.json", "w", encoding="utf-8") as f:
        json.dump(app_store.videos_registry, f, indent=4)
    with open("data/processed/corpus.json", "w", encoding="utf-8") as f:
        json.dump(app_store.corpus, f, indent=4)
    with open("data/processed/entities.json", "w", encoding="utf-8") as f:
        json.dump(app_store.entities, f, indent=4)
    with open("data/processed/triplets.json", "w", encoding="utf-8") as f:
        json.dump(app_store.triplets, f, indent=4)
    with open("data/processed/video_intelligences.json", "w", encoding="utf-8") as f:
        json.dump(app_store.video_intelligences, f, indent=4)

    # 6. Assign to child app if specified
    if app_id:
        app = app_store.get_app(app_id)
        if app:
            vids = app.get("video_ids", [])
            if rec_id not in vids:
                vids.append(rec_id)
                app_store.assign_videos(app_id, vids)

    app_store.reload()

    return {
        "success": True,
        "video_id": rec_id,
        "title": new_media_entry["title"],
        "entity_count": len(extracted_entities),
        "triplet_count": len(new_triplets),
        "assigned_app_id": app_id
    }
