import { useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { TIMEZONES } from "../constants/timezones";
import { useAuth } from "../context/AuthContext";
import { validateDay, validateMonth, validateYear, validateDateExists } from "../utils/validate";
import { getZodiacSign } from "../utils/zodiac";
import { Logo } from "./Logo";
import { ZodiacGlyph } from "./ZodiacGlyph";

interface Props { onClose: () => void; }

const MONTHS_RU = ["", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"];
const MONTHS_EN = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

const RULERS: Record<string, [string, string]> = {
  Aries: ["Марс", "Mars"], Taurus: ["Венера", "Venus"], Gemini: ["Меркурий", "Mercury"],
  Cancer: ["Луна", "Moon"], Leo: ["Солнце", "Sun"], Virgo: ["Меркурий", "Mercury"],
  Libra: ["Венера", "Venus"], Scorpio: ["Плутон", "Pluto"], Sagittarius: ["Юпитер", "Jupiter"],
  Capricorn: ["Сатурн", "Saturn"], Aquarius: ["Уран", "Uranus"], Pisces: ["Нептун", "Neptune"],
};

const ELEMENTS: Record<string, [string, string]> = {
  Aries: ["Огненный", "Fire"], Taurus: ["Земной", "Earth"], Gemini: ["Воздушный", "Air"],
  Cancer: ["Водный", "Water"], Leo: ["Огненный", "Fire"], Virgo: ["Земной", "Earth"],
  Libra: ["Воздушный", "Air"], Scorpio: ["Водный", "Water"], Sagittarius: ["Огненный", "Fire"],
  Capricorn: ["Земной", "Earth"], Aquarius: ["Воздушный", "Air"], Pisces: ["Водный", "Water"],
};

const CURRENT_YEAR = new Date().getFullYear();
const YEARS = Array.from({ length: CURRENT_YEAR - 1923 }, (_, i) => CURRENT_YEAR - i);
const DAYS = Array.from({ length: 31 }, (_, i) => i + 1);

export function OnboardingModal({ onClose }: Props) {
  const { t } = useTranslation();
  const { token, user, updateUser } = useAuth();
  const lang = user?.lang ?? "ru";
  const ru = lang === "ru";

  const [step, setStep] = useState(0);
  const [day, setDay] = useState("");
  const [month, setMonth] = useState("");
  const [year, setYear] = useState("");
  const [hour, setHour] = useState("");
  const [minute, setMinute] = useState("");
  const [city, setCity] = useState("");
  const [tz, setTz] = useState(Intl.DateTimeFormat().resolvedOptions().timeZone || "Europe/Moscow");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [cityInput, setCityInput] = useState(false);

  const dayRef = useRef<HTMLSelectElement>(null);
  const monthRef = useRef<HTMLSelectElement>(null);
  const yearRef = useRef<HTMLSelectElement>(null);
  const timeRef = useRef<HTMLInputElement>(null);

  const birthDate = day && month && year ? `${year}-${month.padStart(2, "0")}-${day.padStart(2, "0")}` : null;
  const zodiac = birthDate ? getZodiacSign(birthDate) : null;

  async function saveAllData() {
    setLoading(true);
    try {
      const body: Record<string, unknown> = {
        notifications_enabled: true,
        timezone: tz,
      };
      if (birthDate) body.birth_date = birthDate;
      if (hour) {
        body.birth_time = `${hour.padStart(2, "0")}:${(minute || "0").padStart(2, "0")}`;
        body.birth_time_known = true;
      }
      if (city) body.birth_city = city;

      const res = await fetch("/api/v1/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(body),
      });
      if (!res.ok) console.error("Onboarding save failed:", res.status, await res.text().catch(() => ""));
      updateUser({ has_birth_date: true });
    } catch (e) {
      console.error("Onboarding save error:", e);
    } finally {
      setLoading(false);
    }
  }

  async function handleNext() {
    if (step === 0) { setStep(1); return; }
    if (step === 1) {
      if (!day || !month || !year) return;
      const errs: Record<string, string> = {};
      const de = validateDay(day); if (de) errs.day = de;
      const me = validateMonth(month); if (me) errs.month = me;
      const ye = validateYear(year); if (ye) errs.year = ye;
      if (!de && !me && !ye) { const dx = validateDateExists(day, month, year); if (dx) errs.date = dx; }
      if (Object.values(errs).some(Boolean)) { setErrors(errs); return; }
      setStep(2);
      return;
    }
    if (step === 2) { setStep(3); return; }
    if (step === 3) {
      await saveAllData();
      onClose();
    }
  }

  const btnTexts = [t("onboarding.begin"), t("onboarding.next"), t("onboarding.next"), t("onboarding.enter_mystral")];
  const canNext = step === 0 || step === 2 || step === 3 || (step === 1 && !!day && !!month && !!year);

  const fieldStyle = (gold?: boolean): React.CSSProperties => ({
    padding: "14px 0", borderRadius: 14, textAlign: "center",
    background: "rgba(255,255,255,.04)",
    border: `1px solid ${gold ? "rgba(201,168,76,.22)" : "rgba(255,255,255,.08)"}`,
    cursor: "pointer", position: "relative", overflow: "hidden",
  });

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 200, height: "100vh", display: "flex", flexDirection: "column", overflow: "hidden", background: "radial-gradient(130% 60% at 50% -5%, #0F0A26 0%, #07060F 55%)" }}>

      {/* Top bar */}
      <div style={{ padding: "20px 24px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", gap: 7 }}>
          {[0, 1, 2, 3].map(i => (
            <div key={i} style={{ width: i === step ? 22 : 7, height: 7, borderRadius: 99, background: i === step ? "linear-gradient(90deg,#C9A84C,#E8CD7E)" : "rgba(255,255,255,.16)", transition: ".3s" }} />
          ))}
        </div>
        {step < 3 && (
          <button onClick={onClose} style={{ fontSize: 13, color: "#8A8170", cursor: "pointer", background: "none", border: "none" }}>
            {t("onboarding.skip")}
          </button>
        )}
      </div>

      {/* Center */}
      <div key={step} style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", textAlign: "center", padding: "0 30px", animation: "mystral-fadeup .25s ease-out" }}>
        <div style={{ width: "100%", maxWidth: 460 }}>

          {/* STEP 0 — Welcome */}
          {step === 0 && (
            <>
              <div style={{ width: 130, height: 130, margin: "0 auto", filter: "drop-shadow(0 0 38px rgba(201,168,76,.5))", animation: "mystral-float 7s ease-in-out infinite" }}>
                <Logo size={120} />
              </div>
              <p className="font-cinzel" style={{ fontSize: 13, letterSpacing: ".4em", color: "#E8CD7E", marginTop: 30 }}>MYSTRAL</p>
              <p className="font-cormorant" style={{ fontSize: 38, color: "#F0E9DA", lineHeight: 1.1, marginTop: 14 }}>
                {t("onboarding.welcome_title")}
              </p>
              <p style={{ fontSize: 15, lineHeight: 1.7, color: "#A89E8B", margin: "16px auto 0", maxWidth: 380 }}>
                {t("onboarding.welcome_desc")}
              </p>
            </>
          )}

          {/* STEP 1 — Birth date */}
          {step === 1 && (
            <>
              <p className="font-cormorant" style={{ fontSize: 34, color: "#F0E9DA", lineHeight: 1.1, marginTop: 24 }}>
                {t("onboarding.when_born")}
              </p>
              <p style={{ fontSize: 14, color: "#A89E8B", margin: "10px auto 28px", maxWidth: 340 }}>
                {t("onboarding.birth_determines")}
              </p>

              <div style={{ display: "flex", gap: 10 }}>
                {/* DAY */}
                <div style={{ ...fieldStyle(true), flex: 1 }} onClick={() => dayRef.current?.focus()}>
                  <select ref={dayRef} value={day} onChange={e => { setDay(e.target.value); setErrors({}); }}
                    style={{ position: "absolute", inset: 0, opacity: 0, width: "100%", height: "100%", cursor: "pointer" }}>
                    <option value="">—</option>
                    {DAYS.map(d => <option key={d} value={String(d)}>{d}</option>)}
                  </select>
                  <div style={{ fontSize: 10, color: "#6E6757", letterSpacing: ".1em" }}>{t("onboarding.day_label")}</div>
                  <div className="font-cormorant" style={{ fontSize: 26, color: "#F0E9DA", marginTop: 2 }}>{day || "—"}</div>
                </div>

                {/* MONTH */}
                <div style={{ ...fieldStyle(true), flex: 1.4 }} onClick={() => monthRef.current?.focus()}>
                  <select ref={monthRef} value={month} onChange={e => { setMonth(e.target.value); setErrors({}); }}
                    style={{ position: "absolute", inset: 0, opacity: 0, width: "100%", height: "100%", cursor: "pointer" }}>
                    <option value="">—</option>
                    {(ru ? MONTHS_RU : MONTHS_EN).slice(1).map((m, i) => <option key={i + 1} value={String(i + 1)}>{m}</option>)}
                  </select>
                  <div style={{ fontSize: 10, color: "#6E6757", letterSpacing: ".1em" }}>{t("onboarding.month_label")}</div>
                  <div className="font-cormorant" style={{ fontSize: 26, color: "#F0E9DA", marginTop: 2 }}>
                    {month ? (ru ? MONTHS_RU[Number(month)] : MONTHS_EN[Number(month)]) : "—"}
                  </div>
                </div>

                {/* YEAR */}
                <div style={{ ...fieldStyle(true), flex: 1.2 }} onClick={() => yearRef.current?.focus()}>
                  <select ref={yearRef} value={year} onChange={e => { setYear(e.target.value); setErrors({}); }}
                    style={{ position: "absolute", inset: 0, opacity: 0, width: "100%", height: "100%", cursor: "pointer" }}>
                    <option value="">—</option>
                    {YEARS.map(y => <option key={y} value={String(y)}>{y}</option>)}
                  </select>
                  <div style={{ fontSize: 10, color: "#6E6757", letterSpacing: ".1em" }}>{t("onboarding.year_label")}</div>
                  <div className="font-cormorant" style={{ fontSize: 26, color: "#F0E9DA", marginTop: 2 }}>{year || "—"}</div>
                </div>
              </div>

              {(errors.day || errors.month || errors.year || errors.date) && (
                <p style={{ color: "#D98A8A", fontSize: 12, marginTop: 8 }}>{errors.day || errors.month || errors.year || errors.date}</p>
              )}

              {/* Real native time input overlaid on the styled row (same pattern as
                  day/month/year above) so a plain click/tap opens the picker via the
                  browser's own default behavior — showPicker() alone isn't supported
                  everywhere (e.g. Safari < 16.4, some in-app WebViews) and silently
                  no-ops via the optional-chaining call, leaving the field unusable. */}
              <div style={{ marginTop: 12, width: "100%", position: "relative", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 16px", borderRadius: 14, background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,.08)", cursor: "pointer" }}>
                <input
                  ref={timeRef}
                  type="time"
                  value={hour ? `${hour.padStart(2, "0")}:${(minute || "0").padStart(2, "0")}` : ""}
                  onChange={e => {
                    if (e.target.value) { const [h, m] = e.target.value.split(":"); setHour(h); setMinute(m); }
                    else { setHour(""); setMinute(""); }
                  }}
                  style={{ position: "absolute", inset: 0, opacity: 0, width: "100%", height: "100%", cursor: "pointer", border: "none" }}
                />
                <span style={{ fontSize: 13.5, color: "#B6AC98" }}>{t("onboarding.birth_time")}</span>
                <span className="font-cormorant" style={{ fontSize: 20, color: "#F0E9DA" }}>
                  {hour ? `${hour.padStart(2, "0")}:${(minute || "0").padStart(2, "0")}` : "—"}
                </span>
              </div>
            </>
          )}

          {/* STEP 2 — Location */}
          {step === 2 && (
            <>
              <p className="font-cormorant" style={{ fontSize: 34, color: "#F0E9DA", lineHeight: 1.1, marginTop: 24 }}>
                {t("onboarding.where_born")}
              </p>
              <p style={{ fontSize: 14, color: "#A89E8B", margin: "10px auto 28px", maxWidth: 340 }}>
                {t("onboarding.place_needed")}
              </p>

              {cityInput ? (
                <input autoFocus value={city} onChange={e => setCity(e.target.value)} onBlur={() => { if (!city) setCityInput(false); }}
                  placeholder={t("onboarding.enter_city")} style={{ width: "100%", padding: "16px 18px", borderRadius: 14, background: "rgba(255,255,255,.04)", border: "1px solid rgba(201,168,76,.22)", color: "#F0E9DA", fontSize: 16, outline: "none" }} />
              ) : (
                <button onClick={() => setCityInput(true)} style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 18px", borderRadius: 14, background: "rgba(255,255,255,.04)", border: "1px solid rgba(201,168,76,.22)", cursor: "pointer", textAlign: "left" }}>
                  <div>
                    <div style={{ fontSize: 11, color: "#6E6757", letterSpacing: ".06em", textTransform: "uppercase" }}>{t("onboarding.city")}</div>
                    <div style={{ fontSize: 16, color: city ? "#F0E9DA" : "#6E6757", marginTop: 1 }}>{city || t("onboarding.select_city")}</div>
                  </div>
                  <span style={{ color: "#C9A84C", fontSize: 18 }}>›</span>
                </button>
              )}

              <div style={{ marginTop: 12, display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 18px", borderRadius: 14, background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,.08)" }}>
                <span style={{ fontSize: 13.5, color: "#B6AC98" }}>{t("onboarding.timezone")}</span>
                <select value={tz} onChange={e => setTz(e.target.value)} style={{ background: "transparent", border: "none", color: "#F0E9DA", fontSize: 15, textAlign: "right", outline: "none", maxWidth: 180 }}>
                  {TIMEZONES.map(t => <option key={t.value} value={t.value} style={{ background: "#0D0B1F" }}>{t.label}</option>)}
                </select>
              </div>
            </>
          )}

          {/* STEP 3 — Result */}
          {step === 3 && zodiac && (
            <>
              <div style={{ display: "flex", justifyContent: "center", margin: "0 auto" }}>
                <ZodiacGlyph sign={zodiac.en} size={150} />
              </div>
              <p className="font-cinzel uppercase" style={{ fontSize: 11, letterSpacing: ".34em", color: "#C9A84C", marginTop: 8 }}>
                {t("onboarding.stars_ready")}
              </p>
              <p className="font-cormorant" style={{ fontSize: 40, color: "#F0E9DA", lineHeight: 1, marginTop: 8 }}>
                {t("onboarding.you_are", { sign: ru ? zodiac.sign : zodiac.en })}
              </p>
              <p style={{ fontSize: 14.5, lineHeight: 1.7, color: "#A89E8B", margin: "14px auto 0", maxWidth: 360 }}>
                {t("onboarding.result_desc", {
                  element: ru ? (ELEMENTS[zodiac.en]?.[0] ?? "Огненный") : (ELEMENTS[zodiac.en]?.[1] ?? "Fire"),
                  ruler: ru ? (RULERS[zodiac.en]?.[0] ?? "Марса") : (RULERS[zodiac.en]?.[1] ?? "Mars"),
                })}
              </p>
            </>
          )}
        </div>
      </div>

      {/* Bottom */}
      <div style={{ padding: "18px 30px 30px", width: "100%", maxWidth: 520, margin: "0 auto", display: "flex", gap: 12 }}>
        {step > 0 && (
          <button onClick={() => setStep(step - 1)} style={{ height: 52, flex: 1, borderRadius: 16, background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,.1)", color: "#B6AC98", fontSize: 15, cursor: "pointer" }}>
            {t("onboarding.back")}
          </button>
        )}
        <button onClick={handleNext} disabled={loading || !canNext}
          style={{ height: 52, flex: step > 0 ? 2 : 1, borderRadius: 16, background: canNext ? "linear-gradient(100deg,#A9882F,#C9A84C 50%,#E8CD7E)" : "rgba(255,255,255,.06)", color: canNext ? "#1A1206" : "#6E6757", fontWeight: 600, fontSize: 15.5, cursor: canNext ? "pointer" : "default", boxShadow: canNext ? "0 10px 28px -8px rgba(201,168,76,.5)" : "none", border: "none", transition: ".2s" }}>
          {loading ? "..." : btnTexts[step]}
        </button>
      </div>
    </div>
  );
}
