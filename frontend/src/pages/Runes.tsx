import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { PaywallSheet } from "../components/PaywallSheet";
import { BottomNav, Button } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { apiRequest, streamRequest } from "../utils/api";

const RUNE_SPREAD_ICONS: Record<string, string> = {
  rune_of_day: "☀", three_norns: "△", runic_cross: "+",
  relationship: "♡", yes_no: "?", yggdrasil: "⚘", year_spread: "▦",
};

interface RunesProps { onNavigate: (page: string) => void; }

interface DrawnRune {
  id: string; index: number; name: string; symbol: string; keyword: string;
  meaning: string; reversed: boolean; can_reverse: boolean; position_name: string;
  aett: number; element: string; deity: string;
  love: string; career: string; health: string; magic: string; as_amulet: string;
}

interface SpreadInfo {
  id: string; name: string; description: string; icon: string; count: number; tier: string; positions: string[];
}

interface DrawResult {
  spread_type: string; spread_name: string; positions: string[]; drawn_runes: DrawnRune[]; question: string | null;
}

interface PersonalData {
  life_path: number;
  personal_rune: DrawnRune;
  year_rune: DrawnRune;
  year: number;
}

interface Stave {
  id: string; name: string; symbols: string; runes_used: string[]; purpose: string; description: string; how_to_use: string;
}

interface HistoryEntry {
  id: string; spread_type: string; spread_name: string; question: string | null; rune_preview: string[]; created_at: string;
}

type Screen = "spreads" | "question" | "drawing" | "result" | "personal" | "staves" | "history";

