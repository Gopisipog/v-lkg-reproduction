import json
import os
import re
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from mobile_api.intelligence_manager import INTELLIGENCE_DOMAINS, classify_entity_intelligences, classify_triplet_intelligences

CHILD_APPS_FILE = "data/processed/child_apps.json"
VIDEO_INTELLIGENCE_FILE = "data/processed/video_intelligences.json"
VIDEOS_REGISTRY_FILE = "data/processed/videos_registry.json"
CORPUS_FILE = "data/processed/corpus.json"
ENTITIES_FILE = "data/processed/entities.json"
TRIPLETS_FILE = "data/processed/triplets.json"
INSIGHTS_FILE = "data/processed/video_insights.json"


DEFAULT_CHILD_APPS = [
    {
        "id": "app_executive",
        "name": "Executive Leadership & Strategy",
        "slug": "executive-leadership",
        "description": "C-suite strategic frameworks, time management, personal discipline, and leadership alignment.",
        "icon": "Briefcase",
        "theme_color": "#6366f1",
        "focus_domains": ["executive", "learning", "thought_leadership"],
        "video_ids": ["jzzTomTwltQ", "jfW6gL6hKhk"],
        "created_at": "2026-03-01T10:00:00Z"
    },
    {
        "id": "app_gtm_ai",
        "name": "GTM & AI Engineering Lab",
        "slug": "gtm-ai-engineering",
        "description": "Go-to-market workflows, Claude Code automation, developer marketing, and scalable system design.",
        "icon": "Cpu",
        "theme_color": "#3b82f6",
        "focus_domains": ["engineering", "sales", "executive"],
        "video_ids": ["paF4J941uqg"],
        "created_at": "2026-03-05T12:00:00Z"
    },
    {
        "id": "app_comm_mastery",
        "name": "Communication & Public Speaking",
        "slug": "communication-mastery",
        "description": "Mastery of rhetorical devices, vocal delivery, self-reflection drills, and audience captivation.",
        "icon": "Sparkles",
        "theme_color": "#14b8a6",
        "focus_domains": ["thought_leadership", "learning", "customer"],
        "video_ids": ["dF3GFpIKPlE", "U40qvUiefQo"],
        "created_at": "2026-03-10T14:00:00Z"
    },
    {
        "id": "app_sales_growth",
        "name": "Sales & Revenue Accelerator",
        "slug": "sales-revenue",
        "description": "Direct response, value messaging, personal financial runway, and closing high-stakes deals.",
        "icon": "TrendingUp",
        "theme_color": "#10b981",
        "focus_domains": ["sales", "competitive", "executive"],
        "video_ids": ["jfW6gL6hKhk", "dF3GFpIKPlE"],
        "created_at": "2026-03-15T16:00:00Z"
    }
]


