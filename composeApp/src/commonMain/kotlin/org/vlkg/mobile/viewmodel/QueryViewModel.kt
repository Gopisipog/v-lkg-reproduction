package org.vlkg.mobile.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import org.vlkg.mobile.model.AppQueryResult
import org.vlkg.mobile.network.VlkgApiClient

data class ChatMessage(
    val id: String,
    val sender: String, // "user" | "ai"
    val text: String,
    val result: AppQueryResult? = null,
    val multiResult: org.vlkg.mobile.model.MultiAppQueryResponse? = null,
    val timestamp: String = ""
)

data class QueryUiState(
    val messages: List<ChatMessage> = listOf(
        ChatMessage(
            id = "msg_init",
            sender = "ai",
            text = "Hello! Ask me any question grounded in your child app's video knowledge graph, transcripts, and mined triplets.",
            timestamp = "Now"
        )
    ),
    val currentQuestion: String = "",
    val queryMode: String = "single", // "single" | "multi"
    val selectedAppIds: List<String> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

class QueryViewModel(
    private val apiClient: VlkgApiClient = VlkgApiClient()
) : ViewModel() {

    private val _uiState = MutableStateFlow(QueryUiState())
    val uiState: StateFlow<QueryUiState> = _uiState.asStateFlow()

    fun updateQuestion(q: String) {
        _uiState.update { it.copy(currentQuestion = q) }
    }

    fun setQueryMode(mode: String) {
        _uiState.update { it.copy(queryMode = mode) }
    }

    fun toggleAppSelection(appId: String) {
        _uiState.update { state ->
            val current = state.selectedAppIds
            val updated = if (current.contains(appId)) {
                if (current.size > 1) current - appId else current
            } else {
                current + appId
            }
            state.copy(selectedAppIds = updated)
        }
    }

    fun askMultiAppQuestion(appIds: List<String>, question: String) {
        if (question.isBlank() || appIds.isEmpty()) return

        val userMsg = ChatMessage(
            id = "user_${System.currentTimeMillis()}",
            sender = "user",
            text = question
        )

        _uiState.update {
            it.copy(
                messages = it.messages + userMsg,
                currentQuestion = "",
                isLoading = true,
                error = null
            )
        }

        viewModelScope.launch {
            try {
                val res = apiClient.queryMultiApps(appIds, question)
                val aiMsg = ChatMessage(
                    id = "ai_${System.currentTimeMillis()}",
                    sender = "ai",
                    text = res?.consolidated_answer ?: "No comparison generated.",
                    multiResult = res
                )
                _uiState.update {
                    it.copy(
                        messages = it.messages + aiMsg,
                        isLoading = false
                    )
                }
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false, error = e.message) }
            }
        }
    }

    fun askQuestion(appId: String, question: String, lens: String? = null) {
        if (question.isBlank()) return

        val userMsg = ChatMessage(
            id = "user_${System.currentTimeMillis()}",
            sender = "user",
            text = question
        )

        _uiState.update {
            it.copy(
                messages = it.messages + userMsg,
                currentQuestion = "",
                isLoading = true,
                error = null
            )
        }

        viewModelScope.launch {
            try {
                val res = apiClient.queryApp(appId, question, lens)
                val aiMsg = ChatMessage(
                    id = "ai_${System.currentTimeMillis()}",
                    sender = "ai",
                    text = res.answer,
                    result = res
                )
                _uiState.update {
                    it.copy(
                        messages = it.messages + aiMsg,
                        isLoading = false
                    )
                }
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false, error = e.message) }
            }
        }
    }
}