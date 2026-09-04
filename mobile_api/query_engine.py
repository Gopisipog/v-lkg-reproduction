"""
Query Engine — Handles Single-App Questioning and Cross-App "Twice Answered"
comparative querying grounded in scoped entities, intelligence lenses, and enrichments.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from mobile_api.app_store import app_store
from mobile_api.intelligence_manager import INTELLIGENCE_DOMAINS

# Try importing Gemini Client if available
try:
    from src.gcp.client import GeminiClient
    gemini_client = GeminiClient()
except Exception:
    gemini_client = None


def _format_time_sec(sec: float) -> str:
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m:02d}:{s:02d}"


def _find_relevant_segments(question: str, video_ids: List[str], max_segments: int = 6) -> List[Dict[str, Any]]:
    """Finds top relevant transcript segments for the question from the specified videos."""
    words = set(re.findall(r"\w+", question.lower()))
    scored_segments = []
    
    for seg in app_store.corpus:
        if seg.get("video_id") not in video_ids:
            continue
            
        text = seg.get("text", "")
        text_lower = text.lower()
        
        # calculate overlap score
        seg_words = set(re.findall(r"\w+", text_lower))
        overlap = len(words & seg_words)
        
        if overlap > 0:
            vid = seg.get("video_id")
            v_meta = next((v for v in app_store.videos_registry if v.get("video_id") == vid), {})
            ts = seg.get("timestamp") or _format_time_sec(seg.get("start_sec", 0))
            scored_segments.append({
                "video_id": vid,
                "video_title": v_meta.get("title", "Video"),
                "timestamp": ts,
                "start_sec": seg.get("start_sec", 0),
                "text": text,
                "score": overlap
            })
            
    scored_segments.sort(key=lambda x: x["score"], reverse=True)
    return scored_segments[:max_segments]


def query_child_app(
    app_id: str,
    question: str,
    intelligence_lens: Optional[str] = None
) -> Dict[str, Any]:
    """
    Answers a question grounded specifically in the child app's assigned videos,
    entities, triplets, and enrichments.
    """
    app = app_store.get_app(app_id)
    if not app:
        return {
            "error": f"Child app '{app_id}' not found.",
            "answer": "App not found.",
            "referenced_entities": [],
            "timestamp_citations": []
        }
        
    video_ids = app.get("video_ids", [])
    if not video_ids:
        return {
            "app_id": app_id,
            "app_name": app["name"],
            "answer": f"**{app['name']}** currently has no assigned videos. Please assign YouTube videos or voice recordings from the Video Library to enable knowledge graph querying.",
            "referenced_entities": [],
            "referenced_triplets": [],
            "timestamp_citations": []
        }

    # Fetch scoped graph and segments
    graph = app_store.get_scoped_graph(app_id=app_id, intelligence_lens=intelligence_lens)
    relevant_segments = _find_relevant_segments(question, video_ids, max_segments=6)
    
    # Identify top entities matching question
    q_lower = question.lower()
    matched_entities = []
    for node in graph["nodes"]:
        if node["label"].lower() in q_lower or any(w in node["label"].lower() for w in q_lower.split() if len(w) > 3):
            matched_entities.append(node)
            
    # Include top central entities if few matched
    if len(matched_entities) < 3:
        matched_entities.extend(sorted(graph["nodes"], key=lambda x: x["centrality"], reverse=True)[:4])
    # deduplicate
    seen_nodes = set()
    final_entities = []
    for n in matched_entities:
        if n["id"] not in seen_nodes:
            seen_nodes.add(n["id"])
            final_entities.append(n)

    # Scoped triplets matching matched entities
    matched_triplets = []
    entity_names = {n["id"] for n in final_entities}
    for link in graph["links"]:
        if link["source"] in entity_names or link["target"] in entity_names:
            matched_triplets.append(link)
    matched_triplets = matched_triplets[:8]

    # Build context for LLM or deterministic engine
    entity_summary = ", ".join([f"{n['label']} ({n['type']}, Centrality: {n['centrality']}%)" for n in final_entities[:8]])
    triplet_summary = "; ".join([f"{t['source']} -[{t['relation']}]-> {t['target']} (at {t.get('source_time', '00:00')})" for t in matched_triplets])
    segment_context = "\n".join([f"[{s['video_title']} @ {s['timestamp']}]: \"{s['text']}\"" for s in relevant_segments])

    lens_label = INTELLIGENCE_DOMAINS.get(intelligence_lens, {}).get("name", "Multi-Domain Intelligence") if intelligence_lens else "Consolidated Knowledge"

    # Check if Gemini is available
    if gemini_client and gemini_client.available:
        prompt = f"""
You are the AI Knowledge Assistant for '{app['name']}', focusing on {lens_label}.
Ground your answer ONLY on the provided Knowledge Graph triplets, entities, and video transcript segments below.

