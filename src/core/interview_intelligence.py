import os
import json
import re
import numpy as np
from openai import OpenAI


class InterviewIntelligenceEngine:
    """Analyzes interview-style YouTube content for Q&A patterns, term extraction,
    and on-similar-terms discovery across the knowledge graph."""

    def __init__(self, db_client=None, model_name="all-MiniLM-L6-v2"):
        self.db = db_client
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.llm_client = OpenAI(api_key=self.api_key) if self.api_key else None
        self._model_name = model_name
        self._embedder = None
        print(f"InterviewIntelligenceEngine initialized (model will load on first use)")

    @property
    def embedder(self):
        """Lazy-load SentenceTransformer on first use."""
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                print(f"Loading Sentence Transformer model: {self._model_name}...")
                self._embedder = SentenceTransformer(self._model_name, trust_remote_code=True)
                print("Sentence Transformer loaded successfully.")
            except Exception as e:
                print(f"SentenceTransformer unavailable: {e}")
                print("Falling back to basic string-matching similarity.")
                self._embedder = None
        return self._embedder

    # ── On Similar Terms ────────────────────────────────────────────────────

    def find_similar_terms(self, query_term, top_k=10, min_similarity=0.3):
        """Find semantically similar terms in the knowledge graph to the query term.
        Uses sentence embeddings + cosine similarity against all graph nodes.
        Falls back to basic string matching if embeddings unavailable.
        """
        # Gather nodes from whichever store is available
        all_nodes = []
        if self.db and self.db.driver:
            all_nodes = self.db.execute_read(
                "MATCH (n) WHERE n.name IS NOT NULL RETURN n.name AS name, labels(n)[0] AS type"
            ) or []
        elif hasattr(self.db, '_local_fallback') and self.db._local_fallback:
            local = self.db._local_fallback
            for e in local.get_entities():
                all_nodes.append({"name": e.get("name", ""), "type": e.get("type", "Entity")})
            # Also add intelligence-derived nodes from the cache
            if hasattr(local, 'get_triplets'):
                for t in local.get_triplets():
                    for name in (t.get("subject", ""), t.get("object", "")):
                        if name and not any(n["name"] == name for n in all_nodes):
                            all_nodes.append({"name": name, "type": "Extracted"})

        if not all_nodes:
            return {"error": "No nodes in knowledge graph", "results": []}

        query_lower = query_term.lower()
        similarities = []

        if self.embedder is not None:
            # Use semantic embeddings
            query_embedding = self.embedder.encode([query_term])[0]
            node_names = [n["name"] for n in all_nodes]
            node_embeddings = self.embedder.encode(node_names)

            for i, node_emb in enumerate(node_embeddings):
                sim = self._cosine_similarity(query_embedding, node_emb)
                if sim >= min_similarity:
                    rels = self._get_node_relationships(all_nodes[i]["name"])
                    similarities.append({
                        "term": all_nodes[i]["name"],
                        "type": all_nodes[i]["type"],
                        "similarity": round(float(sim), 4),
                        "relationships": rels,
                    })
        else:
            # Fallback: basic string matching (substring + word overlap)
            query_words = set(query_lower.split())
            for node in all_nodes:
                name_lower = node["name"].lower()
                # Check substring match
                if query_lower in name_lower or name_lower in query_lower:
                    sim = 0.5
                else:
                    # Word overlap
                    name_words = set(name_lower.split())
                    if not query_words or not name_words:
                        continue
                    overlap = len(query_words & name_words) / max(len(query_words | name_words), 1)
                    if overlap < min_similarity:
                        continue
                    sim = overlap * 0.8  # discount word-level matches
                rels = self._get_node_relationships(node["name"])
                similarities.append({
                    "term": node["name"],
                    "type": node["type"],
                    "similarity": round(sim, 4),
                    "relationships": rels,
                })

        similarities.sort(key=lambda x: x["similarity"], reverse=True)

        return {
            "query": query_term,
            "total_nodes": len(all_nodes),
            "matches": len(similarities),
            "results": similarities[:top_k],
        }

    def expand_terms(self, seed_terms, max_terms=15):
        """Expand a list of seed terms with semantically similar terms from the graph.
        Useful for interview analysis to find related concepts discussed.
        """
        expanded = {}
        for term in seed_terms:
            result = self.find_similar_terms(term, top_k=5, min_similarity=0.4)
            if "results" in result:
                for r in result["results"]:
                    t = r["term"]
                    if t not in expanded or r["similarity"] > expanded[t]["similarity"]:
                        expanded[t] = r
        sorted_terms = sorted(expanded.values(), key=lambda x: x["similarity"], reverse=True)
        return sorted_terms[:max_terms]

    # ── Interview Q&A Detection ─────────────────────────────────────────────

    def detect_qa_pairs(self, transcript_segments):
        """Detect question-answer patterns in interview transcript segments.
        Returns structured Q&A pairs with timestamps.
        """
        qa_pairs = []
        for i, seg in enumerate(transcript_segments):
            text = seg.get("transcript", "")
            if self._is_question(text):
                answer_text = ""
                answer_end = seg.get("end_time", seg.get("end", 0))
                for j in range(i + 1, min(i + 5, len(transcript_segments))):
                    next_text = transcript_segments[j].get("transcript", "")
                    if self._is_question(next_text):
                        break
                    answer_text += next_text + " "
                    answer_end = transcript_segments[j].get("end_time", transcript_segments[j].get("end", 0))

                qa_pairs.append({
                    "question": text.strip(),
                    "answer": answer_text.strip()[:500],
                    "timestamp": seg.get("start_time", seg.get("start", 0)),
                    "answer_end": answer_end,
                    "video_id": seg.get("video_id"),
                })
        return qa_pairs

    def analyze_interview_style(self, qa_pairs):
        """Analyze interviewing patterns from detected Q&A pairs.
        Returns statistics about question types, lengths, and patterns.
        """
        if not qa_pairs:
            return {}

        question_words = {"what", "how", "why", "when", "where", "who", "which", "do", "does", "did", "is", "are", "can", "could", "would", "tell", "explain", "describe"}
        types = {"open": 0, "closed": 0, "hypothetical": 0, "leading": 0}
        total_q_len = 0
        total_a_len = 0

        for qa in qa_pairs:
            q_text = qa["question"].lower()
            total_q_len += len(qa["question"].split())
            total_a_len += len(qa["answer"].split())

            first_word = q_text.split()[0] if q_text.split() else ""
            if first_word in {"what", "how", "why", "tell", "explain", "describe"}:
                types["open"] += 1
            elif q_text.startswith("what if") or q_text.startswith("imagine") or q_text.startswith("suppose"):
                types["hypothetical"] += 1
            elif any(phrase in q_text for phrase in ["wouldn't you", "don't you", "isn't it", "aren't you"]):
                types["leading"] += 1
            else:
                types["closed"] += 1

        return {
            "total_qa_pairs": len(qa_pairs),
            "avg_question_length_words": round(total_q_len / len(qa_pairs), 1),
            "avg_answer_length_words": round(total_a_len / len(qa_pairs), 1),
            "question_types": types,
            "open_ratio": round(types["open"] / max(len(qa_pairs), 1), 2),
        }

    # ── Key Term Extraction ─────────────────────────────────────────────────

    def extract_key_terms(self, text, use_llm=False):
        """Extract key leadership terms from interview text.
        Uses keyword heuristics by default, optional LLM for deeper extraction.
        """
        if use_llm and self.llm_client:
            return self._llm_term_extraction(text)

        leadership_terms = [
            "leadership", "vision", "mission", "strategy", "culture", "trust",
            "communication", "empathy", "resilience", "innovation", "change",
            "motivation", "accountability", "delegation", "feedback", "coaching",
            "mentoring", "teamwork", "collaboration", "decision-making",
            "conflict resolution", "emotional intelligence", "growth mindset",
            "psychological safety", "active listening", "purpose", "passion",
            "integrity", "transparency", "authenticity", "courage",
            "adaptability", "agility", "discipline", "focus", "excellence",
            "influence", "negotiation", "persuasion", "storytelling",
            "inclusion", "diversity", "belonging", "well-being", "burnout",
        ]

        text_lower = text.lower()
        found = []
        for term in leadership_terms:
            if term in text_lower:
                count = text_lower.count(term)
                found.append({"term": term, "count": count})

        found.sort(key=lambda x: x["count"], reverse=True)
        return found

    def _llm_term_extraction(self, text):
        """Use LLM to extract key terms from interview text."""
        if not self.llm_client:
            return self.extract_key_terms(text, use_llm=False)

        prompt = f"""
Analyze this interview transcript excerpt and extract key leadership/management terms.
Return ONLY a JSON array of objects with "term" and "category" keys.

Categories: Leadership, Communication, Strategy, Culture, Personal Development, Teamwork, Innovation

Text: "{text[:2000]}"

Example output:
[{{"term": "psychological safety", "category": "Culture"}}, {{"term": "active listening", "category": "Communication"}}]
"""
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Extract key leadership terms from interview text. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            return json.loads(content)
        except Exception as e:
            print(f"LLM term extraction error: {e}")
            return self.extract_key_terms(text, use_llm=False)

    # ── Interview Insight Generation ────────────────────────────────────────

    def generate_interview_insights(self, qa_pairs, similar_terms=None):
        """Generate insights about interview content using LLM."""
        if not self.llm_client or not qa_pairs:
            return self._default_insights(qa_pairs)

        top_qa = qa_pairs[:5]
        qa_summary = "\n".join(
            f"Q: {q['question'][:150]}\nA: {q['answer'][:200]}"
            for q in top_qa
        )
        terms_summary = ""
        if similar_terms:
            terms_summary = "Related terms in knowledge graph:\n" + "\n".join(
                f"- {t['term']} ({t.get('type', 'unknown')}) sim={t.get('similarity', 0):.2f}"
                for t in similar_terms[:8]
            )

        prompt = f"""
You are an interview intelligence analyst. Analyze these Q&A pairs from a leadership interview.

**Q&A Pairs:**
{qa_summary}

{terms_summary}

Generate interview intelligence insights as JSON:
{{
    "interview_topic": "Main topic of this interview segment",
    "key_insights": ["insight1", "insight2", "insight3"],
    "interviewer_approach": "How the interviewer is guiding the conversation",
    "notable_quotes": ["quote1", "quote2"],
    "knowledge_gap": "What's missing or worth exploring further",
    "related_concepts": ["concept1", "concept2", "concept3"]
}}

Return ONLY valid JSON.
"""
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an interview intelligence analyst. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            return json.loads(content)
        except Exception as e:
            print(f"Insight generation error: {e}")
            return self._default_insights(qa_pairs)

    def _default_insights(self, qa_pairs):
        """Fallback insights."""
        return {
            "interview_topic": "Leadership development",
            "key_insights": ["Interview covers leadership concepts and practices"],
            "interviewer_approach": "Question-driven exploration",
            "notable_quotes": [],
            "knowledge_gap": "Explore further by searching related terms",
            "related_concepts": [],
        }

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _cosine_similarity(self, vec_a, vec_b):
        dot = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))

    def _is_question(self, text):
        text = text.strip()
        if not text:
            return False
        if text.endswith("?"):
            return True
        question_starts = {"what", "how", "why", "when", "where", "who", "which",
                           "do", "does", "did", "is", "are", "can", "could",
                           "would", "will", "shall", "tell me", "explain",
                           "describe", "have you", "has he", "was it"}
        first_word = text.lower().split()[0] if text.split() else ""
        first_two = " ".join(text.lower().split()[:2]) if len(text.split()) >= 2 else ""
        return first_word in question_starts or first_two in question_starts

    def _get_node_relationships(self, node_name):
        """Get outgoing relationships for a node to provide context."""
        if not self.db or not self.db.driver:
            return []
        try:
            rels = self.db.execute_read(
                """MATCH (n {name: $name})-[r]->(m)
                   WHERE m.name IS NOT NULL
                   RETURN type(r) AS relation, m.name AS target, labels(m)[0] AS target_type
                   LIMIT 5""",
                {"name": node_name},
            ) or []
            return [{"relation": r["relation"], "target": r["target"], "target_type": r["target_type"]} for r in rels]
        except Exception:
            return []

    def get_video_corpus(self):
        """Load transcript corpus from disk."""
        if os.path.exists("data/processed/corpus.json"):
            with open("data/processed/corpus.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return []
