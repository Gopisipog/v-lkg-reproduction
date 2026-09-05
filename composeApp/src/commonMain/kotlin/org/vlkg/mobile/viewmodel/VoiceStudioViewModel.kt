package org.vlkg.mobile.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import org.vlkg.mobile.network.VlkgApiClient
import kotlin.random.Random

data class VoiceStudioUiState(
    val isRecording: Boolean = false,
    val durationSeconds: Int = 0,
    val waveforms: List<Float> = List(16) { 0.2f },
    val liveTranscript: String = "",
    val extractedKeywords: List<String> = emptyList(),
    val suggestedEntities: List<String> = emptyList(),
    val isProcessing: Boolean = false,
    val savedNoteTitle: String? = null
)

class VoiceStudioViewModel(
    private val apiClient: VlkgApiClient = VlkgApiClient()
) : ViewModel() {

    private val _uiState = MutableStateFlow(VoiceStudioUiState())
    val uiState: StateFlow<VoiceStudioUiState> = _uiState.asStateFlow()

    private var recordJob: Job? = null

    private val sampleSnippets = listOf(
        "Deconstructing the executive decision matrix...",
        "When building autonomous agent workflows, latency and precision are paramount.",
        "A leader establishes psychological safety before enforcing metrics.",
        "First-principles reasoning removes false legacy constraints."
    )

    fun toggleRecording() {
        if (_uiState.value.isRecording) {
            stopRecording()
        } else {
            startRecording()
        }
    }

    private fun startRecording() {
        _uiState.update {
            it.copy(
                isRecording = true,
                durationSeconds = 0,
                liveTranscript = "Listening and transcribing in real-time...",
                savedNoteTitle = null
            )
        }

        recordJob = viewModelScope.launch {
            var seconds = 0
            while (isActive) {
                delay(1000)
                seconds++
                val randomWaves = List(16) { Random.nextFloat().coerceIn(0.2f, 1.0f) }
                val snippet = sampleSnippets[(seconds - 1) % sampleSnippets.size]

                _uiState.update {
                    it.copy(
                        durationSeconds = seconds,
                        waveforms = randomWaves,
                        liveTranscript = "${it.liveTranscript} $snippet"
                    )
                }

                if (seconds % 3 == 0) {
                    val extract = apiClient.liveExtract(_uiState.value.liveTranscript)
                    _uiState.update {
                        it.copy(
                            extractedKeywords = extract.keywords,
                            suggestedEntities = extract.suggested_entities
                        )
                    }
                }
            }
        }
    }

    private fun stopRecording() {
        recordJob?.cancel()
        recordJob = null
        _uiState.update {
            it.copy(
                isRecording = false,
                waveforms = List(16) { 0.15f }
            )
        }
    }

    fun saveRecording(title: String, onSuccess: () -> Unit) {
        viewModelScope.launch {
            _uiState.update { it.copy(isProcessing = true) }
            delay(800)
            _uiState.update {
                it.copy(
                    isProcessing = false,
                    savedNoteTitle = title,
                    liveTranscript = ""
                )
            }
            onSuccess()
        }
    }
}