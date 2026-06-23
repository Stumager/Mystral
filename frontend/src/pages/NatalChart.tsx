import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { PaywallSheet } from "../components/PaywallSheet";
import { BottomNav, Button, Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { streamRequest } from "../utils/api";
import { validateDay, validateMonth, validateYear, validateDateExists, validateName, validateCity } from "../utils/validate";

interface NatalChartProps { onNavigate: (page: string) => void; }

interface PlanetData {
  name: string; name_ru: string; name_en: string; symbol: string;
  sign: string; sign_ru: string; degree: number;
  house: number | null; retrograde: boolean; type?: string;
}
interface HouseData { number: number; sign: string; sign_ru: string; degree: number; }
interface AspectData {
  planet1_ru: string; planet2_ru: string;
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
const SECTION_ICONS: Record<Section, string> = {
  personality: "☀️", planets: "🪐", houses: "🏠", aspects: "🔗", transits: "⏰",
};

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
  const [svgContent, setSvgContent] = useState("");
  const [activeSection, setActiveSection] = useState<Section>("personality");
  const [interpretation, setInterpretation] = useState("");
  const [interpretLoading, setInterpretLoading] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);

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
      setInterpretation(""); setActiveSection("personality"); setSvgContent("");

      // Load SVG in background
      fetch("/api/v1/natal/svg", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildBody()),
      }).then(r => r.ok ? r.text() : "").then(setSvgContent).catch(() => {});

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

  async function handleInterpret(section: Section) {
    if (section !== "personality" && user?.tier !== "pro") { setShowPaywall(true); return; }
    setActiveSection(section);
    setInterpretLoading(true); setInterpretation("");
    try {
      await streamRequest("/natal/interpret", { ...buildBody(), section },
        (c) => setInterpretation(prev => prev + c),
        () => setInterpretLoading(false),
        token ?? undefined,
        (msg) => { setInterpretation(msg); setInterpretLoading(false); },
      );
    } catch (e: unknown) {
      const err = e as { code?: string; message?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setInterpretation(err.message || t("natal.connection_error"));
      setInterpretLoading(false);
    }
  }

  const inputCls = "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 text-text-primary text-sm placeholder:text-text-faint focus:outline-none focus:border-violet-600 transition-colors";
  const canSubmit = form.name && form.day && form.month && form.year && form.city;
  const elColors: Record<string, string> = { fire: "#ef4444", earth: "#a3e635", air: "#38bdf8", water: "#818cf8" };
  const elIcons: Record<string, string> = { fire: "🔥", earth: "🌍", air: "💨", water: "💧" };
  const elLabels: Record<string, string> = lang === "ru"
    ? { fire: "Огонь", earth: "Земля", air: "Воздух", water: "Вода" }
    : { fire: "Fire", earth: "Earth", air: "Air", water: "Water" };
  const sectionLabels: Record<Section, string> = lang === "ru"
    ? { personality: "Личность", planets: "Планеты", houses: "Дома", aspects: "Аспекты", transits: "Транзиты" }
    : { personality: "Personality", planets: "Planets", houses: "Houses", aspects: "Aspects", transits: "Transits" };

  return (
    <div className="flex flex-col min-h-screen relative" style={{ background: "var(--gradient-page)" }}>
      <header className="flex items-center justify-between px-4 shrink-0 backdrop-blur-md" style={{ height: 46, background: "var(--bg-header)", borderBottom: "1px solid var(--border-gold)" }}>
        <button className="text-text-muted text-lg w-8" onClick={() => step === "result" ? setStep("form") : onNavigate("home")}>‹</button>
        <span className="font-cinzel text-sm tracking-[.25em]" style={{ color: "#E8CD7E" }}>{t("natal.title")}</span>
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

            {/* SVG Chart Wheel */}
            {svgContent && (
              <Card className="overflow-hidden">
                <div
                  dangerouslySetInnerHTML={{ __html: svgContent }}
                  className="w-full [&>svg]:w-full [&>svg]:h-auto [&>svg]:max-h-[300px]"
                />
              </Card>
            )}

            {/* Stelliums */}
            {chart.stelliums.length > 0 && chart.stelliums.map((s, i) => (
              <div key={i} className="rounded-xl px-4 py-3" style={{ background: "rgba(201,168,76,0.08)", border: "1px solid rgba(201,168,76,0.25)" }}>
                <span className="font-display text-sm" style={{ color: "#C9A84C" }}>
                  ✦ {lang === "ru" ? "Стеллиум" : "Stellium"} {s.type === "sign" ? (lang === "ru" ? "в" : "in") : ""} {lang === "ru" ? s.name_ru : s.name_en}
                </span>
                <p className="text-text-muted text-xs mt-1">{(lang === "ru" ? s.planets_ru : s.planets_en).join(", ")}</p>
              </div>
            ))}

            {/* Big Three */}
            <Card>
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">{t("natal.big_three")}</p>
              <div className="flex flex-col gap-2.5">
                {[
                  { icon: "☀️", label: lang === "ru" ? "Солнце" : "Sun", data: chart.planets[0] },
                  { icon: "🌙", label: lang === "ru" ? "Луна" : "Moon", data: chart.planets[1] },
                  { icon: "⬆️", label: lang === "ru" ? "Асцендент" : "Ascendant",
                    data: { sign_ru: chart.ascendant.sign_ru, sign: chart.ascendant.sign, degree: chart.ascendant.degree } },
                  { icon: "🔝", label: lang === "ru" ? "MC (Середина Неба)" : "MC (Midheaven)",
                    data: { sign_ru: chart.midheaven.sign_ru, sign: chart.midheaven.sign, degree: chart.midheaven.degree } },
                ].map(({ icon, label, data }) => (
                  <div key={label} className="flex items-center justify-between">
                    <span className="text-text-muted text-sm">{icon} {label}</span>
                    <span className="font-display text-sm" style={{ color: "#C9A84C" }}>
                      {lang === "ru" ? data.sign_ru : data.sign} <span className="text-text-faint text-xs">{data.degree}°</span>
                    </span>
                  </div>
                ))}
              </div>
            </Card>

            {/* All Planets */}
            <Card>
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">{t("natal.planets")}</p>
              <div className="flex flex-col gap-1.5">
                {chart.planets.map(p => (
                  <div key={p.name} className="flex items-center justify-between text-xs">
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
                <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">
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
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">
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
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">
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
                <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">{t("natal.aspects_label")}</p>
                <div className="flex flex-col gap-1.5">
                  {chart.aspects.slice(0, 7).map((a, i) => (
                    <div key={i} className="flex items-center justify-between text-xs">
                      <span className="text-text-muted">{a.planet1_ru} {a.symbol} {a.planet2_ru}</span>
                      <span style={{ color: a.harmony ? "#4ade80" : "#f87171" }}>
                        {a.name_ru} <span className="text-text-faint">{a.orb}°</span>
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* AI Interpretation */}
            <Card>
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">
                {lang === "ru" ? "AI Интерпретация" : "AI Interpretation"}
              </p>
              <div className="flex gap-1 overflow-x-auto pb-2 mb-3">
                {SECTIONS.map(s => (
                  <button key={s} onClick={() => handleInterpret(s)}
                    className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[10px] whitespace-nowrap transition-colors shrink-0"
                    style={{
                      background: activeSection === s ? "rgba(107,78,255,0.2)" : "transparent",
                      color: activeSection === s ? "#9B8AFF" : "#9B8FBB",
                      border: `1px solid ${activeSection === s ? "rgba(107,78,255,0.3)" : "rgba(107,78,255,0.08)"}`,
                    }}>
                    <span>{SECTION_ICONS[s]}</span><span>{sectionLabels[s]}</span>
                    {s !== "personality" && user?.tier !== "pro" && <span className="text-[7px] ml-0.5" style={{ color: "#C9A84C" }}>Pro</span>}
                  </button>
                ))}
              </div>
              {interpretation ? (
                <p className="text-text-muted text-xs leading-relaxed">
                  {interpretation}{interpretLoading && <span className="animate-pulse">▍</span>}
                </p>
              ) : (
                <p className="text-text-faint text-xs text-center">
                  {lang === "ru" ? "Выбери раздел для анализа" : "Select a section"}
                </p>
              )}
            </Card>

          </div>
        ) : null}
      </main>

      <BottomNav active="natal" onNavigate={onNavigate} />
      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
    </div>
  );
}
