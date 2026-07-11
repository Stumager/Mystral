import { useEffect, useRef, useState } from "react";
import { Logo } from "../components/Logo";
import { useAuth } from "../context/AuthContext";
import { applyStoredReferralCode } from "../utils/api";

interface Props { email: string; }

export function VerifyEmail({ email }: Props) {
  const { login } = useAuth();
  const [digits, setDigits] = useState<string[]>(["", "", "", "", "", ""]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [cooldown, setCooldown] = useState(0);
  const refs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    if (cooldown <= 0) return;
    const t = setInterval(() => setCooldown(c => c - 1), 1000);
    return () => clearInterval(t);
  }, [cooldown]);

  function handleChange(i: number, val: string) {
    if (val && !/^\d$/.test(val)) return;
    const next = [...digits];
    next[i] = val;
    setDigits(next);
    setError("");
    if (val && i < 5) refs.current[i + 1]?.focus();
  }

  function handleKey(i: number, e: React.KeyboardEvent) {
    if (e.key === "Backspace" && !digits[i] && i > 0) {
      refs.current[i - 1]?.focus();
    }
  }

  function handlePaste(e: React.ClipboardEvent) {
    const text = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    if (text.length === 6) {
      setDigits(text.split(""));
      refs.current[5]?.focus();
      e.preventDefault();
    }
  }

  const code = digits.join("");
  const canSubmit = code.length === 6;

  async function handleVerify() {
    if (!canSubmit) return;
    setLoading(true); setError("");
    try {
      const res = await fetch("/api/v1/auth/verify-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, code }),
      });
      const data = await res.json();
      if (!res.ok) { setError(data.detail || data.message || "Ошибка"); setLoading(false); return; }
      await applyStoredReferralCode(data.access_token);
      login(data.access_token, data.user);
    } catch { setError("Ошибка соединения"); }
    finally { setLoading(false); }
  }

  async function handleResend() {
    if (cooldown > 0) return;
    try {
      const res = await fetch("/api/v1/auth/resend-verification", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      if (res.status === 429) { setCooldown(60); return; }
      setCooldown(60);
    } catch {}
  }

  const inputStyle: React.CSSProperties = {
    width: 52, height: 64, textAlign: "center", borderRadius: 14,
    background: "rgba(255,255,255,.04)", border: "1px solid rgba(201,168,76,.22)",
    color: "#F0E9DA", fontSize: 32, outline: "none",
    fontFamily: "'Cormorant Garamond', serif",
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "0 24px", textAlign: "center", background: "var(--gradient-page)" }}>
      <div style={{ animation: "mystral-float 7s ease-in-out infinite", filter: "drop-shadow(0 0 30px rgba(201,168,76,.5))" }}>
        <Logo size={72} />
      </div>

      <p className="font-cormorant" style={{ fontSize: 34, color: "#F0E9DA", marginTop: 24 }}>
        Подтвердите почту
      </p>
      <p style={{ fontSize: 14, color: "#A89E8B", marginTop: 10 }}>
        Мы отправили 6-значный код на <span style={{ color: "#E8CD7E", fontWeight: 500 }}>{email}</span>
      </p>

      <div style={{ display: "flex", gap: 10, marginTop: 32 }} onPaste={handlePaste}>
        {digits.map((d, i) => (
          <input
            key={i}
            ref={el => { refs.current[i] = el; }}
            type="text"
            inputMode="numeric"
            maxLength={1}
            value={d}
            onChange={e => handleChange(i, e.target.value)}
            onKeyDown={e => handleKey(i, e)}
            style={{ ...inputStyle, borderColor: d ? "rgba(201,168,76,.6)" : "rgba(201,168,76,.22)" }}
          />
        ))}
      </div>

      {error && <p style={{ fontSize: 13, color: "#D98A8A", marginTop: 12 }}>{error}</p>}

      <button onClick={handleVerify} disabled={!canSubmit || loading}
        style={{ marginTop: 24, width: "100%", maxWidth: 360, height: 52, borderRadius: 16, border: "none", cursor: canSubmit ? "pointer" : "default", fontWeight: 600, fontSize: 15.5, background: canSubmit ? "linear-gradient(100deg,#A9882F,#C9A84C 50%,#E8CD7E)" : "rgba(255,255,255,.06)", color: canSubmit ? "#1A1206" : "#6E6757", boxShadow: canSubmit ? "0 10px 28px -8px rgba(201,168,76,.5)" : "none" }}>
        {loading ? "..." : "Подтвердить"}
      </button>

      <div style={{ marginTop: 20 }}>
        <span style={{ fontSize: 13, color: "#6E6757" }}>Не получили письмо? </span>
        {cooldown > 0 ? (
          <span style={{ fontSize: 13, color: "#6E6757" }}>Повторно через {cooldown} сек</span>
        ) : (
          <button onClick={handleResend} style={{ fontSize: 13, color: "#C9A84C", cursor: "pointer", background: "none", border: "none" }}>
            Отправить повторно
          </button>
        )}
      </div>
    </div>
  );
}
