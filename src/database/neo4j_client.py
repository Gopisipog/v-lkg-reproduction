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
            print("✅ Successfully connected to Neo4j.")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            print("⚠️  Falling back to LocalGraphStore (JSON-based local knowledge graph).")
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
        # Fallback: return empty list for Cypher queries
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
            MEREE (o:{o_label} {{name: $obj}})
            MEREE (s)-[r:{rel_type}]->(o)
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
