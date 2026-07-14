import os
import sys
import json
import argparse
import datetime
import shutil

# Ensure stdout/stderr use UTF-8 on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from dotenv import load_dotenv

# Ensure ffmpeg is available for yt-dlp and Whisper
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    pass

# Check if running in cloud (Streamlit Cloud) or locally
_IS_CLOUD = os.environ.get("STREAMLIT_CLOUD", False) or os.path.exists("/mount/src")

from src.ingestion.downloader import YouTubeDownloader
from src.ingestion.processor import MultimodalProcessor
from src.core.extractor import SemanticEntityRecognizer
from src.core.clustering import DependencyMiner
from src.core.enrichment import GraphEnrichmentEngine
from src.database.neo4j_client import Neo4jClient
from src.database.schema import Neo4jSchemaManager

# Load environment variables (API keys, DB credentials)
load_dotenv()

REGISTRY_PATH = "data/processed/videos_registry.json"
CORPUS_PATH   = "data/processed/corpus.json"


def _load_registry():
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def _save_registry(registry):
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=4)


def _generate_summary(segments, meta):
    """Generates a concise summary of the video using DeepSeek."""
    from openai import OpenAI
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return "Summary unavailable (no DeepSeek key)."
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    # Use up to ~3 000 chars of transcript
    full_text = " ".join(s["transcript"] for s in segments)[:3000]
    prompt = (
        f"Video title: {meta['title']}\nChannel: {meta['channel']}\n\n"
        f"Transcript excerpt:\n{full_text}\n\n"
        "Write a 3-sentence summary of what this video teaches about leadership or communication."
    )
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"Summary generation error: {e}")
        return "Summary unavailable."


