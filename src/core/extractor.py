import os
import json
import re
from openai import OpenAI


def _safe_parse_json_array(raw: str) -> list:
    """Parse a JSON array from LLM output, tolerating common malformations.

    Handles markdown fences, prose around the array, unescaped control
    characters inside string values, trailing commas, and truncated output
    (LLM hitting the token limit mid-stream).
    """
    if not raw:
        return []

    text = raw.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)

    start = text.find("[")
    if start == -1:
        return []

    end = text.rfind("]")
    has_close = end != -1 and end > start

    if not has_close:
        text = _close_truncated_array(text, start)
    else:
        text = text[start : end + 1]

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    text = _escape_controls_in_strings(text)
    text = re.sub(r",\s*([}\]])", r"\1", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"  JSON repair failed: {e}")
        return []


def _close_truncated_array(text: str, start: int) -> str:
    """Salvage a truncated JSON array by closing it at the last complete object."""
    body = text[start:]
    last_brace = body.rfind("}")
    if last_brace == -1:
        return text
    trimmed = body[: last_brace + 1]
    trimmed = re.sub(r",\s*$", "", trimmed)
    return trimmed + "\n]"


def _escape_controls_in_strings(s: str) -> str:
    """Replace literal control characters inside JSON string values."""
    out = []
    in_str = False
    esc = False
    for ch in s:
        if esc:
            out.append(ch)
            esc = False
            continue
        if ch == "\\":
            out.append(ch)
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            out.append(ch)
            continue
        if in_str and ch in ("\n", "\r", "\t"):
            out.append("\\" + {"\n": "n", "\r": "r", "\t": "t"}[ch])
        else:
            out.append(ch)
    return "".join(out)


