from neo4j import GraphDatabase
import os
from src.core.entity_registry import canonical_color

class Neo4jClient:
    """Handles connections to Neo4j (Aura or local).
    Auto-falls back to LocalGraphStore if Neo4j is unreachable.
    All operations route to whichever backend is active."""

    def __init__(self):
        self._local_fallback = None
        self.driver = None

        aura_id = os.environ.get("AURA_INSTANCEID")
        if aura_id:
            uri = f"neo4j+s://{aura_id}.databases.neo4j.io:7687"
            user = os.environ.get("NEO4J_USER") or os.environ.get("NEO4J_USERNAME", "neo4j")
            password = os.environ.get("NEO4J_PASSWORD", "password")
        else:
            uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
            user = os.environ.get("NEO4J_USER") or os.environ.get("NEO4J_USERNAME", "neo4j")
            password = os.environ.get("NEO4J_PASSWORD", "password")

        print(f"Connecting to Neo4j at: {uri} (user={user})")
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            print("[INFO] Successfully connected to Neo4j.")
        except Exception as e:
            print(f"[ERROR] Failed to connect to Neo4j: {e}")
            print("[WARNING] Falling back to LocalGraphStore (JSON-based local knowledge graph).")
            self.driver = None
            from src.database.local_graph import LocalGraphStore
            self._local_fallback = LocalGraphStore()

    # ── Internal routing ───────────────────────────────────────────────────

    @property
    def _store(self):
        """Return the active store: Neo4j driver or local fallback."""
        if self.driver is not None:
            return self.driver
        return self._local_fallback

    # ── public API ─────────────────────────────────────────────────────────

    def close(self):
        if self.driver:
            self.driver.close()
        elif self._local_fallback:
            self._local_fallback.close()

    def execute_write(self, query, parameters=None):
        if self.driver:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return result.data()
        return None

    def execute_read(self, query, parameters=None):
        if self.driver:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return result.data()
        if self._local_fallback:
            return self._local_execute_read(query, parameters)
        return []

    def _local_execute_read(self, query, parameters=None):
        import re as _re

        params = parameters or {}
        q = query.strip()

        if _re.search(r"\(\s*n\s*\)\s*RETURN\s+count\s*\(\s*n\s*\)", q, _re.I):
            return [{"count": len(self._local_fallback.entities)}]
        if _re.search(r"\(\s*\)-\s*\[\s*r\s*\]->\(\s*\)\s*RETURN\s+count\s*\(\s*r\s*\)", q, _re.I):
            return [{"count": len(self._local_fallback.triplets)}]
        if "avg(" in q.lower() and "degree" in q.lower():
            return [{"avg": self._local_fallback.get_stats().get("avg_degree", 0.0)}]
        if _re.search(r"labels\s*\(\s*n\s*\)", q, _re.I) and "n.name" in q.lower():
            return [
                {"name": e["name"], "type": e.get("type", "Entity"), "color": e.get("color")}
                for e in self._local_fallback.entities.values()
            ]
        if "contains" in q.lower() and "$keyword" in q:
            keyword = (params.get("keyword") or "").lower()
            hits = []
            for e in self._local_fallback.entities.values():
                if keyword in e["name"].lower():
                    hits.append({
                        "node": e["name"],
                        "type": e.get("type", "Entity"),
                        "time": None,
                        "related": "",
                    })
            return hits[:5]
        if "r.video_id" in q or "$vid_id" in q:
            vid = params.get("vid_id") or ""
            rows = []
            for t in self._local_fallback.get_triplets(video_id=vid):
                rows.append({
                    "from_type": t.get("subject_type"),
                    "from_name": t["subject"],
                    "relation": t["relation"],
                    "to_type": t.get("object_type"),
                    "to_name": t["object"],
                    "time": t.get("source_time"),
                })
            return rows
        if "type(r)" in q.lower() or "from_node" in q.lower():
            rows = []
            for t in self._local_fallback.triplets:
                rows.append({
                    "from_node": t["subject"],
                    "relation": t["relation"],
                    "to_node": t["object"],
                    "node": t["object"],
                    "node_type": t.get("object_type"),
                })
            return rows
        rels = ("HAS_STRATEGY", "HAS_ALTERNATIVE", "IS_PREQUEL_TO", "LEADS_TO",
                "IS_PART_OF", "HAS_TACTIC")
        if any(r in q for r in rels) or "collect(" in q.lower():
            return self._local_execute_aggregate(q, params)
        return []

    def _local_execute_aggregate(self, query, parameters=None):
        import re as _re

        params = parameters or {}
        name = params.get("name") or params.get("comp") or ""
        triplets = self._local_fallback.get_triplets()
        if "IS_PREQUEL_TO" in query:
            return [{"prequels": [t["subject"] for t in triplets
                                  if t["relation"] == "IS_PREQUEL_TO" and t["object"] == name]}]
        if "LEADS_TO" in query and "outcome" in query.lower():
            return [{"outcomes": [t["object"] for t in triplets
                                  if t["relation"] == "LEADS_TO" and t["subject"] == name]}]
        if ("HAS_STRATEGY" in query or "HAS_ALTERNATIVE" in query) and "collect(" not in query.lower():
            comps = sorted({t["subject"] for t in triplets
                            if t["relation"] in ("HAS_STRATEGY", "HAS_ALTERNATIVE")})
            return [{"name": c, "label": "Competency"} for c in comps]
        if "HAS_TACTIC" in query or "tactics" in query.lower():
            comp_name = params.get("comp") or params.get("name") or ""
            strat_map: dict = {}
            for t in triplets:
                if t["relation"] in ("HAS_STRATEGY", "HAS_ALTERNATIVE") and t["subject"] == comp_name:
                    strat_map.setdefault(t["object"], {
                        "strategy": t["object"],
                        "rel_type": t["relation"], "tactics": [], "strategy_prequels": [],
                    })
            for t in triplets:
                if t["relation"] == "HAS_TACTIC" and t["subject"] in strat_map:
                    strat_map[t["subject"]]["tactics"].append(t["object"])
            return list(strat_map.values())
        if "type(r) AS relation" in query:
            rows = []
            for t in triplets:
                if t["subject"] == name or t["object"] == name:
                    other = t["object"] if t["subject"] == name else t["subject"]
                    rows.append({
                        "relation": t["relation"],
                        "node": other,
                        "node_type": t.get("object_type") if t["subject"] == name else t.get("subject_type"),
                    })
            return rows
        return []

    def insert_triplet(self, subject, subject_type, relation, obj, obj_type,
                       source_time=None, video_id=None, color=None):
        from src.core.entity_registry import canonical_color
        # Resolve canonical colors for both endpoint nodes so the shared,
        # color-coded knowledge layer is persisted uniformly across all
        # intelligence domains.
        s_color = color or canonical_color(subject_type)
        o_color = canonical_color(obj_type)

        if self.driver:
            s_label  = ''.join(e for e in subject_type if e.isalnum()) or "Entity"
            o_label  = ''.join(e for e in obj_type    if e.isalnum()) or "Entity"
            rel_type = ''.join(e for e in relation if e.isalnum() or e == '_').upper()

            query = f"""
            MERGE (s:{s_label} {{name: $subject}})
            MERGE (o:{o_label} {{name: $obj}})
            MERGE (s)-[r:{rel_type}]->(o)
            ON CREATE SET r.source_time = $source_time, r.video_id = $video_id, r.weight = 1,
                            s.color = $s_color, o.color = $o_color
            ON MATCH SET  r.weight = coalesce(r.weight, 1) + 1,
                            s.color = coalesce(s.color, $s_color), o.color = coalesce(o.color, $o_color)
            """
            try:
                self.execute_write(query, {
                    "subject":     subject,
                    "obj":         obj,
                    "source_time": source_time,
                    "video_id":    video_id,
                    "s_color":     s_color,
                    "o_color":     o_color,
                })
                print(f"Inserted into Neo4j: ({subject}) -[{rel_type}]-> ({obj})")
                return
            except Exception as e:
                print(f"Neo4j insert failed, routing to local: {e}")

        # Fallback to local store
        if self._local_fallback:
            self._local_fallback.insert_triplet(
                subject, subject_type, relation, obj, obj_type,
                source_time=source_time, video_id=video_id,
            )

    # ── Local query helpers (delegated to fallback) ────────────────────────

    def get_entities(self, type_filter=None):
        if self._local_fallback:
            return self._local_fallback.get_entities(type_filter=type_filter)
        if self.driver:
            # Try simple Neo4j read
            rows = self.execute_read(
                "MATCH (n) RETURN n.name AS name, labels(n)[0] AS type, "
                "n.color AS color"
            ) or []
            out = []
            for r in rows:
                if not r.get("name"):
                    continue
                if type_filter and r.get("type") != type_filter:
                    continue
                out.append({
                    "name": r["name"],
                    "type": r.get("type"),
                    "color": r.get("color") or canonical_color(r.get("type")),
                })
            return out
        return []

    def get_triplets(self, subject=None, relation=None, obj=None, video_id=None):
        if self._local_fallback:
            return self._local_fallback.get_triplets(
                subject=subject, relation=relation, obj=obj, video_id=video_id,
            )
        return []

    def get_stats(self):
        if self._local_fallback:
            return self._local_fallback.get_stats()
        if self.driver:
            try:
                nodes = self.execute_read("MATCH (n) RETURN count(n) as count") or [{"count": 0}]
                rels = self.execute_read("MATCH ()-[r]->() RETURN count(r) as count") or [{"count": 0}]
                degrees = self.execute_read(
                    "MATCH (n) WITH n, COUNT { (n)--() } as degree RETURN avg(degree) as avg"
                ) or [{"avg": 0.0}]
                return {
                    "node_count": nodes[0]["count"],
                    "rel_count": rels[0]["count"],
                    "avg_degree": round(degrees[0]["avg"] if degrees[0]["avg"] else 0.0, 2),
                }
            except Exception:
                pass
        return {"node_count": 0, "rel_count": 0, "avg_degree": 0.0}

    def get_type_counts(self):
        if self._local_fallback:
            return self._local_fallback.get_type_counts()
        return {}

    def get_video_ids(self):
        if self._local_fallback:
            return self._local_fallback.get_video_ids()
        return []

    def get_knowledge_entities(self, exclude_types=None):
        """Return all color-coded knowledge entities (Neo4j backend).

        Reads `color` property when present so the shared cross-domain
        entity layer is available to every intelligence tab.
        """
        from src.core.entity_registry import canonical_color
        exclude = set(exclude_types or [])
        if self._local_fallback:
            return self._local_fallback.get_knowledge_entities(exclude_types=exclude_types)
        if self.driver:
            try:
                rows = self.execute_read(
                    "MATCH (n) RETURN n.name AS name, labels(n)[0] AS type, "
                    "n.color AS color"
                ) or []
                out = []
                for r in rows:
                    name = r.get("name")
                    if not name:
                        continue
                    if r.get("type") in exclude:
                        continue
                    out.append({
                        "name": name,
                        "type": r.get("type"),
                        "color": r.get("color") or canonical_color(r.get("type")),
                    })
                return out
            except Exception:
                pass
        return []

    def get_entities_by_domain(self, domain_name):
        """Return intelligence entities extracted by a specific domain, with video provenance.

        Returns list of dicts: {name, type, color, video_ids: [...], source_domain}
        """
        from src.core.entity_registry import canonical_color
        if self._local_fallback:
            triplets = self._local_fallback.get_triplets()
            out = []
            for t in triplets:
                if t.get("obj") == domain_name and t.get("relation") == "EXTRACTED_BY":
                    out.append({
                        "name": t["subject"],
                        "type": t.get("subject_type", "Entity"),
                        "color": canonical_color(t.get("subject_type", "Entity")),
                        "video_ids": [t.get("video_id", "all")] if t.get("video_id") else ["all"],
                        "source_domain": domain_name,
                    })
            return out
        if self.driver:
            try:
                rows = self.execute_read(
                    "MATCH (n)-[r:EXTRACTED_BY]->(d:IntelligenceDomain {name: $domain}) "
                    "RETURN n.name AS name, labels(n)[0] AS type, n.color AS color, "
                    "collect(DISTINCT r.video_id) AS video_ids",
                    {"domain": domain_name}
                ) or []
                out = []
                for r in rows:
                    name = r.get("name")
                    if not name:
                        continue
                    vid_ids = r.get("video_ids", [])
                    if not vid_ids:
                        vid_ids = ["all"]
                    out.append({
                        "name": name,
                        "type": r.get("type"),
                        "color": r.get("color") or canonical_color(r.get("type")),
                        "video_ids": vid_ids,
                        "source_domain": domain_name,
                    })
                return out
            except Exception as e:
                print(f"Error fetching entities for domain {domain_name}: {e}")
        return []
