import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { NatalWheel } from "../components/NatalWheel";
import { PaywallSheet } from "../components/PaywallSheet";
import { ShareCard } from "../components/ShareCard";
import { BottomNav, Button, Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { streamRequest } from "../utils/api";
import { stripMarkdown } from "../utils/markdown";
import { validateDay, validateMonth, validateYear, validateDateExists, validateName, validateCity } from "../utils/validate";

interface NatalChartProps { onNavigate: (page: string) => void; }

interface PlanetData {
  name: string; name_ru: string; name_en: string; name_local: string; symbol: string;
  sign: string; sign_ru: string; sign_local: string; degree: number; abs_pos: number;
  house: number | null; retrograde: boolean; type?: string;
}
interface HouseData { number: number; sign: string; sign_ru: string; sign_local: string; degree: number; abs_pos: number; }
interface AspectData {
  planet1: string; planet2: string; planet1_ru: string; planet2_ru: string;
  planet1_en: string; planet2_en: string; planet1_local: string; planet2_local: string;
  type: string; name_ru: string; name_en: string; name_local: string; symbol: string; orb: number; harmony: boolean;
  category: "tense" | "harmonious" | "minor" | "neutral"; is_major: boolean;
}
interface HouseSystem { code: string; name: string; }
interface ChartOptions {
  house_systems: HouseSystem[];
  default_house_system: string;
  points: string[];
  default_points: string[];
}
interface Stellium {
  type: string; name_ru: string; name_en: string; name_local: string;
  planets_ru: string[]; planets_en: string[]; planets_local: string[];
}
interface ChartResult {
  planets: PlanetData[]; extra_points: PlanetData[]; houses: HouseData[];
  aspects: AspectData[];
  ascendant: { sign: string; sign_ru: string; sign_local: string; degree: number; abs_pos: number };
  midheaven: { sign: string; sign_ru: string; sign_local: string; degree: number; abs_pos: number };
  part_of_fortune: PlanetData | null;
  house_system: HouseSystem;
  points_included: string[];
  stelliums: Stellium[];
  element_balance: { fire: number; earth: number; air: number; water: number };
  modality_balance: { cardinal: number; fixed: number; mutable: number };
  dominant_sign: string; dominant_sign_ru: string; dominant_sign_local: string;
  time_known: boolean; time_used: string;
}

const SECTIONS = ["personality", "planets", "houses", "aspects", "transits"] as const;
type Section = typeof SECTIONS[number];

// Mirrors the wheel's line colours so the table and the drawing read as one
// thing — the reference convention verified in TZ-103 step 0: red tense,
// blue harmonious, green minor, gold neutral (conjunction).
const ASPECT_CATEGORY_COLOR: Record<string, string> = {
  tense: "#CE4A4A",
  harmonious: "#5A8CD2",
  minor: "#609E74",
  neutral: "#C9A84C",
};

function computeWheelSize() {
  if (typeof window === "undefined") return 480;
  return window.innerWidth >= 768 ? 480 : Math.min(window.innerWidth - 48, 520);
}

export function NatalChart({ onNavigate }: NatalChartProps) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const lang = user?.lang ?? "ru";
  const [step, setStep] = useState<"form" | "result">("form");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [saveToProfile, setSaveToProfile] = useState(true);
  const [form, setForm] = useState({ name: "", day: "", month: "", year: "", hour: "", minute: "", city: "" });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  // TZ-103. The backend owns both lists (GET /natal/options) so the form can't
  // offer a house system kerykeion would reject; these are only the fallback
  // for the moment before that request lands.
  const [options, setOptions] = useState<ChartOptions | null>(null);
  const [houseSystem, setHouseSystem] = useState("P");
  const [points, setPoints] = useState<string[]>(["nodes", "lilith", "chiron", "part_of_fortune"]);
  const [showOptions, setShowOptions] = useState(false);
  const [chart, setChart] = useState<ChartResult | null>(null);
  const [activeSection, setActiveSection] = useState<Section>("personality");
  const [interpretations, setInterpretations] = useState<Partial<Record<Section, string>>>({});
  const [loadingSection, setLoadingSection] = useState<Section | null>(null);
  const [errorSection, setErrorSection] = useState<Section | null>(null);
  const interpretRequestId = useRef(0);
  const [showPaywall, setShowPaywall] = useState(false);
  const [showShareCard, setShowShareCard] = useState(false);
  const [showAllAspects, setShowAllAspects] = useState(false);
  const [wheelSize, setWheelSize] = useState(() => computeWheelSize());
  const nameRef = useRef<HTMLInputElement>(null);
  const dayRef = useRef<HTMLInputElement>(null);
  const monthRef = useRef<HTMLInputElement>(null);
  const yearRef = useRef<HTMLInputElement>(null);
  const cityRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const onResize = () => setWheelSize(computeWheelSize());
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  const optionsLoaded = useRef(false);
  useEffect(() => {
    if (optionsLoaded.current || !token) return;
    optionsLoaded.current = true;
    fetch("/api/v1/natal/options", { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then((o: ChartOptions) => {
        setOptions(o);
        setHouseSystem(o.default_house_system);
        setPoints(o.default_points);
      })
      // The defaults above already match the server's, so a failed options
      // fetch costs the user the extra asteroids, not the chart itself.
      .catch(() => {});
  }, [token]);

  const profileLoaded = useRef(false);
  useEffect(() => {
    if (profileLoaded.current || !token) return;
    profileLoaded.current = true;
    fetch("/api/v1/profile", { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => {
        if (data.birth_date || data.birth_city) {
          const [y, m, d] = (data.birth_date ?? "").split("-");
          const [h, min] = (data.birth_time ?? "").split(":");
          setForm(prev => ({
            name: data.birth_name || prev.name, year: y || prev.year, month: m || prev.month,
            day: d || prev.day, hour: h || prev.hour, minute: min || prev.minute,
            city: data.birth_city || prev.city,
          }));
        }
      }).catch(() => {});
  }, [token]);

  const setField = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm(prev => ({ ...prev, [field]: e.target.value }));
    setFormErrors(prev => ({ ...prev, [field]: "", date: "" }));
  };

  const buildBody = () => ({
    name: form.name, year: parseInt(form.year), month: parseInt(form.month),
    day: parseInt(form.day),
    // QA-002: null (not a silent 12/0 default) so the backend can tell
    // "birth time not provided" apart from an explicit midnight/noon entry
    // and flag the result as approximate.
    hour: form.hour !== "" ? parseInt(form.hour) : null,
    minute: form.minute !== "" ? parseInt(form.minute) : null,
    city: form.city, lang,
    house_system: houseSystem, points,
  });

  function togglePoint(id: string) {
    setPoints(prev => prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]);
  }

  async function handleCalculate() {
    const errs: Record<string, string> = {};
    const ne = validateName(form.name); if (ne) errs.name = ne;
    const de = validateDay(form.day); if (de) errs.day = de;
    const me = validateMonth(form.month); if (me) errs.month = me;
    const ye = validateYear(form.year); if (ye) errs.year = ye;
    const ce = validateCity(form.city); if (ce) errs.city = ce;
    if (!de && !me && !ye) { const dex = validateDateExists(form.day, form.month, form.year); if (dex) errs.date = dex; }
    if (Object.values(errs).some(Boolean)) { setFormErrors(errs); return; }
    setLoading(true); setError("");
    try {
      const res = await fetch("/api/v1/natal/calculate", {
        method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(buildBody()),
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: "Server error" }));
        throw new Error(errData.detail || `HTTP ${res.status}`);
      }
      const data = await res.json();
      setChart(data);
      setStep("result");
      setInterpretations({}); setActiveSection("personality"); setErrorSection(null); setLoadingSection(null);

      if (saveToProfile && token) {
        const b = buildBody();
        const pb: Record<string, unknown> = {
          birth_city: b.city, birth_name: b.name,
          birth_date: `${b.year}-${String(b.month).padStart(2, "0")}-${String(b.day).padStart(2, "0")}`,
        };
        if (form.hour) { pb.birth_time = `${String(b.hour).padStart(2, "0")}:${String(b.minute).padStart(2, "0")}`; pb.birth_time_known = true; }
        fetch("/api/v1/profile", { method: "PUT", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify(pb) }).catch(() => {});
      }
    } catch (e) { setError(e instanceof Error && e.message !== "Server error" ? e.message : t("natal.calc_error")); }
    finally { setLoading(false); }
  }

  function selectSection(section: Section) {
    if (section !== "personality" && user?.tier !== "pro") { setShowPaywall(true); return; }
    setActiveSection(section);
  }

  async function fetchInterpretation(section: Section) {
    setErrorSection(null);
    setLoadingSection(section);
    // Guards against a still-running stream from a previously requested
    // section appending its late chunks into this section's cached text.
    const requestId = ++interpretRequestId.current;
    const isStale = () => interpretRequestId.current !== requestId;

    setInterpretations(prev => ({ ...prev, [section]: "" }));
    try {
      await streamRequest("/natal/interpret", { ...buildBody(), section },
        (c) => { if (!isStale()) setInterpretations(prev => ({ ...prev, [section]: (prev[section] ?? "") + c })); },
        () => { if (!isStale()) setLoadingSection(null); },
        token ?? undefined,
        () => {
          if (isStale()) return;
          setErrorSection(section);
          setLoadingSection(null);
          setInterpretations(prev => { const next = { ...prev }; delete next[section]; return next; });
        },
      );
    } catch (e: unknown) {
      if (isStale()) return;
      const err = e as { code?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setErrorSection(section);
      setLoadingSection(null);
      setInterpretations(prev => { const next = { ...prev }; delete next[section]; return next; });
    }
  }

  const inputCls = "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 text-text-primary text-sm placeholder:text-text-faint focus:outline-none focus:border-violet-600 transition-colors";
  const canSubmit = form.name && form.day && form.month && form.year && form.city;
  // Кнопка визуально не отличается disabled/enabled без явного стиля (см.
  // Button.tsx) — без этой подсказки пользователь не понимает, что расчёт
  // блокирует конкретно незаполненное имя (оно не приходит из онбординга,
  // только из Профиля или прошлого успешного расчёта) (ТЗ-071).
  const missingFields = useMemo(() => {
    const miss: { label: string; ref: React.RefObject<HTMLInputElement> }[] = [];
    if (!form.name) miss.push({ label: t("natal.name"), ref: nameRef });
    if (!form.day) miss.push({ label: t("natal.day"), ref: dayRef });
    if (!form.month) miss.push({ label: t("natal.month"), ref: monthRef });
    if (!form.year) miss.push({ label: t("natal.year"), ref: yearRef });
    if (!form.city) miss.push({ label: t("natal.birth_city"), ref: cityRef });
    return miss;
  }, [form.name, form.day, form.month, form.year, form.city, t]);
  const elColors: Record<string, string> = { fire: "#ef4444", earth: "#a3e635", air: "#38bdf8", water: "#818cf8" };
  const elIcons: Record<string, string> = { fire: "^", earth: "v", air: "~", water: "o" };
  const elLabels: Record<string, string> = lang === "ru"
    ? { fire: "Огонь", earth: "Земля", air: "Воздух", water: "Вода" }
    : { fire: "Fire", earth: "Earth", air: "Air", water: "Water" };
  const sectionLabels: Record<Section, string> = {
    personality: t("natal.sections.personality"),
    planets: t("natal.sections.planets"),
    houses: t("natal.sections.houses"),
    aspects: t("natal.sections.aspects"),
    transits: t("natal.sections.transits"),
  };

  const bigThreeForShare = chart ? [
    { label: chart.planets[0].name_local, sign: chart.planets[0].sign_local, degree: chart.planets[0].degree },
    { label: chart.planets[1].name_local, sign: chart.planets[1].sign_local, degree: chart.planets[1].degree },
    { label: lang === "ru" ? "Асцендент" : "Ascendant", sign: chart.ascendant.sign_local, degree: chart.ascendant.degree },
  ] : [];

  // NatalWheel matches aspects.planet1/planet2 (raw keys like "sun") against
  // planets[].name internally, so this must stay in the English key-space
  // rather than the localized display name.
  // TZ-103: the extra points now go on the wheel too — enabling Lilith and
  // then not seeing her anywhere on the drawing was the obvious gap. Aspect
  // matching is by the raw key, so `name` stays the key here and the wheel's
  // own glyph/colour tables key off the same string.
  const wheelPlanets = useMemo(() => {
    const bodies = [...(chart?.planets ?? []), ...(chart?.extra_points ?? [])];
    if (chart?.part_of_fortune) bodies.push(chart.part_of_fortune);
    return bodies.map(p => ({
      name: p.name,
      label: p.name_local,
      sign: p.sign_local,
      degree: p.abs_pos,
      retrograde: p.retrograde,
    }));
  }, [chart]);
  const wheelHouses = useMemo(() => (chart?.houses ?? []).map(h => ({
    number: h.number, degree: h.abs_pos,
  })), [chart]);
  const wheelAspects = useMemo(() => (chart?.aspects ?? []).map(a => ({
    planet1: a.planet1, planet2: a.planet2, type: a.type, orb: a.orb,
  })), [chart]);

  return (
    <div className="flex flex-col min-h-screen relative" style={{ background: "var(--gradient-page)", animation: "mystral-fadeup .3s ease-out" }}>
      <header className="flex items-center justify-between px-4 shrink-0 backdrop-blur-md lg:hidden" style={{ height: 46, background: "var(--bg-header)", borderBottom: "1px solid var(--border-gold)" }}>
        <button className="text-text-muted text-lg w-8" onClick={() => step === "result" ? setStep("form") : onNavigate("home")}>‹</button>
        <span className="font-cinzel tracking-[.26em]" style={{ fontSize: 13, letterSpacing: ".26em", color: "#E8CD7E" }}>{t("natal.title")}</span>
        <div className="w-8" />
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-6 pb-24">
        {step === "form" ? (
          <div className="flex flex-col gap-3">
            <p className="text-text-muted text-xs text-center mb-1">{t("natal.subtitle")}</p>
            <div>
              <input ref={nameRef} className={inputCls} placeholder={t("natal.name")} value={form.name} onChange={setField("name")} />
              {formErrors.name && <p className="text-red-400 text-xs mt-1">{formErrors.name}</p>}
            </div>
            <div>
              <div className="grid grid-cols-3 gap-2">
                <input ref={dayRef} className={inputCls} placeholder={t("natal.day")} type="number" min="1" max="31" value={form.day} onChange={setField("day")} />
                <input ref={monthRef} className={inputCls} placeholder={t("natal.month")} type="number" min="1" max="12" value={form.month} onChange={setField("month")} />
                <input ref={yearRef} className={inputCls} placeholder={t("natal.year")} type="number" min="1900" max="2025" value={form.year} onChange={setField("year")} />
              </div>
              {(formErrors.day || formErrors.month || formErrors.year || formErrors.date) && (
                <p className="text-red-400 text-xs mt-1">{formErrors.day || formErrors.month || formErrors.year || formErrors.date}</p>
              )}
            </div>
            <div className="grid grid-cols-2 gap-2">
              <input className={inputCls} placeholder={t("natal.hour")} type="number" min="0" max="23" value={form.hour} onChange={setField("hour")} />
              <input className={inputCls} placeholder={t("natal.minutes")} type="number" min="0" max="59" value={form.minute} onChange={setField("minute")} />
            </div>
            <div>
              <input ref={cityRef} className={inputCls} placeholder={t("natal.birth_city")} value={form.city} onChange={setField("city")} />
              {formErrors.city && <p className="text-red-400 text-xs mt-1">{formErrors.city}</p>}
            </div>
            <p className="text-text-faint text-[10px] text-center">{t("natal.time_hint")}</p>

            {/* Chart options — collapsed by default so the everyday path stays
                five fields and a button, and only someone who cares about
                Koch vs Placidus has to look at it. */}
            <button
              type="button"
              onClick={() => setShowOptions(v => !v)}
              className="flex items-center justify-between text-xs self-stretch"
              style={{ padding: "9px 12px", borderRadius: 12, cursor: "pointer",
                       background: "rgba(255,255,255,.03)", border: "1px solid rgba(201,168,76,.14)", color: "#A89E8B" }}
            >
              <span>{t("natal.chart_options")}</span>
              <span style={{ color: "#C9A84C" }}>{showOptions ? "−" : "+"}</span>
            </button>
            {showOptions && (
              <div className="flex flex-col gap-3" style={{ padding: "12px 14px", borderRadius: 14, background: "rgba(255,255,255,.02)", border: "1px solid rgba(201,168,76,.1)" }}>
                <div>
                  <p className="text-text-faint text-[10px] mb-1.5">{t("natal.house_system")}</p>
                  <select
                    value={houseSystem}
                    onChange={e => setHouseSystem(e.target.value)}
                    className={inputCls}
                    style={{ cursor: "pointer" }}
                  >
                    {(options?.house_systems ?? [{ code: "P", name: "Placidus" }]).map(hs => (
                      <option key={hs.code} value={hs.code} style={{ background: "#141024" }}>
                        {t(`natal.house_systems.${hs.code}`, hs.name)}
                        {hs.code === (options?.default_house_system ?? "P") ? ` — ${t("natal.default_label")}` : ""}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <p className="text-text-faint text-[10px] mb-1.5">{t("natal.extra_points")}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {(options?.points ?? points).map(id => {
                      const on = points.includes(id);
                      return (
                        <button
                          key={id}
                          type="button"
                          onClick={() => togglePoint(id)}
                          className="text-[11px]"
                          style={{
                            padding: "6px 11px", borderRadius: 99, cursor: "pointer",
                            background: on ? "rgba(201,168,76,.14)" : "rgba(255,255,255,.03)",
                            border: `1px solid ${on ? "rgba(201,168,76,.36)" : "rgba(255,255,255,.08)"}`,
                            color: on ? "#E8CD7E" : "#8A8170",
                          }}
                        >
                          {t(`natal.points.${id}`, id)}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            <label className="flex items-center gap-2 cursor-pointer self-start">
              <input type="checkbox" checked={saveToProfile} onChange={e => setSaveToProfile(e.target.checked)} className="w-3.5 h-3.5 accent-violet-600" />
              <span className="text-text-muted text-xs">{t("natal.save_to_profile")}</span>
            </label>
            {error && <p className="text-red-400 text-xs text-center">{error}</p>}
            <Button variant="primary" className="w-full mt-1" onClick={handleCalculate} disabled={loading || !canSubmit}>
              {loading ? t("natal.calculating") : t("natal.calculate")}
            </Button>
            {!loading && missingFields.length > 0 && (
              <p className="text-text-faint text-xs text-center -mt-1">
                {lang === "ru" ? "Заполните: " : "Fill in: "}
                {missingFields.map((f, i) => (
                  <span key={f.label}>
                    {i > 0 && ", "}
                    <button
                      type="button"
                      onClick={() => { f.ref.current?.focus(); f.ref.current?.scrollIntoView({ behavior: "smooth", block: "center" }); }}
                      style={{ color: "#C9A84C", background: "none", border: "none", padding: 0, font: "inherit", textDecoration: "underline", cursor: "pointer" }}
                    >
                      {f.label}
                    </button>
                  </span>
                ))}
              </p>
            )}
          </div>
        ) : chart ? (
          <div className="flex flex-col gap-4">

            {/* Natal Wheel */}
            <div style={{
              position: "relative", width: "100%", display: "flex", justifyContent: "center",
              padding: "20px 0", background: "radial-gradient(circle at 50% 50%, rgba(75,60,134,.15), transparent 70%)",
              borderRadius: 24,
            }}>
              <NatalWheel planets={wheelPlanets} houses={wheelHouses} aspects={wheelAspects}
                ascendant={chart.ascendant.abs_pos} midheaven={chart.midheaven.abs_pos} size={wheelSize} />
            </div>

            {/* Stelliums */}
            {chart.stelliums.length > 0 && chart.stelliums.map((s, i) => (
              <div key={i} className="rounded-xl px-4 py-3" style={{ background: "rgba(201,168,76,0.08)", border: "1px solid rgba(201,168,76,0.25)" }}>
                <span className="font-display text-sm" style={{ color: "#C9A84C" }}>
                  * {lang === "ru" ? "Стеллиум" : "Stellium"} {s.type === "sign" ? (lang === "ru" ? "в" : "in") : ""} {s.name_local}
                </span>
                <p className="text-text-muted text-xs mt-1">{s.planets_local.join(", ")}</p>
              </div>
            ))}

            {/* Big Three */}
            <Card>
              <p className="font-cinzel uppercase mb-3" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>{t("natal.big_three")}</p>
              <div className="flex flex-col gap-2.5">
                {[
                  { label: chart.planets[0].name_local, data: chart.planets[0] },
                  { label: chart.planets[1].name_local, data: chart.planets[1] },
                  { label: lang === "ru" ? "Асцендент" : "Ascendant",
                    data: { sign_local: chart.ascendant.sign_local, degree: chart.ascendant.degree } },
                  { label: lang === "ru" ? "MC (Середина Неба)" : "MC (Midheaven)",
                    data: { sign_local: chart.midheaven.sign_local, degree: chart.midheaven.degree } },
                ].map(({ label, data }) => (
                  <div key={label} className="flex items-center justify-between">
                    <span className="text-text-muted text-sm">{label}</span>
                    <span className="font-display text-sm" style={{ color: "#C9A84C" }}>
                      {data.sign_local} <span className="text-text-faint text-xs">{data.degree}°</span>
                    </span>
                  </div>
                ))}
              </div>
              {!chart.time_known && (
                <p className="text-text-faint text-[10px] mt-3 pt-3" style={{ borderTop: "1px solid rgba(255,255,255,.06)" }}>
                  {lang === "ru"
                    ? `Время рождения не указано — расчёт приблизительный (использовано ${chart.time_used}). Асцендент и дома могут отличаться от реальных.`
                    : `Birth time not provided — this is an approximate calculation (used ${chart.time_used}). Ascendant and houses may differ from the actual chart.`}
                </p>
              )}
            </Card>

            {/* All Planets */}
            <Card>
              <p className="font-cinzel uppercase mb-3" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>{t("natal.planets")}</p>
              <div className="flex flex-col">
                {chart.planets.map(p => (
                  <div key={p.name} className="text-xs" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0", borderBottom: "1px solid rgba(255,255,255,.06)" }}>
                    <span className="text-text-muted">
                      {p.symbol} {p.name_local}
                      {p.retrograde && <span className="text-red-400 ml-1">R</span>}
                    </span>
                    <span className="text-text-primary">
                      {p.sign_local} {p.degree}°
                      {p.house && <span className="text-text-faint ml-1">({lang === "ru" ? "дом" : "H"} {p.house})</span>}
                    </span>
                  </div>
                ))}
              </div>
            </Card>

            {/* Extra Points */}
            {(chart.extra_points.length > 0 || chart.part_of_fortune) && (
              <Card>
                <p className="font-cinzel uppercase mb-3" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                  {t("natal.extra_points")}
                </p>
                <div className="flex flex-col gap-1.5">
                  {/* Part of Fortune now comes back in the same shape as every
                      other point, so it no longer needs its own hand-built row. */}
                  {[...chart.extra_points, ...(chart.part_of_fortune ? [chart.part_of_fortune] : [])].map(p => (
                    <div key={p.name} className="flex items-center justify-between text-xs">
                      <span className="text-text-muted">
                        {p.symbol} {p.name_local}
                        {p.retrograde && <span className="text-red-400 ml-1">R</span>}
                      </span>
                      <span className="text-text-primary">
                        {p.sign_local} {p.degree}°
                        {p.house && <span className="text-text-faint ml-1">(H{p.house})</span>}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Houses Table */}
            <Card>
              <p className="font-cinzel uppercase mb-3" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                {lang === "ru" ? "Куспиды домов" : "House Cusps"}
                <span className="ml-2 normal-case tracking-normal" style={{ color: "#8A8170" }}>
                  {t(`natal.house_systems.${chart.house_system.code}`, chart.house_system.name)}
                </span>
              </p>
              <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                {chart.houses.map(h => (
                  <div key={h.number} className="flex items-center justify-between text-xs py-0.5">
                    <span className="text-text-muted">{lang === "ru" ? "Дом" : "House"} {h.number}</span>
                    <span className="text-text-primary">{h.sign_local} {h.degree}°</span>
                  </div>
                ))}
              </div>
            </Card>

            {/* Element Balance */}
            <Card>
              <p className="font-cinzel uppercase mb-3" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                {lang === "ru" ? "Баланс стихий" : "Element Balance"}
              </p>
              <div className="flex flex-col gap-2">
                {(["fire", "earth", "air", "water"] as const).map(el => (
                  <div key={el} className="flex items-center gap-2">
                    <span className="text-xs w-16">{elIcons[el]} {elLabels[el]}</span>
                    <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ background: "rgba(107,78,255,0.1)" }}>
                      <div className="h-full rounded-full" style={{ width: `${(chart.element_balance[el] / 10) * 100}%`, background: elColors[el] }} />
                    </div>
                    <span className="text-text-faint text-[10px] w-4 text-right">{chart.element_balance[el]}</span>
                  </div>
                ))}
              </div>
              <p className="text-text-faint text-[10px] mt-2">
                {lang === "ru" ? "Доминантный знак" : "Dominant"}: <span style={{ color: "#C9A84C" }}>{chart.dominant_sign_local || chart.dominant_sign}</span>
              </p>
            </Card>

            {/* Aspects */}
            {chart.aspects.length > 0 && (
              <Card>
                <p className="font-cinzel uppercase mb-3" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>{t("natal.aspects_label")}</p>
                <div className="flex flex-col">
                  {chart.aspects.slice(0, showAllAspects ? chart.aspects.length : 8).map((a, i) => (
                    <div key={i} className="text-xs" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0", borderBottom: "1px solid rgba(255,255,255,.06)" }}>
                      <span className="text-text-muted">{a.planet1_local} {a.symbol} {a.planet2_local}</span>
                      <span style={{ color: ASPECT_CATEGORY_COLOR[a.category] ?? "#C9A84C" }}>
                        {a.name_local} <span className="text-text-faint">{a.orb}°</span>
                      </span>
                    </div>
                  ))}
                </div>
                {chart.aspects.length > 8 && (
                  <button onClick={() => setShowAllAspects(v => !v)} className="text-[11px] mt-2 w-full text-center"
                    style={{ color: "#C9A84C", background: "none", border: "none", cursor: "pointer" }}>
                    {showAllAspects ? t("natal.show_less") : t("natal.show_all_aspects", { count: chart.aspects.length })}
                  </button>
                )}
                <div className="flex flex-wrap gap-3 mt-3 pt-3" style={{ borderTop: "1px solid rgba(255,255,255,.06)" }}>
                  {(["tense", "harmonious", "minor"] as const).map(cat => (
                    <span key={cat} className="flex items-center gap-1.5 text-[10px]" style={{ color: "#8A8170" }}>
                      <span style={{ width: 14, height: 2, borderRadius: 2, background: ASPECT_CATEGORY_COLOR[cat] }} />
                      {t(`natal.aspect_category.${cat}`)}
                    </span>
                  ))}
                </div>
              </Card>
            )}

            {/* Chart interpretation. The heading was hardcoded "AI
                Интерпретация"/"AI Interpretation" in two languages; natal.interpretation
                already exists, is AI-free per the TZ-095 glossary, and covers all six. */}
            <Card>
              <p className="font-cinzel uppercase mb-3" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                {t("natal.interpretation")}
              </p>
              <div className="flex gap-1 overflow-x-auto pb-2 mb-3">
                {SECTIONS.map(s => (
                  <button key={s} onClick={() => selectSection(s)}
                    className="flex items-center gap-1 text-[11px] whitespace-nowrap transition-colors shrink-0"
                    style={{
                      padding: "8px 16px",
                      borderRadius: 99,
                      background: activeSection === s ? "rgba(201,168,76,.15)" : "rgba(255,255,255,.04)",
                      color: activeSection === s ? "#E8CD7E" : "#A89E8B",
                      border: activeSection === s ? "1px solid rgba(201,168,76,.3)" : "1px solid transparent",
                    }}>
                    <span>{sectionLabels[s]}</span>
                    {s !== "personality" && user?.tier !== "pro" && <span className="text-[7px] ml-0.5" style={{ color: "#C9A84C" }}>Pro</span>}
                  </button>
                ))}
              </div>

              {errorSection === activeSection ? (
                <div className="flex flex-col items-center gap-3 py-2">
                  <p className="text-red-400 text-xs text-center">
                    {lang === "ru" ? "Не удалось сгенерировать интерпретацию, попробуйте снова" : "Failed to generate interpretation, try again"}
                  </p>
                  <button onClick={() => fetchInterpretation(activeSection)}
                    style={{ width: "100%", height: 44, borderRadius: 14, border: "none", background: "#C9A84C", color: "#07060F", fontSize: 13, fontWeight: 600, cursor: "pointer" }}>
                    {lang === "ru" ? "Получить интерпретацию" : "Get interpretation"}
                  </button>
                </div>
              ) : loadingSection === activeSection ? (
                <div className="flex items-center justify-center gap-2 py-3">
                  <span style={{ width: 14, height: 14, border: "2px solid rgba(201,168,76,.3)", borderTopColor: "#C9A84C", borderRadius: "50%", display: "inline-block" }}
                    className="animate-spin" />
                  <span className="text-text-muted text-xs">
                    {lang === "ru" ? "Генерируем интерпретацию…" : "Generating interpretation…"}
                  </span>
                </div>
              ) : interpretations[activeSection] !== undefined ? (
                <>
                  <p className="text-text-muted text-xs leading-relaxed">{stripMarkdown(interpretations[activeSection]!)}</p>
                </>
              ) : (
                <button onClick={() => fetchInterpretation(activeSection)}
                  style={{ width: "100%", height: 44, borderRadius: 14, border: "none", background: "#C9A84C", color: "#07060F", fontSize: 13, fontWeight: 600, cursor: "pointer" }}>
                  {lang === "ru" ? "Получить интерпретацию" : "Get interpretation"}
                </button>
              )}
            </Card>

          </div>
        ) : null}
      </main>

      <BottomNav active="natal" onNavigate={onNavigate} />
      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
      {showShareCard && chart && (
        <ShareCard
          type="natal"
          title={lang === "ru" ? "Натальная карта" : "Natal Chart"}
          natalName={form.name || undefined}
          bigThree={bigThreeForShare}
          onClose={() => setShowShareCard(false)}
        />
      )}
    </div>
  );
}
