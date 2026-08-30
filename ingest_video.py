"""Ingest a single YouTube video: fetch transcript, extract entities via LLM (batched), store in graph."""
import os, sys, json, datetime
os.chdir(r"D:\v_lkg_reproduction")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

# ── 1. Fetch video metadata + transcript ───────────────────────────────────
from src.ingestion.downloader import YouTubeDownloader

url = "https://www.youtube.com/watch?v=DQO8HsCw_eU"
downloader = YouTubeDownloader()
print(f"Fetching metadata for {url}...")
meta = downloader.fetch_metadata(url)
video_id = meta["video_id"]
print(f"  Title: {meta.get('title', '?')}")
print(f"  Channel: {meta.get('channel', '?')}")

print("Fetching transcript...")
text_segments = downloader.fetch_transcript_only(video_id)
if not text_segments:
    print("  Trying yt-dlp subtitles...")
    text_segments = downloader.fetch_subtitles_via_ytdlp(video_id)
if not text_segments:
    print("  Trying yt-dlp info extract...")
    text_segments = downloader.fetch_captions_from_info(video_id)

if not text_segments:
    print("ERROR: No transcript available for this video.")
    sys.exit(1)

print(f"  Got {len(text_segments)} transcript segments")

# Build corpus segments
corpus_segments = [
    {
        "video_id": video_id,
        "start_time": seg["start"],
        "end_time": seg["end"],
        "transcript": seg["text"],
        "visual_text": "",
    }
    for seg in text_segments
]

# ── 2. Extract triplets with LLM (batched) ──────────────────────────────────
print("\nExtracting entities via LLM (batched)...")
from src.core.extractor import SemanticEntityRecognizer

ext = SemanticEntityRecognizer()
if not ext.client:
    print("  LLM client not available, falling back to rule-based...")
    from src.core.fallback_extractor import FallbackExtractor
    ext = FallbackExtractor()

full_text = " ".join(seg.get("transcript", "") for seg in corpus_segments)
print(f"  Full transcript: {len(full_text)} chars")

# Process in 3 chunks to avoid token limits
chunk_size = len(full_text) // 3 + 1
all_triplets = []

for i in range(3):
    chunk = full_text[i*chunk_size:(i+1)*chunk_size]
    print(f"  Processing chunk {i+1}/3 ({len(chunk)} chars)...")
    trips = ext.extract_triplets(chunk)
    print(f"    -> {len(trips)} triplets")
    all_triplets.extend(trips)

# Deduplicate triplets (by subject+relation+object)
seen = set()
dedup_triplets = []
for t in all_triplets:
    key = (t["subject"], t["relation"], t["object"])
    if key not in seen:
        seen.add(key)
        dedup_triplets.append(t)

all_triplets = dedup_triplets

# Derive entities from triplet subjects/objects
all_entities = []
seen_ents = set()
for t in all_triplets:
    for name, typ in [(t["subject"], t["subject_type"]), (t["object"], t["object_type"])]:
        key = (name, typ)
        if key not in seen_ents:
            seen_ents.add(key)
            all_entities.append({"name": name, "type": typ})

print(f"  Total after dedup: {len(all_triplets)} triplets, {len(all_entities)} entities")

# Show entities by type
by_type = {}
for e in all_entities:
    by_type[e["type"]] = by_type.get(e["type"], 0) + 1
print("  Entities by type:")
for k, v in sorted(by_type.items(), key=lambda x: -x[1]):
    print(f"    {k}: {v}")

# ── 3. Store in graph ──────────────────────────────────────────────────────
print("\nStoring in knowledge graph...")
from src.database.local_graph import LocalGraphStore

store = LocalGraphStore()
timestamp = datetime.datetime.utcnow().isoformat() + "Z"

for t in all_triplets:
    store.insert_triplet(
        subject=t["subject"],
        subject_type=t["subject_type"],
        relation=t["relation"],
        obj=t["object"],
        obj_type=t["object_type"],
        source_time=timestamp,
        video_id=video_id,
    )

print(f"  Graph store: {len(store.entities)} entities, {len(store.triplets)} triplets")

# ── 4. Update videos registry ──────────────────────────────────────────────
registry_path = "data/processed/videos_registry.json"
try:
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    registry = []

registry = [v for v in registry if v.get("video_id") != video_id]
registry.append({
    "video_id": video_id,
    "title": meta.get("title", "Untitled"),
    "channel": meta.get("channel", "Unknown"),
    "url": url,
    "summary": f"Ingested via LLM extractor. {len(all_entities)} entities, {len(all_triplets)} triplets extracted.",
    "segment_count": len(corpus_segments),
    "ingested_at": timestamp,
})

with open(registry_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)
print(f"  Registry updated ({len(registry)} videos)")

# ── 5. Show sample triplets ────────────────────────────────────────────────
print("\nSample triplets:")
for t in all_triplets[:20]:
    print(f"  ({t['subject']}) -[{t['relation']}]-> ({t['object']})  [{t['subject_type']}->{t['object_type']}]")

print("\nDone! Entities stored in data/processed/entities.json")