export function Runes({ onNavigate }: RunesProps) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const lang = user?.lang ?? "ru";
  const ru = lang === "ru";
  const isPro = user?.tier === "pro";

  const [screen, setScreen] = useState<Screen>("spreads");
  const [spreads, setSpreads] = useState<SpreadInfo[]>([]);
  const [selectedSpread, setSelectedSpread] = useState<SpreadInfo | null>(null);
  const [question, setQuestion] = useState("");
  const [drawResult, setDrawResult] = useState<DrawResult | null>(null);
  const [interpretation, setInterpretation] = useState("");
  const [interpretLoading, setInterpretLoading] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);
  const [error, setError] = useState("");

  const [personalData, setPersonalData] = useState<PersonalData | null>(null);
  const [personalAI, setPersonalAI] = useState("");
  const [personalAILoading, setPersonalAILoading] = useState(false);

  const [staves, setStaves] = useState<Stave[]>([]);
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  const [revealedCount, setRevealedCount] = useState(0);

  const loaded = useRef(false);

  useEffect(() => {
    if (loaded.current) return;
    loaded.current = true;
    fetch(`/api/v1/runes/spreads?lang=${lang}`).then(r => r.json()).then(setSpreads).catch(() => {});
  }, []);

  function selectSpread(s: SpreadInfo) {
    if (s.tier === "pro" && !isPro) { setShowPaywall(true); return; }
    setSelectedSpread(s);
    if (s.id === "rune_of_day") { doDrawRunes(s.id, ""); return; }
    setQuestion(""); setScreen("question");
  }

  async function doDrawRunes(spreadType: string, q: string) {
    setError(""); setInterpretation(""); setRevealedCount(0);
    setScreen("drawing");
    try {
      const data = await apiRequest<DrawResult>(
        "/runes/draw",
        { spread_type: spreadType, question: q || null, lang },
        token ?? undefined,
      );
      setDrawResult(data);
      let count = 0;
      const interval = setInterval(() => {
        count++;
        setRevealedCount(count);
        if (count >= data.drawn_runes.length) clearInterval(interval);
      }, 400);
      setTimeout(() => setScreen("result"), data.drawn_runes.length * 400 + 200);
    } catch (e: unknown) {
      const err = e as { code?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setError(ru ? "Ошибка" : "Error");
      setScreen("spreads");
    }
  }

  async function handleInterpret() {
    if (!drawResult) return;
    if (drawResult.spread_type !== "rune_of_day" && !isPro) { setShowPaywall(true); return; }
    setInterpretLoading(true); setInterpretation("");
    try {
      await streamRequest("/runes/interpret", {
        spread_type: drawResult.spread_type,
        drawn_runes: drawResult.drawn_runes.map(r => ({ id: r.id, name: r.name, reversed: r.reversed, position_name: r.position_name })),
        question: drawResult.question, lang,
      }, (c) => setInterpretation(prev => prev + c), () => setInterpretLoading(false), token ?? undefined,
        (msg) => { setInterpretation(msg); setInterpretLoading(false); });
    } catch (e: unknown) {
      const err = e as { code?: string; message?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setInterpretation(err.message || (ru ? "Ошибка" : "Error"));
      setInterpretLoading(false);
    }
  }

  async function loadPersonal() {
    setScreen("personal"); setPersonalAI("");
    if (personalData) return;
    try {
      const r = await fetch("/api/v1/runes/personal", { headers: { Authorization: `Bearer ${token}` } });
      if (!r.ok) throw new Error();
      setPersonalData(await r.json());
    } catch { setError(ru ? "Заполни дату рождения в профиле" : "Set birth date in profile"); }
  }

  async function loadStaves() {
    setScreen("staves");
    if (staves.length) return;
    fetch(`/api/v1/runes/staves?lang=${lang}`).then(r => r.json()).then(setStaves).catch(() => {});
  }

  async function loadHistory() {
    setScreen("history");
    fetch("/api/v1/runes/history", { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json()).then(setHistory).catch(() => {});
  }

  async function handlePersonalAI() {
    if (!personalData) return;
    setPersonalAILoading(true); setPersonalAI("");
    try {
      await streamRequest("/runes/interpret", {
        spread_type: "rune_of_day",
        drawn_runes: [{ id: personalData.personal_rune.id, name: personalData.personal_rune.name, reversed: false, position_name: ru ? "Личная руна" : "Personal rune" }],
        question: ru ? "Расскажи подробно о моей личной руне и руне года" : "Tell me about my personal rune and year rune in detail",
        lang,
      }, (c) => setPersonalAI(prev => prev + c), () => setPersonalAILoading(false), token ?? undefined,
        (msg) => { setPersonalAI(msg); setPersonalAILoading(false); });
    } catch (e: unknown) {
      const err = e as { message?: string };
      setPersonalAI(err.message || (ru ? "Ошибка" : "Error")); setPersonalAILoading(false);
    }
  }

  function reset() {
    setScreen("spreads"); setDrawResult(null); setInterpretation(""); setError(""); setSelectedSpread(null);
  }

  const inputCls = "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 text-text-primary text-sm placeholder:text-text-faint focus:outline-none focus:border-violet-600 transition-colors";

  function backBtn(target: Screen = "spreads") {
    return <button className="text-text-muted text-lg w-8" onClick={() => setScreen(target)}>&#8249;</button>;
  }

  return (
    <div className="flex flex-col min-h-screen relative" style={{ background: "var(--gradient-page)", animation: "mystral-fadeup .3s ease-out" }}>
      <header className="flex items-center justify-between px-4 shrink-0 backdrop-blur-md lg:hidden" style={{ height: 46, background: "var(--bg-header)", borderBottom: "1px solid var(--border-gold)" }}>
        {screen === "spreads" ? (
          <button className="text-text-muted text-lg w-8" onClick={() => onNavigate("home")}>&#8249;</button>
        ) : backBtn("spreads")}
        <span className="font-cinzel tracking-[.26em]" style={{ fontSize: 13, color: "#E8CD7E" }}>{t("runes.title")}</span>
        <div className="w-8" />
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-6 pb-24 flex flex-col gap-4">

        {/* SPREADS SCREEN */}
        {screen === "spreads" && (
          <>
            <p className="text-text-muted text-xs text-center">{t("runes.focus")}</p>
            <div className="flex flex-col gap-4">
              {spreads.map(s => (
                <button key={s.id} onClick={() => selectSpread(s)}
                  className="text-left transition-all"
                  style={{ display: "flex", gap: 16, padding: "18px 20px", borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)" }}>
                  <span className="shrink-0" style={{ width: 44, height: 44, borderRadius: 12, background: "rgba(201,168,76,.08)", border: "1px solid rgba(201,168,76,.2)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20, color: "#C9A84C" }}>{RUNE_SPREAD_ICONS[s.id] ?? s.icon}</span>
                  <div className="flex-1 min-w-0">
                    <span className="font-cormorant" style={{ fontSize: 22, color: "#F0E9DA" }}>{s.name}</span>
                    <p className="text-text-faint text-[10px] mt-0.5">{s.description}</p>
                    <div className="flex items-center gap-2 mt-1.5">
                      <span className="text-text-faint text-[9px]">{s.count} {ru ? "рун" : "runes"}</span>
                      {s.tier === "pro" && (
                        <span className="text-[8px] px-1.5 py-0.5 rounded-full" style={{ background: "#C9A84C", color: "#0D0B1F" }}>Pro</span>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>

            <div className="flex gap-2">
              <Button variant="ghost" size="sm" className="flex-1" onClick={loadPersonal}>
                {ru ? "Моя руна" : "My Rune"}
              </Button>
              <Button variant="ghost" size="sm" className="flex-1" onClick={loadStaves}>
                {ru ? "Ставы" : "Staves"}
              </Button>
              <Button variant="ghost" size="sm" className="flex-1" onClick={loadHistory}>
                {ru ? "История" : "History"}
              </Button>
            </div>
          </>
        )}

        {/* QUESTION SCREEN */}
        {screen === "question" && selectedSpread && (
          <div className="flex flex-col gap-4 pt-4">
            <div className="text-center">
              <span className="text-3xl">{selectedSpread.icon}</span>
              <p className="font-cormorant mt-2" style={{ fontSize: 22, color: "#F0E9DA" }}>{selectedSpread.name}</p>
              <p className="text-text-faint text-xs">{selectedSpread.description}</p>
            </div>
            {selectedSpread.id !== "rune_of_day" && (
              <textarea className={inputCls + " min-h-[80px]"} value={question} onChange={e => setQuestion(e.target.value)}
                placeholder={ru ? "Задай вопрос рунам..." : "Ask the runes a question..."} />
            )}
            {selectedSpread.id === "relationship" && (
              <input className={inputCls} placeholder={ru ? "Имя партнёра" : "Partner's name"} />
            )}
            <Button variant="primary" className="w-full" onClick={() => doDrawRunes(selectedSpread.id, question)}>
              {t("runes.draw")}
            </Button>
          </div>
        )}

        {/* DRAWING ANIMATION */}
        {screen === "drawing" && drawResult && (
          <div className="flex justify-center items-center pt-8">
            <div className="flex gap-3 flex-wrap justify-center">
              {drawResult.drawn_runes.map((r, i) => (
                <div key={i} className="w-20 h-28 flex flex-col items-center justify-center gap-1 transition-all duration-500"
                  style={{
                    borderRadius: 14,
                    background: i < revealedCount ? "linear-gradient(160deg,rgba(75,60,134,.22),rgba(255,255,255,.012))" : "rgba(255,255,255,.03)",
                    border: `1px solid ${i < revealedCount ? "rgba(138,127,192,.24)" : "rgba(138,127,192,.1)"}`,
                    opacity: i < revealedCount ? 1 : 0.3,
                    transform: i < revealedCount ? "scale(1)" : "scale(0.9)",
                  }}>
                  {i < revealedCount ? (
                    <>
                      <span style={{ fontSize: 48, color: r.reversed ? "#D98A8A" : "#A99BE0", transform: r.reversed ? "rotate(180deg)" : "none", display: "inline-block" }}>
                        {r.symbol}
                      </span>
                      <span className="font-cinzel uppercase" style={{ fontSize: 9, letterSpacing: ".2em", color: "#C9A84C" }}>{r.name}</span>
                    </>
                  ) : <span className="text-2xl animate-pulse" style={{ color: "#A99BE0" }}>&#5765;</span>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* RESULT SCREEN */}
        {screen === "result" && drawResult && (
          <>
            <p className="font-cinzel uppercase text-center" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>{drawResult.spread_name}</p>

            <div className="flex gap-3 flex-wrap justify-center mb-2">
              {drawResult.drawn_runes.map((r, i) => (
                <div key={i} className="w-20 flex flex-col items-center py-3 gap-1"
                  style={{ borderRadius: 14, background: "linear-gradient(160deg,rgba(75,60,134,.22),rgba(255,255,255,.012))", border: "1px solid rgba(138,127,192,.24)", boxShadow: "0 0 20px rgba(75,60,134,0.15)" }}>
                  <span className="text-[8px] text-text-faint">{r.position_name}</span>
                  <span style={{ fontSize: 48, color: r.reversed ? "#D98A8A" : "#A99BE0", transform: r.reversed ? "rotate(180deg)" : "none", display: "inline-block" }}>
                    {r.symbol}
                  </span>
                  <span className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".2em", color: "#C9A84C" }}>{r.name}</span>
                  <span className="text-[8px] px-1.5 py-0.5 rounded-full"
                    style={{ background: r.reversed ? "rgba(217,138,138,0.12)" : "rgba(138,127,192,.12)", color: r.reversed ? "#D98A8A" : "#A99BE0" }}>
                    {r.reversed ? t("runes.reversed") : t("runes.upright")}
                  </span>
                </div>
              ))}
            </div>

            {drawResult.drawn_runes.map((r, i) => (
              <div key={i} style={{ borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "16px 18px" }}>
                <div className="flex items-center gap-2 mb-1">
                  <span style={{ fontSize: 28, color: r.reversed ? "#D98A8A" : "#A99BE0", transform: r.reversed ? "rotate(180deg)" : "none", display: "inline-block" }}>{r.symbol}</span>
                  <span className="font-cormorant" style={{ fontSize: 22, color: "#F0E9DA" }}>{r.name}</span>
                  <span className="text-text-faint text-[9px]">{r.keyword}</span>
                </div>
                <p className="font-cinzel uppercase" style={{ fontSize: 9, letterSpacing: ".2em", color: "#C9A84C", marginBottom: 4 }}>{r.position_name}</p>
                <p className="text-text-muted text-xs leading-relaxed">{r.meaning}</p>
              </div>
            ))}

            {interpretation ? (
              <div style={{ borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "16px 18px" }}>
                <p className="font-cinzel uppercase mb-2" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>{t("runes.interpretation_label")}</p>
                <p className="text-text-muted text-xs leading-relaxed">
                  {interpretation}{interpretLoading && <span className="animate-pulse">|</span>}
                </p>
              </div>
            ) : (
              <Button variant="primary" className="w-full" onClick={handleInterpret} disabled={interpretLoading}>
                {interpretLoading ? t("runes.reading") : t("runes.get_interpretation")}
                {drawResult.spread_type !== "rune_of_day" && !isPro && <span className="ml-1" style={{ color: "#C9A84C" }}>*</span>}
              </Button>
            )}

            <Button variant="ghost" className="w-full" onClick={reset}>{t("runes.new_draw")}</Button>
          </>
        )}

        {/* PERSONAL RUNE SCREEN */}
        {screen === "personal" && (
          <>
            {error && !personalData ? (
              <div style={{ borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "16px 18px" }}>
                <p className="text-text-muted text-sm text-center">{error}</p>
                <Button variant="primary" size="sm" className="w-full mt-3" onClick={() => onNavigate("profile")}>
                  {ru ? "Открыть профиль" : "Open profile"}
                </Button>
              </div>
            ) : personalData ? (
              <>
                <div className="text-center">
                  <p className="font-cinzel uppercase mb-2" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                    {ru ? "Твоя личная руна" : "Your Personal Rune"}
                  </p>
                  <div className="w-28 h-28 mx-auto flex items-center justify-center mb-2"
                    style={{ borderRadius: 18, background: "linear-gradient(160deg,rgba(75,60,134,.22),rgba(255,255,255,.012))", border: "1px solid rgba(138,127,192,.24)", boxShadow: "0 0 40px rgba(75,60,134,0.2)" }}>
                    <span style={{ fontSize: 56, color: "#C9A84C" }}>{personalData.personal_rune.symbol}</span>
                  </div>
                  <p className="font-cormorant" style={{ fontSize: 22, color: "#F0E9DA" }}>{personalData.personal_rune.name}</p>
                  <p className="text-text-muted text-xs">{personalData.personal_rune.keyword}</p>
                  <p className="text-text-faint text-[10px] mt-1">{ru ? "Число жизненного пути" : "Life path"}: {personalData.life_path}</p>
                </div>

                <div style={{ borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "16px 18px" }}>
                  <p className="text-text-muted text-xs leading-relaxed">{personalData.personal_rune.meaning}</p>
                </div>

                <div className="text-center mt-2">
                  <p className="font-cinzel uppercase mb-2" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                    {ru ? `Руна ${personalData.year} года` : `Rune of ${personalData.year}`}
                  </p>
                  <div className="w-20 h-20 mx-auto flex items-center justify-center mb-2"
                    style={{ borderRadius: 14, background: "linear-gradient(160deg,rgba(75,60,134,.22),rgba(255,255,255,.012))", border: "1px solid rgba(138,127,192,.24)" }}>
                    <span style={{ fontSize: 48, color: "#A99BE0" }}>{personalData.year_rune.symbol}</span>
                  </div>
                  <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".2em", color: "#C9A84C" }}>{personalData.year_rune.name}</p>
                  <p className="text-text-muted text-[10px]">{personalData.year_rune.keyword}</p>
                </div>

                <div style={{ borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "16px 18px" }}>
                  <p className="text-text-muted text-xs leading-relaxed">{personalData.year_rune.meaning}</p>
                </div>

                {personalAI ? (
                  <div style={{ borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "16px 18px" }}>
                    <p className="font-cinzel uppercase mb-2" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>{t("runes.interpretation_label")}</p>
                    <p className="text-text-muted text-xs leading-relaxed">
                      {personalAI}{personalAILoading && <span className="animate-pulse">|</span>}
                    </p>
                  </div>
                ) : (
                  <Button variant="primary" className="w-full" onClick={handlePersonalAI} disabled={personalAILoading}>
                    {personalAILoading ? t("runes.reading") : (ru ? "Узнать подробнее" : "Learn more")}
                  </Button>
                )}
              </>
            ) : (
              <p className="text-text-muted text-xs text-center animate-pulse">{ru ? "Загрузка..." : "Loading..."}</p>
            )}
          </>
        )}

        {/* STAVES SCREEN */}
        {screen === "staves" && (
          <>
            <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
              {ru ? "Ставы-обереги" : "Protective Staves"}
            </p>
            <p className="text-text-muted text-[10px] mb-2">
              {ru ? "Комбинации рун для достижения целей. Нарисуйте или носите как амулет." : "Rune combinations for achieving goals. Draw or wear as an amulet."}
            </p>
            {staves.map(s => (
              <div key={s.id} style={{ borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "16px 18px" }}>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-display text-lg tracking-widest" style={{ color: "#C9A84C" }}>{s.symbols}</span>
                  <span className="font-cormorant" style={{ fontSize: 22, color: "#F0E9DA" }}>{s.name}</span>
                </div>
                <p className="font-cinzel uppercase" style={{ fontSize: 9, letterSpacing: ".2em", color: "#C9A84C", marginBottom: 4 }}>{s.purpose}</p>
                <p className="text-text-muted text-xs leading-relaxed mb-2">{s.description}</p>
                <div className="px-2 py-1.5" style={{ borderRadius: 12, background: "rgba(255,255,255,.03)", border: "1px solid rgba(201,168,76,.1)" }}>
                  <p className="font-cinzel uppercase mb-0.5" style={{ fontSize: 9, letterSpacing: ".2em", color: "#C9A84C" }}>{ru ? "Как использовать" : "How to use"}</p>
                  <p className="text-text-muted text-[10px]">{s.how_to_use}</p>
                </div>
              </div>
            ))}

            <div style={{ borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "16px 18px" }}>
              <p className="font-cinzel uppercase mb-2" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                {ru ? "Биндруны" : "Bindrunes"}
              </p>
              <p className="text-text-muted text-xs leading-relaxed">
                {ru
                  ? "Биндруна — это комбинация двух или более рун, наложенных друг на друга. Создаёт уникальный символ с объединённой энергией всех составляющих рун. Каждый став выше — по сути биндруна."
                  : "A bindrune is a combination of two or more runes overlaid on each other. Creates a unique symbol with combined energy of all component runes. Each stave above is essentially a bindrune."}
              </p>
            </div>
          </>
        )}

        {/* HISTORY SCREEN */}
        {screen === "history" && (
          <>
            <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
              {ru ? "Последние расклады" : "Recent Readings"}
            </p>
            {history.length === 0 ? (
              <p className="text-text-muted text-xs text-center mt-4">{ru ? "Пока нет раскладов" : "No readings yet"}</p>
            ) : history.map(h => (
              <div key={h.id} style={{ borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "16px 18px" }}>
                <div className="flex items-center justify-between mb-1">
                  <span className="font-cormorant" style={{ fontSize: 22, color: "#F0E9DA" }}>{h.spread_name}</span>
                  <span className="text-text-faint text-[9px]">{h.created_at ? new Date(h.created_at).toLocaleDateString() : ""}</span>
                </div>
                {h.question && <p className="text-text-faint text-[10px] mb-1">{h.question}</p>}
                <div className="flex gap-1">
                  {h.rune_preview.map((id, i) => {
                    const sym = id;
                    return <span key={i} style={{ fontSize: 28, color: "#A99BE0" }}>{sym}</span>;
                  })}
                </div>
              </div>
            ))}
          </>
        )}
      </main>

      <BottomNav active="home" onNavigate={onNavigate} />
      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
    </div>
  );
}