class SemanticEntityRecognizer:
    """Uses LLM to identify Nodes and relationships from text segments."""

    def __init__(self):
        self.api_key = os.environ.get("DEEPSEEK_API_KEY")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com",
        ) if self.api_key else None

    def extract_triplets(self, text_segment):
        """
        Extracts (Subject, Relation, Object) from a text segment using few-shot prompting.
        Returns a list of dictionaries representing the graph edges.
        """
        if not self.client:
            print("Warning: OPENAI_API_KEY not found. Returning empty triplets.")
            return []

        print(f"Extracting triplets from: {text_segment[:50]}...")
        
        prompt = f"""
        You are a Knowledge Graph extraction engine specialized in Leadership Education.
        Analyze the following text segment and extract entity relationships as a JSON array of triplets.

        Valid Node Types: Competency, Concept, Strategy, Tactic, Path, Object, Personality, Outcome.

        Node Type Guidance:
        - Competency: A learnable leadership skill or capability (e.g. "Active Listening", "Decision Making")
        - Concept: An abstract idea or principle (e.g. "Psychological Safety", "Growth Mindset")
        - Strategy: A high-level approach to achieving a goal (e.g. "Transformational Leadership", "Servant Leadership")
        - Tactic: A specific, actionable technique or practice (e.g. "Daily Stand-up", "One-on-One Meetings", "SMART Goals")
        - Path: An ordered sequence or learning journey (e.g. "Leadership Development Path", "Conflict Resolution Path")
        - Outcome: A measurable result (e.g. "Team Performance", "Employee Retention")
        - Personality: A personality trait or style (e.g. "Empathy", "Resilience")
        - Object: A concrete artifact, tool, or resource

        Valid Relations:
        - DEVELOPS_SKILL: Subject builds or develops the object skill/competency
        - IS_EXAMPLE_OF: Subject is a concrete instance of the object concept
        - SEMANTICALLY_RELATED: Subject and object share semantic proximity
        - HAS_STRATEGY: A competency or concept is pursued via this strategy
        - HAS_TACTIC: A strategy is implemented using this specific tactic
        - LEADS_TO: Subject is a step or cause that leads to the object outcome or next concept
        - ENABLES: Subject enables or unlocks the object capability
        - REQUIRES: Subject requires the object as a prerequisite
        - IS_PART_OF: Subject is a component or sub-element of the object path or concept

        Instructions:
        1. Extract all clearly stated relationships first, then infer implicit ones from context.
        2. If a strategy is mentioned, link it to its parent competency via HAS_STRATEGY.
        3. If a specific technique or practice is mentioned, classify it as Tactic and link to its strategy via HAS_TACTIC.
        4. If a causal or sequential flow is implied, use LEADS_TO.
        5. Return at least one triplet per clear concept present.

        Input Text: "{text_segment}"

        Output JSON Format:
        [
          {{
            "subject": "Entity Name 1",
            "subject_type": "Node Type",
            "relation": "VALID_RELATION",
            "object": "Entity Name 2",
            "object_type": "Node Type"
          }}
        ]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a specialized triple extraction API matching a predefined schema. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=16384,
            )
            content = response.choices[0].message.content.strip()
            result = _safe_parse_json_array(content)
            if not result:
                print(f"  Warning: no triplets parsed from response ({len(content)} chars)")
            return result
        except Exception as e:
            print(f"Error extracting triplets: {e}")
            return []

    def map_to_dbpedia(self, entity_str):
        """Cross-references entity with DBpedia URIs to standardize terminology."""
        # Simple heuristic matching for common leadership terms
        # In a full production system, this would make an external HTTP call to DBpedia Spotlight
        standardized_maps = {
            # Core leadership concepts
            "strategic planning": "http://dbpedia.org/resource/Strategic_management",
            "conflict": "http://dbpedia.org/resource/Conflict_resolution",
            "listening": "http://dbpedia.org/resource/Active_listening",
            "empathy": "http://dbpedia.org/resource/Empathy",
            # Strategies
            "transformational leadership": "http://dbpedia.org/resource/Transformational_leadership",
            "servant leadership": "http://dbpedia.org/resource/Servant_leadership",
            "situational leadership": "http://dbpedia.org/resource/Situational_leadership_theory",
            "coaching": "http://dbpedia.org/resource/Coaching",
            "mentoring": "http://dbpedia.org/resource/Mentorship",
            "delegation": "http://dbpedia.org/resource/Delegation",
            # Competencies
            "decision making": "http://dbpedia.org/resource/Decision-making",
            "communication": "http://dbpedia.org/resource/Communication",
            "emotional intelligence": "http://dbpedia.org/resource/Emotional_intelligence",
            "team building": "http://dbpedia.org/resource/Team_building",
            "motivation": "http://dbpedia.org/resource/Motivation",
            "negotiation": "http://dbpedia.org/resource/Negotiation",
            "feedback": "http://dbpedia.org/resource/Feedback",
            "trust": "http://dbpedia.org/resource/Trust_(social_science)",
            "accountability": "http://dbpedia.org/resource/Accountability",
            "vision": "http://dbpedia.org/resource/Strategic_vision",
            # Tactics
            "smart goals": "http://dbpedia.org/resource/SMART_criteria",
            "one-on-one": "http://dbpedia.org/resource/One-on-one_(management)",
            "stand-up": "http://dbpedia.org/resource/Stand-up_meeting",
            "retrospective": "http://dbpedia.org/resource/Retrospective",
            "brainstorming": "http://dbpedia.org/resource/Brainstorming",
            # Outcomes
            "employee retention": "http://dbpedia.org/resource/Employee_retention",
            "team performance": "http://dbpedia.org/resource/Team_effectiveness",
            "psychological safety": "http://dbpedia.org/resource/Psychological_safety",
            "growth mindset": "http://dbpedia.org/resource/Mindset#Fixed_and_growth_mindset",
        }
        
        lower_entity = entity_str.lower()
        for key, uri in standardized_maps.items():
            if key in lower_entity:
                return uri
                
        return entity_str
