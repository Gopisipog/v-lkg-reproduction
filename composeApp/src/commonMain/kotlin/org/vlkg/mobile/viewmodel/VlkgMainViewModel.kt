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

enum class AppNavigationTab(val label: String, val code: String) {
    HUB("Hub", "HUB"),
    WORDS("Words", "WRD"),
    PLAYER("Player", "PLY"),
    ASK("Query", "QRY"),
    VOICE("Voice", "MIC"),
    LIBRARY("Library", "LIB")
}

data class VlkgMainUiState(
    val apps: List<ChildApp> = emptyList(),
    val activeApp: ChildApp? = null,
    val allVideos: List<VideoMetadata> = emptyList(),
    val entities: List<ConceptNode> = emptyList(),
    val databaseStatus: DatabaseStatusResponse? = null,
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
                val status = apiClient.getDatabaseStatus()
                val active = apps.firstOrNull()
                val ents = if (active != null) apiClient.getScopedEntities(active.id) else apiClient.getAllEntities()
                
                _uiState.update {
                    it.copy(
                        apps = apps,
                        activeApp = active,
                        allVideos = videos,
                        entities = ents,
                        databaseStatus = status,
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
        viewModelScope.launch {
            val scopedEnts = apiClient.getScopedEntities(app.id)
            _uiState.update { it.copy(entities = scopedEnts) }
        }
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

    fun addVideoToActiveApp(videoId: String) {
        val app = _uiState.value.activeApp ?: return
        if (app.video_ids.contains(videoId)) return

        val updatedIds = app.video_ids + videoId
        val newApp = app.copy(video_ids = updatedIds)

        _uiState.update { state ->
            state.copy(
                activeApp = newApp,
                apps = state.apps.map { if (it.id == app.id) newApp else it }
            )
        }

        viewModelScope.launch {
            assignVideosToApp(app.id, updatedIds)
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

    fun createOrUpdateApp(
        name: String,
        description: String,
        colorScheme: String = "cyber-cyan",
        pattern: String = "gradient-bi",
        patternColors: List<String> = listOf("#0EA5E9", "#10B981"),
        domains: List<String> = listOf("executive", "learning"),
        saveToAura: Boolean = true
    ) {
        viewModelScope.launch {
            val editing = _uiState.value.editingApp
            val primaryColor = patternColors.firstOrNull() ?: "#0EA5E9"
            if (editing != null) {
                val updated = editing.copy(
                    name = name,
                    description = description,
                    theme_color = primaryColor,
                    color_scheme = colorScheme,
                    pattern = pattern,
                    pattern_colors = patternColors,
                    focus_domains = domains,
                    saved_to_aura = saveToAura
                )
                val payload = CreateAppPayload(
                    name = name,
                    description = description,
                    theme_color = primaryColor,
                    color_scheme = colorScheme,
                    pattern = pattern,
                    pattern_colors = patternColors,
                    focus_domains = domains,
                    video_ids = editing.video_ids,
                    prioritized_entities = editing.prioritized_entities,
                    save_to_aura = saveToAura
                )
                apiClient.updateApp(editing.id, payload)
                if (saveToAura) {
                    apiClient.saveChildAppToAura(editing.id)
                }
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
                    theme_color = primaryColor,
                    color_scheme = colorScheme,
                    pattern = pattern,
                    pattern_colors = patternColors,
                    focus_domains = domains,
                    save_to_aura = saveToAura
                )
                val created = apiClient.createApp(payload) ?: ChildApp(
                    id = "app_${System.currentTimeMillis()}",
                    name = name,
                    description = description,
                    theme_color = primaryColor,
                    color_scheme = colorScheme,
                    pattern = pattern,
                    pattern_colors = patternColors,
                    focus_domains = domains,
                    saved_to_aura = saveToAura
                )
                if (saveToAura) {
                    apiClient.saveChildAppToAura(created.id)
                }
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

    fun updateAppScheme(
        appId: String,
        colorScheme: String,
        pattern: String,
        patternColors: List<String>
    ) {
        viewModelScope.launch {
            val target = _uiState.value.apps.find { it.id == appId } ?: _uiState.value.activeApp ?: return@launch
            val primaryColor = patternColors.firstOrNull() ?: target.theme_color
            val updated = target.copy(
                theme_color = primaryColor,
                color_scheme = colorScheme,
                pattern = pattern,
                pattern_colors = patternColors
            )
            _uiState.update { state ->
                state.copy(
                    apps = state.apps.map { if (it.id == target.id) updated else it },
                    activeApp = if (state.activeApp?.id == target.id) updated else state.activeApp
                )
            }
            val payload = CreateAppPayload(
                name = updated.name,
                description = updated.description,
                theme_color = primaryColor,
                color_scheme = colorScheme,
                pattern = pattern,
                pattern_colors = patternColors,
                focus_domains = updated.focus_domains,
                video_ids = updated.video_ids,
                prioritized_entities = updated.prioritized_entities,
                save_to_aura = updated.saved_to_aura
            )
            apiClient.updateApp(target.id, payload)
            if (updated.saved_to_aura) {
                apiClient.saveChildAppToAura(target.id)
            }
        }
    }

    fun saveAppToAura(appId: String) {
        viewModelScope.launch {
            val ok = apiClient.saveChildAppToAura(appId)
            _uiState.update { state ->
                state.copy(
                    apps = state.apps.map { 
                        if (it.id == appId) it.copy(saved_to_aura = true, aura_message = if (ok) "Synced to Aura DB" else "Queued in LocalStore") else it 
                    },
                    activeApp = if (state.activeApp?.id == appId) {
                        state.activeApp.copy(saved_to_aura = true, aura_message = if (ok) "Synced to Aura DB" else "Queued in LocalStore")
                    } else state.activeApp
                )
            }
        }
    }
}