package org.vlkg.mobile

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import org.vlkg.mobile.theme.*
import org.vlkg.mobile.ui.components.CreateAppDialog
import org.vlkg.mobile.ui.components.EnrichmentsDialog
import org.vlkg.mobile.ui.components.VideoManagerDialog
import org.vlkg.mobile.ui.components.VlkgBottomNav
import org.vlkg.mobile.ui.components.VlkgTopHeader
import org.vlkg.mobile.ui.graph.KnowledgeGraphScreen
import org.vlkg.mobile.ui.hub.AppsHubScreen
import org.vlkg.mobile.ui.library.MediaLibraryScreen
import org.vlkg.mobile.ui.player.VideoPlayerScreen
import org.vlkg.mobile.ui.query.AppQueryScreen
import org.vlkg.mobile.ui.voice.VoiceStudioScreen
import org.vlkg.mobile.ui.words.LinearWordsScreen
import org.vlkg.mobile.viewmodel.AppNavigationTab
import org.vlkg.mobile.viewmodel.VlkgMainViewModel

@Composable
fun App(
    viewModel: VlkgMainViewModel = remember { VlkgMainViewModel() }
) {
    val uiState by viewModel.uiState.collectAsState()

    VlkgTheme(darkTheme = true) {
        Scaffold(
            contentWindowInsets = WindowInsets.safeDrawing,
            topBar = {
                VlkgTopHeader(
                    activeApp = uiState.activeApp,
                    apps = uiState.apps,
                    onSelectApp = { viewModel.selectApp(it) },
                    onCreateAppClick = { viewModel.setCreateAppDialogVisible(true) }
                )
            },
            bottomBar = {
                VlkgBottomNav(
                    activeTab = uiState.activeTab,
                    onTabChange = { viewModel.switchTab(it) }
                )
            }
        ) { paddingValues ->
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .background(DarkBackground)
            ) {
                when (uiState.activeTab) {
                    AppNavigationTab.HUB -> {
                        AppsHubScreen(
                            activeApp = uiState.activeApp,
                            apps = uiState.apps,
                            onSelectApp = { viewModel.selectApp(it) },
                            onNavigateTab = { viewModel.switchTab(it) },
                            onTogglePriority = { viewModel.toggleEntityPriority(it) },
                            onCreateAppClick = { viewModel.setCreateAppDialogVisible(true) },
                            onEditAppClick = { viewModel.setCreateAppDialogVisible(true, it) },
                            onDeleteApp = { viewModel.deleteApp(it) },
                            onOpenVideoManager = { viewModel.setVideoManagerDialogVisible(true) },
                            onOpenEnrichments = { viewModel.setEnrichmentsDialogVisible(true) }
                        )
                    }

                    AppNavigationTab.WORDS -> {
                        LinearWordsScreen(
                            activeApp = uiState.activeApp,
                            viewMode = uiState.linearWordsMode,
                            onSetViewMode = { viewModel.setLinearWordsMode(it) },
                            selectedLens = uiState.selectedLens,
                            onSelectLens = { viewModel.selectLens(it) },
                            onTogglePriority = { viewModel.toggleEntityPriority(it) },
                            onJumpToVideo = { vid, ts -> viewModel.jumpToVideo(vid, ts) }
                        )
                    }

                    AppNavigationTab.GRAPH -> {
                        KnowledgeGraphScreen(
                            activeApp = uiState.activeApp,
                            selectedLens = uiState.selectedLens,
                            onSelectLens = { viewModel.selectLens(it) },
                            onJumpToVideo = { vid, ts -> viewModel.jumpToVideo(vid, ts) }
                        )
                    }

                    AppNavigationTab.PLAYER -> {
                        VideoPlayerScreen(
                            activeApp = uiState.activeApp,
                            allVideos = uiState.allVideos,
                            initialVideoId = uiState.targetVideoId,
                            initialTimestamp = uiState.targetTimestamp
                        )
                    }

                    AppNavigationTab.ASK -> {
                        AppQueryScreen(
                            activeApp = uiState.activeApp,
                            selectedLens = uiState.selectedLens,
                            onJumpToVideo = { vid, ts -> viewModel.jumpToVideo(vid, ts) }
                        )
                    }

                    AppNavigationTab.VOICE -> {
                        VoiceStudioScreen(
                            activeApp = uiState.activeApp,
                            onRecordingSaved = { viewModel.switchTab(AppNavigationTab.HUB) }
                        )
                    }

                    AppNavigationTab.LIBRARY -> {
                        MediaLibraryScreen(
                            allVideos = uiState.allVideos,
                            activeApp = uiState.activeApp,
                            onJumpToVideo = { vid, ts -> viewModel.jumpToVideo(vid, ts) }
                        )
                    }
                }
            }
        }

        // Create / Edit Child App Modal
        CreateAppDialog(
            isOpen = uiState.isCreateAppOpen,
            editingApp = uiState.editingApp,
            onClose = { viewModel.setCreateAppDialogVisible(false) },
            onCreate = { name, desc, color, domains ->
                viewModel.createOrUpdateApp(name, desc, color, domains)
            }
        )

        // Video Manager Dialog
        VideoManagerDialog(
            isOpen = uiState.isVideoManagerOpen,
            onClose = { viewModel.setVideoManagerDialogVisible(false) },
            activeApp = uiState.activeApp,
            allVideos = uiState.allVideos,
            onSave = { selectedVideoIds ->
                uiState.activeApp?.let { app ->
                    viewModel.assignVideosToApp(app.id, selectedVideoIds)
                }
            }
        )

        // Enrichments & Dossier Dialog
        EnrichmentsDialog(
            isOpen = uiState.isEnrichmentsOpen,
            onClose = { viewModel.setEnrichmentsDialogVisible(false) },
            activeApp = uiState.activeApp
        )
    }
}