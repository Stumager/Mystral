import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { PaywallSheet } from "../components/PaywallSheet";
import { ShareCard } from "../components/ShareCard";
import { BottomNav, Button } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { streamRequest } from "../utils/api";
import { stripMarkdown } from "../utils/markdown";

interface NumerologyProps { onNavigate: (page: string) => void; }

interface NumData {
  name: string; title: string; description: string;
  strengths: string[]; challenges: string[]; career: string; love: string; famous: string[];
}

interface NumEntry { number: number; is_master?: boolean; data: NumData | null; year?: number; }

interface SquareCell { number: number; count: number; strength: string; name: string; description: string; }
interface SquareLine { cells: number[]; total: number; filled: boolean; title: string; description: string; }
interface PythagorasSquare {
  matrix: Record<number, number>;
  working_numbers: number[];
  cells: SquareCell[];
  lines: SquareLine[];
}

interface KarmicEntry { number: number; description: string; }

interface NumerologyProfile {
  life_path: NumEntry;
  birthday: NumEntry;
  destiny: NumEntry | null;
  soul: NumEntry | null;
  personality: NumEntry | null;
  personal_year: NumEntry;
  personal_month: NumEntry;
  personal_day: NumEntry;
  karmic_numbers: KarmicEntry[];
  missing_numbers: number[];
  pythagoras_square: PythagorasSquare;
  requires_full_name: boolean;
}

const STRENGTH_COLORS: Record<string, string> = {
  absent: "#6b7280", weak: "#9B8FBB", average: "#9B8AFF", strong: "#C9A84C", very_strong: "#f59e0b",
};

const AI_SECTIONS = ["core", "square", "forecast", "karmic"] as const;
type AISection = typeof AI_SECTIONS[number];

