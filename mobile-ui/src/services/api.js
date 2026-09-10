import { 
  FALLBACK_APPS, 
  FALLBACK_VIDEOS, 
  FALLBACK_ENTITIES, 
  FALLBACK_TRIPLETS, 
  FALLBACK_INSIGHTS 
} from "./fallbackData";

const API_BASE = "/api";

export async function fetchJson(url, options = {}) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);
    const res = await fetch(`${API_BASE}${url}`, {
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {})
      },
      ...options
    });
    clearTimeout(timeoutId);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Request failed with status ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    if (options.method && options.method.toUpperCase() !== "GET") {
      throw error;
    }
    console.warn(`[V-LKG API Offline/Fallback] ${url}:`, error.message);
    return getOfflineFallback(url, options);
  }
}

function getOfflineFallback(url, options) {
  if (url === "/database/status") {
    return {
      status: "fallback_local",
      is_connected_to_aura: false,
      active_store: "LocalGraphStore (JSON Storage)",
      uri: "neo4j+s://60634b9c.databases.neo4j.io",
      user: "60634b9c",
      last_error: null,
      aura_stats: { nodes: null, relationships: null, labels: [] },
      repository_stats: {
        entities_count: FALLBACK_ENTITIES.length,
        triplets_count: FALLBACK_TRIPLETS.length,
        videos_count: FALLBACK_VIDEOS.length,
        child_apps_count: FALLBACK_APPS.length,
        corpus_segments_count: 50,
        insights_count: FALLBACK_INSIGHTS.length
      },
      notice: "Operating in local JSON storage mode."
    };
  }
  if (url === "/apps") return FALLBACK_APPS;
  if (url.startsWith("/apps/") && url.endsWith("/graph")) {
    return {
      nodes: FALLBACK_ENTITIES.slice(0, 30).map(e => ({ id: e.name, name: e.name, type: e.type, color: e.color || "#0ea5e9" })),
      links: FALLBACK_TRIPLETS.slice(0, 45).map(t => ({ source: t.subject, target: t.object, relation: t.relation, weight: 1 }))
    };
  }
  if (url.startsWith("/apps/") && url.endsWith("/insights")) {
    return FALLBACK_INSIGHTS[0] || {
      total_nodes: FALLBACK_ENTITIES.length,
      total_links: FALLBACK_TRIPLETS.length,
      top_central_entities: FALLBACK_ENTITIES.slice(0, 6).map((e, idx) => ({ id: e.name, label: e.name, type: e.type, centrality: 90 - idx * 5 })),
      dependency_chains: FALLBACK_TRIPLETS.slice(0, 5).map(t => ({ source: t.subject, target: t.object, relation: t.relation }))
    };
  }
  if (url.startsWith("/apps/") && url.endsWith("/entities")) {
    return FALLBACK_ENTITIES.slice(0, 35);
  }
  if (url.startsWith("/apps/")) {
    const id = url.split("/")[2];
    return FALLBACK_APPS.find(a => a.id === id) || FALLBACK_APPS[0];
  }
  if (url === "/videos") return FALLBACK_VIDEOS;
  if (url === "/entities") return FALLBACK_ENTITIES;
  if (url === "/graph") {
    return {
      nodes: FALLBACK_ENTITIES.slice(0, 40).map(e => ({ id: e.name, name: e.name, type: e.type, color: e.color || "#0ea5e9" })),
      links: FALLBACK_TRIPLETS.slice(0, 60).map(t => ({ source: t.subject, target: t.object, relation: t.relation, weight: 1 }))
    };
  }
  if (url.startsWith("/videos/") && url.endsWith("/transcript")) {
    return {
      video_id: "test",
      segments: [
        { timestamp: "00:00", text: "Welcome to the executive leadership knowledge graph session." },
        { timestamp: "00:14", text: "Today we focus on high agency systems and first principles thinking." },
        { timestamp: "00:32", text: "When teams align around clear boundary setting, execution velocity multiplies." }
      ]
    };
  }
  if (url === "/voice/live-extract") {
    return [
      { name: "First-Principles Thinking", type: "Framework", detected_at: "00:04", color: "#0ea5e9", intelligences: ["executive", "learning"] },
      { name: "Executive Presence", type: "Competency", detected_at: "00:08", color: "#10b981", intelligences: ["thought_leadership"] }
    ];
  }
  return [];
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
export const saveAppToAura = (appId) => 
  fetchJson(`/apps/${appId}/save-to-aura`, { method: "POST" });
export const getDatabaseStatus = () => 
  fetchJson("/database/status");
export const connectDatabase = (creds) => 
  fetchJson("/database/connect", { method: "POST", body: JSON.stringify(creds) });
export const syncDataToAura = () => 
  fetchJson("/database/sync-to-aura", { method: "POST" });

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
