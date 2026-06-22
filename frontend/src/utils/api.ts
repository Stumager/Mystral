import { parseApiError, parseNetworkError, parseStreamError } from "./errorHandler";

const BASE_URL = import.meta.env.VITE_API_URL || "";

export async function streamRequest(
  endpoint: string,
  body: object,
  onChunk: (text: string) => void,
  onDone: () => void,
  token?: string,
  onError?: (msg: string) => void,
): Promise<void> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let res: Response;
  try {
    res = await fetch(`${BASE_URL}/api/v1${endpoint}`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
  } catch {
    const err = parseNetworkError();
    if (onError) onError(err.message);
    throw { code: "network", message: err.message };
  }

  if (!res.ok) {
    const raw = await res.json().catch(() => ({}));
    const err = parseApiError(res.status, raw);
    if (onError) onError(err.message);
    throw { code: err.code, message: err.message, retryAfter: err.retryAfter };
  }

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split("\n");

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const data = line.slice(6).trim();
      if (data === "[DONE]") {
        onDone();
        return;
      }
      try {
        const parsed = JSON.parse(data);
        const streamErr = parseStreamError(parsed);
        if (streamErr) {
          if (onError) onError(streamErr.message);
          else onChunk(`\n⚠️ ${streamErr.message}`);
          onDone();
          return;
        }
        if (parsed.text) onChunk(parsed.text);
      } catch {
        // skip malformed lines
      }
    }
  }
  onDone();
}

export async function apiRequest<T = unknown>(
  endpoint: string,
  body: object,
  token?: string,
): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let res: Response;
  try {
    res = await fetch(`${BASE_URL}/api/v1${endpoint}`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
  } catch {
    const err = parseNetworkError();
    throw { code: "network", message: err.message };
  }

  if (!res.ok) {
    const raw = await res.json().catch(() => ({}));
    const err = parseApiError(res.status, raw);
    throw { code: err.code, message: err.message, retryAfter: err.retryAfter };
  }

  return res.json();
}
