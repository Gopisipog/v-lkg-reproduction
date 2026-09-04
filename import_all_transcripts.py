#!/usr/bin/env python3
"""
Import all transcripts for every video analysed in V-LKG.
Fetches transcripts for NeqEKCrTbL4, jl3OLK9vP1o, iCvmsMzlF7o, VozV9KmhPTU,
indexes live recordings, adds them to corpus.json and videos_registry.json,
and assigns them to appropriate child apps.
"""

import os
import sys
import json
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi

CORPUS_PATH = "data/processed/corpus.json"
REGISTRY_PATH = "data/processed/videos_registry.json"
CHILD_APPS_PATH = "data/processed/child_apps.json"

VIDEOS_TO_IMPORT = [
    {
        "video_id": "NeqEKCrTbL4",
        "title": "This Is How Smart People Handle Toxic People | Brené Brown’s Most Transformative Lesson",
        "channel": "Unapologetically Human",
        "duration_sec": 1023,
        "summary": "Brené Brown explores emotional boundaries, empathy, navigating toxic workplace dynamics, and organizational trust.",
        "url": "https://www.youtube.com/watch?v=NeqEKCrTbL4",
        "thumbnail_url": "https://i.ytimg.com/vi/NeqEKCrTbL4/hqdefault.jpg",
        "app_assignments": ["app_executive"]
    },
    {
        "video_id": "jl3OLK9vP1o",
        "title": "The Problem-Solving Method They Removed From Every Textbook | Feynman Archives",
        "channel": "Feynman Archives",
        "duration_sec": 1092,
        "summary": "Richard Feynman's principles of first-principles thinking, rigorous problem decomposition, and hypothesis testing.",
        "url": "https://www.youtube.com/watch?v=jl3OLK9vP1o",
        "thumbnail_url": "https://i.ytimg.com/vi/jl3OLK9vP1o/hqdefault.jpg",
        "app_assignments": ["app_executive", "app_gtm_ai"]
    },
    {
        "video_id": "iCvmsMzlF7o",
        "title": "The Power of Vulnerability | Brené Brown | TED",
        "channel": "TED",
        "duration_sec": 1250,
        "summary": "Brené Brown's world-famous study on human connection, courage, authentic leadership, and communicative presence.",
        "url": "https://www.youtube.com/watch?v=iCvmsMzlF7o",
        "thumbnail_url": "https://i.ytimg.com/vi/iCvmsMzlF7o/hqdefault.jpg",
        "app_assignments": ["app_comm_mastery", "app_executive"]
    },
    {
        "video_id": "VozV9KmhPTU",
        "title": "STOP WORKING SO HARD ON YOUR JOB | Jim Rohn Seminar",
        "channel": "Victorix",
        "duration_sec": 929,
        "summary": "Jim Rohn's legendary masterclass on compounding personal value, market attractiveness, and strategic career growth.",
        "url": "https://www.youtube.com/watch?v=VozV9KmhPTU",
        "thumbnail_url": "https://i.ytimg.com/vi/VozV9KmhPTU/hqdefault.jpg",
        "app_assignments": ["app_sales_growth", "app_executive"]
    }
]

def format_time(val) -> str:
    if val is None or val == "":
        return "00:00"
    try:
        f = float(val)
        m = int(f // 60)
        s = int(f % 60)
        return f"{m:02d}:{s:02d}"
    except Exception:
        return "00:00"

def main():
    print("=" * 60)
    print("  Importing All Transcripts for Every Analysed Video")
    print("=" * 60)

    # 1. Load data
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        corpus = json.load(f)
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)
    with open(CHILD_APPS_PATH, "r", encoding="utf-8") as f:
        child_apps = json.load(f)

    existing_corpus_vids = set(s.get("video_id") for s in corpus if s.get("video_id"))
    existing_reg_vids = set(v.get("video_id") for v in registry if v.get("video_id"))

    api = YouTubeTranscriptApi()

    new_segments_total = 0

    # 2. Fetch and append transcripts for each video
    for item in VIDEOS_TO_IMPORT:
        vid = item["video_id"]
        print(f"\nProcessing {vid} ({item['title'][:40]}...)...")

        # Fetch transcript if not already in corpus
        if vid not in existing_corpus_vids:
            try:
                trans = api.fetch(vid)
                raw = trans.to_raw_data()
                print(f"  -> Fetched {len(raw)} segments from YouTube API")
                
                for r in raw:
                    sec = r.get("start", 0)
                    ts_str = format_time(sec)
                    text = r.get("text", "").replace("\n", " ").strip()
                    if not text:
                        continue
                    corpus.append({
                        "video_id": vid,
                        "start_sec": sec,
                        "timestamp": ts_str,
                        "text": text,
                        "visual_text": ""
                    })
                    new_segments_total += 1
            except Exception as e:
                print(f"  -> Error fetching transcript: {e}")
        else:
            print("  -> Transcripts already present in corpus")

        # Update or add in registry
        if vid not in existing_reg_vids:
            registry.append({
                "video_id": vid,
                "title": item["title"],
                "channel": item["channel"],
                "duration_sec": item["duration_sec"],
                "summary": item["summary"],
                "url": item["url"],
                "thumbnail_url": item["thumbnail_url"],
                "ingested_at": datetime.utcnow().isoformat() + "Z",
                "segment_count": len([s for s in corpus if s.get("video_id") == vid])
            })
            existing_reg_vids.add(vid)
            print("  -> Added to videos registry")

        # Assign to child apps
        for app_id in item.get("app_assignments", []):
            for a in child_apps:
                if a["id"] == app_id:
                    v_list = a.setdefault("video_ids", [])
                    if vid not in v_list:
                        v_list.append(vid)
                        print(f"  -> Assigned to child app '{a['name']}'")

    # 3. Also index live recordings in registry
    live_vids = set(s.get("video_id") for s in corpus if s.get("video_id", "").startswith("live_"))
    for lvid in live_vids:
        if lvid not in existing_reg_vids:
            segs = [s for s in corpus if s.get("video_id") == lvid]
            registry.append({
                "video_id": lvid,
                "title": f"Live Voice Session [{lvid[-6:]}]",
                "channel": "Live Voice Capture",
                "duration_sec": len(segs) * 8,
                "summary": f"Captured voice transcript containing {len(segs)} spoken segments and real-time concepts.",
                "url": "",
                "is_voice_recording": True,
                "ingested_at": datetime.utcnow().isoformat() + "Z",
                "segment_count": len(segs)
            })
            existing_reg_vids.add(lvid)
            # Assign to executive app
            for a in child_apps:
                if a["id"] == "app_executive" and lvid not in a.get("video_ids", []):
                    a.setdefault("video_ids", []).append(lvid)
            print(f"  -> Indexed live recording {lvid} in registry")

    # 4. Save updated corpus, registry, and child apps
    with open(CORPUS_PATH, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2)
    print(f"\nSaved updated {CORPUS_PATH} (total segments: {len(corpus)})")

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
    print(f"Saved updated {REGISTRY_PATH} (total videos: {len(registry)})")

    with open(CHILD_APPS_PATH, "w", encoding="utf-8") as f:
        json.dump(child_apps, f, indent=2)
    print(f"Saved updated {CHILD_APPS_PATH}")

    print("\nRe-correlating entities and relationships for all videos...")
    from import_vlkg_entities_and_enrichments import run_import
    run_import()

    print("\nAll transcripts and semantics imported successfully!")

if __name__ == "__main__":
    main()
