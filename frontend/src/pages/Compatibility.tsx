import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { CompositeChart } from "../components/CompositeChart";
import { PaywallSheet } from "../components/PaywallSheet";
import { ShareCard } from "../components/ShareCard";
import { BottomNav, Button, Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { apiRequest, streamRequest } from "../utils/api";
import { stripMarkdown } from "../utils/markdown";
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

type Step = "partners" | "types" | "result" | "composite";

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
  { id: "signs", icon: "*", tier: "free" },
  { id: "elements", icon: "~", tier: "free" },
  { id: "numerology", icon: "#", tier: "free" },
  { id: "chinese", icon: "+", tier: "free" },
  { id: "moon", icon: ")", tier: "free" },
  { id: "synastry", icon: "*", tier: "pro" },
  { id: "composite", icon: "∞", tier: "pro" },
  { id: "overall", icon: "=", tier: "free" },
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
  const [showShareCard, setShowShareCard] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [addForm, setAddForm] = useState({ name: "", day: "", month: "", year: "", hour: "", minute: "", city: "" });
  const [addErrors, setAddErrors] = useState<Record<string, string>>({});
  const [compositePartnerId, setCompositePartnerId] = useState<string | null>(null);
  const [compositePartnerName, setCompositePartnerName] = useState("");

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
      const body: Record<string, unknown> = { name: addForm.name, birth_date: bd };
      if (addForm.hour) body.birth_hour = parseInt(addForm.hour);
      if (addForm.minute) body.birth_minute = parseInt(addForm.minute);
      if (addForm.city.trim()) body.birth_city = addForm.city;
      await apiRequest("/partners", body, token ?? undefined);
      await loadPartners();
      setShowAddForm(false);
      setAddForm({ name: "", day: "", month: "", year: "", hour: "", minute: "", city: "" });
    } catch (e: unknown) {
      const err = e as { code?: string; message?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      // QA-001/004: the backend now rejects an unresolvable birth_city
      // instead of silently accepting it — surface its actual message
      // (e.g. "City not found, check the spelling") instead of a generic one.
      else setError(err.message || (lang === "ru" ? "Ошибка" : "Error"));
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
    if (typeId === "composite") {
      if (user?.tier !== "pro") { setShowPaywall(true); return; }
      setCompositePartnerId(selectedPartner.id);
      setCompositePartnerName(selectedPartner.name);
      setStep("composite");
      return;
    }
    if (typeId === "synastry" && user?.tier !== "pro") { setShowPaywall(true); return; }

    setLoading(true); setError("");
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;
      const res = await fetch(`/api/v1/compatibility/${typeId}`, {
        method: "POST", headers, body: JSON.stringify({ partner_id: selectedPartner.id, lang }),
      });
      if (res.status === 402) { setShowPaywall(true); return; }
      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
        setError(errData.detail || `HTTP ${res.status}`);
        return;
      }
      setResult(await res.json());
      setStep("result");
      setInterpretation("");
    } catch {
      setError(lang === "ru" ? "Ошибка соединения" : "Connection error");
    } finally { setLoading(false); }
  }

  async function handleInterpret() {
    if (!result || !selectedPartner) return;
    setInterpretLoading(true); setInterpretation("");
    try {
      await streamRequest("/compatibility/interpret",
        { compat_type: result.type, partner_id: selectedPartner.id, score: result.score, lang },
        (c) => setInterpretation(prev => prev + c),
        () => setInterpretLoading(false), token ?? undefined,
        (msg) => { setInterpretation(msg); setInterpretLoading(false); });
    } catch (e: unknown) {
      const err = e as { code?: string; message?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setInterpretation(err.message || (lang === "ru" ? "Ошибка" : "Error"));
      setInterpretLoading(false);
    }
  }

  const inputCls = "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 text-text-primary text-sm placeholder:text-text-faint focus:outline-none focus:border-violet-600 transition-colors";
  const typeLabels: Record<string, [string, string]> = {
    signs: ["По знакам", "By Signs"], elements: ["По стихиям", "By Elements"],
    numerology: ["Нумерология", "Numerology"], chinese: ["Китайский", "Chinese"],
    moon: ["Лунная", "Moon"], synastry: ["Синастрия", "Synastry"],
    composite: ["Композитная карта", "Composite Chart"],
    overall: ["Полный анализ", "Full Analysis"],
  };

  function scoreColor(s: number) { return s >= 70 ? "#4ade80" : s >= 40 ? "#C9A84C" : "#f87171"; }

  return (
    <div className="flex flex-col min-h-screen relative" style={{ background: "var(--gradient-page)", animation: "mystral-fadeup .3s ease-out" }}>
      <header className="flex items-center justify-between px-4 shrink-0 backdrop-blur-md lg:hidden" style={{ height: 46, background: "var(--bg-header)", borderBottom: "1px solid var(--border-gold)" }}>
        <button className="text-text-muted text-lg w-8" onClick={() => {
          if (step === "result") { setStep("types"); setResult(null); }
          else if (step === "composite") setStep("types");
          else if (step === "types") setStep("partners");
          else onNavigate("home");
        }}>‹</button>
        <span className="font-cinzel tracking-[.26em]" style={{ fontSize: 13, letterSpacing: ".26em", color: "#E8CD7E" }}>{t("compat.title")}</span>
        <div className="w-8" />
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-6 pb-24">

        {/* Step 1: Partners */}
        {step === "partners" && (
          <div className="flex flex-col gap-3">
            <p className="font-cinzel uppercase mb-1" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
              {lang === "ru" ? "Твои партнёры" : "Your partners"}
            </p>

            {partners.map(p => (
              <div key={p.id} className="cursor-pointer active:scale-[0.98] transition-all"
                style={{ display: "flex", gap: 14, padding: "14px 16px", borderRadius: 14, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", alignItems: "center", justifyContent: "space-between" }}
                onClick={() => selectPartner(p)}>
                <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                  <div className="font-cormorant" style={{ width: 40, height: 40, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, color: "#F0E9DA", background: "linear-gradient(135deg,#4B3C86,#C9A84C)" }}>
                    {p.name[0]?.toUpperCase()}
                  </div>
                  <div>
                    <p className="text-text-primary text-sm">{p.name}</p>
                    <p className="text-text-faint text-[10px]">{p.zodiac_symbol} {lang === "ru" ? p.zodiac_sign_ru : p.zodiac_sign}</p>
                  </div>
                </div>
                <button className="text-text-faint text-xs px-2" onClick={e => { e.stopPropagation(); handleDeletePartner(p.id); }}>x</button>
              </div>
            ))}

            {showAddForm ? (
              <div style={{ borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "16px" }}>
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
                  <p className="text-text-faint text-[9px] mt-1">{lang === "ru" ? "Время рождения (для лунной совместимости)" : "Birth time (for moon compatibility)"}</p>
                  <div className="grid grid-cols-2 gap-2">
                    <input className={inputCls} placeholder={lang === "ru" ? "Час (0–23)" : "Hour (0–23)"} type="number" min="0" max="23" value={addForm.hour}
                      onChange={e => setAddForm(p => ({ ...p, hour: e.target.value }))} />
                    <input className={inputCls} placeholder={lang === "ru" ? "Минуты" : "Minutes"} type="number" min="0" max="59" value={addForm.minute}
                      onChange={e => setAddForm(p => ({ ...p, minute: e.target.value }))} />
                  </div>
                  <input className={inputCls} placeholder={lang === "ru" ? "Город рождения (для синастрии)" : "Birth city (for synastry)"} value={addForm.city}
                    onChange={e => setAddForm(p => ({ ...p, city: e.target.value }))} />
                  <div className="flex gap-2">
                    <Button variant="primary" size="sm" className="flex-1" onClick={handleAddPartner} disabled={loading}>
                      {loading ? "..." : (lang === "ru" ? "Добавить" : "Add")}
                    </Button>
                    <Button variant="ghost" size="sm" className="flex-1" onClick={() => setShowAddForm(false)}>
                      {lang === "ru" ? "Отмена" : "Cancel"}
                    </Button>
                  </div>
                </div>
              </div>
            ) : (
              <button className="w-full py-3 text-sm transition-colors" onClick={() => setShowAddForm(true)}
                style={{ borderRadius: 14, border: "1px solid rgba(201,168,76,.4)", color: "#E8CD7E", background: "transparent" }}>
                {lang === "ru" ? "Добавить партнёра" : "Add partner"} +
              </button>
            )}

            {error && <p className="text-red-400 text-xs text-center">{error}</p>}
          </div>
        )}

        {/* Step 2: Type selection */}
        {step === "types" && selectedPartner && (
          <div className="flex flex-col gap-3">
            {/* Pair visualization */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 0, marginBottom: 16 }}>
              <div style={{ width: 64, height: 64, borderRadius: "50%", background: "linear-gradient(135deg,#4B3C86,#C9A84C)", border: "2px solid rgba(201,168,76,.4)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 2 }}>
                <span className="font-cormorant" style={{ fontSize: 28, color: "#0C0A18", fontWeight: 600 }}>{(user?.name ?? "?")[0]?.toUpperCase()}</span>
              </div>
              <div style={{ width: 32, height: 32, borderRadius: "50%", background: "linear-gradient(135deg,rgba(201,168,76,.3),rgba(138,127,192,.3))", border: "1.5px solid rgba(201,168,76,.4)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 -12px", zIndex: 3 }}>
                <span style={{ fontSize: 14, color: "#E8CD7E" }}>♡</span>
              </div>
              <div style={{ width: 64, height: 64, borderRadius: "50%", background: "linear-gradient(225deg,#4B3C86,#C9A84C)", border: "2px solid rgba(201,168,76,.4)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 2 }}>
                <span className="font-cormorant" style={{ fontSize: 28, color: "#0C0A18", fontWeight: 600 }}>{selectedPartner.name[0]?.toUpperCase()}</span>
              </div>
            </div>
            <div style={{ textAlign: "center", marginBottom: 12 }}>
              <p style={{ fontSize: 14, color: "#F0E9DA" }}>{user?.name ?? "?"} & {selectedPartner.name}</p>
              <p style={{ fontSize: 12, color: "#8A8170", marginTop: 2 }}>{lang === "ru" ? selectedPartner.zodiac_sign_ru : selectedPartner.zodiac_sign}</p>
            </div>

            <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>{lang === "ru" ? "Выбери тип анализа" : "Choose analysis type"}</p>

            <div className="flex flex-col gap-2">
              {COMPAT_TYPES.map(ct => (
                <div key={ct.id} className="cursor-pointer active:scale-[0.98] transition-all relative"
                  style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 16px", borderRadius: 14, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)" }}
                  onClick={() => runCompat(ct.id)}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ fontSize: 14, color: "#C9A84C", fontWeight: 600, width: 20, textAlign: "center" }}>{ct.icon}</span>
                    <span className="text-text-primary text-xs">{typeLabels[ct.id]?.[lang === "ru" ? 0 : 1] ?? ct.id}</span>
                    {ct.tier === "pro" && user?.tier !== "pro" && (
                      <span className="text-[8px] px-1.5 py-0.5 rounded-full" style={{ background: "#C9A84C", color: "#0D0B1F" }}>Pro</span>
                    )}
                  </div>
                  <span style={{ color: "#C9A84C", fontSize: 14, opacity: 0.5 }}>›</span>
                </div>
              ))}
            </div>

            {loading && <p className="text-text-muted text-xs text-center animate-pulse">{lang === "ru" ? "Расчёт..." : "Calculating..."}</p>}
            {error && <p className="text-red-400 text-xs text-center">{error}</p>}
          </div>
        )}

        {/* Step 3: Result */}
        {step === "result" && result && (
          <div className="flex flex-col gap-4">
            {/* Score */}
            <div className="flex flex-col items-center gap-3">
              <p className="font-cormorant text-text-primary" style={{ fontSize: 22, color: "#F0E9DA" }}>{result.partner_name}</p>
              <p className="text-text-faint text-xs">{typeLabels[result.type]?.[lang === "ru" ? 0 : 1]}</p>
              <div style={{ width: "100%", display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ flex: 1, height: 8, borderRadius: 99, background: "rgba(255,255,255,.06)", overflow: "hidden" }}>
                  <div style={{ width: `${result.score}%`, height: "100%", borderRadius: 99, background: "linear-gradient(90deg,#8A6E2E,#E8CD7E)", boxShadow: "0 0 12px rgba(201,168,76,.3)" }} />
                </div>
                <span className="font-display text-lg" style={{ color: scoreColor(result.score), minWidth: 44, textAlign: "right" }}>{result.score}%</span>
              </div>
            </div>

            {/* Details */}
            <div style={{ borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "16px" }}>
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
            </div>

            {/* Interpret */}
            {interpretation ? (
              <Card>
                <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">AI</p>
                <p className="text-text-muted text-xs leading-relaxed">
                  {stripMarkdown(interpretation)}{interpretLoading && <span className="animate-pulse">▍</span>}
                </p>
              </Card>
            ) : (
              <Button variant="primary" className="w-full" onClick={handleInterpret} disabled={interpretLoading}>
                {interpretLoading ? "..." : (lang === "ru" ? "AI интерпретация" : "AI interpretation")}
              </Button>
            )}

            <button onClick={() => setShowShareCard(true)}
              style={{ width: "100%", height: 44, marginTop: 8, borderRadius: 14, border: "1px solid rgba(201,168,76,.25)", background: "transparent", color: "#C9A84C", fontSize: 13, cursor: "pointer" }}>
              {t("share.share_btn")}
            </button>

            <Button variant="ghost" className="w-full" onClick={() => { setStep("types"); setResult(null); setInterpretation(""); setShowShareCard(false); }}>
              {lang === "ru" ? "Другой анализ" : "Another analysis"}
            </Button>
          </div>
        )}

        {/* Step: Composite Chart */}
        {step === "composite" && compositePartnerId && (
          <CompositeChart
            partnerId={compositePartnerId}
            partnerName={compositePartnerName}
            onClose={() => setStep("types")}
          />
        )}

      </main>

      <BottomNav active="home" onNavigate={onNavigate} />
      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
      {showShareCard && result && (
        <ShareCard
          type="compat"
          title={result.partner_name}
          subtitle={typeLabels[result.type]?.[lang === "ru" ? 0 : 1]}
          score={result.score}
          scoreLabel={result.description}
          onClose={() => setShowShareCard(false)}
        />
      )}
    </div>
  );
}
