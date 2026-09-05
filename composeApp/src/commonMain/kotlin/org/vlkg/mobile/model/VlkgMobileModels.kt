package org.vlkg.mobile.model

import kotlinx.serialization.Serializable

@Serializable
data class ChildApp(
    val id: String,
    val name: String,
    val slug: String = "",
    val description: String = "",
    val icon: String = "Briefcase",
    val theme_color: String = "#6366f1",
    val focus_domains: List<String> = listOf("executive", "learning"),
    val video_ids: List<String> = emptyList(),
    val created_at: String = "",
    val prioritized_entities: List<String> = emptyList()
)

@Serializable
data class VideoMetadata(
    val video_id: String,
    val title: String,
    val url: String = "",
    val thumbnail_url: String = "",
    val channel: String = "YouTube Leadership Series",
    val duration_sec: Int = 0,
    val summary: String = "",
    val segment_count: Int = 0,
    val ingested_at: String = "",
    val is_voice_recording: Boolean = false
)

@Serializable
data class TranscriptSegment(
    val video_id: String = "",
    val video_title: String = "",
    val timestamp: String = "00:00",
    val start_sec: Float = 0f,
    val text: String = "",
    val score: Int = 0
)

@Serializable
data class IntelligenceDomain(
    val id: String,
    val name: String,
    val color: String,
    val description: String = "",
    val icon: String = "Activity"
)

@Serializable
data class AppQueryResult(
    val answer: String = "",
    val app_id: String = "",
    val app_name: String = "",
    val intelligence_lens: String = "all",
    val triplets: List<VideoTriplet> = emptyList(),
    val relevant_segments: List<TranscriptSegment> = emptyList()
)

@Serializable
data class VoiceExtractionResult(
    val keywords: List<String> = emptyList(),
    val suggested_entities: List<String> = emptyList()
)

@Serializable
data class CreateAppPayload(
    val name: String,
    val description: String = "",
    val icon: String = "Briefcase",
    val theme_color: String = "#6366f1",
    val focus_domains: List<String> = listOf("executive", "learning"),
    val video_ids: List<String> = emptyList(),
    val prioritized_entities: List<String> = emptyList()
)

@Serializable
data class VideoIngestPayload(
    val url: String,
    val app_id: String? = null,
    val intelligence_lenses: List<String> = listOf("executive", "thought_leadership", "learning")
)

@Serializable
data class VoiceProcessPayload(
    val title: String,
    val transcript_segments: List<TranscriptSegment>,
    val app_id: String,
    val intelligence_lenses: List<String> = listOf("executive", "thought_leadership")
)

@Serializable
data class VideoTranscriptResponse(
    val video_id: String = "",
    val segment_count: Int = 0,
    val segments: List<TranscriptSegment> = emptyList()
)

@Serializable
data class RawEntity(
    val name: String = "",
    val type: String = "Concept",
    val color: String = "#3b82f6",
    val centrality: Double = 0.5,
    val first_seen: String = "",
    val video_ids: List<String> = emptyList()
)

@Serializable
data class ApiGraphNode(
    val id: String = "",
    val label: String = "",
    val type: String = "Concept",
    val color: String = "#3b82f6",
    val intelligences: List<String> = emptyList(),
    val video_ids: List<String> = emptyList(),
    val degree: Int = 0,
    val centrality: Double = 0.0,
    val is_priority: Boolean = false
)

@Serializable
data class ApiGraphLink(
    val source: String = "",
    val target: String = "",
    val relation: String = "RELATES_TO",
    val weight: Int = 1
)

@Serializable
data class ApiScopedGraphResponse(
    val app_id: String? = null,
    val intelligence_lens: String = "all",
    val nodes: List<ApiGraphNode> = emptyList(),
    val links: List<ApiGraphLink> = emptyList()
)

@Serializable
data class DatabaseRepoStats(
    val entities_count: Int = 0,
    val triplets_count: Int = 0,
    val videos_count: Int = 0,
    val child_apps_count: Int = 0,
    val corpus_segments_count: Int = 0,
    val insights_count: Int = 0
)

@Serializable
data class DatabaseStatusResponse(
    val status: String = "fallback_local",
    val is_connected_to_aura: Boolean = false,
    val active_store: String = "LocalGraphStore",
    val uri: String? = null,
    val user: String? = null,
    val last_error: String? = null,
    val repository_stats: DatabaseRepoStats? = null,
    val notice: String? = null
)

fun ApiGraphNode.toConceptNode(): ConceptNode {
    val cat = when (type.lowercase()) {
        "competency" -> ConceptCategory.CORE_LEADERSHIP
        "strategy" -> ConceptCategory.DECISION_MAKING
        "tactic" -> ConceptCategory.EXECUTION
        "outcome" -> ConceptCategory.SYSTEMS_THINKING
        "tool" -> ConceptCategory.AI_INNOVATION
        "personality" -> ConceptCategory.COMMUNICATION
        else -> ConceptCategory.CORE_LEADERSHIP
    }
    return ConceptNode(
        id = id.ifBlank { label },
        name = label.ifBlank { id },
        category = cat,
        centrality = (centrality / 100.0).coerceIn(0.05, 1.0),
        description = "$type • ${intelligences.joinToString(", ")}",
        videoCount = video_ids.size.coerceAtLeast(1),
        tags = intelligences
    )
}

fun RawEntity.toConceptNode(): ConceptNode {
    val cat = when (type.lowercase()) {
        "competency" -> ConceptCategory.CORE_LEADERSHIP
        "strategy" -> ConceptCategory.DECISION_MAKING
        "tactic" -> ConceptCategory.EXECUTION
        "outcome" -> ConceptCategory.SYSTEMS_THINKING
        "tool" -> ConceptCategory.AI_INNOVATION
        "personality" -> ConceptCategory.COMMUNICATION
        else -> ConceptCategory.CORE_LEADERSHIP
    }
    return ConceptNode(
        id = name,
        name = name,
        category = cat,
        centrality = (centrality / 100.0).coerceIn(0.05, 1.0),
        description = "$type from V-LKG Knowledge Graph",
        videoCount = video_ids.size.coerceAtLeast(1),
        tags = listOf(type)
    )
}

fun ApiGraphLink.toEdgeRelationship(): EdgeRelationship {
    return EdgeRelationship(
        id = "${source}_${relation}_${target}",
        sourceId = source,
        targetId = target,
        type = relation,
        weight = weight.toFloat()
    )
}