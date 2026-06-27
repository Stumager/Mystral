import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { PaywallSheet } from "../components/PaywallSheet";
import { BottomNav, Button } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { streamRequest } from "../utils/api";

interface LunarCalendarProps { onNavigate: (page: string) => void; }

interface AstroEvent {
  type: string; date: string; icon: string; title: string; description: string; days_until: number;
}

interface LunarToday {
  lunar_day: number; phase_name: string; phase_icon: string; moon_sign: string;
  illumination: number; energy: string;
  day_symbol: string; day_title: string; day_desc: string;
  favorable: string[]; unfavorable: string[];
  health: string; beauty: string; money: string; love: string;
  work: string; spiritual: string; dreams: string; stones: string;
  sign_desc: string; sign_favorable: string[]; sign_unfavorable: string[];
  sign_beauty: string; sign_health: string;
  upcoming_events: AstroEvent[];
}

interface MonthDay {
  date: string; lunar_day: number; phase_icon: string; moon_sign: string; energy: string;
}

const ENERGY_COLORS: Record<string, string> = {
  favorable: "#4ade80", neutral: "#9B8FBB", unfavorable: "#f87171", hecat: "#ef4444",
};
const ENERGY_BG: Record<string, string> = {
  favorable: "rgba(74,222,128,0.08)", neutral: "rgba(155,143,187,0.08)",
  unfavorable: "rgba(248,113,113,0.08)", hecat: "rgba(239,68,68,0.12)",
};

const TABS = ["work", "love", "money", "beauty", "spiritual", "dreams"] as const;
type Tab = typeof TABS[number];
const TAB_ICONS: Record<Tab, string> = { work: "⚒", love: "♡", money: "$", beauty: "✧", spiritual: "☉", dreams: "☽" };