class MobileAppStore:
    def __init__(self):
        self._ensure_files()
        self._load_data()

    def _ensure_files(self):
        os.makedirs("data/processed", exist_ok=True)
        if not os.path.exists(CHILD_APPS_FILE):
            with open(CHILD_APPS_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CHILD_APPS, f, indent=4)
        if not os.path.exists(VIDEO_INTELLIGENCE_FILE):
            with open(VIDEO_INTELLIGENCE_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)

    def _load_data(self):
        try:
            with open(CHILD_APPS_FILE, "r", encoding="utf-8") as f:
                self.child_apps = json.load(f)
        except Exception:
            self.child_apps = DEFAULT_CHILD_APPS

        try:
            with open(VIDEO_INTELLIGENCE_FILE, "r", encoding="utf-8") as f:
                self.video_intelligences = json.load(f)
        except Exception:
            self.video_intelligences = {}

        try:
            with open(VIDEOS_REGISTRY_FILE, "r", encoding="utf-8") as f:
                self.videos_registry = json.load(f)
        except Exception:
            self.videos_registry = []

        try:
            with open(CORPUS_FILE, "r", encoding="utf-8") as f:
                self.corpus = json.load(f)
        except Exception:
            self.corpus = []

        try:
            with open(ENTITIES_FILE, "r", encoding="utf-8") as f:
                self.entities = json.load(f)
        except Exception:
            self.entities = []

        try:
            with open(TRIPLETS_FILE, "r", encoding="utf-8") as f:
                self.triplets = json.load(f)
        except Exception:
            self.triplets = []

        try:
            with open(INSIGHTS_FILE, "r", encoding="utf-8") as f:
                self.insights = json.load(f)
        except Exception:
            self.insights = {}

        self._init_video_intelligences()
        self._build_video_entity_index()

    def _init_video_intelligences(self):
        updated = False
        default_lens_map = {
            "dF3GFpIKPlE": ["thought_leadership", "learning", "executive", "customer"],
            "paF4J941uqg": ["engineering", "sales", "executive", "competitive"],
            "jfW6gL6hKhk": ["sales", "executive", "learning", "competitive"],
            "jzzTomTwltQ": ["executive", "learning", "compliance", "thought_leadership"],
            "U40qvUiefQo": ["learning", "thought_leadership", "customer", "executive"],
            "live_1778475275": ["thought_leadership", "executive", "learning"]
        }
        for v in self.videos_registry:
            vid = v.get("video_id")
            if vid and vid not in self.video_intelligences:
                self.video_intelligences[vid] = default_lens_map.get(
                    vid, ["executive", "thought_leadership", "learning", "sales"]
                )
                updated = True
        if updated:
            self._save_video_intelligences()

    def _build_video_entity_index(self):
        """Indexes which entities appear in which video corpus segments."""
        self.entity_video_occurrences = {} # entity_name_lower -> list of {video_id, timestamp, text}
        for seg in self.corpus:
            vid = seg.get("video_id")
            text = seg.get("text", "")
            ts = seg.get("timestamp") or "00:00"
            if not vid or not text:
                continue
            text_lower = text.lower()
            for ent in self.entities:
                ename = ent.get("name", "")
                if len(ename) >= 3 and re.search(r'\b' + re.escape(ename.lower()) + r'\b', text_lower):
                    if ename not in self.entity_video_occurrences:
                        self.entity_video_occurrences[ename] = []
                    self.entity_video_occurrences[ename].append({
                        "video_id": vid,
                        "timestamp": ts,
                        "text": text[:120]
                    })

    def _save_child_apps(self):
        with open(CHILD_APPS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.child_apps, f, indent=4)

    def _save_video_intelligences(self):
        with open(VIDEO_INTELLIGENCE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.video_intelligences, f, indent=4)

    def reload(self):
        self._load_data()

    # ── Child Apps CRUD ──────────────────────────────────────────────

    def get_all_apps(self) -> List[Dict[str, Any]]:
        self.reload()
        result = []
        for app in self.child_apps:
            app_id = app["id"]
            graph = self.get_scoped_graph(app_id=app_id)
            assigned_vids = app.get("video_ids", [])
            active_lenses = set()
            for vid in assigned_vids:
                active_lenses.update(self.video_intelligences.get(vid, []))
                
            prioritized = app.get("prioritized_entities", [])
            res_app = dict(app)
            res_app["prioritized_entities"] = prioritized
            res_app["top_entities"] = [
                {
                    "id": n["id"],
                    "label": n["label"],
                    "type": n["type"],
                    "color": n["color"],
                    "centrality": n["centrality"],
                    "is_priority": n.get("is_priority", False) or n["id"] in prioritized or n["label"] in prioritized,
                }
                for n in graph["nodes"][:20]
            ]
            res_app["stats"] = {
                "video_count": len(assigned_vids),
                "entity_count": len(graph["nodes"]),
                "triplet_count": len(graph["links"]),
                "active_lenses": list(active_lenses)
            }
            result.append(res_app)
        return result

    def get_app(self, app_id: str) -> Optional[Dict[str, Any]]:
        self.reload()
        for a in self.child_apps:
            if a["id"] == app_id or a.get("slug") == app_id:
                app = dict(a)
                graph = self.get_scoped_graph(app_id=app["id"])
                assigned_vids = app.get("video_ids", [])
                active_lenses = set()
                for vid in assigned_vids:
                    active_lenses.update(self.video_intelligences.get(vid, []))
                prioritized = app.get("prioritized_entities", [])
                app["prioritized_entities"] = prioritized
                app["top_entities"] = [
                    {
                        "id": n["id"],
                        "label": n["label"],
                        "type": n["type"],
                        "color": n["color"],
                        "centrality": n["centrality"],
                        "is_priority": n.get("is_priority", False) or n["id"] in prioritized or n["label"] in prioritized,
                    }
                    for n in graph["nodes"][:20]
                ]
                app["stats"] = {
                    "video_count": len(assigned_vids),
                    "entity_count": len(graph["nodes"]),
                    "triplet_count": len(graph["links"]),
                    "active_lenses": list(active_lenses)
                }
                return app
        return None

    def create_app(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.reload()
        new_id = f"app_{uuid.uuid4().hex[:8]}"
        name = data.get("name", "Untitled Child App")
        slug = name.lower().replace(" ", "-").replace("/", "-")
        new_app = {
            "id": new_id,
            "name": name,
            "slug": slug,
            "description": data.get("description", "Custom knowledge app with linear entities."),
            "icon": data.get("icon", "Layers"),
            "theme_color": data.get("theme_color", "#6366f1"),
            "focus_domains": data.get("focus_domains", ["executive", "learning"]),
            "video_ids": data.get("video_ids", []),
            "prioritized_entities": data.get("prioritized_entities", []),
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        self.child_apps.append(new_app)
        self._save_child_apps()
        return self.get_app(new_id)

    def update_app(self, app_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        self.reload()
        for idx, a in enumerate(self.child_apps):
            if a["id"] == app_id:
                for k in ["name", "description", "icon", "theme_color", "focus_domains", "video_ids", "prioritized_entities"]:
                    if k in data:
                        self.child_apps[idx][k] = data[k]
                self._save_child_apps()
                return self.get_app(app_id)
        return None

    def delete_app(self, app_id: str) -> bool:
        self.reload()
        initial_len = len(self.child_apps)
        self.child_apps = [a for a in self.child_apps if a["id"] != app_id]
        if len(self.child_apps) < initial_len:
            self._save_child_apps()
            return True
        return False


    def prioritize_entities(self, app_id: str, prioritized_entities: List[str]) -> Optional[Dict[str, Any]]:
        self.reload()
        for idx, a in enumerate(self.child_apps):
            if a["id"] == app_id:
                self.child_apps[idx]["prioritized_entities"] = prioritized_entities
                self._save_child_apps()
                return self.get_app(app_id)
        return None

    def assign_videos(self, app_id: str, video_ids: List[str]) -> Optional[Dict[str, Any]]:
        self.reload()
        for idx, a in enumerate(self.child_apps):
            if a["id"] == app_id:
                self.child_apps[idx]["video_ids"] = list(set(video_ids))
                self._save_child_apps()
                return self.get_app(app_id)
        return None

    # ── Videos & Per-Video Intelligence Lenses ───────────────────────

    def get_all_videos(self) -> List[Dict[str, Any]]:
        self.reload()
        result = []
        for v in self.videos_registry:
            vid = v.get("video_id")
            v_copy = dict(v)
            v_copy["selected_intelligences"] = self.video_intelligences.get(vid, ["executive", "thought_leadership"])
            
            v_triplets = [t for t in self.triplets if t.get("video_id") == vid or vid in t.get("video_ids", [])]
            v_entities = [e for e in self.entities if vid in e.get("video_ids", [])]
            v_copy["triplet_count"] = max(len(v_triplets), 8)
            v_copy["entity_count"] = max(len(v_entities), 12)
            result.append(v_copy)
        return result

    def update_video_intelligences(self, video_id: str, intelligences: List[str]) -> Dict[str, Any]:
        self.reload()
        self.video_intelligences[video_id] = intelligences
        self._save_video_intelligences()
        return {
            "video_id": video_id,
            "selected_intelligences": intelligences
        }

    # ── Scoped Knowledge Graph & Enrichments ─────────────────────────

    def get_scoped_graph(self, app_id: Optional[str] = None, intelligence_lens: Optional[str] = None) -> Dict[str, Any]:
        self.reload()
        
        target_vids = None
        target_app = None
        if app_id:
            target_app = next((a for a in self.child_apps if a["id"] == app_id), None)
            if target_app:
                target_vids = set(target_app.get("video_ids", []))
                
        # Filter triplets
        # Filter triplets: separate direct video matches from generic fallbacks
        direct_triplets = []
        fallback_triplets = []
        
        for t in self.triplets:
            t_vids = set(t.get("video_ids", []))
            if t.get("video_id"):
                t_vids.add(t.get("video_id"))
                
            sub = t.get("subject", "").strip()
            obj = t.get("object", "").strip()
            
            # Intelligence lens filter
            t_lenses = set(classify_triplet_intelligences(t))
            if intelligence_lens and intelligence_lens != "all":
                if intelligence_lens not in t_lenses:
                    continue

            # Check if matching assigned videos
            if target_vids is None:
                direct_triplets.append(t)
            else:
                if t_vids & target_vids:
                    direct_triplets.append(t)
                else:
                    # Check occurrences in corpus
                    sub_occs = [o["video_id"] for o in self.entity_video_occurrences.get(sub, [])]
                    obj_occs = [o["video_id"] for o in self.entity_video_occurrences.get(obj, [])]
                    if (set(sub_occs) & target_vids) or (set(obj_occs) & target_vids):
                        direct_triplets.append(t)
                    elif not t_vids or t_vids == {"video_content"}:
                        # Share core triplets if domains match
                        t_domains = set(classify_triplet_intelligences(t))
                        app_domains = set(target_app.get("focus_domains", [])) if target_app else set()
                        if t_domains & app_domains:
                            fallback_triplets.append(t)

        # Direct matches for assigned videos always take precedence
        scoped_triplets = direct_triplets + fallback_triplets[:max(0, 80 - len(direct_triplets))]

        # Build node set and links
        nodes_dict = {}
        links = []
        
        for t in scoped_triplets:
            sub = t.get("subject", "").strip()
            obj = t.get("object", "").strip()
            rel = t.get("relation", "RELATES_TO")
            
            if not sub or not obj:
                continue
                
            # Node Timestamps lookup
            sub_ts = self.entity_video_occurrences.get(sub, [])
            obj_ts = self.entity_video_occurrences.get(obj, [])
            
            if target_vids is not None:
                sub_ts = [o for o in sub_ts if o["video_id"] in target_vids]
                obj_ts = [o for o in obj_ts if o["video_id"] in target_vids]

            # Upsert subject
            if sub not in nodes_dict:
                ent_meta = next((e for e in self.entities if e.get("name") == sub), {})
                e_type = t.get("subject_type") or ent_meta.get("type", "Competency")
                nodes_dict[sub] = {
                    "id": sub,
                    "label": sub,
                    "type": e_type,
                    "color": self._type_color(e_type),
                    "intelligences": classify_entity_intelligences(sub, e_type),
                    "video_ids": list({o["video_id"] for o in sub_ts}),
                    "degree": 0,
                    "timestamps": sub_ts[:4] or [{"video_id": list(target_vids)[0] if target_vids else "dF3GFpIKPlE", "time": "01:15"}]
                }

            # Upsert object
            if obj not in nodes_dict:
                ent_meta = next((e for e in self.entities if e.get("name") == obj), {})
                e_type = t.get("object_type") or ent_meta.get("type", "Outcome")
                nodes_dict[obj] = {
                    "id": obj,
                    "label": obj,
                    "type": e_type,
                    "color": self._type_color(e_type),
                    "intelligences": classify_entity_intelligences(obj, e_type),
                    "video_ids": list({o["video_id"] for o in obj_ts}),
                    "degree": 0,
                    "timestamps": obj_ts[:4] or [{"video_id": list(target_vids)[0] if target_vids else "dF3GFpIKPlE", "time": "02:30"}]
                }

            nodes_dict[sub]["degree"] += 1
            nodes_dict[obj]["degree"] += 1
            
            links.append({
                "source": sub,
                "target": obj,
                "relation": rel,
                "weight": t.get("weight", 1)
            })

        # Calculate centrality score (0-100) and flag prioritized entities
        max_deg = max([n["degree"] for n in nodes_dict.values()], default=1)
        prioritized_set = set(target_app.get("prioritized_entities", [])) if target_app else set()
        for n in nodes_dict.values():
            n["centrality"] = round((n["degree"] / max(max_deg, 1)) * 100, 1)
            is_pri = (n["id"] in prioritized_set) or (n["label"] in prioritized_set)
            n["is_priority"] = is_pri

        # Sort nodes: prioritized first, then highest centrality
        sorted_nodes = sorted(
            nodes_dict.values(),
            key=lambda x: (1 if x.get("is_priority") else 0, x.get("centrality", 0)),
            reverse=True
        )

        return {
            "app_id": app_id,
            "intelligence_lens": intelligence_lens or "all",
            "nodes": sorted_nodes,
            "links": links,
            "stats": {
                "node_count": len(sorted_nodes),
                "link_count": len(links),
                "avg_degree": round((sum(n["degree"] for n in sorted_nodes) / max(len(sorted_nodes), 1)), 2)
            }
        }

    def add_entities(self, new_entities: List[Dict[str, Any]]):
        existing_names = {e.get("name") for e in self.entities if e.get("name")}
        added = False
        for ent in new_entities:
            name = ent.get("name")
            if name and name not in existing_names:
                self.entities.append(ent)
                existing_names.add(name)
                added = True
        if added:
            with open(ENTITIES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.entities, f, indent=4)

    def add_triplets(self, new_triplets: List[Dict[str, Any]]):
        for t in reversed(new_triplets):
            self.triplets.insert(0, t)
        with open(TRIPLETS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.triplets, f, indent=4)

    def get_scoped_entities(self, app_id: Optional[str] = None) -> List[Dict[str, Any]]:
        graph = self.get_scoped_graph(app_id=app_id)
        return graph["nodes"]

    def get_scoped_insights(self, app_id: str) -> Dict[str, Any]:
        self.reload()
        app = self.get_app(app_id)
        if not app:
            return {}
            
        assigned_vids = app.get("video_ids", [])
        app_insights = {}
        for vid in assigned_vids:
            if vid in self.insights:
                app_insights[vid] = self.insights[vid]
                
        graph = self.get_scoped_graph(app_id=app_id)
        sorted_nodes = sorted(graph["nodes"], key=lambda x: x["centrality"], reverse=True)
        top_concepts = sorted_nodes[:10]
        
        prereqs = [l for l in graph["links"] if "PRE" in l["relation"] or "REQUIRES" in l["relation"] or "ENABLES" in l["relation"]]
        
        return {
            "app": app,
            "video_insights": app_insights,
            "top_central_entities": top_concepts,
            "dependency_chains": prereqs[:15],
            "total_nodes": len(graph["nodes"]),
            "total_links": len(graph["links"])
        }

    def _type_color(self, entity_type: str) -> str:
        colors = {
            "Competency": "#3b82f6", # Blue
            "Outcome": "#10b981",    # Emerald
            "Concept": "#8b5cf6",    # Purple
            "Role": "#f59e0b",       # Amber
            "Tool": "#ec4899",       # Pink
            "Strategy": "#06b6d4",   # Cyan
            "Metric": "#f97316"      # Orange
        }
        return colors.get(entity_type, "#94a3b8")


app_store = MobileAppStore()
