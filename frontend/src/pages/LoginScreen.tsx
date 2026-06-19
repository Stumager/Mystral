import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { Button } from "../components/ui";

type Mode = "login" | "register";

const BOT_ID = "8998390466";

export function LoginScreen() {
  const { login } = useAuth();
  const [mode, setMode] = useState<Mode>("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    setError("");
    setLoading(true);
    try {
      const endpoint =
        mode === "login" ? "/api/v1/auth/login" : "/api/v1/auth/register";
      const body =
        mode === "login" ? { email, password } : { email, password, name };

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Ошибка");
      login(data.access_token, data.user);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Ошибка");
    } finally {
      setLoading(false);
    }
  }

  function handleTelegramWebLogin() {
    const origin = encodeURIComponent(window.location.origin);
    const url = `https://oauth.telegram.org/auth?bot_id=${BOT_ID}&origin=${origin}&request_access=write&embed=1`;
    const popup = window.open(url, "_blank", "width=550,height=450,popup");
    if (!popup) {
      setError("Popup заблокирован браузером");
      return;
    }

    const handleMessage = async (event: MessageEvent) => {
      if (event.origin !== "https://oauth.telegram.org") return;
      const data = event.data;
      if (!data || typeof data !== "object" || !data.id) return;
      window.removeEventListener("message", handleMessage);
      clearInterval(checkClosed);
      popup.close();
      setLoading(true);
      try {
        const res = await fetch("/api/v1/auth/telegram", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ widget_data: data }),
        });
        const json = await res.json();
        if (!res.ok) throw new Error(json.detail || "Ошибка");
        login(json.access_token, json.user);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Ошибка входа через Telegram");
      } finally {
        setLoading(false);
      }
    };

    window.addEventListener("message", handleMessage);

    const checkClosed = setInterval(() => {
      if (popup.closed) {
        clearInterval(checkClosed);
        window.removeEventListener("message", handleMessage);
      }
    }, 1000);
  }

  const inputStyle = {
    border: "0.5px solid rgba(140,110,255,0.2)",
  };

  return (
    <div className="min-h-screen bg-bg-deep flex flex-col items-center justify-center px-6">
      <h1
        className="font-display text-5xl font-light tracking-widest mb-2"
        style={{ color: "#F0EAFF" }}
      >
        ✦ Mystral
      </h1>
      <p className="text-text-muted text-xs tracking-widest uppercase mb-10">
        Эзотерическая платформа
      </p>

      {/* Mode switcher */}
      <div
        className="flex mb-6 rounded-xl overflow-hidden"
        style={{ border: "0.5px solid rgba(140,110,255,0.2)" }}
      >
        {(["login", "register"] as const).map(m => (
          <button
            key={m}
            onClick={() => { setMode(m); setError(""); }}
            className="px-6 py-2 text-sm transition-colors"
            style={{
              background: mode === m ? "rgba(107,78,255,0.2)" : "transparent",
              color: mode === m ? "#9B8AFF" : "#9B8FBB",
            }}
          >
            {m === "login" ? "Войти" : "Регистрация"}
          </button>
        ))}
      </div>

      <div className="w-full max-w-[320px] flex flex-col gap-3">
        {mode === "register" && (
          <input
            placeholder="Имя"
            value={name}
            onChange={e => setName(e.target.value)}
            className="w-full px-4 py-3 rounded-xl text-sm bg-bg-surface text-text-primary placeholder-text-muted outline-none"
            style={inputStyle}
          />
        )}
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
          onKeyDown={e => e.key === "Enter" && handleSubmit()}
          className="w-full px-4 py-3 rounded-xl text-sm bg-bg-surface text-text-primary placeholder-text-muted outline-none"
          style={inputStyle}
        />

        {error && (
          <p className="text-red-400 text-xs text-center">{error}</p>
        )}

        <Button
          variant="primary"
          className="w-full mt-1"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "..." : mode === "login" ? "Войти" : "Зарегистрироваться"}
        </Button>

        {/* Divider */}
        <div className="flex items-center gap-3 my-1">
          <div className="flex-1 h-px" style={{ background: "rgba(140,110,255,0.15)" }} />
          <span className="text-text-faint text-[10px]">или</span>
          <div className="flex-1 h-px" style={{ background: "rgba(140,110,255,0.15)" }} />
        </div>

        {/* Telegram web login */}
        <button
          onClick={handleTelegramWebLogin}
          disabled={loading}
          className="w-full px-4 py-3 rounded-xl text-sm flex items-center justify-center gap-2 transition-opacity"
          style={{
            background: "rgba(41,182,246,0.1)",
            border: "0.5px solid rgba(41,182,246,0.25)",
            color: "#29B6F6",
            opacity: loading ? 0.5 : 1,
          }}
        >
          <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 shrink-0">
            <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
          </svg>
          Войти через Telegram
        </button>
      </div>

      <p className="text-text-faint text-[10px] mt-8 text-center">
        В Telegram-приложении вход происходит автоматически
      </p>
    </div>
  );
}
