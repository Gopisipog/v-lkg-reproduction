const API_BASE = "/api";

export async function fetchJson(url, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${url}`, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {})
      },
      ...options
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Request failed with status ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.error(`API Error on ${url}:`, error);
    throw error;
  }
}

// ── Child Apps API ──────────────────────────────────────────────────
export const getApps = () => fetchJson("/apps");
export const getApp = (id) => fetchJson(`/apps/${id}`);
export const createApp = (data) => fetchJson("/apps", { method: "POST", body: JSON.stringify(data) });
export const updateApp = (id, data) => fetchJson(`/apps/${id}`, { method: "PUT", body: JSON.stringify(data) });
export const deleteApp = (id) => fetchJson(`/apps/${id}`, { method: "DELETE" });
export const assignVideosToApp = (appId, videoIds) => 
  fetchJson(`/apps/${appId}/videos/assign`, { method: "POST", body: JSON.stringify({ video_ids: videoIds }) });
export const prioritizeAppEntities = (appId, prioritizedEntities) =>
  fetchJson(`/apps/${appId}/prioritize`, { method: "PUT", body: JSON.stringify({ prioritized_entities: prioritizedEntities }) });

// ── Videos & Intelligences API ──────────────────────────────────────
export const getVideos = () => fetchJson("/videos");
export const getVideoTranscript = (videoId) => fetchJson(`/videos/${videoId}/transcript`);
export const getVideoSemantics = (videoId) => fetchJson(`/videos/${videoId}/semantics`);
export const searchTranscripts = (query, videoId) => {
  const params = new URLSearchParams({ q: query });
  if (videoId) params.append("video_id", videoId);
  return fetchJson(`/transcripts/search?${params.toString()}`);
};
export const updateVideoIntelligences = (videoId, intelligences) =>
  fetchJson(`/videos/${videoId}/intelligence`, { method: "PUT", body: JSON.stringify({ intelligences }) });
export const getIntelligences = () => fetchJson("/intelligences");
export const ingestYouTubeVideo = (url, appId, intelligenceLenses) =>
  fetchJson("/videos/ingest", { method: "POST", body: JSON.stringify({ url, app_id: appId, intelligence_lenses: intelligenceLenses }) });

// ── Scoped Graph & Enrichments API ──────────────────────────────────
export const getAppGraph = (appId, intelligenceLens) => {
  const query = intelligenceLens && intelligenceLens !== "all" ? `?intelligence_lens=${intelligenceLens}` : "";
  return fetchJson(`/apps/${appId}/graph${query}`);
};
export const getGlobalGraph = (intelligenceLens) => {
  const query = intelligenceLens && intelligenceLens !== "all" ? `?intelligence_lens=${intelligenceLens}` : "";
  return fetchJson(`/graph${query}`);
};
export const getAppInsights = (appId) => fetchJson(`/apps/${appId}/insights`);
export const getAppEntities = (appId) => fetchJson(`/apps/${appId}/entities`);

// ── Child App Questioning API ───────────────────────────────────────
export const querySingleApp = (appId, question, intelligenceLens) =>
  fetchJson(`/apps/${appId}/query`, {
    method: "POST",
    body: JSON.stringify({ question, intelligence_lens: intelligenceLens })
  });

export const queryMultiApps = (appIds, question) =>
  fetchJson("/query/multi-app", {
    method: "POST",
    body: JSON.stringify({ app_ids: appIds, question })
  });

// ── Live Voice Recording & Ingestion API ────────────────────────────
export const liveExtractEntities = (text, existingEntities = []) =>
  fetchJson("/voice/live-extract", {
    method: "POST",
    body: JSON.stringify({ text, existing_entities: existingEntities })
  });

export const processVoiceRecording = (title, transcriptSegments, appId, intelligenceLenses) =>
  fetchJson("/voice/process", {
    method: "POST",
    body: JSON.stringify({
      title,
      transcript_segments: transcriptSegments,
      app_id: appId,
      intelligence_lenses: intelligenceLenses
    })
  });
