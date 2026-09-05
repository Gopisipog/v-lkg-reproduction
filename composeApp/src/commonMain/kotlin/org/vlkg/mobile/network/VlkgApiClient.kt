package org.vlkg.mobile.network

import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.plugins.logging.LogLevel
import io.ktor.client.plugins.logging.Logging
import io.ktor.client.request.*
import io.ktor.http.ContentType
import io.ktor.http.contentType
import io.ktor.serialization.kotlinx.json.json
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.json.Json
import org.vlkg.mobile.model.*

class VlkgApiClient(
    private val baseUrl: String = "http://127.0.0.1:8080"
) {
    private val client = HttpClient {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                isLenient = true
                prettyPrint = false
            })
        }
        install(Logging) {
            level = LogLevel.INFO
        }
    }

    suspend fun getApps(): List<ChildApp> = withContext(Dispatchers.Default) {
        try {
            client.get("$baseUrl/api/apps").body<List<ChildApp>>()
        } catch (e: Exception) {
            getOfflineMockApps()
        }
    }

    suspend fun getVideos(): List<VideoMetadata> = withContext(Dispatchers.Default) {
        try {
            client.get("$baseUrl/api/videos").body<List<VideoMetadata>>()
        } catch (e: Exception) {
            getOfflineMockVideos()
        }
    }

    suspend fun getVideoTranscript(videoId: String): List<TranscriptSegment> = withContext(Dispatchers.Default) {
        try {
            val resp = client.get("$baseUrl/api/videos/$videoId/transcript").body<VideoTranscriptResponse>()
            if (resp.segments.isNotEmpty()) resp.segments else getOfflineMockTranscript(videoId)
        } catch (e: Exception) {
            getOfflineMockTranscript(videoId)
        }
    }

    suspend fun getAppGraph(appId: String, lens: String? = null): GraphDataResponse = withContext(Dispatchers.Default) {
        try {
            val query = if (!lens.isNullOrBlank() && lens != "all") "?intelligence_lens=$lens" else ""
            val raw = client.get("$baseUrl/api/apps/$appId/graph$query").body<ApiScopedGraphResponse>()
            val nodes = raw.nodes.map { it.toConceptNode() }
            val edges = raw.links.map { it.toEdgeRelationship() }
            if (nodes.isNotEmpty()) {
                GraphDataResponse(nodes = nodes, edges = edges, timestamp = "")
            } else {
                getOfflineMockGraphData(appId)
            }
        } catch (e: Exception) {
            getOfflineMockGraphData(appId)
        }
    }

    suspend fun getAllEntities(): List<ConceptNode> = withContext(Dispatchers.Default) {
        try {
            val raw = client.get("$baseUrl/api/entities?limit=500").body<List<RawEntity>>()
            if (raw.isNotEmpty()) {
                raw.map { it.toConceptNode() }
            } else {
                getOfflineMockEntities()
            }
        } catch (e: Exception) {
            getOfflineMockEntities()
        }
    }

    suspend fun getScopedEntities(appId: String): List<ConceptNode> = withContext(Dispatchers.Default) {
        try {
            val raw = client.get("$baseUrl/api/apps/$appId/entities").body<List<ApiGraphNode>>()
            if (raw.isNotEmpty()) {
                raw.map { it.toConceptNode() }
            } else {
                getAllEntities()
            }
        } catch (e: Exception) {
            getAllEntities()
        }
    }

    suspend fun getDatabaseStatus(): DatabaseStatusResponse? = withContext(Dispatchers.Default) {
        try {
            client.get("$baseUrl/api/database/status").body<DatabaseStatusResponse>()
        } catch (e: Exception) {
            null
        }
    }

    suspend fun queryApp(appId: String, question: String, lens: String? = null): AppQueryResult = withContext(Dispatchers.Default) {
        try {
            client.post("$baseUrl/api/apps/$appId/query") {
                contentType(ContentType.Application.Json)
                setBody(mapOf("question" to question, "intelligence_lens" to (lens ?: "all")))
            }.body<AppQueryResult>()
        } catch (e: Exception) {
            getOfflineMockQuery(appId, question)
        }
    }

    suspend fun prioritizeEntity(appId: String, entities: List<String>): ChildApp? = withContext(Dispatchers.Default) {
        try {
            client.put("$baseUrl/api/apps/$appId/prioritize") {
                contentType(ContentType.Application.Json)
                setBody(mapOf("prioritized_entities" to entities))
            }.body<ChildApp>()
        } catch (e: Exception) {
            null
        }
    }

    suspend fun getVideoSemantics(videoId: String): VideoSemanticsResponse? = withContext(Dispatchers.Default) {
        try {
            client.get("$baseUrl/api/videos/$videoId/semantics").body<VideoSemanticsResponse>()
        } catch (e: Exception) {
            null
        }
    }

    suspend fun searchTranscripts(query: String, videoId: String? = null): List<TranscriptSearchResultItem> = withContext(Dispatchers.Default) {
        try {
            val vidParam = if (!videoId.isNullOrBlank()) "&video_id=$videoId" else ""
            val resp = client.get("$baseUrl/api/transcripts/search?q=$query$vidParam").body<TranscriptSearchResponse>()
            resp.results
        } catch (e: Exception) {
            emptyList()
        }
    }

    suspend fun queryMultiApps(appIds: List<String>, question: String): MultiAppQueryResponse? = withContext(Dispatchers.Default) {
        try {
            client.post("$baseUrl/api/query/multi-app") {
                contentType(ContentType.Application.Json)
                setBody(mapOf("app_ids" to appIds, "question" to question))
            }.body<MultiAppQueryResponse>()
        } catch (e: Exception) {
            null
        }
    }

    suspend fun ingestVideo(url: String, appId: String? = null, lenses: List<String> = listOf("executive", "thought_leadership")): Boolean = withContext(Dispatchers.Default) {
        try {
            client.post("$baseUrl/api/videos/ingest") {
                contentType(ContentType.Application.Json)
                setBody(mapOf("url" to url, "app_id" to (appId ?: ""), "intelligence_lenses" to lenses))
            }
            true
        } catch (e: Exception) {
            false
        }
    }

    suspend fun createApp(payload: CreateAppPayload): ChildApp? = withContext(Dispatchers.Default) {
        try {
            client.post("$baseUrl/api/apps") {
                contentType(ContentType.Application.Json)
                setBody(payload)
            }.body<ChildApp>()
        } catch (e: Exception) {
            null
        }
    }

    suspend fun liveExtract(text: String): VoiceExtractionResult = withContext(Dispatchers.Default) {
        try {
            client.post("$baseUrl/api/voice/live-extract") {
                contentType(ContentType.Application.Json)
                setBody(mapOf("text" to text))
            }.body<VoiceExtractionResult>()
        } catch (e: Exception) {
            VoiceExtractionResult(
                keywords = text.split(" ").filter { it.length > 5 }.take(4),
                suggested_entities = listOf("Strategic Thinking", "Execution Habit", "Leadership Agency")
            )
        }
    }

    suspend fun processVoiceRecording(
        title: String,
        transcriptText: String,
        appId: String,
        lenses: List<String> = listOf("executive", "thought_leadership")
    ): Boolean = withContext(Dispatchers.Default) {
        try {
            val segs = listOf(TranscriptSegment(video_id = "voice_${System.currentTimeMillis()}", timestamp = "00:00", text = transcriptText))
            client.post("$baseUrl/api/voice/process") {
                contentType(ContentType.Application.Json)
                setBody(mapOf(
                    "title" to title,
                    "transcript_segments" to segs,
                    "app_id" to appId,
                    "intelligence_lenses" to lenses
                ))
            }
            true
        } catch (e: Exception) {
            false
        }
    }


    suspend fun getGraphData(appId: String = "app_executive"): GraphDataResponse = getAppGraph(appId)

    suspend fun getNodeEvidence(nodeId: String): List<VideoTriplet> = withContext(Dispatchers.Default) {
        getOfflineMockQuery("app_executive", "").triplets
    }

    suspend fun getPathways(): List<LearningPathway> = withContext(Dispatchers.Default) {
        listOf(
            LearningPathway(
                id = "path-1",
                title = "AI Era Leadership & Systems Design",
                targetRole = "Engineering Director / VP of AI",
                description = "Master reasoning from fundamentals to orchestrating autonomous agentic pipelines.",
                steps = getOfflineMockGraphData("app_executive").nodes.take(4),
                estimatedDurationHours = 3.5,
                completedStepsCount = 2
            ),
            LearningPathway(
                id = "path-2",
                title = "High-Agency Culture & Radical Candor",
                targetRole = "Founder & Tech Lead",
                description = "Establish feedback mechanisms and transformative vision for high-velocity teams.",
                steps = getOfflineMockGraphData("app_executive").nodes.take(3),
                estimatedDurationHours = 2.0,
                completedStepsCount = 1
            )
        )
    }
    // ── Offline High-Fidelity Fallback Data ─────────────────────────────

    fun getOfflineMockApps(): List<ChildApp> {
        return listOf(
            ChildApp(
                id = "app_executive",
                name = "Executive Leadership & Strategy",
                slug = "executive-leadership",
                description = "C-suite strategic frameworks, time management, personal discipline, and leadership alignment.",
                icon = "Briefcase",
                theme_color = "#6366f1",
                focus_domains = listOf("executive", "learning", "thought_leadership"),
                video_ids = listOf("test_ingest_789", "dF3GFpIKPlE", "paF4J941uqg"),
                prioritized_entities = listOf("First-Principles Thinking", "Transformational Leadership", "Radical Candor")
            ),
            ChildApp(
                id = "app_gtm_ai",
                name = "GTM & AI Engineering Lab",
                slug = "gtm-ai-engineering",
                description = "Go-to-market workflows, Claude Code automation, developer marketing, and scalable system design.",
                icon = "Cpu",
                theme_color = "#3b82f6",
                focus_domains = listOf("engineering", "sales", "executive"),
                video_ids = listOf("paF4J941uqg", "test_ingest_789"),
                prioritized_entities = listOf("Autonomous AI Agents", "Model Context Protocol", "GTM Engineering")
            ),
            ChildApp(
                id = "app_comm_mastery",
                name = "Communication & Public Speaking",
                slug = "communication-mastery",
                description = "Mastery of rhetorical devices, vocal delivery, self-reflection drills, and audience captivation.",
                icon = "Sparkles",
                theme_color = "#14b8a6",
                focus_domains = listOf("thought_leadership", "learning"),
                video_ids = listOf("dF3GFpIKPlE"),
                prioritized_entities = listOf("Rhetorical Devices", "Active Listening", "Vocal Variety")
            ),
            ChildApp(
                id = "app_compliance",
                name = "Enterprise Governance & Trust",
                slug = "enterprise-compliance",
                description = "Risk mitigation, regulatory adherence, ethical boundaries, and cybersecurity leadership.",
                icon = "Shield",
                theme_color = "#f59e0b",
                focus_domains = listOf("compliance", "executive"),
                video_ids = listOf("test_ingest_789"),
                prioritized_entities = listOf("Regulatory Oversight", "Ethical AI Boundaries")
            )
        )
    }

    fun getOfflineMockVideos(): List<VideoMetadata> {
        return listOf(
            VideoMetadata(
                video_id = "dF3GFpIKPlE",
                title = "7 Communication Devices That Separate Great Presenters",
                url = "https://www.youtube.com/watch?v=dF3GFpIKPlE",
                thumbnail_url = "https://i.ytimg.com/vi/dF3GFpIKPlE/maxresdefault.jpg",
                channel = "Leadership & Communication",
                duration_sec = 378,
                summary = "Teaches seven powerful communication techniques used by elite presenters to captivate audiences and inspire action.",
                segment_count = 167
            ),
            VideoMetadata(
                video_id = "paF4J941uqg",
                title = "GTM Engineering with Claude Code Crash Course",
                url = "https://www.youtube.com/watch?v=paF4J941uqg",
                thumbnail_url = "https://i.ytimg.com/vi/paF4J941uqg/maxresdefault.jpg",
                channel = "Cody Schneider",
                duration_sec = 800,
                summary = "Emphasizes leveraging AI tools like Claude Code for effective go-to-market engineering, streamlining marketing and workflows.",
                segment_count = 410
            ),
            VideoMetadata(
                video_id = "test_ingest_789",
                title = "YouTube Leadership Video [High Agency Teams]",
                url = "https://www.youtube.com/watch?v=test_ingest_789",
                thumbnail_url = "https://i.ytimg.com/vi/test_ingest_789/maxresdefault.jpg",
                channel = "YouTube Leadership Series",
                duration_sec = 540,
                summary = "Ingested YouTube educational video covering strategic principles, execution habits, and leadership frameworks.",
                segment_count = 4
            )
        )
    }

    fun getOfflineMockTranscript(videoId: String): List<TranscriptSegment> {
        return listOf(
            TranscriptSegment(videoId, "Video Lecture", "00:15", 15f, "Welcome everyone. Today we deconstruct the core pillars of executive agency and first-principles thinking.", 1),
            TranscriptSegment(videoId, "Video Lecture", "01:24", 84f, "A transformational leader establishes psychological safety first. Without it, team members hide issues.", 1),
            TranscriptSegment(videoId, "Video Lecture", "02:45", 165f, "When you look at modern AI automation, you don't merely copy legacy processes—you reason from fundamentals.", 1),
            TranscriptSegment(videoId, "Video Lecture", "04:10", 250f, "Radical candor means caring personally while challenging directly in fast feedback loops.", 1),
            TranscriptSegment(videoId, "Video Lecture", "06:30", 390f, "High-output execution is driven by clear OKRs, transparent dependencies, and aligned metrics.", 1)
        )
    }

    fun getOfflineMockEntities(): List<ConceptNode> {
        return getOfflineMockGraphData("app_executive").nodes
    }

    fun getOfflineMockGraphData(appId: String): GraphDataResponse {
        val nodes = listOf(
            ConceptNode("1", "First-Principles Thinking", ConceptCategory.DECISION_MAKING, 0.95, "Boiling problems down to fundamentals.", 4, listOf("Mental Models", "Strategy"), 200f, 220f),
            ConceptNode("2", "Transformational Leadership", ConceptCategory.CORE_LEADERSHIP, 0.90, "Inspiring teams to achieve extraordinary outcomes.", 6, listOf("Inspiration", "Vision"), 400f, 320f),
            ConceptNode("3", "Autonomous AI Agents", ConceptCategory.AI_INNOVATION, 0.88, "Self-directed AI architectures with planning.", 5, listOf("Automation", "Agentic"), 620f, 200f),
            ConceptNode("4", "Radical Candor", ConceptCategory.COMMUNICATION, 0.78, "Caring personally while challenging directly.", 3, listOf("Feedback", "Trust"), 320f, 480f),
            ConceptNode("5", "Systems Dynamics", ConceptCategory.SYSTEMS_THINKING, 0.85, "Understanding non-linear causal loops.", 4, listOf("Causal Loops", "Leverage"), 520f, 460f),
            ConceptNode("6", "High-Output Execution", ConceptCategory.EXECUTION, 0.82, "Aligning teams with ambitious Objectives.", 5, listOf("OKRs", "Focus"), 720f, 360f)
        )
        val edges = listOf(
            EdgeRelationship("e1", "1", "2", "ENABLES", 1f),
            EdgeRelationship("e2", "1", "3", "ARCHITECTS", 0.9f),
            EdgeRelationship("e3", "2", "4", "REINFORCES", 0.85f),
            EdgeRelationship("e4", "2", "5", "SHAPES", 0.9f),
            EdgeRelationship("e5", "5", "6", "DRIVES", 0.88f),
            EdgeRelationship("e6", "3", "6", "SCALES", 0.92f)
        )
        return GraphDataResponse(nodes, edges)
    }

    fun getOfflineMockQuery(appId: String, question: String): AppQueryResult {
        return AppQueryResult(
            answer = "Based on the scoped knowledge graph for this child app, effective leadership centers on First-Principles Thinking and psychological safety. Leaders who deconstruct assumptions rather than accepting conventional constraints build high-agency teams capable of navigating non-linear systems.",
            app_id = appId,
            app_name = "Leadership & Strategy",
            intelligence_lens = "executive",
            triplets = listOf(
                VideoTriplet("t1", "Transformational Leader", "ESTABLISHES", "Psychological Safety", "dF3GFpIKPlE", "7 Communication Devices", 84, "01:24", 0.98, "A transformational leader establishes psychological safety first.", "Slide 2: Foundations of High-Agency Culture", "https://www.youtube.com/watch?v=dF3GFpIKPlE&t=84s"),
                VideoTriplet("t2", "First-Principles Thinking", "DECONSTRUCTS", "Conventional Constraints", "paF4J941uqg", "GTM Engineering with Claude Code", 165, "02:45", 0.94, "Reason from fundamentals rather than copying legacy conventions.", "Slide 5: First-Principles Deconstruction", "https://www.youtube.com/watch?v=paF4J941uqg&t=165s")
            ),
            relevant_segments = listOf(
                TranscriptSegment("dF3GFpIKPlE", "7 Communication Devices", "01:24", 84f, "A transformational leader establishes psychological safety first.", 3),
                TranscriptSegment("paF4J941uqg", "GTM Engineering with Claude Code", "02:45", 165f, "When you look at modern AI automation, you don't merely copy legacy processes—you reason from fundamentals.", 2)
            )
        )
    }
}