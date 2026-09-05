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