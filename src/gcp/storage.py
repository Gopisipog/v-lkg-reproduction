"""Google Cloud Storage helper for V-LKG.

Provides transparent read/write of JSON files to GCS with a
local-file fallback so the pipeline works without cloud credentials.

Environment variables:
    GCS_BUCKET                  — GCS bucket name (e.g. ``vlkg-knowledge-graph``)
    GOOGLE_APPLICATION_CREDENTIALS — path to service-account JSON key file
    GOOGLE_CLOUD_PROJECT        — GCP project ID
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


_BUCKET = os.environ.get("GCS_BUCKET", "")


def _get_gcs_client():
    """Return a google.cloud.storage.Client or None if unavailable."""
    try:
        from google.cloud import storage  # type: ignore
        return storage.Client()
    except Exception as exc:
        print(f"[GCS] Cloud Storage unavailable: {exc}")
        return None


def upload_json(data: Any, blob_name: str, local_path: str | None = None) -> bool:
    """Serialise *data* as JSON and upload to GCS (and optionally save locally).

    Args:
        data:        JSON-serialisable object.
        blob_name:   Destination path inside the GCS bucket (e.g. ``processed/entities.json``).
        local_path:  If given, also write to this local path regardless of GCS success.

    Returns:
        True if uploaded to GCS, False if only saved locally (or neither).
    """
    payload = json.dumps(data, indent=2, ensure_ascii=False)

    # Always persist locally if path given
    if local_path:
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        Path(local_path).write_text(payload, encoding="utf-8")
        print(f"[GCS] Saved locally → {local_path}")

    if not _BUCKET:
        return False

    gcs = _get_gcs_client()
    if gcs is None:
        return False

    try:
        bucket = gcs.bucket(_BUCKET)
        blob   = bucket.blob(blob_name)
        blob.upload_from_string(payload, content_type="application/json")
        print(f"[GCS] Uploaded gs://{_BUCKET}/{blob_name}")
        return True
    except Exception as exc:
        print(f"[GCS] Upload failed for {blob_name}: {exc}")
        return False


def download_json(blob_name: str, local_path: str | None = None) -> Any | None:
    """Download JSON from GCS blob (with local fallback).

    Tries GCS first; falls back to *local_path* if GCS is unavailable or the
    blob does not exist.

    Returns:
        Parsed JSON object, or None if unavailable.
    """
    if _BUCKET:
        gcs = _get_gcs_client()
        if gcs is not None:
            try:
                bucket = gcs.bucket(_BUCKET)
                blob   = bucket.blob(blob_name)
                if blob.exists():
                    raw = blob.download_as_text(encoding="utf-8")
                    print(f"[GCS] Downloaded gs://{_BUCKET}/{blob_name}")
                    return json.loads(raw)
            except Exception as exc:
                print(f"[GCS] Download failed for {blob_name}: {exc}")

    # Local fallback
    if local_path and Path(local_path).exists():
        with open(local_path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    return None
