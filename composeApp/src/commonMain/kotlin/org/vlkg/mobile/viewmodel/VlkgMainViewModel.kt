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

enum class AppNavigationTab(val label: String, val icon: String) {
    HUB("Hub", "📱"),
    WORDS("Words", "🏷️"),
    GRAPH("Graph", "🕸️"),
    PLAYER("Player", "▶️"),
    ASK("Ask AI", "✨"),
    VOICE("Voice", "🎙️"),
    LIBRARY("Library", "📚")
}

data class VlkgMainUiState(
    val apps: List<ChildApp> = emptyList(),
    val activeApp: ChildApp? = null,
    val allVideos: List<VideoMetadata> = emptyList(),
    val activeTab: AppNavigationTab = AppNavigationTab.HUB,
    val targetVideoId: String? = null,
    val targetTimestamp: String? = null,
    val selectedLens: String = "all",
    val isCreateAppOpen: Boolean = false,
    val isVideoManagerOpen: Boolean = false,
    val isEnrichmentsOpen: Boolean = false,
    val isPhoneFrame: Boolean = false,
    val linearWordsMode: String = "ladder", // "ladder" | "pathways" | "categories"
    val editingApp: ChildApp? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)

class VlkgMainViewModel(
    private val apiClient: VlkgApiClient = VlkgApiClient()
) : ViewModel() {

    private val _uiState = MutableStateFlow(VlkgMainUiState())
    val uiState: StateFlow<VlkgMainUiState> = _uiState.asStateFlow()

    init {
        loadInitialData()
    }

    fun loadInitialData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val apps = apiClient.getApps()
                val videos = apiClient.getVideos()
                _uiState.update {
                    it.copy(
                        apps = apps,
                        activeApp = apps.firstOrNull(),
                        allVideos = videos,
                        isLoading = false
                    )
                }
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false, error = e.message) }
            }
        }
    }

    fun selectApp(app: ChildApp) {
        _uiState.update { it.copy(activeApp = app) }
    }

    fun switchTab(tab: AppNavigationTab) {
        _uiState.update { it.copy(activeTab = tab) }
    }

    fun jumpToVideo(videoId: String, timestamp: String) {
        _uiState.update {
            it.copy(
                targetVideoId = videoId,
                targetTimestamp = timestamp,
                activeTab = AppNavigationTab.PLAYER
            )
        }
    }

    fun selectLens(lens: String) {
        _uiState.update { it.copy(selectedLens = lens) }
    }

    fun setLinearWordsMode(mode: String) {
        _uiState.update { it.copy(linearWordsMode = mode) }
    }

    fun toggleEntityPriority(entityName: String) {
        val app = _uiState.value.activeApp ?: return
        val current = app.prioritized_entities
        val updated = if (current.contains(entityName)) current - entityName else listOf(entityName) + current
        val newApp = app.copy(prioritized_entities = updated)

        _uiState.update { state ->
            state.copy(
                activeApp = newApp,
                apps = state.apps.map { if (it.id == app.id) newApp else it }
            )
        }

        viewModelScope.launch {
            apiClient.prioritizeEntity(app.id, updated)
        }
    }

    fun setCreateAppDialogVisible(visible: Boolean, appToEdit: ChildApp? = null) {
        _uiState.update { it.copy(isCreateAppOpen = visible, editingApp = appToEdit) }
    }

    fun setVideoManagerDialogVisible(visible: Boolean) {
        _uiState.update { it.copy(isVideoManagerOpen = visible) }
    }

    fun setEnrichmentsDialogVisible(visible: Boolean) {
        _uiState.update { it.copy(isEnrichmentsOpen = visible) }
    }

    fun togglePhoneFrame() {
        _uiState.update { it.copy(isPhoneFrame = !it.isPhoneFrame) }
    }

    fun deleteApp(appId: String) {
        val updated = _uiState.value.apps.filter { it.id != appId }
        _uiState.update { state ->
            state.copy(
                apps = updated,
                activeApp = if (state.activeApp?.id == appId) updated.firstOrNull() else state.activeApp
            )
        }
    }

    fun assignVideosToApp(appId: String, videoIds: List<String>) {
        val app = _uiState.value.apps.firstOrNull { it.id == appId } ?: return
        val updatedApp = app.copy(video_ids = videoIds)
        _uiState.update { state ->
            state.copy(
                apps = state.apps.map { if (it.id == appId) updatedApp else it },
                activeApp = if (state.activeApp?.id == appId) updatedApp else state.activeApp,
                isVideoManagerOpen = false
            )
        }
    }

    fun createOrUpdateApp(name: String, description: String, themeColor: String, domains: List<String>) {
        viewModelScope.launch {
            val editing = _uiState.value.editingApp
            if (editing != null) {
                val updated = editing.copy(
                    name = name,
                    description = description,
                    theme_color = themeColor,
                    focus_domains = domains
                )
                _uiState.update { state ->
                    state.copy(
                        apps = state.apps.map { if (it.id == editing.id) updated else it },
                        activeApp = if (state.activeApp?.id == editing.id) updated else state.activeApp,
                        isCreateAppOpen = false,
                        editingApp = null
                    )
                }
            } else {
                val payload = CreateAppPayload(
                    name = name,
                    description = description,
                    theme_color = themeColor,
                    focus_domains = domains
                )
                val created = apiClient.createApp(payload) ?: ChildApp(
                    id = "app_${System.currentTimeMillis()}",
                    name = name,
                    description = description,
                    theme_color = themeColor,
                    focus_domains = domains
                )
                _uiState.update {
                    it.copy(
                        apps = it.apps + created,
                        activeApp = created,
                        isCreateAppOpen = false
                    )
                }
            }
        }
    }
}