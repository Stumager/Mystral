import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { Button } from "../components/ui";

type Mode = "login" | "register";

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

      {/* Переключатель */}
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
      </div>

      <p className="text-text-faint text-[10px] mt-8 text-center">
        В Telegram вход происходит автоматически
      </p>
    </div>
  );
}
