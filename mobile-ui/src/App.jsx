import React, { useState, useEffect } from "react";
import { 
  getApps, createApp, updateApp, deleteApp, assignVideosToApp, getVideos, prioritizeAppEntities 
} from "./services/api";

import TopHeader from "./components/TopHeader";
import BottomNav from "./components/BottomNav";
import AppsHubView from "./components/AppsHubView";
import LinearWordsView from "./components/LinearWordsView";
import VideoPlayerView from "./components/VideoPlayerView";
import VoiceStudioView from "./components/VoiceStudioView";
import AppQueryView from "./components/AppQueryView";
import MediaLibraryView from "./components/MediaLibraryView";
import CreateAppModal from "./components/CreateAppModal";
import VideoManagerModal from "./components/VideoManagerModal";
import EnrichmentsModal from "./components/EnrichmentsModal";

export default function App() {
  const [apps, setApps] = useState([]);
  const [activeApp, setActiveApp] = useState(null);
  const [allVideos, setAllVideos] = useState([]);
  const [activeTab, setActiveTab] = useState("hub"); // "hub" | "words" | "player" | "voice" | "ask" | "library"

  // Video player jump state
  const [targetVideoId, setTargetVideoId] = useState(null);
  const [targetTimestamp, setTargetTimestamp] = useState(null);

  // Modals state
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editingApp, setEditingApp] = useState(null);
  const [videoManagerOpen, setVideoManagerOpen] = useState(false);
  const [enrichmentsOpen, setEnrichmentsOpen] = useState(false);

  // Frame preview mode
  const [isPhoneFrame, setIsPhoneFrame] = useState(false);

  // Load initial data
  const refreshAll = async () => {
    try {
      const [appsData, videosData] = await Promise.all([getApps(), getVideos()]);
      setApps(appsData);
      setAllVideos(videosData);

      if (!activeApp && appsData.length > 0) {
        setActiveApp(appsData[0]);
      } else if (activeApp) {
        const updated = appsData.find((a) => a.id === activeApp.id);
        if (updated) setActiveApp(updated);
      }
    } catch (err) {
      console.error("Initial load error:", err);
    }
  };

  useEffect(() => {
    refreshAll();
  }, []);

  const handleSaveApp = async (appData) => {
    if (editingApp) {
      const updated = await updateApp(editingApp.id, appData);
      setEditingApp(null);
      await refreshAll();
      setActiveApp(updated);
    } else {
      const created = await createApp(appData);
      await refreshAll();
      setActiveApp(created);
    }
  };

  const handleDeleteApp = async (appId) => {
    await deleteApp(appId);
    const updatedApps = apps.filter((a) => a.id !== appId);
    setApps(updatedApps);
    if (activeApp?.id === appId) {
      setActiveApp(updatedApps[0] || null);
    }
  };

  const handleSaveAssignedVideos = async (appId, videoIds) => {
    const updated = await assignVideosToApp(appId, videoIds);
    await refreshAll();
    setActiveApp(updated);
  };

  const handleToggleEntityPriority = async (appId, entityName) => {
    const target = apps.find((a) => a.id === appId) || activeApp;
    if (!target) return;
    const current = target.prioritized_entities || [];
    const updated = current.includes(entityName)
      ? current.filter((e) => e !== entityName)
      : [entityName, ...current];
    try {
      const res = await prioritizeAppEntities(appId, updated);
      await refreshAll();
      if (activeApp?.id === appId && res) {
        setActiveApp(res);
      }
    } catch (err) {
      console.error("Failed to prioritize entity:", err);
    }
  };

  const handleJumpToVideo = (videoId, timestamp) => {
    setTargetVideoId(videoId);
    setTargetTimestamp(timestamp);
    setActiveTab("player");
  };

  return (
    <div className={`min-h-screen bg-slate-950 text-slate-100 flex justify-center ${isPhoneFrame ? "items-center p-4 sm:p-8" : ""}`}>
      <div 
        className={`w-full flex flex-col bg-slate-950 ${
          isPhoneFrame 
            ? "max-w-[420px] h-[860px] max-h-[92vh] rounded-[42px] border-[8px] border-slate-800 shadow-[0_25px_60px_rgba(0,0,0,0.8)] relative overflow-hidden" 
            : "h-screen h-[100dvh] overflow-hidden"
        }`}
      >
        {/* Top Header */}
        <TopHeader
          activeApp={activeApp}
          apps={apps}
          onSelectApp={(app) => setActiveApp(app)}
          onCreateAppClick={() => {
            setEditingApp(null);
            setCreateModalOpen(true);
          }}
          onManageVideosClick={() => setVideoManagerOpen(true)}
          isPhoneFrame={isPhoneFrame}
          onToggleFrame={() => setIsPhoneFrame(!isPhoneFrame)}
        />

        {/* Main Content Body */}
        <main className="flex-1 overflow-y-auto">
          {activeTab === "hub" && (
            <AppsHubView
              apps={apps}
              activeApp={activeApp}
              onSelectApp={(app) => setActiveApp(app)}
              onCreateAppClick={() => {
                setEditingApp(null);
                setCreateModalOpen(true);
              }}
              onEditAppClick={(app) => {
                setEditingApp(app);
                setCreateModalOpen(true);
              }}
              onDeleteApp={handleDeleteApp}
              onManageVideosClick={() => setVideoManagerOpen(true)}
              onOpenEnrichments={() => setEnrichmentsOpen(true)}
              onNavigateTab={(tab) => setActiveTab(tab === "graph" ? "words" : tab)}
              onToggleEntityPriority={handleToggleEntityPriority}
            />
          )}

          {activeTab === "words" && (
            <LinearWordsView
              activeApp={activeApp}
              onJumpToVideo={handleJumpToVideo}
              onToggleEntityPriority={(entityName) => activeApp && handleToggleEntityPriority(activeApp.id, entityName)}
            />
          )}

          {activeTab === "player" && (
            <VideoPlayerView
              activeApp={activeApp}
              allVideos={allVideos}
              targetVideoId={targetVideoId}
              targetTimestamp={targetTimestamp}
            />
          )}

          {activeTab === "voice" && (
            <VoiceStudioView
              activeApp={activeApp}
              onRecordingSaved={() => {
                refreshAll();
                setActiveTab("words");
              }}
            />
          )}

          {activeTab === "ask" && (
            <AppQueryView
              activeApp={activeApp}
              apps={apps}
              onJumpToVideo={handleJumpToVideo}
            />
          )}

          {activeTab === "library" && (
            <MediaLibraryView
              allVideos={allVideos}
              apps={apps}
              activeApp={activeApp}
              onRefreshVideos={refreshAll}
              onJumpToVideo={handleJumpToVideo}
            />
          )}
        </main>

        {/* Bottom Navigation */}
        <BottomNav
          activeTab={activeTab}
          onTabChange={(tab) => setActiveTab(tab)}
          activeApp={activeApp}
          isPhoneFrame={isPhoneFrame}
        />

        {/* Modals */}
        <CreateAppModal
          isOpen={createModalOpen}
          onClose={() => setCreateModalOpen(false)}
          onSave={handleSaveApp}
          editingApp={editingApp}
        />

        <VideoManagerModal
          isOpen={videoManagerOpen}
          onClose={() => setVideoManagerOpen(false)}
          activeApp={activeApp}
          allVideos={allVideos}
          onSaveAssignedVideos={handleSaveAssignedVideos}
          onRefreshVideos={refreshAll}
        />

        <EnrichmentsModal
          isOpen={enrichmentsOpen}
          onClose={() => setEnrichmentsOpen(false)}
          activeApp={activeApp}
        />
      </div>
    </div>
  );
}
