import { parseApiError, parseNetworkError, parseStreamError } from "./errorHandler";

const BASE_URL = import.meta.env.VITE_API_URL || "";

// Keep ASCII, Latin-1 Supplement + Latin Extended-A/B (ES/PT accents, Turkish
// ĞğİıŞşÇçÖöÜü, Spanish ¡¿ñ), Cyrillic (RU/UK), and the app's typographic +
// zodiac glyphs. Previously only ASCII + Cyrillic survived, so every Latin
// diacritic was silently stripped from streamed AI text (não→no, için→iin,
// gün→gn) for ES/PT/TR. Mirrors the backend allow-list in groq_client._clean_chunk.
const cleanChunk = (text: string) =>
  text.replace(/[^\x00-\x7f -ɏЀ-ӿ\s«»„""'–—…°%№♈-♓☽✦★]/g, "");

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
  // Buffer across reads: a multi-byte UTF-8 char (any accented Latin/Cyrillic
  // glyph) or a whole SSE line can be split across two network chunks.
  // decode({stream:true}) holds an incomplete byte sequence until its
  // continuation arrives — without it, split diacritics decoded to � and
  // corrupted PT/TR mid-word. `buffer` does the same at the line level.
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

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
        if (parsed.text) {
          const cleaned = cleanChunk(parsed.text);
          if (cleaned) onChunk(cleaned);
        }
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

export async function applyStoredReferralCode(token: string): Promise<void> {
  const code = localStorage.getItem("mystral_ref_code");
  if (!code) return;
  try {
    await apiRequest("/referrals/apply", { ref_code: code }, token);
  } catch {
    // best-effort: invalid/self-refer/already-applied/rate-limited — never block login
  } finally {
    localStorage.removeItem("mystral_ref_code");
  }
}

export async function apiGet<T = unknown>(
  endpoint: string,
  token?: string,
): Promise<T> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let res: Response;
  try {
    res = await fetch(`${BASE_URL}/api/v1${endpoint}`, { method: "GET", headers });
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