export function Numerology({ onNavigate }: NumerologyProps) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const lang = user?.lang ?? "ru";
  const ru = lang === "ru";

  const [profile, setProfile] = useState<NumerologyProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [fullNameInput, setFullNameInput] = useState("");
  const [savingName, setSavingName] = useState(false);

  const [angelInput, setAngelInput] = useState("");
  const [angelResult, setAngelResult] = useState<string | null>(null);
  const [angelLoading, setAngelLoading] = useState(false);

  const [aiSection, setAiSection] = useState<AISection | null>(null);
  const [aiText, setAiText] = useState("");
  const [aiLoading, setAiLoading] = useState(false);

  const [showPaywall, setShowPaywall] = useState(false);
  const [showShareCard, setShowShareCard] = useState(false);
  const loaded = useRef(false);

  useEffect(() => {
    if (loaded.current || !token) return;
    loaded.current = true;
    fetch("/api/v1/numerology/profile", { headers: { Authorization: `Bearer ${token}` } })
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then((d: NumerologyProfile) => { setProfile(d); setLoading(false); })
      .catch(() => { setError(ru ? "Заполни дату рождения в профиле" : "Set your birth date in profile"); setLoading(false); });
  }, [token]);

  async function saveFullName() {
    if (!fullNameInput.trim()) return;
    setSavingName(true);
    try {
      await fetch("/api/v1/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ full_name: fullNameInput.trim() }),
      });
      loaded.current = false;
      const r = await fetch("/api/v1/numerology/profile", { headers: { Authorization: `Bearer ${token}` } });
      const d = await r.json();
      setProfile(d);
    } catch {} finally { setSavingName(false); }
  }

  async function lookupAngel() {
    const q = angelInput.trim();
    if (!q) return;
    setAngelLoading(true); setAngelResult(null);
    try {
      const r = await fetch(`/api/v1/numerology/angel/${encodeURIComponent(q)}?lang=${lang}`);
      if (!r.ok) { setAngelResult(ru ? "Число не найдено" : "Number not found"); return; }
      const d = await r.json();
      setAngelResult(d.meaning);
    } catch { setAngelResult(ru ? "Ошибка" : "Error"); }
    finally { setAngelLoading(false); }
  }

  async function handleAI(section: AISection) {
    if (section !== "core" && user?.tier !== "pro") { setShowPaywall(true); return; }
    setAiSection(section); setAiText(""); setAiLoading(true);
    try {
      await streamRequest("/numerology/interpret", { section, lang },
        (c) => setAiText(prev => prev + c), () => setAiLoading(false), token ?? undefined,
        (msg) => { setAiText(msg); setAiLoading(false); });
    } catch (e: unknown) {
      const err = e as { code?: string; message?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setAiText(err.message || (ru ? "Ошибка" : "Error"));
      setAiLoading(false);
    }
  }

  const inputCls = "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 text-text-primary text-sm placeholder:text-text-faint focus:outline-none focus:border-violet-600 transition-colors";

  const aiLabels: Record<AISection, string> = ru
    ? { core: "Характер", square: "Квадрат", forecast: "Прогноз", karmic: "Карма" }
    : { core: "Character", square: "Square", forecast: "Forecast", karmic: "Karma" };

  function NumberCard({ entry, label, locked }: { entry: NumEntry | null; label: string; locked?: boolean }) {
    if (!entry) return (
      <div className="relative overflow-hidden" style={{ padding: "16px 18px", borderRadius: 16, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)" }}>
        <p className="font-cinzel uppercase mb-1" style={{ fontSize: 9, letterSpacing: ".22em", color: "#C9A84C" }}>{label}</p>
        <p className="font-cormorant text-center text-text-faint my-1" style={{ fontSize: 42 }}>--</p>
        <p className="text-text-faint text-[10px] text-center">{ru ? "Введи полное имя" : "Enter full name"}</p>
      </div>
    );
    if (locked) return (
      <div className="relative overflow-hidden" style={{ padding: "16px 18px", borderRadius: 16, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)" }}>
        <p className="font-cinzel uppercase mb-1" style={{ fontSize: 9, letterSpacing: ".22em", color: "#C9A84C" }}>{label}</p>
        <p className="font-cormorant text-center blur-sm my-1" style={{ fontSize: 42 }}>{entry.number}</p>
        <div className="absolute inset-0 flex items-center justify-center" style={{ background: "rgba(6,4,20,0.5)" }}>
          <span className="text-text-muted text-sm">--</span>
        </div>
      </div>
    );
    return (
      <div style={{ padding: "16px 18px", borderRadius: 16, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: `1px solid ${entry.is_master ? "rgba(201,168,76,0.4)" : "rgba(201,168,76,.13)"}` }}>
        <p className="font-cinzel uppercase mb-1" style={{ fontSize: 9, letterSpacing: ".22em", color: "#C9A84C" }}>{label}</p>
        <p className="font-cormorant text-center my-1" style={{ fontSize: 42, color: entry.is_master ? "#C9A84C" : "#9B8AFF" }}>
          {entry.number}
        </p>
        {entry.data && <p className="text-center font-display" style={{ fontSize: 13, color: "#A89E8B" }}>{entry.data.title}</p>}
        {entry.data && <p className="text-text-muted text-[10px] text-center mt-0.5 line-clamp-2">{entry.data.description}</p>}
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen relative" style={{ background: "var(--gradient-page)", animation: "mystral-fadeup .3s ease-out" }}>
      <header className="flex items-center justify-between px-4 shrink-0 backdrop-blur-md lg:hidden" style={{ height: 46, background: "var(--bg-header)", borderBottom: "1px solid var(--border-gold)" }}>
        <button className="text-text-muted text-lg w-8" onClick={() => onNavigate("home")}>&#8249;</button>
        <span className="font-cinzel tracking-[.26em]" style={{ fontSize: 13, color: "#E8CD7E" }}>{t("numerology.title")}</span>
        <div className="w-8" />
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-6 pb-24 flex flex-col gap-4">
        {loading ? (
          <p className="text-text-muted text-xs text-center animate-pulse">{t("numerology.calculating")}</p>
        ) : error ? (
          <div style={{ borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "16px 18px" }}>
            <p className="text-text-muted text-sm text-center">{error}</p>
            <Button variant="primary" size="sm" className="w-full mt-3" onClick={() => onNavigate("profile")}>
              {ru ? "Открыть профиль" : "Open profile"}
            </Button>
          </div>
        ) : profile ? (
          <>
            {/* Block 0: Full name banner */}
            {profile.requires_full_name && (
              <div style={{ borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "16px 18px" }}>
                <p className="text-text-muted text-xs mb-2">
                  {ru ? "Для полного анализа введи полное имя (имя + фамилия)" : "For full analysis enter your full name"}
                </p>
                <div className="flex gap-2">
                  <input className={inputCls + " flex-1"} value={fullNameInput} onChange={e => setFullNameInput(e.target.value)}
                    placeholder={ru ? "Иванов Иван" : "John Smith"} />
                  <Button variant="primary" size="sm" onClick={saveFullName} disabled={savingName || !fullNameInput.trim()}>
                    {savingName ? "..." : "OK"}
                  </Button>
                </div>
              </div>
            )}

            {/* Block 1: Main numbers grid */}
            <div>
              <p className="font-cinzel uppercase mb-2" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                {ru ? "Главные числа" : "Core Numbers"}
              </p>
              <div className="grid grid-cols-2 gap-2">
                <NumberCard entry={profile.life_path} label={ru ? "Жизненный путь" : "Life Path"} />
                <NumberCard entry={profile.destiny} label={ru ? "Число Судьбы" : "Destiny"} />
                <NumberCard entry={profile.soul} label={ru ? "Число Души" : "Soul"} />
                <NumberCard entry={profile.personality} label={ru ? "Число Личности" : "Personality"} />
                <NumberCard entry={profile.birthday} label={ru ? "День рождения" : "Birthday"} />
                <NumberCard entry={profile.personal_year} label={ru ? "Персональный год" : "Personal Year"} />
              </div>
            </div>

            {/* Block 2: Pythagoras Square */}
            <div style={{ borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "16px 18px" }}>
              <p className="font-cinzel uppercase mb-3" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                {ru ? "Квадрат Пифагора" : "Pythagoras Square"}
              </p>
              <div className="grid grid-cols-3 gap-2 mb-3">
                {[1, 2, 3, 4, 5, 6, 7, 8, 9].map(n => {
                  const cell = profile.pythagoras_square.cells[n - 1];
                  const dots = String(cell.count) || "0";
                  return (
                    <div key={n} className="p-2 flex flex-col items-center gap-0.5"
                      style={{
                        borderRadius: 16,
                        background: "rgba(255,255,255,.04)",
                        border: `1px solid ${cell.count >= 3 ? "rgba(201,168,76,0.4)" : "rgba(201,168,76,.13)"}`,
                      }}>
                      <span className="text-text-faint text-[9px]">{n}</span>
                      <span className="font-cormorant" style={{ fontSize: 28, color: cell.count === 0 ? "#3A3730" : (STRENGTH_COLORS[cell.strength] || "#9B8FBB") }}>
                        {cell.count === 0 ? "-" : dots}
                      </span>
                      <span className="text-[8px] text-text-faint text-center leading-tight">{cell.name}</span>
                    </div>
                  );
                })}
              </div>
              {profile.pythagoras_square.lines.filter(l => l.filled).length > 0 && (
                <div className="flex flex-col gap-1">
                  <p className="font-cinzel uppercase mb-1" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                    {ru ? "Сильные линии" : "Strong Lines"}
                  </p>
                  {profile.pythagoras_square.lines.filter(l => l.filled).map((l, i) => (
                    <div key={i} className="flex items-start gap-2">
                      <span className="text-[10px] shrink-0" style={{ color: "#C9A84C" }}>*</span>
                      <div>
                        <p className="text-text-primary text-[10px] font-display">{l.title}</p>
                        <p className="text-text-faint text-[9px]">{l.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Block 3: Forecast */}
            <div>
              <p className="font-cinzel uppercase mb-2" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                {ru ? "Прогноз" : "Forecast"}
              </p>
              <div className="flex flex-col gap-2">
                {[
                  { e: profile.personal_year, l: ru ? "Персональный год" : "Personal Year" },
                  { e: profile.personal_month, l: ru ? "Персональный месяц" : "Personal Month" },
                  { e: profile.personal_day, l: ru ? "Персональный день" : "Personal Day" },
                ].map(({ e, l }) => (
                  <div key={l} className="flex items-center gap-3 px-3 py-2.5"
                    style={{ borderRadius: 16, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)" }}>
                    <span className="font-cormorant shrink-0" style={{ fontSize: 42, color: "#9B8AFF", width: 50, textAlign: "center" }}>
                      {e.number}
                    </span>
                    <div className="min-w-0">
                      <p className="font-cinzel uppercase" style={{ fontSize: 9, letterSpacing: ".22em", color: "#C9A84C" }}>{l}</p>
                      {e.data && <p className="text-text-muted text-[10px] truncate" style={{ color: "#A89E8B" }}>{e.data.title}</p>}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Block 4: Karmic + Missing */}
            {(profile.karmic_numbers.length > 0 || profile.missing_numbers.length > 0) && (
              <div>
                {profile.karmic_numbers.length > 0 && (
                  <>
                    <p className="font-cinzel uppercase mb-2" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                      {ru ? "Кармические числа" : "Karmic Numbers"}
                    </p>
                    <div className="flex flex-col gap-2 mb-3">
                      {profile.karmic_numbers.map(k => (
                        <div key={k.number} className="px-3 py-2.5"
                          style={{ borderRadius: 16, background: "rgba(248,113,113,0.06)", border: "1px solid rgba(248,113,113,0.2)" }}>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-cormorant" style={{ fontSize: 28, color: "#f87171" }}>{k.number}</span>
                            <span className="font-cinzel uppercase" style={{ fontSize: 9, letterSpacing: ".22em", color: "#C9A84C" }}>{ru ? "Кармический долг" : "Karmic Debt"}</span>
                          </div>
                          <p className="text-text-muted text-[10px] leading-relaxed">{k.description}</p>
                        </div>
                      ))}
                    </div>
                  </>
                )}
                {profile.missing_numbers.length > 0 && (
                  <>
                    <p className="font-cinzel uppercase mb-2" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                      {ru ? "Что развивать" : "Areas to Develop"}
                    </p>
                    <div className="flex gap-2 flex-wrap mb-2">
                      {profile.missing_numbers.map(n => (
                        <span key={n} className="font-cormorant px-3 py-1.5"
                          style={{ borderRadius: 12, fontSize: 22, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", color: "#9B8FBB" }}>
                          {n}
                        </span>
                      ))}
                    </div>
                  </>
                )}
              </div>
            )}

            {/* Block 5: Angel Numbers */}
            <div style={{ borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "16px 18px" }}>
              <p className="font-cinzel uppercase mb-2" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                {ru ? "Ангельская нумерология" : "Angel Numerology"}
              </p>
              <p className="text-text-muted text-[10px] mb-2">
                {ru ? "Введи число которое часто видишь (11:11, 444...)" : "Enter a number you often see (11:11, 444...)"}
              </p>
              <div className="flex gap-2 mb-2">
                <input
                  className="flex-1 bg-bg-surface text-text-primary text-sm placeholder:text-text-faint focus:outline-none transition-colors"
                  style={{ borderRadius: 12, border: "1px solid rgba(201,168,76,.22)", padding: "10px 14px", background: "rgba(255,255,255,.03)" }}
                  value={angelInput} onChange={e => setAngelInput(e.target.value)}
                  placeholder="11:11" onKeyDown={e => e.key === "Enter" && lookupAngel()} />
                <Button variant="primary" size="sm" onClick={lookupAngel} disabled={angelLoading || !angelInput.trim()}>
                  {angelLoading ? "..." : "OK"}
                </Button>
              </div>
              {angelResult && (
                <p className="text-text-muted text-xs leading-relaxed">{angelResult}</p>
              )}
            </div>

            {/* Block 6: AI Interpretation */}
            <div style={{ borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "16px 18px" }}>
              <p className="font-cinzel uppercase mb-3" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                {ru ? "AI интерпретация" : "AI Interpretation"}
              </p>
              <div className="flex gap-1 mb-3">
                {AI_SECTIONS.map(s => (
                  <button key={s} onClick={() => handleAI(s)}
                    disabled={aiLoading}
                    className="flex-1 px-2 py-1.5 text-[10px] transition-colors"
                    style={{
                      borderRadius: 10,
                      background: aiSection === s ? "rgba(201,168,76,0.15)" : "rgba(255,255,255,.04)",
                      color: aiSection === s ? "#E8CD7E" : "#A89E8B",
                      border: `1px solid ${aiSection === s ? "rgba(201,168,76,0.4)" : "rgba(201,168,76,.13)"}`,
                      cursor: aiLoading ? "not-allowed" : "pointer",
                      opacity: aiLoading ? 0.45 : 1,
                    }}>
                    {aiLabels[s]}
                    {s !== "core" && user?.tier !== "pro" && <span className="ml-0.5" style={{ color: "#C9A84C" }}>*</span>}
                  </button>
                ))}
              </div>
              {aiText && (
                <p className="text-text-muted text-xs leading-relaxed">
                  {stripMarkdown(aiText)}{aiLoading && <span className="animate-pulse">|</span>}
                </p>
              )}
              {aiText && !aiLoading && (
                <button onClick={() => setShowShareCard(true)}
                  style={{ width: "100%", height: 44, marginTop: 12, borderRadius: 14, border: "1px solid rgba(201,168,76,.25)", background: "transparent", color: "#C9A84C", fontSize: 13, cursor: "pointer" }}>
                  {t("share.share_btn")}
                </button>
              )}
            </div>
          </>
        ) : null}
      </main>

      <BottomNav active="home" onNavigate={onNavigate} />
      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
      {showShareCard && profile && (
        <ShareCard
          type="numerology"
          title={ru ? "Число жизненного пути" : "Life Path Number"}
          number={profile.life_path.number}
          numberLabel={profile.life_path.data?.title}
          onClose={() => setShowShareCard(false)}
        />
      )}
    </div>
  );
}