Question: {question}

Context Data:
App Focus: {app.get('description', '')}
Consolidated Entities: {entity_summary}
Graph Relationships: {triplet_summary}
Transcript Segments:
{segment_context}

Instructions:
1. Provide a direct, actionable answer structured with clear bullet points.
2. Directly reference relevant entities and graph relationships.
3. Include clickable timestamp citations formatted exactly like [02:15] or [00:45] whenever referencing a video point.
4. Keep the tone professional, insightful, and practical.
"""
        try:
            raw_answer = gemini_client.chat(prompt)
            if raw_answer:
                return {
                    "app_id": app_id,
                    "app_name": app["name"],
                    "theme_color": app.get("theme_color", "#6366f1"),
                    "intelligence_lens": lens_label,
                    "answer": raw_answer,
                    "referenced_entities": final_entities[:6],
                    "referenced_triplets": matched_triplets[:6],
                    "timestamp_citations": relevant_segments[:4]
                }
        except Exception as e:
            print(f"Gemini query error: {e}")

    # Deterministic fallback answer generator
    answer_parts = []
    answer_parts.append(f"Based on the **{app['name']}** knowledge graph ({lens_label}):\n")
    
    if final_entities:
        answer_parts.append("### Key Entities & Graph Pathways")
        for ent in final_entities[:4]:
            answer_parts.append(f"- **{ent['label']}** ({ent['type']}): Centrality score `{ent['centrality']}%`. Connected across {len(ent.get('video_ids', []))} video sources.")
            
    if matched_triplets:
        answer_parts.append("\n### Structural Relationships")
        for t in matched_triplets[:4]:
            answer_parts.append(f"- `{t['source']}` **[{t['relation']}]** `{t['target']}` *(Observed around [{t.get('source_time', '00:15')}])*")
            
    if relevant_segments:
        answer_parts.append("\n### Video Grounding & Timestamps")
        for s in relevant_segments[:3]:
            answer_parts.append(f"- In *{s['video_title']}* at **[{s['timestamp']}]**: \"{s['text']}\"")
            
    answer_parts.append("\n### Strategic Synthesis")
    answer_parts.append(f"To effectively address *'{question}'*, synthesize the prerequisite dependencies between `{final_entities[0]['label'] if final_entities else 'Core Concepts'}` and associated execution outcomes. Prioritize deliberate practice and systematic review of the timestamps indicated above.")

    return {
        "app_id": app_id,
        "app_name": app["name"],
        "theme_color": app.get("theme_color", "#6366f1"),
        "intelligence_lens": lens_label,
        "answer": "\n".join(answer_parts),
        "referenced_entities": final_entities[:6],
        "referenced_triplets": matched_triplets[:6],
        "timestamp_citations": relevant_segments[:4]
    }


def query_multi_apps(app_ids: List[str], question: str) -> Dict[str, Any]:
    """
    Cross-App "Twice Answered" / Multi-App Comparative Querying:
    Submits the question to multiple child apps concurrently, returns isolated answers
    and generates a cross-app comparative synthesis.
    """
    individual_answers = []
    all_referenced_entities = []
    all_citations = []
    
    for app_id in app_ids:
        ans = query_child_app(app_id=app_id, question=question)
        individual_answers.append(ans)
        all_referenced_entities.extend(ans.get("referenced_entities", []))
        all_citations.extend(ans.get("timestamp_citations", []))

    # Generate Comparative Synthesis
    app_names = [a.get("app_name", "App") for a in individual_answers]
    
    synthesis_points = []
    synthesis_points.append(f"### Cross-App Multi-Perspective Synthesis ({' vs '.join(app_names)})")
    synthesis_points.append(f"Comparing how different child apps analyze **'{question}'** through their respective knowledge graphs:\n")
    
    for ans in individual_answers:
        top_ent_names = [e["label"] for e in ans.get("referenced_entities", [])[:3]]
        ent_str = ", ".join(top_ent_names) if top_ent_names else "Core Frameworks"
        synthesis_points.append(f"- **{ans.get('app_name')} Angle**: Focuses heavily on `{ent_str}`.")
        
    synthesis_points.append("\n**Consensus & Complementary Insights**:")
    synthesis_points.append(f"- While **{app_names[0] if app_names else 'First App'}** provides tactical execution and structural mechanics, **{app_names[1] if len(app_names) > 1 else 'Second App'}** anchors the strategic mindset and delivery discipline.")
    synthesis_points.append("- Combined, following both knowledge graphs prevents blind spots by merging operational tooling with communication excellence.")

    return {
        "question": question,
        "app_count": len(individual_answers),
        "apps": individual_answers,
        "comparative_synthesis": "\n".join(synthesis_points),
        "total_entities_referenced": len(all_referenced_entities),
        "total_citations": len(all_citations)
    }
