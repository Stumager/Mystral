import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { NatalWheel } from "../components/NatalWheel";
import { PaywallSheet } from "../components/PaywallSheet";
import { ShareCard } from "../components/ShareCard";
import { BottomNav, Button, Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { streamRequest } from "../utils/api";
import { validateDay, validateMonth, validateYear, validateDateExists, validateName, validateCity } from "../utils/validate";

interface NatalChartProps { onNavigate: (page: string) => void; }

interface PlanetData {
  name: string; name_ru: string; name_en: string; symbol: string;
  sign: string; sign_ru: string; degree: number; abs_pos: number;
  house: number | null; retrograde: boolean; type?: string;
}
interface HouseData { number: number; sign: string; sign_ru: string; degree: number; abs_pos: number; }
interface AspectData {
  planet1: string; planet2: string; planet1_ru: string; planet2_ru: string;
  type: string; name_ru: string; symbol: string; orb: number; harmony: boolean;
}
interface Stellium {
  type: string; name_ru: string; name_en: string;
  planets_ru: string[]; planets_en: string[];
}
interface ChartResult {
  planets: PlanetData[]; extra_points: PlanetData[]; houses: HouseData[];
  aspects: AspectData[];
  ascendant: { sign: string; sign_ru: string; degree: number };
  midheaven: { sign: string; sign_ru: string; degree: number };
  part_of_fortune: { sign: string; sign_ru: string; degree: number; house: number | null };
  stelliums: Stellium[];
  element_balance: { fire: number; earth: number; air: number; water: number };
  modality_balance: { cardinal: number; fixed: number; mutable: number };
  dominant_sign: string; dominant_sign_ru: string;
}

const SECTIONS = ["personality", "planets", "houses", "aspects", "transits"] as const;
type Section = typeof SECTIONS[number];

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
  const [chart, setChart] = useState<ChartResult | null>(null);
  const [activeSection, setActiveSection] = useState<Section>("personality");
  const [interpretations, setInterpretations] = useState<Partial<Record<Section, string>>>({});
  const [loadingSection, setLoadingSection] = useState<Section | null>(null);
  const [errorSection, setErrorSection] = useState<Section | null>(null);
  const interpretRequestId = useRef(0);
  const [showPaywall, setShowPaywall] = useState(false);
  const [showShareCard, setShowShareCard] = useState(false);
  const [wheelSize, setWheelSize] = useState(() => computeWheelSize());

  useEffect(() => {
    const onResize = () => setWheelSize(computeWheelSize());
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

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
    day: parseInt(form.day), hour: parseInt(form.hour || "12"), minute: parseInt(form.minute || "0"),
    city: form.city, lang,
  });

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
        method: "POST", headers: { "Content-Type": "application/json" },
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
  const elColors: Record<string, string> = { fire: "#ef4444", earth: "#a3e635", air: "#38bdf8", water: "#818cf8" };
  const elIcons: Record<string, string> = { fire: "^", earth: "v", air: "~", water: "o" };
  const elLabels: Record<string, string> = lang === "ru"
    ? { fire: "Огонь", earth: "Земля", air: "Воздух", water: "Вода" }
    : { fire: "Fire", earth: "Earth", air: "Air", water: "Water" };
  const sectionLabels: Record<Section, string> = lang === "ru"
    ? { personality: "Личность", planets: "Планеты", houses: "Дома", aspects: "Аспекты", transits: "Транзиты" }
    : { personality: "Personality", planets: "Planets", houses: "Houses", aspects: "Aspects", transits: "Transits" };

  // NatalWheel matches aspects.planet1/planet2 (raw keys like "sun") against
  // planets[].name internally, so this must stay in the English key-space
  // rather than the localized display name.
  const wheelPlanets = useMemo(() => (chart?.planets ?? []).map(p => ({
    name: p.name_en,
    sign: p.sign,
    degree: p.abs_pos,
    retrograde: p.retrograde,
  })), [chart]);
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
              <input className={inputCls} placeholder={t("natal.name")} value={form.name} onChange={setField("name")} />
              {formErrors.name && <p className="text-red-400 text-xs mt-1">{formErrors.name}</p>}
            </div>
            <div>
              <div className="grid grid-cols-3 gap-2">
                <input className={inputCls} placeholder={t("natal.day")} type="number" min="1" max="31" value={form.day} onChange={setField("day")} />
                <input className={inputCls} placeholder={t("natal.month")} type="number" min="1" max="12" value={form.month} onChange={setField("month")} />
                <input className={inputCls} placeholder={t("natal.year")} type="number" min="1900" max="2025" value={form.year} onChange={setField("year")} />
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
              <input className={inputCls} placeholder={t("natal.birth_city")} value={form.city} onChange={setField("city")} />
              {formErrors.city && <p className="text-red-400 text-xs mt-1">{formErrors.city}</p>}
            </div>
            <p className="text-text-faint text-[10px] text-center">{t("natal.time_hint")}</p>
            <label className="flex items-center gap-2 cursor-pointer self-start">
              <input type="checkbox" checked={saveToProfile} onChange={e => setSaveToProfile(e.target.checked)} className="w-3.5 h-3.5 accent-violet-600" />
              <span className="text-text-muted text-xs">{t("natal.save_to_profile")}</span>
            </label>
            {error && <p className="text-red-400 text-xs text-center">{error}</p>}
            <Button variant="primary" className="w-full mt-1" onClick={handleCalculate} disabled={loading || !canSubmit}>
              {loading ? t("natal.calculating") : t("natal.calculate")}
            </Button>
          </div>
        ) : chart ? (
          <div className="flex flex-col gap-4">

            {/* Natal Wheel + AI Interpretation */}
            <div className="grid grid-cols-1 md:grid-cols-[480px_1fr] gap-8 items-start">
              <div style={{
                position: "relative", width: "100%", display: "flex", justifyContent: "center",
                padding: "20px 0", background: "radial-gradient(circle at 50% 50%, rgba(75,60,134,.15), transparent 70%)",
                borderRadius: 24,
              }}>
                <NatalWheel planets={wheelPlanets} houses={wheelHouses} aspects={wheelAspects} size={wheelSize} />
              </div>

              <Card>
                <p className="font-cinzel uppercase mb-3" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                  {lang === "ru" ? "AI Интерпретация" : "AI Interpretation"}
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
                    <p className="text-text-muted text-xs leading-relaxed">{interpretations[activeSection]}</p>
                    <button onClick={() => setShowShareCard(true)}
                      style={{ width: "100%", height: 44, marginTop: 12, borderRadius: 14, border: "1px solid rgba(201,168,76,.25)", background: "transparent", color: "#C9A84C", fontSize: 13, cursor: "pointer" }}>
                      {t("share.share_btn")}
                    </button>
                  </>
                ) : (
                  <button onClick={() => fetchInterpretation(activeSection)}
                    style={{ width: "100%", height: 44, borderRadius: 14, border: "none", background: "#C9A84C", color: "#07060F", fontSize: 13, fontWeight: 600, cursor: "pointer" }}>
                    {lang === "ru" ? "Получить интерпретацию" : "Get interpretation"}
                  </button>
                )}
              </Card>
            </div>

            {/* Stelliums */}
            {chart.stelliums.length > 0 && chart.stelliums.map((s, i) => (
              <div key={i} className="rounded-xl px-4 py-3" style={{ background: "rgba(201,168,76,0.08)", border: "1px solid rgba(201,168,76,0.25)" }}>
                <span className="font-display text-sm" style={{ color: "#C9A84C" }}>
                  * {lang === "ru" ? "Стеллиум" : "Stellium"} {s.type === "sign" ? (lang === "ru" ? "в" : "in") : ""} {lang === "ru" ? s.name_ru : s.name_en}
                </span>
                <p className="text-text-muted text-xs mt-1">{(lang === "ru" ? s.planets_ru : s.planets_en).join(", ")}</p>
              </div>
            ))}

            {/* Big Three */}
            <Card>
              <p className="font-cinzel uppercase mb-3" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>{t("natal.big_three")}</p>
              <div className="flex flex-col gap-2.5">
                {[
                  { label: lang === "ru" ? "Солнце" : "Sun", data: chart.planets[0] },
                  { label: lang === "ru" ? "Луна" : "Moon", data: chart.planets[1] },
                  { label: lang === "ru" ? "Асцендент" : "Ascendant",
                    data: { sign_ru: chart.ascendant.sign_ru, sign: chart.ascendant.sign, degree: chart.ascendant.degree } },
                  { label: lang === "ru" ? "MC (Середина Неба)" : "MC (Midheaven)",
                    data: { sign_ru: chart.midheaven.sign_ru, sign: chart.midheaven.sign, degree: chart.midheaven.degree } },
                ].map(({ label, data }) => (
                  <div key={label} className="flex items-center justify-between">
                    <span className="text-text-muted text-sm">{label}</span>
                    <span className="font-display text-sm" style={{ color: "#C9A84C" }}>
                      {lang === "ru" ? data.sign_ru : data.sign} <span className="text-text-faint text-xs">{data.degree}°</span>
                    </span>
                  </div>
                ))}
              </div>
            </Card>

            {/* All Planets */}
            <Card>
              <p className="font-cinzel uppercase mb-3" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>{t("natal.planets")}</p>
              <div className="flex flex-col">
                {chart.planets.map(p => (
                  <div key={p.name} className="text-xs" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0", borderBottom: "1px solid rgba(255,255,255,.06)" }}>
                    <span className="text-text-muted">
                      {p.symbol} {lang === "ru" ? p.name_ru : p.name_en}
                      {p.retrograde && <span className="text-red-400 ml-1">R</span>}
                    </span>
                    <span className="text-text-primary">
                      {lang === "ru" ? p.sign_ru : p.sign} {p.degree}°
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
                  {lang === "ru" ? "Дополнительные точки" : "Additional Points"}
                </p>
                <div className="flex flex-col gap-1.5">
                  {chart.extra_points.map(p => (
                    <div key={p.name} className="flex items-center justify-between text-xs">
                      <span className="text-text-muted">{p.symbol} {lang === "ru" ? p.name_ru : p.name_en}</span>
                      <span className="text-text-primary">
                        {lang === "ru" ? p.sign_ru : p.sign} {p.degree}°
                        {p.house && <span className="text-text-faint ml-1">({lang === "ru" ? "дом" : "H"} {p.house})</span>}
                      </span>
                    </div>
                  ))}
                  {chart.part_of_fortune && (
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-text-muted">⊕ {lang === "ru" ? "Часть Фортуны" : "Part of Fortune"}</span>
                      <span className="text-text-primary">
                        {lang === "ru" ? chart.part_of_fortune.sign_ru : chart.part_of_fortune.sign} {chart.part_of_fortune.degree}°
                        {chart.part_of_fortune.house && <span className="text-text-faint ml-1">({lang === "ru" ? "дом" : "H"} {chart.part_of_fortune.house})</span>}
                      </span>
                    </div>
                  )}
                </div>
              </Card>
            )}

            {/* Houses Table */}
            <Card>
              <p className="font-cinzel uppercase mb-3" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                {lang === "ru" ? "Куспиды домов" : "House Cusps"}
              </p>
              <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                {chart.houses.map(h => (
                  <div key={h.number} className="flex items-center justify-between text-xs py-0.5">
                    <span className="text-text-muted">{lang === "ru" ? "Дом" : "House"} {h.number}</span>
                    <span className="text-text-primary">{lang === "ru" ? h.sign_ru : h.sign} {h.degree}°</span>
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
                {lang === "ru" ? "Доминантный знак" : "Dominant"}: <span style={{ color: "#C9A84C" }}>{chart.dominant_sign_ru || chart.dominant_sign}</span>
              </p>
            </Card>

            {/* Aspects */}
            {chart.aspects.length > 0 && (
              <Card>
                <p className="font-cinzel uppercase mb-3" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>{t("natal.aspects_label")}</p>
                <div className="flex flex-col">
                  {chart.aspects.slice(0, 7).map((a, i) => {
                    const aspectColor = (a.type === "Sextile" || a.type === "Trine") ? "#6E9A8A"
                      : (a.type === "Square" || a.type === "Opposition") ? "#D98A8A"
                      : a.type === "Conjunction" ? "#C9A84C"
                      : a.harmony ? "#6E9A8A" : "#D98A8A";
                    return (
                      <div key={i} className="text-xs" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0", borderBottom: "1px solid rgba(255,255,255,.06)" }}>
                        <span className="text-text-muted">{a.planet1_ru} {a.symbol} {a.planet2_ru}</span>
                        <span style={{ color: aspectColor }}>
                          {a.name_ru} <span className="text-text-faint">{a.orb}°</span>
                        </span>
                      </div>
                    );
                  })}
                </div>
              </Card>
            )}

          </div>
        ) : null}
      </main>

      <BottomNav active="natal" onNavigate={onNavigate} />
      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
      {showShareCard && (
        <ShareCard
          type="natal"
          title={lang === "ru" ? "Натальная карта" : "Natal Chart"}
          onClose={() => setShowShareCard(false)}
        />
      )}
    </div>
  );
}
