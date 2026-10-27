const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeout || 30000);
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      signal: controller.signal,
      headers: options.body instanceof FormData
        ? options.headers
        : { "Content-Type": "application/json", ...options.headers },
    });
    const body = await response.json().catch(() => null);
    if (!response.ok) {
      const detail = body?.detail || `Request failed (${response.status})`;
      throw new Error(detail);
    }
    return body;
  } catch (error) {
    if (error.name === "AbortError") throw new Error("The request timed out.");
    if (error instanceof TypeError) {
      throw new Error("The backend is unavailable. Check that FastAPI is running.");
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

export const api = {
  health: () => request("/health", { timeout: 8000 }),
  documents: () => request("/documents"),
  page: (id, number) => request(`/documents/${id}/pages/${number}`),
  chunks: (id) => request(`/documents/${id}/chunks`),
  chunk: (id) => request(`/documents/${id}/chunk`, { method: "POST" }),
  embed: (id) => request(`/documents/${id}/embed`, { method: "POST", timeout: 120000 }),
  upload: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/documents/upload", { method: "POST", body: form, timeout: 120000 });
  },
  ask: (question, topK = 5) => request("/rag/ask", {
    method: "POST",
    body: JSON.stringify({ question, top_k: topK }),
    timeout: 120000,
  }),
  conversations: () => request("/conversations"),
  financials: (ticker, date) => request(`/financial/${encodeURIComponent(ticker)}${date ? `?date=${date}` : ""}`),
  compare: (ticker, start, end) => request(`/financial/${encodeURIComponent(ticker)}/compare?start_date=${start}&end_date=${end}`),
};

export { API_BASE_URL };
