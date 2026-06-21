import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { PaywallSheet } from "../components/PaywallSheet";
import { BottomNav, Button, Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { apiRequest, streamRequest } from "../utils/api";
import { validateDay, validateMonth, validateYear, validateDateExists } from "../utils/validate";

interface CompatibilityProps { onNavigate: (page: string) => void; }

interface Partner {
  id: string; name: string; birth_date: string;
  zodiac_sign: string; zodiac_sign_ru: string; zodiac_symbol: string;
  has_time: boolean; has_city: boolean;
}

interface CompatResult {
  type: string; score: number; description: string; partner_name: string;
  [key: string]: unknown;
}

type Step = "partners" | "types" | "result";

interface SynAspect { user_planet: string; partner_planet: string; aspect: string; symbol: string; orb: number; harmony: boolean; }
function SynastryAspects({ aspects, lang }: { aspects: SynAspect[]; lang: string }) {
  return (
    <div className="mt-3 flex flex-col gap-1">
      <p className="text-text-faint text-[9px] uppercase tracking-widest mb-1">{lang === "ru" ? "Аспекты" : "Aspects"}</p>
      {aspects.slice(0, 7).map((a, i) => (
        <div key={i} className="flex items-center justify-between text-xs">
          <span className="text-text-muted">{a.user_planet} {a.symbol} {a.partner_planet}</span>
          <span style={{ color: a.harmony ? "#4ade80" : "#f87171" }}>{a.aspect} {a.orb}°</span>
        </div>
      ))}
    </div>
  );
}

function OverallScores({ scores, lang, labels, colorFn }: { scores: Record<string, number>; lang: string; labels: Record<string, [string, string]>; colorFn: (s: number) => string }) {
  return (
    <div className="mt-3 flex flex-col gap-1.5">
      {Object.entries(scores).map(([k, v]) => (
        <div key={k} className="flex items-center justify-between text-xs">
          <span className="text-text-muted">{labels[k]?.[lang === "ru" ? 0 : 1] ?? k}</span>
          <span style={{ color: colorFn(v) }}>{v}%</span>
        </div>
      ))}
    </div>
  );
}

const COMPAT_TYPES = [
  { id: "signs", icon: "☀️", tier: "free" },
  { id: "elements", icon: "🔥", tier: "free" },
  { id: "numerology", icon: "🔢", tier: "free" },
  { id: "chinese", icon: "🐉", tier: "free" },
  { id: "moon", icon: "🌙", tier: "free" },
  { id: "synastry", icon: "⭐", tier: "pro" },
  { id: "overall", icon: "📊", tier: "free" },
];

export function Compatibility({ onNavigate }: CompatibilityProps) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const lang = user?.lang ?? "ru";

  const [step, setStep] = useState<Step>("partners");
  const [partners, setPartners] = useState<Partner[]>([]);
  const [selectedPartner, setSelectedPartner] = useState<Partner | null>(null);
  const [result, setResult] = useState<CompatResult | null>(null);
  const [interpretation, setInterpretation] = useState("");
  const [interpretLoading, setInterpretLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showPaywall, setShowPaywall] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [addForm, setAddForm] = useState({ name: "", day: "", month: "", year: "" });
  const [addErrors, setAddErrors] = useState<Record<string, string>>({});

  const loaded = useRef(false);
  useEffect(() => {
    if (loaded.current || !token) return;
    loaded.current = true;
    loadPartners();
  }, [token]);

  async function loadPartners() {
    try {
      const res = await fetch("/api/v1/partners", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setPartners(Array.isArray(data) ? data : []);
      }
    } catch { setPartners([]); }
  }

  async function handleAddPartner() {
    const errs: Record<string, string> = {};
    if (!addForm.name.trim()) errs.name = lang === "ru" ? "Укажи имя" : "Enter name";
    const de = validateDay(addForm.day); if (de) errs.day = de;
    const me = validateMonth(addForm.month); if (me) errs.month = me;
    const ye = validateYear(addForm.year); if (ye) errs.year = ye;
    if (!de && !me && !ye) { const dx = validateDateExists(addForm.day, addForm.month, addForm.year); if (dx) errs.date = dx; }
    if (Object.values(errs).some(Boolean)) { setAddErrors(errs); return; }

    setLoading(true);
    try {
      const bd = `${addForm.year}-${addForm.month.padStart(2, "0")}-${addForm.day.padStart(2, "0")}`;
      await apiRequest("/partners", { name: addForm.name, birth_date: bd }, token ?? undefined);
      await loadPartners();
      setShowAddForm(false);
      setAddForm({ name: "", day: "", month: "", year: "" });
    } catch (e: unknown) {
      const err = e as { code?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setError(lang === "ru" ? "Ошибка" : "Error");
    } finally { setLoading(false); }
  }

  async function handleDeletePartner(id: string) {
    try {
      await fetch(`/api/v1/partners/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      setPartners(prev => prev.filter(p => p.id !== id));
    } catch {}
  }

  function selectPartner(p: Partner) {
    setSelectedPartner(p);
    setStep("types");
    setResult(null);
    setInterpretation("");
  }

  async function runCompat(typeId: string) {
    if (!selectedPartner) return;
    if (typeId === "synastry" && user?.tier !== "pro") { setShowPaywall(true); return; }

    setLoading(true); setError("");
    try {
      const data = await apiRequest<CompatResult>(
        `/compatibility/${typeId}`,
        { partner_id: selectedPartner.id, lang },
        token ?? undefined,
      );
      setResult(data);
      setStep("result");
      setInterpretation("");
    } catch (e: unknown) {
      const err = e as { code?: string; message?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setError(typeof err.message === "string" ? err.message : (lang === "ru" ? "Ошибка" : "Error"));
    } finally { setLoading(false); }
  }

  async function handleInterpret() {
    if (!result || !selectedPartner) return;
    setInterpretLoading(true); setInterpretation("");
    try {
      await streamRequest("/compatibility/interpret",
        { compat_type: result.type, partner_id: selectedPartner.id, score: result.score, lang },
        (c) => setInterpretation(prev => prev + c),
        () => setInterpretLoading(false), token ?? undefined);
    } catch (e: unknown) {
      const err = e as { code?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setInterpretation(lang === "ru" ? "Ошибка" : "Error");
      setInterpretLoading(false);
    }
  }

  const inputCls = "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 text-text-primary text-sm placeholder:text-text-faint focus:outline-none focus:border-violet-600 transition-colors";
  const typeLabels: Record<string, [string, string]> = {
    signs: ["По знакам", "By Signs"], elements: ["По стихиям", "By Elements"],
    numerology: ["Нумерология", "Numerology"], chinese: ["Китайский", "Chinese"],
    moon: ["Лунная", "Moon"], synastry: ["Синастрия", "Synastry"],
    overall: ["Полный анализ", "Full Analysis"],
  };

  function scoreColor(s: number) { return s >= 70 ? "#4ade80" : s >= 40 ? "#C9A84C" : "#f87171"; }

  return (
    <div className="flex flex-col min-h-screen bg-bg-deep relative">
      <header className="flex items-center justify-between px-4 shrink-0 backdrop-blur-sm" style={{ height: 46, background: "rgba(6,4,20,0.75)" }}>
        <button className="text-text-muted text-lg w-8" onClick={() => {
          if (step === "result") { setStep("types"); setResult(null); }
          else if (step === "types") setStep("partners");
          else onNavigate("home");
        }}>‹</button>
        <span className="font-display text-text-primary text-base tracking-widest">{t("compat.title")}</span>
        <div className="w-8" />
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-6 pb-24">

        {/* Step 1: Partners */}
        {step === "partners" && (
          <div className="flex flex-col gap-3">
            <p className="text-text-faint text-[10px] uppercase tracking-widest mb-1">
              {lang === "ru" ? "Твои партнёры" : "Your partners"}
            </p>

            {partners.map(p => (
              <Card key={p.id} className="cursor-pointer active:scale-[0.98] transition-all" onClick={() => selectPartner(p)}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full flex items-center justify-center text-lg" style={{ background: "#6B4EFF" }}>
                      {p.name[0]?.toUpperCase()}
                    </div>
                    <div>
                      <p className="text-text-primary text-sm">{p.name}</p>
                      <p className="text-text-faint text-[10px]">{p.zodiac_symbol} {lang === "ru" ? p.zodiac_sign_ru : p.zodiac_sign}</p>
                    </div>
                  </div>
                  <button className="text-text-faint text-xs px-2" onClick={e => { e.stopPropagation(); handleDeletePartner(p.id); }}>✕</button>
                </div>
              </Card>
            ))}

            {showAddForm ? (
              <Card>
                <div className="flex flex-col gap-2">
                  <input className={inputCls} placeholder={lang === "ru" ? "Имя" : "Name"} value={addForm.name}
                    onChange={e => { setAddForm(p => ({ ...p, name: e.target.value })); setAddErrors(p => ({ ...p, name: "" })); }} />
                  {addErrors.name && <p className="text-red-400 text-[10px]">{addErrors.name}</p>}
                  <div className="grid grid-cols-3 gap-2">
                    <input className={inputCls} placeholder={lang === "ru" ? "День" : "Day"} type="number" value={addForm.day}
                      onChange={e => { setAddForm(p => ({ ...p, day: e.target.value })); setAddErrors(p => ({ ...p, day: "", date: "" })); }} />
                    <input className={inputCls} placeholder={lang === "ru" ? "Месяц" : "Month"} type="number" value={addForm.month}
                      onChange={e => { setAddForm(p => ({ ...p, month: e.target.value })); setAddErrors(p => ({ ...p, month: "", date: "" })); }} />
                    <input className={inputCls} placeholder={lang === "ru" ? "Год" : "Year"} type="number" value={addForm.year}
                      onChange={e => { setAddForm(p => ({ ...p, year: e.target.value })); setAddErrors(p => ({ ...p, year: "", date: "" })); }} />
                  </div>
                  {(addErrors.day || addErrors.month || addErrors.year || addErrors.date) && (
                    <p className="text-red-400 text-[10px]">{addErrors.day || addErrors.month || addErrors.year || addErrors.date}</p>
                  )}
                  <div className="flex gap-2">
                    <Button variant="primary" size="sm" className="flex-1" onClick={handleAddPartner} disabled={loading}>
                      {loading ? "..." : (lang === "ru" ? "Добавить" : "Add")}
                    </Button>
                    <Button variant="ghost" size="sm" className="flex-1" onClick={() => setShowAddForm(false)}>
                      {lang === "ru" ? "Отмена" : "Cancel"}
                    </Button>
                  </div>
                </div>
              </Card>
            ) : (
              <Button variant="primary" className="w-full" onClick={() => setShowAddForm(true)}>
                {lang === "ru" ? "Добавить партнёра ✦" : "Add partner ✦"}
              </Button>
            )}

            {error && <p className="text-red-400 text-xs text-center">{error}</p>}
          </div>
        )}

        {/* Step 2: Type selection */}
        {step === "types" && selectedPartner && (
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-8 h-8 rounded-full flex items-center justify-center text-sm" style={{ background: "#6B4EFF" }}>
                {selectedPartner.name[0]?.toUpperCase()}
              </div>
              <div>
                <p className="text-text-primary text-sm">{selectedPartner.name}</p>
                <p className="text-text-faint text-[10px]">{selectedPartner.zodiac_symbol} {lang === "ru" ? selectedPartner.zodiac_sign_ru : selectedPartner.zodiac_sign}</p>
              </div>
            </div>

            <p className="text-text-faint text-[10px] uppercase tracking-widest">{lang === "ru" ? "Выбери тип анализа" : "Choose analysis type"}</p>

            <div className="grid grid-cols-2 gap-2">
              {COMPAT_TYPES.map(ct => (
                <Card key={ct.id} className="cursor-pointer active:scale-[0.98] transition-all relative" onClick={() => runCompat(ct.id)}>
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{ct.icon}</span>
                    <span className="text-text-primary text-xs">{typeLabels[ct.id]?.[lang === "ru" ? 0 : 1] ?? ct.id}</span>
                  </div>
                  {ct.tier === "pro" && user?.tier !== "pro" && (
                    <span className="absolute top-2 right-2 text-[8px] px-1.5 py-0.5 rounded-full" style={{ background: "#C9A84C", color: "#0D0B1F" }}>Pro</span>
                  )}
                </Card>
              ))}
            </div>

            {loading && <p className="text-text-muted text-xs text-center animate-pulse">{lang === "ru" ? "Расчёт..." : "Calculating..."}</p>}
            {error && <p className="text-red-400 text-xs text-center">{error}</p>}
          </div>
        )}

        {/* Step 3: Result */}
        {step === "result" && result && (
          <div className="flex flex-col gap-4">
            {/* Score circle */}
            <div className="flex flex-col items-center gap-2">
              <div className="relative w-28 h-28">
                <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                  <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(107,78,255,0.1)" strokeWidth="6" />
                  <circle cx="50" cy="50" r="42" fill="none" stroke={scoreColor(result.score)}
                    strokeWidth="6" strokeLinecap="round"
                    strokeDasharray={`${result.score * 2.64} 264`} />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="font-display text-2xl" style={{ color: scoreColor(result.score) }}>{result.score}%</span>
                </div>
              </div>
              <p className="text-text-primary text-sm font-display">{result.partner_name}</p>
              <p className="text-text-faint text-xs">{typeLabels[result.type]?.[lang === "ru" ? 0 : 1]}</p>
            </div>

            {/* Details */}
            <Card>
              <p className="text-text-muted text-xs leading-relaxed">{result.description}</p>

              {/* Type-specific details */}
              {result.type === "signs" && (
                <div className="flex items-center justify-center gap-4 mt-3">
                  <span className="text-2xl">{result.user_symbol as string}</span>
                  <span className="text-text-faint">+</span>
                  <span className="text-2xl">{result.partner_symbol as string}</span>
                </div>
              )}

              {result.type === "chinese" && (
                <div className="flex items-center justify-center gap-4 mt-3">
                  <div className="text-center">
                    <span className="text-2xl">{result.user_emoji as string}</span>
                    <p className="text-text-faint text-[10px]">{result.user_animal as string}</p>
                  </div>
                  <span className="text-text-faint">+</span>
                  <div className="text-center">
                    <span className="text-2xl">{result.partner_emoji as string}</span>
                    <p className="text-text-faint text-[10px]">{result.partner_animal as string}</p>
                  </div>
                </div>
              )}

              {result.type === "numerology" && (
                <div className="flex items-center justify-center gap-6 mt-3">
                  <span className="font-display text-2xl" style={{ color: "#9B8AFF" }}>{result.user_number as number}</span>
                  <span className="text-text-faint">+</span>
                  <span className="font-display text-2xl" style={{ color: "#9B8AFF" }}>{result.partner_number as number}</span>
                </div>
              )}

              {result.type === "synastry" && Array.isArray(result.aspects) ? (
                <SynastryAspects aspects={result.aspects as SynAspect[]} lang={lang} />
              ) : null}

              {result.type === "overall" && result.scores ? (
                <OverallScores scores={result.scores as Record<string, number>} lang={lang} labels={typeLabels} colorFn={scoreColor} />
              ) : null}
            </Card>

            {/* Interpret */}
            {interpretation ? (
              <Card>
                <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">AI</p>
                <p className="text-text-muted text-xs leading-relaxed">
                  {interpretation}{interpretLoading && <span className="animate-pulse">▍</span>}
                </p>
              </Card>
            ) : (
              <Button variant="primary" className="w-full" onClick={handleInterpret} disabled={interpretLoading}>
                {interpretLoading ? "..." : (lang === "ru" ? "AI интерпретация ✦" : "AI interpretation ✦")}
              </Button>
            )}

            <Button variant="ghost" className="w-full" onClick={() => { setStep("types"); setResult(null); setInterpretation(""); }}>
              {lang === "ru" ? "Другой анализ" : "Another analysis"}
            </Button>
          </div>
        )}

      </main>

      <BottomNav active="home" onNavigate={onNavigate} />
      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
    </div>
  );
}