def run_pipeline(url, progress_cb=None):
    """Executes the full Multimodal Knowledge Graph Pipeline.

    Args:
        url: YouTube video URL.
        progress_cb: optional callable(fraction: float, label: str) for UI updates.
    """
    def _progress(frac, label):
        print(f"[{int(frac*100):3d}%] {label}")
        if progress_cb:
            progress_cb(frac, label)

    _progress(0.0, "Starting pipeline...")

    # ── Init DB ──────────────────────────────────────────────────────────────
    db = Neo4jClient()
    schema = Neo4jSchemaManager(db)
    schema.setup_constraints()

    # ── Phase 0: Fetch video metadata ────────────────────────────────────────
    _progress(0.05, "Fetching video metadata...")
    downloader = YouTubeDownloader()
    meta = downloader.fetch_metadata(url)
    video_id = meta["video_id"]
    print(f"  -> {meta['title']}  [{video_id}]")

    # ── Phase 1a: Download video & audio (with fallback) ──────────────────
    video_path = None
    audio_path = None
    text_segments = None

    try:
        _progress(0.10, f"Downloading video: {meta['title'][:50]}...")
        video_path = downloader.download_video(url, video_id=video_id)
        _progress(0.20, "Downloading audio...")
        audio_path = downloader.download_audio(url, video_id=video_id)
    except Exception as e:
        print(f"Download failed (common on cloud servers): {e}")
        print("Falling back to transcript-only mode (youtube-transcript-api)...")
        video_path = None
        audio_path = None

    # ── Phase 1b: Transcribe ───────────────────────────────────────────────
    if audio_path and video_path:
        _progress(0.30, "Transcribing audio (Whisper)...")
        processor = MultimodalProcessor()
        text_segments = processor.process(
            video_path, audio_path, CORPUS_PATH, video_id=video_id
        )
    else:
        _progress(0.30, "Fetching YouTube captions...")
        text_segments = None

        # Try youtube-transcript-api first (works great when captions exist)
        _progress(0.30, "  Trying youtube-transcript-api...")
        text_segments = downloader.fetch_transcript_only(video_id)

        # Try yt-dlp subtitles extraction as second fallback
        if not text_segments:
            _progress(0.35, "  Trying yt-dlp auto-subtitles...")
            text_segments = downloader.fetch_subtitles_via_ytdlp(video_id)

        # Try yt-dlp info extractor for captions as third fallback
        if not text_segments:
            _progress(0.40, "  Trying yt-dlp info extract captions...")
            text_segments = downloader.fetch_captions_from_info(video_id)

        if text_segments:
            import json
            os.makedirs(os.path.dirname(CORPUS_PATH), exist_ok=True)
            existing = []
            if os.path.exists(CORPUS_PATH):
                try:
                    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                    existing = [s for s in existing if s.get("video_id") != video_id]
                except (json.JSONDecodeError, IOError):
                    existing = []
            new_segments = [
                {
                    "video_id":    video_id,
                    "start_time":  seg["start"],
                    "end_time":    seg["end"],
                    "transcript":  seg["text"],
                    "visual_text": "",
                }
                for seg in text_segments
            ]
            output_corpus = existing + new_segments
            with open(CORPUS_PATH, "w", encoding="utf-8") as f:
                json.dump(output_corpus, f, indent=4)
            text_segments = new_segments
            print(f"Corpus saved to {CORPUS_PATH} ({len(new_segments)} transcript segments)")

    if not text_segments:
        raise RuntimeError(
            "Transcription produced 0 segments — video not ingested. "
            "The video may not have captions available."
        )

    # ── Generate & store summary ─────────────────────────────────────────────
    _progress(0.40, f"Summarising video ({len(text_segments)} segments)...")
    summary = _generate_summary(text_segments, meta)

    registry = _load_registry()
    registry = [v for v in registry if v["video_id"] != video_id]
    registry.append({
        **meta,
        "summary":       summary,
        "segment_count": len(text_segments),
        "ingested_at":   datetime.datetime.utcnow().isoformat() + "Z",
    })
    _save_registry(registry)
    print(f"Registry updated ({len(registry)} video(s) total).")

    # ── Phase 2 & 3: Triplet Extraction & Graph Insertion ───────────────────
    # Try LLM-based extraction first; fall back to rule-based if API unavailable
    extractor = SemanticEntityRecognizer()
    use_fallback = not extractor.client
    if not use_fallback:
        # Quick probe: if LLM key is invalid / out of balance, detect early
        try:
            _probe = extractor.extract_triplets("test leadership communication")
            if not _probe:
                use_fallback = True
                print("LLM extractor returned empty — falling back to rule-based extraction")
        except Exception:
            use_fallback = True
            print("LLM extractor failed — falling back to rule-based extraction")

    if use_fallback:
        from src.core.fallback_extractor import FallbackExtractor
        fallback = FallbackExtractor()
        # Concatenate full transcript for better keyword co-occurrence
        full_text = " ".join(seg.get("transcript", "") for seg in text_segments)
        _progress(0.45, "Extracting triplets (rule-based fallback)...")
        triplets = fallback.extract_triplets(full_text)
        for t in triplets:
            db.insert_triplet(
                subject=t["subject"],
                subject_type=t["subject_type"],
                relation=t["relation"],
                obj=t["object"],
                obj_type=t["object_type"],
                source_time=datetime.datetime.utcnow().isoformat(),
                video_id=video_id,
            )
        _progress(0.65, f"Extracted {len(triplets)} triplets via rule-based fallback")
    else:
        total_segs = len(text_segments)
        for idx, segment in enumerate(text_segments):
            frac = 0.40 + 0.25 * ((idx + 1) / max(total_segs, 1))
            _progress(frac, f"Extracting triplets — segment {idx+1}/{total_segs}...")
            combined_text = (
                f"{segment['transcript']} [Visual Context: {segment['visual_text']}]"
            )
            triplets = extractor.extract_triplets(combined_text)

            for t in triplets:
                subject_name = extractor.map_to_dbpedia(t["subject"])
                object_name  = extractor.map_to_dbpedia(t["object"])
                db.insert_triplet(
                    subject=subject_name,
                    subject_type=t["subject_type"],
                    relation=t["relation"],
                    obj=object_name,
                    obj_type=t["object_type"],
                    source_time=segment["start_time"],
                    video_id=video_id,
                )

    # ── Phase 4: Dependency mining & path detection ──────────────────────────
    _progress(0.65, "Mining prerequisites and learning paths...")
    miner = DependencyMiner(db_client=db)
    miner.determine_prerequisites(text_segments)
    miner.detect_learning_paths(text_segments)

    # ── Phase 5: Graph enrichment (A-F) ─────────────────────────────────────
    _progress(0.75, "Running graph enrichment (strategies, tactics, paths)...")
    enrichment = GraphEnrichmentEngine(db)
    enrichment.run_enrichment()

    db.close()
    _progress(1.0, "Pipeline complete!")
    print("\nPipeline Complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="V-LKG Construction Pipeline")
    parser.add_argument("--url", type=str, help="YouTube Video URL", required=True)
    args = parser.parse_args()

    run_pipeline(args.url)
