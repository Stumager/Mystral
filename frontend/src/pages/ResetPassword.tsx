import { useState } from "react";
import { Logo } from "../components/Logo";

export function ResetPassword() {
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [expired, setExpired] = useState(false);

  const token = new URLSearchParams(window.location.search).get("token") || "";

  async function handleSubmit() {
    if (password.length < 8) { setError("Минимум 8 символов"); return; }
    if (password !== confirm) { setError("Пароли не совпадают"); return; }
    setLoading(true); setError("");
    try {
      const res = await fetch("/api/v1/auth/reset-password", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: password }),
      });
      const data = await res.json();
      if (!res.ok) {
        if (data.detail?.includes("устарела") || data.detail?.includes("Недейств")) setExpired(true);
        else setError(data.detail || "Ошибка");
        return;
      }
      setDone(true);
    } catch { setError("Нет соединения"); }
    finally { setLoading(false); }
  }

  const inputStyle: React.CSSProperties = {
    width: "100%", maxWidth: 380, padding: "14px 18px", borderRadius: 14,
    background: "rgba(255,255,255,.04)", border: "1px solid rgba(201,168,76,.22)",
    color: "#F0E9DA", fontSize: 15, outline: "none", boxSizing: "border-box",
  };

  function goLogin() { window.location.hash = ""; window.location.search = ""; window.location.reload(); }
  function goForgot() { window.location.href = "/#forgot-password"; }

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "0 24px", background: "var(--gradient-page)" }}>
      <div style={{ animation: "mystral-float 7s ease-in-out infinite", filter: "drop-shadow(0 0 30px rgba(201,168,76,.5))" }}>
        <Logo size={64} />
      </div>

      {done ? (
        <>
          <p style={{ fontSize: 48, color: "#C9A84C", marginTop: 24 }}>✓</p>
          <p className="font-cormorant" style={{ fontSize: 28, color: "#F0E9DA", marginTop: 12 }}>Пароль обновлён</p>
          <button onClick={goLogin} style={{ marginTop: 20, height: 48, padding: "0 32px", borderRadius: 14, background: "linear-gradient(100deg,#A9882F,#C9A84C,#E8CD7E)", color: "#1A1206", fontWeight: 600, fontSize: 14, border: "none", cursor: "pointer" }}>
            Войти
          </button>
        </>
      ) : expired ? (
        <>
          <p className="font-cormorant" style={{ fontSize: 28, color: "#F0E9DA", marginTop: 24 }}>Ссылка устарела</p>
          <p style={{ fontSize: 14, color: "#A89E8B", marginTop: 8, textAlign: "center" }}>Запросите новую ссылку для сброса пароля</p>
          <button onClick={goForgot} style={{ marginTop: 20, height: 48, padding: "0 32px", borderRadius: 14, background: "linear-gradient(100deg,#A9882F,#C9A84C,#E8CD7E)", color: "#1A1206", fontWeight: 600, fontSize: 14, border: "none", cursor: "pointer" }}>
            Запросить новую
          </button>
        </>
      ) : (
        <>
          <p className="font-cormorant" style={{ fontSize: 32, color: "#F0E9DA", marginTop: 24 }}>Новый пароль</p>
          <div style={{ width: "100%", maxWidth: 380, marginTop: 28, display: "flex", flexDirection: "column", gap: 12 }}>
            <input type="password" placeholder="Новый пароль" value={password}
              onChange={e => { setPassword(e.target.value); setError(""); }} style={inputStyle} />
            <input type="password" placeholder="Подтвердить пароль" value={confirm}
              onChange={e => { setConfirm(e.target.value); setError(""); }}
              onKeyDown={e => e.key === "Enter" && handleSubmit()} style={inputStyle} />
            {error && <p style={{ color: "#D98A8A", fontSize: 13, textAlign: "center" }}>{error}</p>}
            <button onClick={handleSubmit} disabled={loading || !password || !confirm}
              style={{ width: "100%", height: 52, borderRadius: 16, border: "none", cursor: "pointer", fontWeight: 600, fontSize: 15.5, background: password && confirm ? "linear-gradient(100deg,#A9882F,#C9A84C 50%,#E8CD7E)" : "rgba(255,255,255,.06)", color: password && confirm ? "#1A1206" : "#6E6757", boxShadow: password && confirm ? "0 10px 28px -8px rgba(201,168,76,.5)" : "none" }}>
              {loading ? "..." : "Сохранить"}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
