"""Local JSON-based knowledge graph store.
Falls back gracefully when Neo4j AuraDB is unreachable.
Mirrors the Neo4j data model for drop-in compatibility."""

import json
import os
from datetime import datetime

from src.core.entity_registry import canonical_color


class LocalGraphStore:
    """Persists knowledge graph data to local JSON files.
    
    Supports the same operations as Neo4jClient (insert_triplet,
    execute_read, execute_write) but stores to disk instead.
    """

    TRIPLETS_PATH = "data/processed/triplets.json"
    ENTITIES_PATH = "data/processed/entities.json"

    def __init__(self):
        self.driver = self  # self-reference for duck-typing compatibility
        self.triplets = []
        self.entities = {}
        self._load()

    # ── persistence ────────────────────────────────────────────────────────

    def _load(self):
        os.makedirs(os.path.dirname(self.TRIPLETS_PATH), exist_ok=True)
        try:
            with open(self.TRIPLETS_PATH, "r", encoding="utf-8") as f:
                self.triplets = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.triplets = []
        try:
            with open(self.ENTITIES_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # rebuild dict from list for fast lookup
            for i, e in enumerate(raw):
                self.entities[e.get("name", f"entity_{i}")] = e
        except (FileNotFoundError, json.JSONDecodeError):
            self.entities = {}

    def _save(self):
        with open(self.TRIPLETS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.triplets, f, indent=4, ensure_ascii=False)
        with open(self.ENTITIES_PATH, "w", encoding="utf-8") as f:
            json.dump(list(self.entities.values()), f, indent=4, ensure_ascii=False)

    def _sanitize_label(self, label: str) -> str:
        return "".join(e for e in label if e.isalnum()) or "Entity"

    # ── public API (mirrors Neo4jClient) ──────────────────────────────────

    def execute_write(self, query, parameters=None):
        """Stub for compatibility — local graph uses insert_triplet."""
        pass

    def execute_read(self, query, parameters=None):
        """Stub for compatibility — returns empty list."""
        return []

    def close(self):
        pass

    def insert_triplet(self, subject, subject_type, relation, obj, obj_type,
                       source_time=None, video_id=None):
        """Inserts a Subject-[Relation]->Object triplet into the local store."""
        s_type = self._sanitize_label(subject_type)
        o_type = self._sanitize_label(obj_type)
        rel = "".join(e for e in relation if e.isalnum() or e == "_").upper()

        # upsert entities (persist canonical color for shared cross-domain layer)
        for name, label in [(subject, s_type), (obj, o_type)]:
            if name not in self.entities:
                self.entities[name] = {
                    "name": name,
                    "type": label,
                    "color": canonical_color(label),
                    "first_seen": source_time or datetime.utcnow().isoformat(),
                    "video_ids": [],
                }
            else:
                # ensure an existing entity always carries a color
                self.entities[name].setdefault("color", canonical_color(label))
            if video_id and video_id not in self.entities[name].get("video_ids", []):
                self.entities[name].setdefault("video_ids", []).append(video_id)

        # upsert triplet
        found = None
        for i, t in enumerate(self.triplets):
            if (t["subject"] == subject and t["relation"] == rel
                    and t["object"] == obj):
                found = i
                break

        if found is not None:
            self.triplets[found]["weight"] = self.triplets[found].get("weight", 1) + 1
            if video_id and video_id not in self.triplets[found].get("video_ids", []):
                self.triplets[found].setdefault("video_ids", []).append(video_id)
        else:
            self.triplets.append({
                "subject":      subject,
                "subject_type": s_type,
                "relation":     rel,
                "object":       obj,
                "object_type":  o_type,
                "source_time":  source_time or datetime.utcnow().isoformat(),
                "video_ids":    [video_id] if video_id else [],
                "weight":       1,
            })

        self._save()
        print(f"LocalStore: ({subject}) -[{rel}]-> ({obj})  [video={video_id}]")

    # ── query helpers ─────────────────────────────────────────────────────

    def get_entities(self, type_filter=None):
        """Return all entities, optionally filtered by type.

        Every returned entity carries a `color` (canonical hex) so the
        shared, color-coded knowledge layer is available to all
        intelligence tabs uniformly.
        """
        items = []
        for e in self.entities.values():
            ent = dict(e)
            ent["color"] = ent.get("color") or canonical_color(ent.get("type"))
            items.append(ent)
        if type_filter:
            items = [e for e in items if e.get("type") == type_filter]
        return items

    def get_knowledge_entities(self, exclude_types=None):
        """Return all color-coded knowledge entities for cross-domain surfacing.

        `exclude_types` lets a tab hide its own domain nodes if desired
        (e.g. hide IntelligenceDomain markers). Always returns a `color`.
        """
        exclude = set(exclude_types or [])
        out = []
        for e in self.get_entities():
            if e.get("type") in exclude:
                continue
            out.append(e)
        return out

    def get_triplets(self, subject=None, relation=None, obj=None, video_id=None):
        """Filter triplets by any combination of fields."""
        results = self.triplets
        if subject:
            results = [t for t in results if subject.lower() in t["subject"].lower()]
        if relation:
            results = [t for t in results if t["relation"] == relation]
        if obj:
            results = [t for t in results if obj.lower() in t["object"].lower()]
        if video_id:
            results = [t for t in results if video_id in t.get("video_ids", [])]
        return results

    def get_stats(self):
        """Return graph statistics similar to Neo4j."""
        return {
            "node_count":   len(self.entities),
            "rel_count":    len(self.triplets),
            "avg_degree":   round(sum(
                self._count_entity_edges(name)
                for name in self.entities
            ) / max(len(self.entities), 1), 2),
        }

    def _count_entity_edges(self, name):
        count = 0
        for t in self.triplets:
            if t["subject"] == name:
                count += 1
            if t["object"] == name:
                count += 1
        return count

    def get_type_counts(self):
        """Return count of entities by type."""
        counts = {}
        for e in self.entities.values():
            t = e.get("type", "Unknown")
            counts[t] = counts.get(t, 0) + 1
        return counts

    def get_video_ids(self):
        """Return unique video IDs referenced in triplets."""
        vids = set()
        for t in self.triplets:
            for vid in t.get("video_ids", []):
                vids.add(vid)
        for e in self.entities.values():
            for vid in e.get("video_ids", []):
                vids.add(vid)
        return sorted(vids)