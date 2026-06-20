import { useState } from "react";
import { useTranslation } from "react-i18next";
import { TIMEZONES } from "../constants/timezones";
import { useAuth } from "../context/AuthContext";
import { validateDay, validateMonth, validateYear, validateDateExists } from "../utils/validate";
import { Button } from "./ui";

interface Props {
  onClose: () => void;
}

export function OnboardingModal({ onClose }: Props) {
  const { t } = useTranslation();
  const { token, updateUser } = useAuth();
  const [step, setStep] = useState<"birth" | "notifications">("birth");

  const [day, setDay] = useState("");
  const [month, setMonth] = useState("");
  const [year, setYear] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const [tz, setTz] = useState("Europe/Moscow");

  function clearFieldError(field: string) {
    setErrors(prev => ({ ...prev, [field]: "" }));
  }

  async function handleBirthSubmit() {
    const errs: Record<string, string> = {};
    const dayErr = validateDay(day);
    const monthErr = validateMonth(month);
    const yearErr = validateYear(year);
    if (dayErr) errs.day = dayErr;
    if (monthErr) errs.month = monthErr;
    if (yearErr) errs.year = yearErr;
    if (!dayErr && !monthErr && !yearErr) {
      const dateErr = validateDateExists(day, month, year);
      if (dateErr) errs.date = dateErr;
    }
    if (Object.values(errs).some(Boolean)) { setErrors(errs); return; }

    setLoading(true);
    try {
      const birthDate = `${year}-${month.padStart(2, "0")}-${day.padStart(2, "0")}`;
      const res = await fetch("/api/v1/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ birth_date: birthDate }),
      });
      if (res.ok) {
        updateUser({ has_birth_date: true });
        setStep("notifications");
      }
    } catch {}
    finally { setLoading(false); }
  }

  async function handleEnableNotifications() {
    setLoading(true);
    try {
      await fetch("/api/v1/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ notifications_enabled: true, timezone: tz }),
      });
    } catch {}
    finally { setLoading(false); onClose(); }
  }

  const inputCls =
    "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 " +
    "text-text-primary text-sm text-center placeholder:text-text-faint " +
    "focus:outline-none focus:border-violet-600 transition-colors";
  const errCls = "text-red-400 text-[10px] mt-1 text-center";

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
        {step === "birth" ? (
          <>
            <div className="flex items-center justify-between">
              <p className="font-display text-text-primary text-lg">{t("onboarding.title")}</p>
              <button onClick={onClose} className="text-text-faint text-xl leading-none w-8 h-8 flex items-center justify-center">✕</button>
            </div>

            <p className="text-text-muted text-sm">{t("onboarding.subtitle")}</p>

            <div>
              <div className="grid grid-cols-3 gap-2">
                <input className={inputCls} placeholder={t("onboarding.day")} type="number" min="1" max="31"
                  value={day} onChange={e => { setDay(e.target.value); clearFieldError("day"); clearFieldError("date"); }} />
                <input className={inputCls} placeholder={t("onboarding.month")} type="number" min="1" max="12"
                  value={month} onChange={e => { setMonth(e.target.value); clearFieldError("month"); clearFieldError("date"); }} />
                <input className={inputCls} placeholder={t("onboarding.year")} type="number" min="1900" max="2025"
                  value={year} onChange={e => { setYear(e.target.value); clearFieldError("year"); clearFieldError("date"); }} />
              </div>
              {(errors.day || errors.month || errors.year || errors.date) && (
                <p className={errCls}>{errors.day || errors.month || errors.year || errors.date}</p>
              )}
            </div>

            <Button variant="primary" className="w-full" onClick={handleBirthSubmit} disabled={loading || !day || !month || !year}>
              {loading ? "..." : t("onboarding.continue")}
            </Button>

            <p className="text-text-faint text-[10px] text-center">{t("onboarding.hint")}</p>
          </>
        ) : (
          <>
            <div className="flex items-center justify-between">
              <p className="font-display text-text-primary text-lg">{t("onboarding.notif_title")}</p>
              <button onClick={onClose} className="text-text-faint text-xl leading-none w-8 h-8 flex items-center justify-center">✕</button>
            </div>

            <p className="text-text-muted text-sm">{t("onboarding.notif_subtitle")}</p>

            <div>
              <p className="text-text-faint text-[10px] mb-1.5">{t("onboarding.notif_tz")}</p>
              <select
                value={tz}
                onChange={e => setTz(e.target.value)}
                className="w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 text-text-primary text-sm focus:outline-none focus:border-violet-600 transition-colors"
              >
                {TIMEZONES.map(t => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>

            <Button variant="primary" className="w-full" onClick={handleEnableNotifications} disabled={loading}>
              {loading ? "..." : t("onboarding.notif_yes")}
            </Button>

            <button onClick={onClose} className="text-text-faint text-xs text-center py-1">
              {t("onboarding.notif_skip")}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
