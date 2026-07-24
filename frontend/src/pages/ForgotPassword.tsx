import { useState } from "react";
import { Logo } from "../components/Logo";

interface Props { onBack: () => void; }

export function ForgotPassword({ onBack }: Props) {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit() {
    if (!email.trim()) return;
    setLoading(true); setError("");
    try {
      const res = await fetch("/api/v1/auth/forgot-password", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim() }),
      });
      if (!res.ok) { const d = await res.json().catch(() => ({})); setError(d.detail || "Ошибка"); }
      else setSent(true);
    } catch { setError("Нет соединения"); }
    finally { setLoading(false); }
  }

  const inputStyle: React.CSSProperties = {
    width: "100%", maxWidth: 380, padding: "14px 18px", borderRadius: 14,
    background: "rgba(255,255,255,.04)", border: "1px solid rgba(201,168,76,.22)",
    color: "#F0E9DA", fontSize: 15, outline: "none", boxSizing: "border-box",
  };

  return (
    <main style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "0 24px", background: "var(--gradient-page)" }}>
      <div style={{ animation: "mystral-float 7s ease-in-out infinite", filter: "drop-shadow(0 0 30px rgba(201,168,76,.5))" }}>
        <Logo size={64} />
      </div>

      {sent ? (
        <>
          <p style={{ fontSize: 48, color: "#C9A84C", marginTop: 24 }}>✓</p>
          <p className="font-cormorant" style={{ fontSize: 28, color: "#F0E9DA", marginTop: 12 }}>Письмо отправлено</p>
          <p style={{ fontSize: 14, color: "#A89E8B", marginTop: 8, textAlign: "center" }}>Проверьте <span style={{ color: "#E8CD7E" }}>{email}</span></p>
          <button onClick={onBack} style={{ marginTop: 24, fontSize: 13, color: "#C9A84C", background: "none", border: "none", cursor: "pointer" }}>
            Вернуться к входу
          </button>
        </>
      ) : (
        <>
          <p className="font-cormorant" style={{ fontSize: 32, color: "#F0E9DA", marginTop: 24 }}>Восстановление пароля</p>
          <p style={{ fontSize: 14, color: "#A89E8B", textAlign: "center", margin: "10px 0 28px", maxWidth: 380 }}>
            Введите email указанный при регистрации — мы отправим ссылку для сброса пароля
          </p>
          <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSubmit()} style={inputStyle} />
          {error && <p style={{ color: "#D98A8A", fontSize: 13, marginTop: 8 }}>{error}</p>}
          <button onClick={handleSubmit} disabled={loading || !email.trim()}
            style={{ width: "100%", maxWidth: 380, height: 52, marginTop: 12, borderRadius: 16, border: "none", cursor: "pointer", fontWeight: 600, fontSize: 15.5, background: email.trim() ? "linear-gradient(100deg,#A9882F,#C9A84C 50%,#E8CD7E)" : "rgba(255,255,255,.06)", color: email.trim() ? "#1A1206" : "#827A69", boxShadow: email.trim() ? "0 10px 28px -8px rgba(201,168,76,.5)" : "none" }}>
            {loading ? "..." : "Отправить"}
          </button>
          <button onClick={onBack} style={{ marginTop: 16, fontSize: 13, color: "#C9A84C", background: "none", border: "none", cursor: "pointer" }}>
            Вернуться к входу
          </button>
        </>
      )}
    </main>
  );
}
