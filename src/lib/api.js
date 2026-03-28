const RENDER_BACKEND_FALLBACK = "https://voxai-backend-w30b.onrender.com";

const API_BASE_CANDIDATES = [
  import.meta.env.VITE_API_BASE_URL,
  import.meta.env.VITE_API_URL,
  typeof window !== "undefined" && window.location.hostname.endsWith(".onrender.com")
    ? RENDER_BACKEND_FALLBACK
    : null,
  "http://localhost:8000",
]
  .filter(Boolean)
  .map((base) => base.replace(/\/$/, ""));

const API_BASE = API_BASE_CANDIDATES[0];
const API_PREFIXES = ["/api/v1", "/api/v1/api", "/api"];

async function parseJsonResponse(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data.detail || data.message || "Request failed";
    throw new Error(message);
  }
  return data;
}

async function fetchWithPrefixFallback(path, options = {}) {
  let lastResponse = null;
  let lastError = null;

  for (const base of API_BASE_CANDIDATES) {
    for (const prefix of API_PREFIXES) {
      try {
        const response = await fetch(`${base}${prefix}${path}`, options);
        if (response.status === 404) {
          lastResponse = response;
          continue;
        }
        return response;
      } catch (error) {
        lastError = error;
      }
    }
  }

  if (lastError) throw lastError;
  return lastResponse;
}

export async function queryAssistant(query, modelRouting = null) {
  const res = await fetchWithPrefixFallback(`/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, model_routing: modelRouting || undefined }),
  });
  if (!res) throw new Error("Unable to reach backend API");
  return parseJsonResponse(res);
}

export async function uploadPdf(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetchWithPrefixFallback(`/upload-pdf`, {
    method: "POST",
    body: formData,
  });
  if (!res) throw new Error("Unable to reach backend API");
  return parseJsonResponse(res);
}

export async function createQuiz(topic, modelRouting = null) {
  const res = await fetchWithPrefixFallback(`/quiz`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, model_routing: modelRouting || undefined }),
  });
  if (!res) throw new Error("Unable to reach backend API");
  return parseJsonResponse(res);
}

export async function getTtsAudio(text, options = {}) {
  const { model, voice } = options;
  const res = await fetchWithPrefixFallback(`/tts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, model, voice }),
  });
  if (!res) throw new Error("Unable to reach backend API");
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "TTS failed");
  }
  return res.blob();
}

export async function transcribeAudio(file, options = {}) {
  const formData = new FormData();
  formData.append("file", file);
  if (options.model) formData.append("model", options.model);

  const res = await fetchWithPrefixFallback(`/stt`, {
    method: "POST",
    body: formData,
  });
  if (!res) throw new Error("Unable to reach backend API");
  return parseJsonResponse(res);
}
