import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { Button } from "./ui";

interface Props {
  onClose: () => void;
}

export function MergeAccountPrompt({ onClose }: Props) {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const initData = (window as any).Telegram?.WebApp?.initData ?? "";

  async function handleMerge() {
    if (!email || !password) return;
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/v1/auth/merge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ init_data: initData, email, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Ошибка");
      login(data.access_token, data.user);
      onClose();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Ошибка объединения аккаунтов");
    } finally {
      setLoading(false);
    }
  }

  const inputStyle = {
    border: "0.5px solid rgba(140,110,255,0.2)",
  };

  return (
    <div
      className="fixed inset-0 flex flex-col justify-end"
      style={{ zIndex: 100, background: "rgba(0,0,0,0.75)" }}
      onClick={e => e.target === e.currentTarget && onClose()}
    >
      <div
        className="w-full max-w-[390px] mx-auto rounded-t-2xl px-5 pt-6 pb-10 flex flex-col gap-4"
        style={{ background: "#100d24", border: "0.5px solid rgba(107,78,255,0.2)" }}
      >
        <div className="flex items-center justify-between">
          <p className="font-display text-text-primary text-base">
            Связать с аккаунтом
          </p>
          <button
            onClick={onClose}
            className="text-text-faint text-xl leading-none w-8 h-8 flex items-center justify-center"
          >
            ✕
          </button>
        </div>

        <p className="text-text-muted text-sm leading-relaxed">
          Есть аккаунт с email? Введите данные — и Telegram привяжется к нему автоматически.
        </p>

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          className="w-full px-4 py-3 rounded-xl text-sm bg-bg-surface text-text-primary placeholder-text-muted outline-none"
          style={inputStyle}
        />
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={e => setPassword(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleMerge()}
          className="w-full px-4 py-3 rounded-xl text-sm bg-bg-surface text-text-primary placeholder-text-muted outline-none"
          style={inputStyle}
        />

        {error && (
          <p className="text-red-400 text-xs text-center">{error}</p>
        )}

        <Button variant="primary" className="w-full" onClick={handleMerge} disabled={loading || !email || !password}>
          {loading ? "..." : "Связать аккаунты"}
        </Button>

        <button
          onClick={onClose}
          className="text-text-faint text-xs text-center py-1"
        >
          Пропустить
        </button>
      </div>
    </div>
  );
}
