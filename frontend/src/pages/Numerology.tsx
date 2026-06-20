import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { PaywallSheet } from "../components/PaywallSheet";
import { BottomNav, Button, Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { apiRequest, streamRequest } from "../utils/api";

interface NumerologyProps {
  onNavigate: (page: string) => void;
}

interface NumEntry {
  number: number;
  title?: string;
  description?: string;
  locked?: boolean;
}

interface NumResult {
  life_path: NumEntry;
  expression?: NumEntry;
  soul_urge?: NumEntry;
  personality?: NumEntry;
}

export function Numerology({ onNavigate }: NumerologyProps) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const [step, setStep] = useState<"form" | "result">("form");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<NumResult | null>(null);
  const [interpretation, setInterpretation] = useState("");
  const [interpretLoading, setInterpretLoading] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);

  const [form, setForm] = useState({ day: "", month: "", year: "", fullName: "" });

  const profileLoaded = useRef(false);
  useEffect(() => {
    if (profileLoaded.current || !token) return;
    profileLoaded.current = true;
    fetch("/api/v1/profile", { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => {
        if (data.birth_date) {
          const [y, m, d] = data.birth_date.split("-");
          setForm(p => ({ ...p, day: d || "", month: m || "", year: y || "" }));
        }
        if (data.birth_name) setForm(p => ({ ...p, fullName: data.birth_name }));
      })
      .catch(() => {});
  }, [token]);

  async function handleCalculate() {
    setLoading(true);
    setError("");
    try {
      const birthDate = `${form.year}-${form.month.padStart(2, "0")}-${form.day.padStart(2, "0")}`;
      const data = await apiRequest<NumResult>(
        "/numerology/calculate",
        { birth_date: birthDate, full_name: form.fullName || null, lang: user?.lang ?? "ru" },
        token ?? undefined,
      );
      setResult(data);
      setStep("result");
    } catch {
      setError(t("numerology.error"));
    } finally {
      setLoading(false);
    }
  }

  async function handleInterpret() {
    setInterpretLoading(true);
    setInterpretation("");
    const birthDate = `${form.year}-${form.month.padStart(2, "0")}-${form.day.padStart(2, "0")}`;
    try {
      await streamRequest(
        "/numerology/interpret",
        { birth_date: birthDate, full_name: form.fullName || null, lang: user?.lang ?? "ru" },
        (chunk) => setInterpretation(prev => prev + chunk),
        () => setInterpretLoading(false),
        token ?? undefined,
      );
    } catch (e: unknown) {
      const err = e as { code?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setInterpretation(t("numerology.error"));
      setInterpretLoading(false);
    }
  }

  const inputCls =
    "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 " +
    "text-text-primary text-sm placeholder:text-text-faint " +
    "focus:outline-none focus:border-violet-600 transition-colors";

  const canSubmit = form.day && form.month && form.year;

  const numberLabels: Record<string, string> = {
    life_path: t("numerology.life_path"),
    expression: t("numerology.expression"),
    soul_urge: t("numerology.soul_urge"),
    personality: t("numerology.personality"),
  };

  return (
    <div className="flex flex-col min-h-screen bg-bg-deep relative">
      <header
        className="flex items-center justify-between px-4 shrink-0 backdrop-blur-sm"
        style={{ height: 46, background: "rgba(6,4,20,0.75)" }}
      >
        <button className="text-text-muted text-lg w-8" onClick={() => step === "result" ? setStep("form") : onNavigate("home")}>‹</button>
        <span className="font-display text-text-primary text-base tracking-widest">{t("numerology.title")}</span>
        <div className="w-8" />
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-6 pb-24">
        {step === "form" ? (
          <div className="flex flex-col gap-3">
            <p className="text-text-muted text-xs text-center mb-1">{t("numerology.subtitle")}</p>
            <div className="grid grid-cols-3 gap-2">
              <input className={inputCls} placeholder={t("profile.day")} type="number" min="1" max="31" value={form.day} onChange={e => setForm(p => ({ ...p, day: e.target.value }))} />
              <input className={inputCls} placeholder={t("profile.month")} type="number" min="1" max="12" value={form.month} onChange={e => setForm(p => ({ ...p, month: e.target.value }))} />
              <input className={inputCls} placeholder={t("profile.year")} type="number" min="1900" max="2025" value={form.year} onChange={e => setForm(p => ({ ...p, year: e.target.value }))} />
            </div>
            <input className={inputCls} placeholder={t("numerology.full_name")} value={form.fullName} onChange={e => setForm(p => ({ ...p, fullName: e.target.value }))} />
            <p className="text-text-faint text-[10px] text-center">{t("numerology.name_hint")}</p>
            {error && <p className="text-red-400 text-xs text-center">{error}</p>}
            <Button variant="primary" className="w-full mt-1" onClick={handleCalculate} disabled={loading || !canSubmit}>
              {loading ? t("numerology.calculating") : t("numerology.calculate")}
            </Button>
          </div>
        ) : result ? (
          <div className="flex flex-col gap-4">
            {/* Life Path — always visible */}
            <Card>
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">{numberLabels.life_path}</p>
              <p className="font-display text-5xl text-center my-3" style={{ color: "#C9A84C" }}>
                {result.life_path.number}
              </p>
              {result.life_path.title && (
                <p className="font-display text-sm text-text-primary text-center mb-1">{result.life_path.title}</p>
              )}
              {result.life_path.description && (
                <p className="text-text-muted text-xs text-center leading-relaxed">{result.life_path.description}</p>
              )}
            </Card>

            {/* Other numbers */}
            {(["expression", "soul_urge", "personality"] as const).map(key => {
              const entry = result[key];
              if (!entry) return null;
              if (entry.locked) {
                return (
                  <Card key={key} className="relative overflow-hidden">
                    <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">{numberLabels[key]}</p>
                    <p className="font-display text-3xl text-center my-2 blur-sm">{entry.number}</p>
                    <div className="absolute inset-0 flex items-center justify-center" style={{ background: "rgba(6,4,20,0.6)" }}>
                      <span className="text-text-muted text-sm">🔒</span>
                    </div>
                  </Card>
                );
              }
              return (
                <Card key={key}>
                  <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">{numberLabels[key]}</p>
                  <p className="font-display text-3xl text-center my-2" style={{ color: "#9B8AFF" }}>{entry.number}</p>
                  {entry.title && <p className="font-display text-sm text-text-primary text-center mb-1">{entry.title}</p>}
                  {entry.description && <p className="text-text-muted text-xs text-center leading-relaxed">{entry.description}</p>}
                </Card>
              );
            })}

            {user?.tier !== "pro" && result.expression?.locked && (
              <Card>
                <p className="text-text-muted text-sm mb-3">{t("numerology.pro_lock")}</p>
                <Button variant="gold" size="sm" className="w-full" onClick={() => setShowPaywall(true)}>
                  {t("profile.upgrade")}
                </Button>
              </Card>
            )}

            {user?.tier === "pro" && (
              interpretation ? (
                <Card>
                  <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">{t("natal.interpretation")}</p>
                  <p className="text-text-muted text-xs leading-relaxed">
                    {interpretation}
                    {interpretLoading && <span className="animate-pulse">▍</span>}
                  </p>
                </Card>
              ) : (
                <Button variant="primary" className="w-full" onClick={handleInterpret} disabled={interpretLoading}>
                  {interpretLoading ? t("numerology.reading") : t("numerology.get_interpretation")}
                </Button>
              )
            )}

            <Button variant="ghost" className="w-full" onClick={() => { setStep("form"); setResult(null); setInterpretation(""); }}>
              {t("numerology.back")}
            </Button>
          </div>
        ) : null}
      </main>

      <BottomNav active="home" onNavigate={onNavigate} />
      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
    </div>
  );
}
