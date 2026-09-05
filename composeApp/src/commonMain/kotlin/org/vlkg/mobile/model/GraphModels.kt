package org.vlkg.mobile.model

import kotlinx.serialization.Serializable

@Serializable
enum class ConceptCategory {
    CORE_LEADERSHIP,
    DECISION_MAKING,
    SYSTEMS_THINKING,
    EXECUTION,
    AI_INNOVATION,
    COMMUNICATION
}

@Serializable
data class ConceptNode(
    val id: String,
    val name: String,
    val category: ConceptCategory = ConceptCategory.CORE_LEADERSHIP,
    val centrality: Double = 0.5,
    val description: String = "",
    val videoCount: Int = 1,
    val tags: List<String> = emptyList(),
    var x: Float = 0f,
    var y: Float = 0f,
    var vx: Float = 0f,
    var vy: Float = 0f
)

@Serializable
data class EdgeRelationship(
    val id: String,
    val sourceId: String,
    val targetId: String,
    val type: String, // "PREREQUISITE_OF", "INFLUENCES", "REINFORCES"
    val weight: Float = 1.0f
)

@Serializable
data class VideoTriplet(
    val id: String,
    val subject: String,
    val predicate: String,
    val `object`: String,
    val videoId: String,
    val videoTitle: String,
    val timestampSeconds: Int,
    val timestampFormatted: String,
    val confidence: Double = 0.95,
    val transcriptSnippet: String = "",
    val ocrSlideText: String = "",
    val youtubeUrl: String = ""
)

@Serializable
data class LearningPathway(
    val id: String,
    val title: String,
    val targetRole: String,
    val description: String,
    val steps: List<ConceptNode>,
    val estimatedDurationHours: Double,
    val completedStepsCount: Int = 0
)

@Serializable
data class GraphDataResponse(
    val nodes: List<ConceptNode>,
    val edges: List<EdgeRelationship>,
    val timestamp: String = ""
)
