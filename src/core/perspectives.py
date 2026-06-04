import os
import json
from openai import OpenAI


class YouTubePerspectivesEngine:
    """Generates answers from different YouTube leaders AND the ingested video knowledge graphs."""

    # Famous YouTube leadership content creators with their styles
    YOUTUBERS = {
        "Simon Sinek": {
            "style": "Starts with 'Why', uses golden circle framework, inspirational tone",
            "expertise": "Leadership motivation, organizational psychology, finding purpose",
            "catchphrases": [
                "People don't buy what you do, they buy why you do it",
                "Start with why",
            ],
        },
        "Brene Brown": {
            "style": "Vulnerable, research-based, Houston accent, talks about shame and vulnerability",
            "expertise": "Vulnerability, courage, shame research, leadership authenticity",
            "catchphrases": ["Vulnerability is not winning or losing", "Dare to lead"],
        },
        "Gary Vaynerchuk": {
            "style": "Direct, energetic, NYC accent, no-nonsense hustle culture",
            "expertise": "Entrepreneurship, social media marketing, hustle, Jab Jab Jab Right Hook",
            "catchphrases": ["Hustle harder", "Work harder than your competition"],
        },
        "Mel Robbins": {
            "style": "Practical, science-backed, high energy, action-oriented",
            "expertise": "Productivity, habit change, motivation, the 5-second rule",
            "catchphrases": [
                "5-4-3-2-1 rule",
                "You are one decision away from a totally different life",
            ],
        },
        "James Clear": {
            "style": "Calm, research-focused, atomic habits author, gradual improvement",
            "expertise": "Habit formation, continuous improvement, behavior design",
            "catchphrases": [
                "You do not rise to the level of your goals",
                "Every action you take is a vote for the type of person you wish to become",
            ],
        },
        "Dale Carnegie": {
            "style": "Classic, timeless wisdom, How to Win Friends principles",
            "expertise": "People skills, influence, relationships, communication",
            "catchphrases": ["Become genuinely interested in other people", "Smile"],
        },
        "Tony Robbins": {
            "style": "High energy, transformative, life coaching, asks powerful questions",
            "expertise": "Life coaching, peak performance, personal development, massive action",
            "catchphrases": [
                "It's in your moments of decision that your destiny is shaped"
            ],
        },
        "Ted Lasso": {
            "style": "Optimistic, kind, uses sports metaphors, believe slogan",
            "expertise": "Team morale, optimism, leading with kindness, work-life balance",
            "catchphrases": ["Believe", "Be curious, not judgmental"],
        },
    }

    def __init__(self, db_client=None):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.db_client = db_client

    def get_video_knowledge_context(self):
        """Get all knowledge graphs from processed YouTube videos."""
        if not self.db_client or not self.db_client.driver:
            return {"nodes": [], "relationships": [], "videos": [], "corpus": []}

        # Get all nodes
        nodes = (
            self.db_client.execute_read(
                "MATCH (n) WHERE n.name IS NOT NULL RETURN labels(n)[0] AS type, n.name AS name"
            )
            or []
        )

        # Get all relationships
        relationships = (
            self.db_client.execute_read(
                """MATCH (a)-[r]->(b) 
               WHERE a.name IS NOT NULL AND b.name IS NOT NULL 
               RETURN a.name AS from_node, type(r) AS relation, b.name AS to_node"""
            )
            or []
        )

        # Get video registry
        corpus = []
        if os.path.exists("data/processed/corpus.json"):
            with open("data/processed/corpus.json", "r") as f:
                corpus = json.load(f)

        # Get all registered videos
        videos = []
        if os.path.exists("data/processed/videos_registry.json"):
            with open("data/processed/videos_registry.json", "r") as f:
                videos = json.load(f)

        return {
            "nodes": nodes,
            "relationships": relationships,
            "videos": videos,
            "corpus": corpus,
        }

    def find_relevant_knowledge(self, question):
        """Find knowledge graph content relevant to the user's question."""
        if not self.db_client or not self.db_client.driver:
            return {
                "relevant_nodes": [],
                "relevant_relationships": [],
                "transcript_segments": [],
            }

        # Extract keywords from question
        keywords = [w.lower() for w in question.split() if len(w) > 3]

        # Find nodes matching keywords
        relevant_nodes = []
        all_nodes = (
            self.db_client.execute_read(
                "MATCH (n) WHERE n.name IS NOT NULL RETURN labels(n)[0] AS type, n.name AS name"
            )
            or []
        )

        for node in all_nodes:
            node_name_lower = node["name"].lower()
            for keyword in keywords:
                if keyword in node_name_lower or node_name_lower in keyword:
                    relevant_nodes.append(node)
                    break

        # Find related relationships
        relevant_rels = []
        all_rels = (
            self.db_client.execute_read(
                """MATCH (a)-[r]->(b) 
               WHERE a.name IS NOT NULL AND b.name IS NOT NULL 
               RETURN a.name AS from_node, type(r) AS relation, b.name AS to_node"""
            )
            or []
        )

        relevant_node_names = {n["name"] for n in relevant_nodes}
        for rel in all_rels:
            if (
                rel["from_node"] in relevant_node_names
                or rel["to_node"] in relevant_node_names
            ):
                relevant_rels.append(rel)

        # Find relevant transcript segments
        transcript_segments = []
        if os.path.exists("data/processed/corpus.json"):
            with open("data/processed/corpus.json", "r") as f:
                corpus = json.load(f)
                for seg in corpus:
                    seg_text = seg["transcript"].lower()
                    for keyword in keywords:
                        if keyword in seg_text:
                            transcript_segments.append(seg)
                            break

        return {
            "relevant_nodes": relevant_nodes[:10],
            "relevant_relationships": relevant_rels[:10],
            "transcript_segments": transcript_segments[:5],
        }

    def get_youtuber_perspective(self, youtuber_name, question, video_context=None):
        """Get how a specific YouTuber would answer, incorporating video knowledge."""
        if not self.client:
            return self._default_perspective(youtuber_name, question)

        youtuber = self.YOUTUBERS.get(youtuber_name, {})
        style = youtuber.get("style", "")
        expertise = youtuber.get("expertise", "")

        # Add video knowledge context if available
        context_note = ""
        if video_context and video_context.get("relevant_nodes"):
            nodes_str = ", ".join(
                [n["name"] for n in video_context["relevant_nodes"][:5]]
            )
            context_note = f"\n\nBased on ingested YouTube videos, relevant concepts include: {nodes_str}"

        if video_context and video_context.get("transcript_segments"):
            segs = video_context["transcript_segments"]
            if segs:
                transcript_excerpt = segs[0]["transcript"][:200]
                context_note += (
                    f'\n\nFrom the video transcripts: "{transcript_excerpt}..."'
                )

        prompt = f"""
You are {youtuber_name}, a famous leadership/development YouTube content creator.

Your style: {style}
Your expertise: {expertise}

A user asks: "{question}"{context_note}

Answer this question AS {youtuber_name} would, incorporating:
- Your typical speaking style and tone
- Your core beliefs and frameworks
- If relevant, connect to concepts from the ingested YouTube videos
- Real examples or stories you might use
- A call to action or specific advice

Then, based on your answer, suggest ONE specific action item the viewer should take.

Return JSON:
{{
    "youtuber": "{youtuber_name}",
    "answer": "Your answer as {youtuber_name} would give it (2-3 sentences)",
    "action_item": "ONE specific action item the viewer should take",
    "key_insight": "One key insight from your perspective",
    "quote": "A memorable quote or phrase {youtuber_name} might use",
    "video_connection": "How this connects to concepts from ingested YouTube videos (or 'N/A' if no connection)"
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are {youtuber_name}. Answer as they would, incorporating video knowledge if relevant.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            return json.loads(content)
        except Exception as e:
            print(f"Error generating perspective: {e}")
            return self._default_perspective(youtuber_name, question)

    def _default_perspective(self, youtuber_name, question):
        """Fallback perspective if LLM fails."""
        perspectives = {
            "Simon Sinek": {
                "youtuber": "Simon Sinek",
                "answer": "The answer lies in understanding your WHY. Most people focus on WHAT they do, but leaders who inspire start with WHY - the purpose, cause, or belief that drives them.",
                "action_item": "Write down your WHY in one sentence and share it with one person today.",
                "key_insight": "People follow leaders who inspire, not just those in positions of power.",
                "quote": "Leadership is not about being in charge. It's about taking care of those in your charge.",
                "video_connection": "Based on leadership videos you've watched",
            },
            "Brene Brown": {
                "youtuber": "Brene Brown",
                "answer": "This is such a brave question to ask. The truth is, vulnerability is at the core of [the topic]. It takes courage to show up authentically, even when it's uncomfortable.",
                "action_item": "Practice one vulnerable conversation this week - share something you've been avoiding saying.",
                "key_insight": "Vulnerability is not weakness. It's our most accurate measure of courage.",
                "quote": "Daring greatly means showing up when you can't control the outcome.",
                "video_connection": "Based on authenticity videos you've watched",
            },
        }
        return perspectives.get(youtuber_name, perspectives["Simon Sinek"])

    def generate_all_perspectives(self, question, db_client=None, num_perspectives=5):
        """Get perspectives from multiple YouTubers, incorporating video knowledge."""
        self.db_client = db_client

        # Get video knowledge context
        video_context = self.find_relevant_knowledge(question)

        selected_youtubers = list(self.YOUTUBERS.keys())[:num_perspectives]

        results = []
        for youtuber in selected_youtubers:
            perspective = self.get_youtuber_perspective(
                youtuber, question, video_context
            )
            perspective["youtuber"] = youtuber
            results.append(perspective)

        # Add video knowledge as first "perspective"
        if video_context["relevant_nodes"]:
            video_summary = {
                "youtuber": "📺 Your Ingested Videos",
                "answer": f"Based on {len(video_context['relevant_nodes'])} relevant concepts from your processed YouTube videos.",
                "action_item": self._extract_action_from_video_knowledge(video_context),
                "key_insight": f"Found {len(video_context['relevant_relationships'])} related concepts",
                "quote": "From your video knowledge graph",
                "video_connection": "From your ingested YouTube content",
                "is_video_knowledge": True,
                "relevant_nodes": [
                    n["name"] for n in video_context["relevant_nodes"][:5]
                ],
                "transcript_excerpt": video_context["transcript_segments"][0][
                    "transcript"
                ][:150]
                if video_context["transcript_segments"]
                else "",
            }
            results.insert(0, video_summary)

        return results

    def _extract_action_from_video_knowledge(self, video_context):
        """Extract an action item from video knowledge."""
        if video_context["transcript_segments"]:
            return f"Review the transcript segments about: {video_context['transcript_segments'][0]['transcript'][:80]}..."
        if video_context["relevant_nodes"]:
            return f"Practice applying these concepts: {', '.join(video_context['relevant_nodes'][:3])}"
        return "Watch more videos to expand your knowledge graph"

    def generate_consensus_action_plan(self, perspectives, db_client=None):
        """Generate a consolidated action plan from all perspectives and video knowledge."""
        if not self.client:
            return self._default_action_plan(perspectives)

        self.db_client = db_client

        # Get video knowledge
        video_context = self.find_relevant_knowledge("")

        perspectives_text = "\n".join(
            [f"- {p['youtuber']}: {p.get('action_item', 'N/A')}" for p in perspectives]
        )

        video_knowledge = ""
        if video_context["relevant_nodes"]:
            video_knowledge = f"\n\nFrom user's ingested YouTube videos:\n"
            video_knowledge += f"Concepts: {', '.join([n['name'] for n in video_context['relevant_nodes'][:5]])}"

        prompt = f"""