export function LunarCalendar({ onNavigate }: LunarCalendarProps) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const lang = user?.lang ?? "ru";
  const [today, setToday] = useState<LunarToday | null>(null);
  const [month, setMonth] = useState<MonthDay[]>([]);
  const [tab, setTab] = useState<Tab>("work");
  const [question, setQuestion] = useState("");
  const [aiText, setAiText] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);
  const loaded = useRef(false);

  useEffect(() => {
    if (loaded.current) return;
    loaded.current = true;
    Promise.all([
      fetch(`/api/v1/lunar/today?lang=${lang}`).then(r => r.json()),
      fetch(`/api/v1/lunar/month?lang=${lang}`).then(r => r.json()),
    ]).then(([t, m]) => { setToday(t); setMonth(m); }).catch(() => {});
  }, []);

  async function handleAI() {
    if (user?.tier !== "pro") { setShowPaywall(true); return; }
    setAiLoading(true); setAiText("");
    try {
      await streamRequest("/lunar/ai-recommend", { question: question || null, lang },
        (c) => setAiText(prev => prev + c), () => setAiLoading(false), token ?? undefined,
        (msg) => { setAiText(msg); setAiLoading(false); });
    } catch (e: unknown) {
      const err = e as { code?: string; message?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setAiText(err.message || (lang === "ru" ? "Ошибка" : "Error"));
      setAiLoading(false);
    }
  }

  const todayStr = new Date().toISOString().slice(0, 10);
  const weekdays = t("lunar.weekdays").split(",");
  const firstDay = month.length > 0 ? (new Date(month[0].date).getDay() + 6) % 7 : 0;

  const tabLabels: Record<Tab, string> = lang === "ru"
    ? { work: "Работа", love: "Любовь", money: "Деньги", beauty: "Красота", spiritual: "Дух", dreams: "Сны" }
    : { work: "Work", love: "Love", money: "Money", beauty: "Beauty", spiritual: "Spirit", dreams: "Dreams" };

  const inputCls = "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 text-text-primary text-sm placeholder:text-text-faint focus:outline-none focus:border-violet-600 transition-colors";

  return (
    <div className="flex flex-col min-h-screen relative" style={{ background: "var(--gradient-page)", animation: "mystral-fadeup .3s ease-out" }}>
      <header className="flex items-center justify-between px-4 shrink-0 backdrop-blur-md lg:hidden" style={{ height: 46, background: "var(--bg-header)", borderBottom: "1px solid var(--border-gold)" }}>
        <button className="text-text-muted text-lg w-8" onClick={() => onNavigate("home")}>{"‹"}</button>
        <span className="font-cinzel" style={{ fontSize: 13, letterSpacing: ".26em", color: "#E8CD7E" }}>
          {t("lunar.title")}
        </span>
        <div className="w-8" />
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-6 pb-24 flex flex-col gap-4">
        {!today ? (
          <p className="text-text-muted text-xs text-center animate-pulse">{t("lunar.loading")}</p>
        ) : (
          <>
            {/* Block 1: Lunar day header card */}
            <div
              className="flex flex-col items-center gap-3 p-5"
              style={{
                borderRadius: 22,
                background: "linear-gradient(160deg,rgba(58,76,134,.22),rgba(255,255,255,.012))",
                border: "1px solid rgba(138,127,192,.24)",
              }}
            >
              <div className="w-24 h-24 rounded-full flex items-center justify-center text-4xl"
                style={{ background: "radial-gradient(circle at 35% 35%, rgba(255,255,255,0.15), rgba(138,127,192,0.08))", border: "1px solid rgba(138,127,192,.2)", boxShadow: "0 0 40px rgba(138,127,192,0.15)" }}>
                {today.phase_icon}
              </div>
              <p className="font-cormorant" style={{ fontSize: 38, color: "#F0E9DA", lineHeight: 1 }}>{today.lunar_day}</p>
              <p style={{ fontSize: 13, color: "#9890B8" }}>{today.lunar_day} {t("lunar.lunar_day_label")} · {today.phase_name}</p>
              <p style={{ fontSize: 13, color: "#9890B8" }}>{t("lunar.moon_in")} {today.moon_sign} · {today.illumination}%</p>
            </div>

            {/* Block 2: Day energy */}
            <div style={{ borderRadius: 18, padding: "16px 20px", background: ENERGY_BG[today.energy], border: `1px solid ${ENERGY_COLORS[today.energy]}30` }}>
              <div className="flex items-center gap-2 mb-1">
                <span style={{ fontSize: 14, color: ENERGY_COLORS[today.energy] }}>
                  {today.day_symbol === "Лампада" || today.day_symbol === "Lamp" ? "✧" : "*"}
                </span>
                <span className="font-cormorant" style={{ fontSize: 16, color: ENERGY_COLORS[today.energy] }}>
                  {"«"}{today.day_symbol}{"»"} — {today.day_title}
                </span>
              </div>
              <p className="text-text-muted text-xs leading-relaxed">{today.day_desc}</p>
              {today.energy === "hecat" && (
                <p className="text-xs mt-2" style={{ color: "#ef4444" }}>
                  {"⚠"} {lang === "ru" ? "День Гекаты — будьте осторожны" : "Hecate Day — be careful"}
                </p>
              )}
            </div>

            {/* Block 3: Favorable / Unfavorable */}
            <div
              className="p-4"
              style={{
                borderRadius: 18,
                background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))",
                border: "1px solid rgba(201,168,76,.13)",
              }}
            >
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".22em", color: "#4ade80", marginBottom: 8 }}>
                    {"✓"} {lang === "ru" ? "Благоприятно" : "Favorable"}
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {today.favorable.map(f => (
                      <span key={f} className="text-[10px] px-2 py-0.5 rounded-full" style={{ background: "rgba(74,222,128,0.1)", color: "#4ade80" }}>{f}</span>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".22em", color: "#f87171", marginBottom: 8 }}>
                    {"✗"} {lang === "ru" ? "Избегать" : "Avoid"}
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {today.unfavorable.map(f => (
                      <span key={f} className="text-[10px] px-2 py-0.5 rounded-full" style={{ background: "rgba(248,113,113,0.1)", color: "#f87171" }}>{f}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Block 4: Category tabs */}
            <div
              className="p-4"
              style={{
                borderRadius: 18,
                background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))",
                border: "1px solid rgba(201,168,76,.13)",
              }}
            >
              <div className="flex gap-1 overflow-x-auto pb-2 mb-3">
                {TABS.map(tb => (
                  <button key={tb} onClick={() => setTab(tb)}
                    className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[10px] whitespace-nowrap shrink-0 transition-colors"
                    style={{
                      background: tab === tb ? "rgba(201,168,76,.15)" : "transparent",
                      color: tab === tb ? "#E8CD7E" : "#9B8FBB",
                      border: `1px solid ${tab === tb ? "rgba(201,168,76,.3)" : "rgba(201,168,76,.08)"}`,
                    }}>
                    <span>{TAB_ICONS[tb]}</span><span>{tabLabels[tb]}</span>
                    <span style={{ display: "flex", gap: 2, marginLeft: 2 }}>
                      {Array.from({ length: 5 }, (_, i) => {
                        const seed = (today?.lunar_day ?? 1) * 7 + TABS.indexOf(tb) * 13 + 3;
                        const val = ((seed * 31 + i * 17) % 5) + 1;
                        return <span key={i} style={{ width: 4, height: 4, borderRadius: "50%", background: i < val ? "#C9A84C" : "rgba(255,255,255,.1)", boxShadow: i < val ? "0 0 4px rgba(201,168,76,.6)" : "none" }} />;
                      })}
                    </span>
                  </button>
                ))}
              </div>
              <p className="text-text-muted text-xs leading-relaxed">
                {today[tab as keyof LunarToday] as string}
              </p>
            </div>

            {/* Block 5: Moon in sign */}
            <div
              className="p-4"
              style={{
                borderRadius: 18,
                background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))",
                border: "1px solid rgba(201,168,76,.13)",
              }}
            >
              <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C", marginBottom: 8 }}>
                {t("lunar.moon_in")} {today.moon_sign}
              </p>
              <p className="text-text-muted text-xs leading-relaxed mb-2">{today.sign_desc}</p>
              <div className="grid grid-cols-2 gap-2 text-[10px]">
                <div>
                  <p style={{ color: "#4ade80" }} className="mb-1">{"✓"}</p>
                  {today.sign_favorable.map(f => <p key={f} className="text-text-faint">{f}</p>)}
                </div>
                <div>
                  <p style={{ color: "#f87171" }} className="mb-1">{"✗"}</p>
                  {today.sign_unfavorable.map(f => <p key={f} className="text-text-faint">{f}</p>)}
                </div>
              </div>
            </div>

            {/* Block 6: Upcoming events */}
            {today.upcoming_events && today.upcoming_events.length > 0 && (
              <div>
                <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C", marginBottom: 8 }}>
                  {lang === "ru" ? "Ближайшие события" : "Upcoming Events"}
                </p>
                <div className="flex gap-2 overflow-x-auto pb-2">
                  {today.upcoming_events.map((ev, i) => {
                    const isToday = ev.days_until === 0;
                    const isSoon = ev.days_until <= 2;
                    return (
                      <div key={i} className="shrink-0 w-36 flex flex-col gap-1"
                        style={{
                          borderRadius: 18,
                          padding: "12px 14px",
                          background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))",
                          border: isToday ? "1px solid rgba(201,168,76,0.5)"
                            : isSoon ? "1px solid rgba(201,168,76,.2)"
                            : "1px solid rgba(201,168,76,.08)",
                        }}>
                        <div className="flex items-center gap-1.5">
                          <span className="text-sm">{ev.icon}</span>
                          <span className="text-text-primary text-[10px] font-cormorant leading-tight">{ev.title}</span>
                        </div>
                        <p className="text-text-faint text-[9px]">{ev.date}</p>
                        <p className="text-[9px]" style={{ color: isToday ? "#C9A84C" : isSoon ? "#E8CD7E" : "#9B8FBB" }}>
                          {isToday ? (lang === "ru" ? "Сегодня!" : "Today!")
                            : lang === "ru" ? `через ${ev.days_until} дн.` : `in ${ev.days_until} days`}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Block 7: Stones */}
            <div
              className="p-4"
              style={{
                borderRadius: 18,
                background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))",
                border: "1px solid rgba(201,168,76,.13)",
              }}
            >
              <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C", marginBottom: 8 }}>
                {"♦"} {lang === "ru" ? "Камни дня" : "Day Stones"}
              </p>
              <p className="text-text-muted text-xs">{today.stones}</p>
            </div>

            {/* Block 8: Month calendar */}
            <div
              className="p-4"
              style={{
                borderRadius: 18,
                background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))",
                border: "1px solid rgba(201,168,76,.13)",
              }}
            >
              <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C", marginBottom: 12 }}>
                {t("lunar.calendar")}
              </p>
              <div className="grid grid-cols-7 gap-1 text-center">
                {weekdays.map(d => (
                  <span key={d} className="text-text-faint text-[9px] pb-1">{d}</span>
                ))}
                {Array.from({ length: firstDay }).map((_, i) => <div key={`e${i}`} />)}
                {month.map(day => {
                  const dayNum = parseInt(day.date.split("-")[2]);
                  const isToday = day.date === todayStr;
                  return (
                    <div key={day.date} className="flex flex-col items-center py-1"
                      style={{
                        borderRadius: 10,
                        background: isToday ? "rgba(201,168,76,.12)" : "transparent",
                        border: isToday ? "1px solid rgba(201,168,76,.3)" : "1px solid transparent",
                      }}>
                      <span className={`text-[10px] ${isToday ? "text-text-primary font-bold" : "text-text-muted"}`} style={isToday ? { color: "#E8CD7E" } : undefined}>{dayNum}</span>
                      <span className="text-[8px] leading-none">{day.phase_icon}</span>
                      <span className="w-1.5 h-1.5 rounded-full mt-0.5" style={{ background: ENERGY_COLORS[day.energy] || "#9B8FBB" }} />
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Block 9: AI recommendation (Pro) */}
            <div
              className="p-4"
              style={{
                borderRadius: 18,
                background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))",
                border: "1px solid rgba(201,168,76,.13)",
              }}
            >
              <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C", marginBottom: 12 }}>
                {lang === "ru" ? "AI рекомендация" : "AI Recommendation"}
                {user?.tier !== "pro" && <span className="ml-1" style={{ color: "#C9A84C" }}>Pro</span>}
              </p>
              <input className={inputCls + " mb-2"} value={question} onChange={e => setQuestion(e.target.value)}
                placeholder={lang === "ru" ? "Задай вопрос лунному календарю..." : "Ask the lunar calendar..."} />
              {aiText ? (
                <p className="text-text-muted text-xs leading-relaxed mb-2">
                  {aiText}{aiLoading && <span className="animate-pulse">{"▍"}</span>}
                </p>
              ) : null}
              <Button variant="primary" size="sm" className="w-full" style={{ borderRadius: 14 }} onClick={handleAI} disabled={aiLoading}>
                {aiLoading ? "..." : (lang === "ru" ? "Получить рекомендацию" : "Get recommendation")}
              </Button>
            </div>
          </>
        )}
      </main>

      <BottomNav active="moon" onNavigate={onNavigate} />
      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
    </div>
  );
}
