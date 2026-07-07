"""
Recording processor — handles transcription of recorded audio/video files
and integration with the V-LKG corpus.
"""

import os
import json
import datetime
import hashlib
import tempfile


REGISTRY_PATH = "data/processed/videos_registry.json"
CORPUS_PATH = "data/processed/corpus.json"


def generate_recording_id(file_bytes: bytes) -> str:
    """Generate a unique ID for a recording based on its content hash."""
    h = hashlib.sha256(file_bytes).hexdigest()[:11]
    return f"rec_{h}"


def transcribe_recording(file_path: str, model_size: str = "base") -> list[dict]:
    """
    Transcribe an audio/video file using OpenAI Whisper.

    Args:
        file_path: Path to the audio/video file.
        model_size: Whisper model size (tiny, base, small, medium, large).

    Returns:
        List of segment dicts with keys: start, end, text
    """
    try:
        import whisper
    except ImportError:
        raise ImportError(
            "openai-whisper is required for transcription. "
            "Install it with: pip install openai-whisper"
        )

    model = whisper.load_model(model_size)
    result = model.transcribe(file_path, verbose=False)

    segments = []
    for seg in result.get("segments", []):
        segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip(),
        })

    return segments


def transcribe_recording_openai(file_path: str) -> list[dict]:
    """
    Transcribe using OpenAI's Whisper API (cloud-based, no local model needed).

    Args:
        file_path: Path to the audio/video file.

    Returns:
        List of segment dicts with keys: start, end, text
    """
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment")

    client = OpenAI(api_key=api_key)

    with open(file_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )

    segments = []
    for seg in getattr(response, "segments", []):
        segments.append({
            "start": seg.get("start", 0),
            "end": seg.get("end", 0),
            "text": seg.get("text", "").strip(),
        })

    # Fallback if no segments returned
    if not segments and hasattr(response, "text") and response.text:
        segments.append({
            "start": 0.0,
            "end": 60.0,
            "text": response.text.strip(),
        })

    return segments


def save_to_corpus(
    recording_id: str,
    segments: list[dict],
    title: str = "",
    duration_sec: float = 0,
    source: str = "Recording",
) -> int:
    """
    Save transcribed segments to the V-LKG corpus and registry.

    Args:
        recording_id: Unique ID for this recording.
        segments: List of transcribed segment dicts.
        title: Title/label for the recording.
        duration_sec: Total duration in seconds.
        source: Source label (e.g., 'Recording', 'Meeting', 'Lecture').

    Returns:
        Number of segments saved.
    """
    os.makedirs(os.path.dirname(CORPUS_PATH), exist_ok=True)

    # Load existing corpus
    corpus = []
    if os.path.exists(CORPUS_PATH):
        with open(CORPUS_PATH, "r", encoding="utf-8") as f:
            try:
                corpus = json.load(f)
            except json.JSONDecodeError:
                corpus = []

    # Remove existing segments for this recording
    corpus = [s for s in corpus if s.get("video_id") != recording_id]

    # Add new segments
    new_segments = []
    for seg in segments:
        new_segments.append({
            "video_id": recording_id,
            "start_time": seg["start"],
            "end_time": seg["end"],
            "transcript": seg["text"],
            "visual_text": "",
        })

    corpus.extend(new_segments)

    with open(CORPUS_PATH, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=4, ensure_ascii=False)

    # Update registry
    registry = []
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            try:
                registry = json.load(f)
            except json.JSONDecodeError:
                registry = []

    registry = [v for v in registry if v.get("video_id") != recording_id]
    registry.append({
        "video_id": recording_id,
        "title": title or f"Recording {recording_id}",
        "url": "",
        "channel": source,
        "duration_sec": duration_sec,
        "thumbnail_url": "",
        "summary": f"Recorded {source.lower()} with {len(new_segments)} segments",
        "ingested_at": str(datetime.datetime.now()),
    })

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=4, ensure_ascii=False)

    return len(new_segments)