Based on these different YouTube leadership perspectives AND the user's ingested video knowledge, create a unified action plan:

{perspectives_text}{video_knowledge}

Synthesize these different approaches into:
1. A primary action that incorporates the best from all perspectives AND video knowledge
2. A mindset shift to adopt
3. A daily habit to build
4. How to measure progress
5. How to leverage the ingested video knowledge for continued learning

Return JSON:
{{
    "primary_action": "The main action incorporating multiple perspectives and video knowledge",
    "mindset_shift": "The underlying mindset to embrace",
    "daily_habit": "One small thing to do every day",
    "measurement": "How to track progress",
    "video_learning": "How to continue learning from ingested videos",
    "perspective_summary": "Brief summary of how different sources would approach this"
}}

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a leadership coach synthesizing multiple perspectives and video knowledge into actionable guidance.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            return json.loads(content)
        except Exception as e:
            print(f"Error generating consensus: {e}")
            return self._default_action_plan(perspectives)

    def _default_action_plan(self, perspectives):
        """Fallback action plan."""
        return {
            "primary_action": "Take consistent daily action toward your goal",
            "mindset_shift": "Focus on progress, not perfection",
            "daily_habit": "Spend 15 minutes each morning on this topic",
            "measurement": "Track completion of daily actions",
            "video_learning": "Watch more videos to expand your knowledge",
            "perspective_summary": f"You have perspectives from {len(perspectives)} different sources",
        }

    def get_video_stats(self):
        """Get statistics about ingested videos."""
        video_context = self.get_video_knowledge_context()
        return {
            "videos_ingested": len(video_context["videos"]),
            "total_nodes": len(video_context["nodes"]),
            "total_relationships": len(video_context["relationships"]),
            "transcript_segments": len(video_context["corpus"]),
        }
