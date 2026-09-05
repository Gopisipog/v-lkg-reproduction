package org.vlkg.mobile.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import org.vlkg.mobile.model.*
import org.vlkg.mobile.network.VlkgApiClient

data class GraphUiState(
    val nodes: List<ConceptNode> = emptyList(),
    val edges: List<EdgeRelationship> = emptyList(),
    val selectedNode: ConceptNode? = null,
    val selectedNodeEvidence: List<VideoTriplet> = emptyList(),
    val searchQuery: String = "",
    val scale: Float = 1.0f,
    val offsetX: Float = 0f,
    val offsetY: Float = 0f,
    val isLoading: Boolean = false,
    val error: String? = null
)

class GraphViewModel(
    private val apiClient: VlkgApiClient = VlkgApiClient()
) : ViewModel() {

    private val _uiState = MutableStateFlow(GraphUiState())
    val uiState: StateFlow<GraphUiState> = _uiState.asStateFlow()

    init {
        loadGraph()
    }

    fun loadGraph() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                val data = apiClient.getGraphData()
                _uiState.update {
                    it.copy(
                        nodes = data.nodes,
                        edges = data.edges,
                        selectedNode = data.nodes.firstOrNull(),
                        isLoading = false
                    )
                }
                data.nodes.firstOrNull()?.let { firstNode ->
                    loadEvidence(firstNode.id)
                }
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false, error = e.message) }
            }
        }
    }

    fun selectNode(node: ConceptNode) {
        _uiState.update { it.copy(selectedNode = node) }
        loadEvidence(node.id)
    }

    fun search(query: String) {
        _uiState.update { it.copy(searchQuery = query) }
    }

    fun pan(dx: Float, dy: Float) {
        _uiState.update {
            it.copy(
                offsetX = it.offsetX + dx,
                offsetY = it.offsetY + dy
            )
        }
    }

    fun zoom(zoomMultiplier: Float) {
        _uiState.update {
            val newScale = (it.scale * zoomMultiplier).coerceIn(0.5f, 3.0f)
            it.copy(scale = newScale)
        }
    }

    fun resetView() {
        _uiState.update { it.copy(scale = 1.0f, offsetX = 0f, offsetY = 0f) }
    }

    private fun loadEvidence(nodeId: String) {
        viewModelScope.launch {
            try {
                val evidence = apiClient.getNodeEvidence(nodeId)
                _uiState.update { it.copy(selectedNodeEvidence = evidence) }
            } catch (_: Exception) {
                // Keep existing or fallback
            }
        }
    }
}
