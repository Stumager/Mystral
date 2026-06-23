import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";
import { Button } from "../components/ui";
import { validateEmail, validatePassword, validateName } from "../utils/validate";

type Mode = "login" | "register";

const BOT_USERNAME = "Mystrallbot";

export function LoginScreen() {
  const { t } = useTranslation();
  const { login } = useAuth();
  const [mode, setMode] = useState<Mode>("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const tgBtnRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!tgBtnRef.current) return;

    (window as any).onTelegramWidgetAuth = async (user: Record<string, unknown>) => {
      setError("");
      setLoading(true);
      try {
        const res = await fetch("/api/v1/auth/telegram", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ widget_data: user }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || t("login.tg_error"));
        login(data.access_token, data.user);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : t("login.tg_error"));
      } finally {
        setLoading(false);
      }
    };

    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.setAttribute("data-telegram-login", BOT_USERNAME);
    script.setAttribute("data-size", "large");
    script.setAttribute("data-onauth", "onTelegramWidgetAuth(user)");
    script.setAttribute("data-request-access", "write");
    script.async = true;
    tgBtnRef.current.appendChild(script);

    return () => {
      delete (window as any).onTelegramWidgetAuth;
    };
  }, []);

  function clearFieldError(field: string) {
    setErrors(prev => ({ ...prev, [field]: "" }));
  }

  async function handleSubmit() {
    const errs: Record<string, string> = {};
    const emailErr = validateEmail(email);
    const passErr = validatePassword(password);
    if (emailErr) errs.email = emailErr;
    if (passErr) errs.password = passErr;
    if (mode === "register") {
      const nameErr = validateName(name);
      if (nameErr) errs.name = nameErr;
    }
    if (Object.values(errs).some(Boolean)) { setErrors(errs); return; }

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
      if (!res.ok) throw new Error(data.detail || "Error");
      login(data.access_token, data.user);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setLoading(false);
    }
  }

  const inputStyle = {
    border: "0.5px solid rgba(140,110,255,0.2)",
  };
  const errCls = "text-red-400 text-xs mt-1";

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6" style={{ background: "var(--gradient-page)" }}>
      <h1
        className="font-display text-5xl font-light tracking-widest mb-2"
        style={{ color: "#F0EAFF" }}
      >
        ✦ Mystral
      </h1>
      <p className="text-text-muted text-xs tracking-widest uppercase mb-10">
        {t("login.subtitle")}
      </p>

      {/* Mode switcher */}
      <div
        className="flex mb-6 rounded-xl overflow-hidden"
        style={{ border: "0.5px solid rgba(140,110,255,0.2)" }}
      >
        {(["login", "register"] as const).map(m => (
          <button
            key={m}
            onClick={() => { setMode(m); setError(""); setErrors({}); }}
            className="px-6 py-2 text-sm transition-colors"
            style={{
              background: mode === m ? "rgba(107,78,255,0.2)" : "transparent",
              color: mode === m ? "#9B8AFF" : "#9B8FBB",
            }}
          >
            {m === "login" ? t("login.tab_login") : t("login.tab_register")}
          </button>
        ))}
      </div>

      <div className="w-full max-w-[320px] flex flex-col gap-3">
        {mode === "register" && (
          <div>
            <input
              placeholder={t("login.name")}
              value={name}
              onChange={e => { setName(e.target.value); clearFieldError("name"); }}
              className="w-full px-4 py-3 rounded-xl text-sm bg-bg-surface text-text-primary placeholder-text-muted outline-none"
              style={inputStyle}
            />
            {errors.name && <p className={errCls}>{errors.name}</p>}
          </div>
        )}
        <div>
          <input
            type="email"
            placeholder={t("login.email")}
            value={email}
            onChange={e => { setEmail(e.target.value); clearFieldError("email"); }}
            className="w-full px-4 py-3 rounded-xl text-sm bg-bg-surface text-text-primary placeholder-text-muted outline-none"
            style={inputStyle}
          />
          {errors.email && <p className={errCls}>{errors.email}</p>}
        </div>
        <div>
          <input
            type="password"
            placeholder={t("login.password")}
            value={password}
            onChange={e => { setPassword(e.target.value); clearFieldError("password"); }}
            onKeyDown={e => e.key === "Enter" && handleSubmit()}
            className="w-full px-4 py-3 rounded-xl text-sm bg-bg-surface text-text-primary placeholder-text-muted outline-none"
            style={inputStyle}
          />
          {errors.password && <p className={errCls}>{errors.password}</p>}
        </div>

        {error && (
          <p className="text-red-400 text-xs text-center">{error}</p>
        )}

        <Button
          variant="primary"
          className="w-full mt-1"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "..." : mode === "login" ? t("login.submit_login") : t("login.submit_register")}
        </Button>

        {/* Divider */}
        <div className="flex items-center gap-3 my-1">
          <div className="flex-1 h-px" style={{ background: "rgba(140,110,255,0.15)" }} />
          <span className="text-text-faint text-[10px]">{t("login.or")}</span>
          <div className="flex-1 h-px" style={{ background: "rgba(140,110,255,0.15)" }} />
        </div>

        {/* Official Telegram Login Widget */}
        <div ref={tgBtnRef} className="flex justify-center" />
      </div>

      <p className="text-text-faint text-[10px] mt-8 text-center">
        {t("login.tma_hint")}
      </p>
    </div>
  );
}
