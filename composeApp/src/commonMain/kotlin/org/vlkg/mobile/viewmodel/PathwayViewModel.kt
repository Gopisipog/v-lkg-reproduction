package org.vlkg.mobile.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import org.vlkg.mobile.model.LearningPathway
import org.vlkg.mobile.network.VlkgApiClient

data class PathwayUiState(
    val pathways: List<LearningPathway> = emptyList(),
    val selectedPathway: LearningPathway? = null,
    val completedStepIds: Set<String> = emptySet(),
    val isLoading: Boolean = false,
    val error: String? = null
)

class PathwayViewModel(
    private val apiClient: VlkgApiClient = VlkgApiClient()
) : ViewModel() {

    private val _uiState = MutableStateFlow(PathwayUiState())
    val uiState: StateFlow<PathwayUiState> = _uiState.asStateFlow()

    init {
        loadPathways()
    }

    fun loadPathways() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                val list = apiClient.getPathways()
                _uiState.update {
                    it.copy(
                        pathways = list,
                        selectedPathway = list.firstOrNull(),
                        completedStepIds = setOf("1"), // First step pre-mastered
                        isLoading = false
                    )
                }
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false, error = e.message) }
            }
        }
    }

    fun selectPathway(pathway: LearningPathway) {
        _uiState.update { it.copy(selectedPathway = pathway) }
    }

    fun toggleStepMastery(stepId: String) {
        _uiState.update { state ->
            val updated = if (state.completedStepIds.contains(stepId)) {
                state.completedStepIds - stepId
            } else {
                state.completedStepIds + stepId
            }
            state.copy(completedStepIds = updated)
        }
    }
}
