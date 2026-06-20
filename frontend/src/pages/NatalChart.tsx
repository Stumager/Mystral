import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { PaywallSheet } from "../components/PaywallSheet";
import { BottomNav, Button, Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { streamRequest } from "../utils/api";
import { validateDay, validateMonth, validateYear, validateDateExists, validateName, validateCity } from "../utils/validate";

interface NatalChartProps {
  onNavigate: (page: string) => void;
}

interface Planet {
  sign: string;
  degree?: number;
}

interface NatalResult {
  sun: Planet;
  moon: Planet;
  rising: Planet;
  mercury: Planet;
  venus: Planet;
  mars: Planet;
}

export function NatalChart({ onNavigate }: NatalChartProps) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const [step, setStep] = useState<"form" | "result">("form");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [saveToProfile, setSaveToProfile] = useState(true);
  const [form, setForm] = useState({
    name: "", day: "", month: "", year: "",
    hour: "", minute: "", city: "",
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [result, setResult] = useState<NatalResult | null>(null);
  const [interpretation, setInterpretation] = useState("");
  const [interpretLoading, setInterpretLoading] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);

  const profileLoaded = useRef(false);

  useEffect(() => {
    if (profileLoaded.current || !token) return;
    profileLoaded.current = true;

    fetch("/api/v1/profile", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(r => r.json())
      .then(data => {
        if (data.birth_date || data.birth_city) {
          const [y, m, d] = (data.birth_date ?? "").split("-");
          const [h, min] = (data.birth_time ?? "").split(":");
          setForm(prev => ({
            name:   data.birth_name  || prev.name,
            year:   y    || prev.year,
            month:  m    || prev.month,
            day:    d    || prev.day,
            hour:   h    || prev.hour,
            minute: min  || prev.minute,
            city:   data.birth_city  || prev.city,
          }));
        }
      })
      .catch(() => {});
  }, [token]);

  const setField = (field: string) =>
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setForm(prev => ({ ...prev, [field]: e.target.value }));
      clearFieldError(field);
      clearFieldError("date");
    };

  const buildBody = () => ({
    name: form.name,
    year: parseInt(form.year),
    month: parseInt(form.month),
    day: parseInt(form.day),
    hour: parseInt(form.hour || "12"),
    minute: parseInt(form.minute || "0"),
    city: form.city,
    lang: user?.lang ?? "ru",
  });

  function clearFieldError(field: string) {
    setFormErrors(prev => ({ ...prev, [field]: "" }));
  }

  async function handleCalculate() {
    const errs: Record<string, string> = {};
    const nameErr = validateName(form.name); if (nameErr) errs.name = nameErr;
    const dayErr = validateDay(form.day); if (dayErr) errs.day = dayErr;
    const monthErr = validateMonth(form.month); if (monthErr) errs.month = monthErr;
    const yearErr = validateYear(form.year); if (yearErr) errs.year = yearErr;
    const cityErr = validateCity(form.city); if (cityErr) errs.city = cityErr;
    if (!dayErr && !monthErr && !yearErr) {
      const dateErr = validateDateExists(form.day, form.month, form.year);
      if (dateErr) errs.date = dateErr;
    }
    if (Object.values(errs).some(Boolean)) { setFormErrors(errs); return; }
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/v1/natal/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildBody()),
      });
      if (!res.ok) throw new Error();
      setResult(await res.json());
      setStep("result");

      if (saveToProfile && token) {
        const b = buildBody();
        const profileBody: Record<string, unknown> = {
          birth_city: b.city,
          birth_name: b.name,
          birth_date: `${b.year}-${String(b.month).padStart(2, "0")}-${String(b.day).padStart(2, "0")}`,
        };
        if (form.hour) {
          profileBody.birth_time = `${String(b.hour).padStart(2, "0")}:${String(b.minute).padStart(2, "0")}`;
          profileBody.birth_time_known = true;
        }
        fetch("/api/v1/profile", {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(profileBody),
        }).catch(() => {});
      }
    } catch {
      setError(t("natal.calc_error"));
    } finally {
      setLoading(false);
    }
  }

  async function handleInterpret() {
    if (interpretLoading) return;
    setInterpretLoading(true);
    setInterpretation("");
    try {
      await streamRequest(
        "/natal/interpret",
        buildBody(),
        (chunk) => setInterpretation(prev => prev + chunk),
        () => setInterpretLoading(false),
        token ?? undefined
      );
    } catch (e: unknown) {
      const err = e as { code?: string };
      if (err.code === "FREE_LIMIT_REACHED") {
        setShowPaywall(true);
      } else {
        setInterpretation(t("natal.connection_error"));
      }
      setInterpretLoading(false);
    }
  }

  const inputCls =
    "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 " +
    "text-text-primary text-sm placeholder:text-text-faint " +
    "focus:outline-none focus:border-violet-600 transition-colors";

  const canSubmit = form.name && form.day && form.month && form.year && form.city;

  return (
    <div className="flex flex-col min-h-screen bg-bg-deep relative">
      <header
        className="flex items-center justify-between px-4 shrink-0 backdrop-blur-sm"
        style={{ height: 46, background: "rgba(6,4,20,0.75)" }}
      >
        <button
          className="text-text-muted text-lg w-8"
          onClick={() => step === "result" ? setStep("form") : onNavigate("home")}
        >
          ‹
        </button>
        <span className="font-display text-text-primary text-base tracking-widest">
          {t("natal.title")}
        </span>
        <div className="w-8" />
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-6 pb-24">
        {step === "form" ? (
          <div className="flex flex-col gap-3">
            <p className="text-text-muted text-xs text-center mb-1">
              {t("natal.subtitle")}
            </p>

            <div>
              <input className={inputCls} placeholder={t("natal.name")} value={form.name} onChange={setField("name")} />
              {formErrors.name && <p className="text-red-400 text-xs mt-1">{formErrors.name}</p>}
            </div>

            <div>
              <div className="grid grid-cols-3 gap-2">
                <input className={inputCls} placeholder={t("natal.day")}   type="number" min="1"    max="31"   value={form.day}   onChange={setField("day")} />
                <input className={inputCls} placeholder={t("natal.month")} type="number" min="1"    max="12"   value={form.month} onChange={setField("month")} />
                <input className={inputCls} placeholder={t("natal.year")}  type="number" min="1900" max="2025" value={form.year}  onChange={setField("year")} />
              </div>
              {(formErrors.day || formErrors.month || formErrors.year || formErrors.date) && (
                <p className="text-red-400 text-xs mt-1">{formErrors.day || formErrors.month || formErrors.year || formErrors.date}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-2">
              <input className={inputCls} placeholder={t("natal.hour")}    type="number" min="0" max="23" value={form.hour}   onChange={setField("hour")} />
              <input className={inputCls} placeholder={t("natal.minutes")} type="number" min="0" max="59" value={form.minute} onChange={setField("minute")} />
            </div>

            <div>
              <input className={inputCls} placeholder={t("natal.birth_city")} value={form.city} onChange={setField("city")} />
              {formErrors.city && <p className="text-red-400 text-xs mt-1">{formErrors.city}</p>}
            </div>

            <p className="text-text-faint text-[10px] text-center">
              {t("natal.time_hint")}
            </p>

            <label className="flex items-center gap-2 cursor-pointer self-start">
              <input
                type="checkbox"
                checked={saveToProfile}
                onChange={e => setSaveToProfile(e.target.checked)}
                className="w-3.5 h-3.5 accent-violet-600"
              />
              <span className="text-text-muted text-xs">{t("natal.save_to_profile")}</span>
            </label>

            {error && (
              <p className="text-red-400 text-xs text-center">{error}</p>
            )}

            <Button
              variant="primary"
              className="w-full mt-1"
              onClick={handleCalculate}
              disabled={loading || !canSubmit}
            >
              {loading ? t("natal.calculating") : t("natal.calculate")}
            </Button>
          </div>
        ) : result ? (
          <div className="flex flex-col gap-4">
            <Card>
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">
                {t("natal.big_three")}
              </p>
              <div className="flex flex-col gap-2.5">
                {[
                  { icon: "☀️", label: t("natal.sun"),       planet: result.sun },
                  { icon: "🌙", label: t("natal.moon"),      planet: result.moon },
                  { icon: "⬆️", label: t("natal.ascendant"), planet: result.rising },
                ].map(({ icon, label, planet }) => (
                  <div key={label} className="flex items-center justify-between">
                    <span className="text-text-muted text-sm">{icon} {label}</span>
                    <span className="font-display text-sm" style={{ color: "#C9A84C" }}>
                      {planet.sign}
                      {planet.degree !== undefined && (
                        <span className="text-text-faint text-xs ml-1">{planet.degree}°</span>
                      )}
                    </span>
                  </div>
                ))}
              </div>
            </Card>

            <Card>
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">
                {t("natal.planets")}
              </p>
              <div className="flex flex-col gap-2.5">
                {[
                  { label: "Меркурий ☿", planet: result.mercury },
                  { label: "Венера ♀",   planet: result.venus },
                  { label: "Марс ♂",     planet: result.mars },
                ].map(({ label, planet }) => (
                  <div key={label} className="flex items-center justify-between">
                    <span className="text-text-muted text-sm">{label}</span>
                    <span className="text-text-primary text-sm">{planet.sign}</span>
                  </div>
                ))}
              </div>
            </Card>

            {interpretation ? (
              <Card>
                <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">
                  {t("natal.interpretation")}
                </p>
                <p className="text-text-muted text-xs leading-relaxed">
                  {interpretation}
                  {interpretLoading && <span className="animate-pulse">▍</span>}
                </p>
              </Card>
            ) : (
              <Button
                variant="primary"
                className="w-full"
                onClick={handleInterpret}
                disabled={interpretLoading}
              >
                {interpretLoading ? t("natal.reading") : t("natal.get_interpretation")}
              </Button>
            )}
          </div>
        ) : null}
      </main>

      <BottomNav active="natal" onNavigate={onNavigate} />

      <PaywallSheet
        open={showPaywall}
        onClose={() => setShowPaywall(false)}
      />
    </div>
  );
}
