import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { PaywallSheet } from "../components/PaywallSheet";
import { BottomNav, Button, Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { streamRequest } from "../utils/api";

interface CompatibilityProps {
  onNavigate: (page: string) => void;
}

interface CompatResult {
  person1_sign: string;
  person1_symbol: string;
  person2_sign: string;
  person2_symbol: string;
  sun_compatibility: { percent: number; description: string };
}

export function Compatibility({ onNavigate }: CompatibilityProps) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const [step, setStep] = useState<"form" | "result">("form");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<CompatResult | null>(null);
  const [interpretation, setInterpretation] = useState("");
  const [interpretLoading, setInterpretLoading] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);

  const [me, setMe] = useState({ day: "", month: "", year: "" });
  const [partner, setPartner] = useState({ name: "", day: "", month: "", year: "" });

  const profileLoaded = useRef(false);
  useEffect(() => {
    if (profileLoaded.current || !token) return;
    profileLoaded.current = true;
    fetch("/api/v1/profile", { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => {
        if (data.birth_date) {
          const [y, m, d] = data.birth_date.split("-");
          setMe({ day: d || "", month: m || "", year: y || "" });
        }
      })
      .catch(() => {});
  }, [token]);

  async function handleCalculate() {
    setLoading(true);
    setError("");
    try {
      const p1Date = `${me.year}-${me.month.padStart(2, "0")}-${me.day.padStart(2, "0")}`;
      const p2Date = `${partner.year}-${partner.month.padStart(2, "0")}-${partner.day.padStart(2, "0")}`;
      const res = await fetch("/api/v1/compatibility/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          person1: { birth_date: p1Date },
          person2: { birth_date: p2Date },
          lang: user?.lang ?? "ru",
        }),
      });
      if (!res.ok) throw new Error();
      setResult(await res.json());
      setStep("result");
    } catch {
      setError(t("compat.error"));
    } finally {
      setLoading(false);
    }
  }

  async function handleInterpret() {
    if (!result) return;
    setInterpretLoading(true);
    setInterpretation("");
    const p1Date = `${me.year}-${me.month.padStart(2, "0")}-${me.day.padStart(2, "0")}`;
    const p2Date = `${partner.year}-${partner.month.padStart(2, "0")}-${partner.day.padStart(2, "0")}`;
    try {
      await streamRequest(
        "/compatibility/interpret",
        { person1: { birth_date: p1Date }, person2: { birth_date: p2Date }, lang: user?.lang ?? "ru" },
        (chunk) => setInterpretation(prev => prev + chunk),
        () => setInterpretLoading(false),
        token ?? undefined,
      );
    } catch (e: unknown) {
      const err = e as { code?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setInterpretation(t("compat.error"));
      setInterpretLoading(false);
    }
  }

  const inputCls =
    "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 " +
    "text-text-primary text-sm placeholder:text-text-faint " +
    "focus:outline-none focus:border-violet-600 transition-colors";

  const canSubmit = me.day && me.month && me.year && partner.day && partner.month && partner.year;

  return (
    <div className="flex flex-col min-h-screen bg-bg-deep relative">
      <header
        className="flex items-center justify-between px-4 shrink-0 backdrop-blur-sm"
        style={{ height: 46, background: "rgba(6,4,20,0.75)" }}
      >
        <button className="text-text-muted text-lg w-8" onClick={() => step === "result" ? setStep("form") : onNavigate("home")}>‹</button>
        <span className="font-display text-text-primary text-base tracking-widest">{t("compat.title")}</span>
        <div className="w-8" />
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-6 pb-24">
        {step === "form" ? (
          <div className="flex flex-col gap-4">
            <Card>
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">{t("compat.you")}</p>
              <div className="grid grid-cols-3 gap-2">
                <input className={inputCls} placeholder={t("compat.day")} type="number" min="1" max="31" value={me.day} onChange={e => setMe(p => ({ ...p, day: e.target.value }))} />
                <input className={inputCls} placeholder={t("compat.month")} type="number" min="1" max="12" value={me.month} onChange={e => setMe(p => ({ ...p, month: e.target.value }))} />
                <input className={inputCls} placeholder={t("compat.year")} type="number" min="1900" max="2025" value={me.year} onChange={e => setMe(p => ({ ...p, year: e.target.value }))} />
              </div>
            </Card>

            <Card>
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">{t("compat.partner")}</p>
              <input className={inputCls + " mb-2"} placeholder={t("compat.partner_name")} value={partner.name} onChange={e => setPartner(p => ({ ...p, name: e.target.value }))} />
              <div className="grid grid-cols-3 gap-2">
                <input className={inputCls} placeholder={t("compat.day")} type="number" min="1" max="31" value={partner.day} onChange={e => setPartner(p => ({ ...p, day: e.target.value }))} />
                <input className={inputCls} placeholder={t("compat.month")} type="number" min="1" max="12" value={partner.month} onChange={e => setPartner(p => ({ ...p, month: e.target.value }))} />
                <input className={inputCls} placeholder={t("compat.year")} type="number" min="1900" max="2025" value={partner.year} onChange={e => setPartner(p => ({ ...p, year: e.target.value }))} />
              </div>
            </Card>

            {error && <p className="text-red-400 text-xs text-center">{error}</p>}

            <Button variant="primary" className="w-full" onClick={handleCalculate} disabled={loading || !canSubmit}>
              {loading ? t("compat.calculating") : t("compat.calculate")}
            </Button>
          </div>
        ) : result ? (
          <div className="flex flex-col gap-4">
            <Card>
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-4">{t("compat.sun_compat")}</p>
              <div className="flex items-center justify-center gap-4 mb-4">
                <div className="flex flex-col items-center gap-1">
                  <span className="text-3xl">{result.person1_symbol}</span>
                  <span className="text-text-muted text-xs">{result.person1_sign}</span>
                </div>
                <span className="text-text-faint text-xl">+</span>
                <div className="flex flex-col items-center gap-1">
                  <span className="text-3xl">{result.person2_symbol}</span>
                  <span className="text-text-muted text-xs">{result.person2_sign}</span>
                </div>
              </div>
              <p className="font-display text-4xl text-center mb-3" style={{ color: result.sun_compatibility.percent >= 70 ? "#C9A84C" : "#9B8AFF" }}>
                {result.sun_compatibility.percent}%
              </p>
              <div className="w-full rounded-full overflow-hidden mb-3" style={{ height: 4, background: "rgba(107,78,255,0.15)" }}>
                <div className="h-full rounded-full transition-all duration-700" style={{ width: `${result.sun_compatibility.percent}%`, background: result.sun_compatibility.percent >= 70 ? "#C9A84C" : "#6B4EFF" }} />
              </div>
              <p className="text-text-muted text-xs leading-relaxed">{result.sun_compatibility.description}</p>
            </Card>

            {user?.tier !== "pro" ? (
              <Card>
                <p className="text-text-muted text-sm mb-2">{t("compat.pro_lock")}</p>
                <p className="text-text-faint text-xs mb-3">{t("compat.pro_includes")}</p>
                <Button variant="gold" size="sm" className="w-full" onClick={() => setShowPaywall(true)}>
                  {t("profile.upgrade")}
                </Button>
              </Card>
            ) : (
              <>
                {interpretation ? (
                  <Card>
                    <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">{t("natal.interpretation")}</p>
                    <p className="text-text-muted text-xs leading-relaxed">
                      {interpretation}
                      {interpretLoading && <span className="animate-pulse">▍</span>}
                    </p>
                  </Card>
                ) : (
                  <Button variant="primary" className="w-full" onClick={handleInterpret} disabled={interpretLoading}>
                    {interpretLoading ? t("compat.reading") : t("compat.get_interpretation")}
                  </Button>
                )}
              </>
            )}

            <Button variant="ghost" className="w-full" onClick={() => { setStep("form"); setResult(null); setInterpretation(""); }}>
              {t("compat.back")}
            </Button>
          </div>
        ) : null}
      </main>

      <BottomNav active="home" onNavigate={onNavigate} />
      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
    </div>
  );
}
