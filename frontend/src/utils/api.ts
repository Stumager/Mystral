const BASE_URL = import.meta.env.VITE_API_URL || "";

export async function streamRequest(
  endpoint: string,
  body: object,
  onChunk: (text: string) => void,
  onDone: () => void,
  token?: string
): Promise<void> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}/api/v1${endpoint}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  if (res.status === 402) {
    const data = await res.json().catch(() => ({ detail: "FREE_LIMIT_REACHED" }));
    throw { code: data.detail ?? "FREE_LIMIT_REACHED" };
  }

  if (!res.ok) throw new Error(`HTTP ${res.status}`);

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
  token?: string
): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}/api/v1${endpoint}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  if (res.status === 402) {
    const data = await res.json().catch(() => ({ detail: "FREE_LIMIT_REACHED" }));
    throw { code: data.detail ?? "FREE_LIMIT_REACHED" };
  }

  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
