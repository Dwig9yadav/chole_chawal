const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
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

  for (const prefix of API_PREFIXES) {
    try {
      const response = await fetch(`${API_BASE}${prefix}${path}`, options);
      if (response.status === 404) {
        lastResponse = response;
        continue;
      }
      return response;
    } catch (error) {
      lastError = error;
    }
  }

  if (lastError) throw lastError;
  return lastResponse;
}

export async function queryAssistant(query) {
  const res = await fetchWithPrefixFallback(`/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
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

export async function createQuiz(topic) {
  const res = await fetchWithPrefixFallback(`/quiz`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic }),
  });
  if (!res) throw new Error("Unable to reach backend API");
  return parseJsonResponse(res);
}

export async function getTtsAudio(text) {
  const res = await fetchWithPrefixFallback(`/tts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res) throw new Error("Unable to reach backend API");
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "TTS failed");
  }
  return res.blob();
}
