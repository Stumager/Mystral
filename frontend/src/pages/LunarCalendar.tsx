import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { PaywallSheet } from "../components/PaywallSheet";
import { BottomNav, Button, Card } from "../components/ui";
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
const TAB_ICONS: Record<Tab, string> = { work: "💼", love: "❤️", money: "💰", beauty: "💇", spiritual: "🧘", dreams: "😴" };

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
        (c) => setAiText(prev => prev + c), () => setAiLoading(false), token ?? undefined);
    } catch (e: unknown) {
      const err = e as { code?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setAiText(lang === "ru" ? "Ошибка" : "Error");
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
    <div className="flex flex-col min-h-screen relative" style={{ background: "var(--gradient-page)" }}>
      <header className="flex items-center justify-between px-4 shrink-0 backdrop-blur-md" style={{ height: 46, background: "var(--bg-header)", borderBottom: "1px solid var(--border-gold)" }}>
        <button className="text-text-muted text-lg w-8" onClick={() => onNavigate("home")}>‹</button>
        <span className="font-cinzel text-sm tracking-[.25em]" style={{ color: "#E8CD7E" }}>{t("lunar.title")}</span>
        <div className="w-8" />
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-6 pb-24 flex flex-col gap-4">
        {!today ? (
          <p className="text-text-muted text-xs text-center animate-pulse">{t("lunar.loading")}</p>
        ) : (
          <>
            {/* Block 1: Moon visualization */}
            <div className="flex flex-col items-center gap-2">
              <div className="w-24 h-24 rounded-full flex items-center justify-center text-4xl"
                style={{ background: "radial-gradient(circle at 35% 35%, rgba(255,255,255,0.15), rgba(107,78,255,0.08))", border: "1px solid rgba(255,255,255,0.1)", boxShadow: "0 0 40px rgba(107,78,255,0.2)" }}>
                {today.phase_icon}
              </div>
              <p className="font-display text-3xl text-text-primary">{today.lunar_day}</p>
              <p className="text-text-muted text-xs">{today.lunar_day} {t("lunar.lunar_day_label")} · {today.phase_name}</p>
              <p className="text-text-faint text-xs">{t("lunar.moon_in")} {today.moon_sign} · {today.illumination}%</p>
            </div>

            {/* Block 2: Day energy */}
            <div className="rounded-xl px-4 py-3" style={{ background: ENERGY_BG[today.energy], border: `1px solid ${ENERGY_COLORS[today.energy]}30` }}>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-lg">{today.day_symbol === "Лампада" || today.day_symbol === "Lamp" ? "🪔" : "✦"}</span>
                <span className="font-display text-sm" style={{ color: ENERGY_COLORS[today.energy] }}>
                  «{today.day_symbol}» — {today.day_title}
                </span>
              </div>
              <p className="text-text-muted text-xs leading-relaxed">{today.day_desc}</p>
              {today.energy === "hecat" && (
                <p className="text-xs mt-2" style={{ color: "#ef4444" }}>
                  ⚠️ {lang === "ru" ? "День Гекаты — будьте осторожны" : "Hecate Day — be careful"}
                </p>
              )}
            </div>

            {/* Block 3: Favorable / Unfavorable */}
            <Card>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="text-[9px] uppercase tracking-widest mb-2" style={{ color: "#4ade80" }}>
                    ✅ {lang === "ru" ? "Благоприятно" : "Favorable"}
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {today.favorable.map(f => (
                      <span key={f} className="text-[10px] px-2 py-0.5 rounded-full" style={{ background: "rgba(74,222,128,0.1)", color: "#4ade80" }}>{f}</span>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-[9px] uppercase tracking-widest mb-2" style={{ color: "#f87171" }}>
                    ❌ {lang === "ru" ? "Избегать" : "Avoid"}
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {today.unfavorable.map(f => (
                      <span key={f} className="text-[10px] px-2 py-0.5 rounded-full" style={{ background: "rgba(248,113,113,0.1)", color: "#f87171" }}>{f}</span>
                    ))}
                  </div>
                </div>
              </div>
            </Card>

            {/* Block 4: Category tabs */}
            <Card>
              <div className="flex gap-1 overflow-x-auto pb-2 mb-3">
                {TABS.map(tb => (
                  <button key={tb} onClick={() => setTab(tb)}
                    className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[10px] whitespace-nowrap shrink-0 transition-colors"
                    style={{
                      background: tab === tb ? "rgba(107,78,255,0.2)" : "transparent",
                      color: tab === tb ? "#9B8AFF" : "#9B8FBB",
                      border: `1px solid ${tab === tb ? "rgba(107,78,255,0.3)" : "rgba(107,78,255,0.08)"}`,
                    }}>
                    <span>{TAB_ICONS[tb]}</span><span>{tabLabels[tb]}</span>
                  </button>
                ))}
              </div>
              <p className="text-text-muted text-xs leading-relaxed">
                {today[tab as keyof LunarToday] as string}
              </p>
            </Card>

            {/* Block 5: Moon in sign */}
            <Card>
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">
                {t("lunar.moon_in")} {today.moon_sign}
              </p>
              <p className="text-text-muted text-xs leading-relaxed mb-2">{today.sign_desc}</p>
              <div className="grid grid-cols-2 gap-2 text-[10px]">
                <div>
                  <p style={{ color: "#4ade80" }} className="mb-1">✅</p>
                  {today.sign_favorable.map(f => <p key={f} className="text-text-faint">{f}</p>)}
                </div>
                <div>
                  <p style={{ color: "#f87171" }} className="mb-1">❌</p>
                  {today.sign_unfavorable.map(f => <p key={f} className="text-text-faint">{f}</p>)}
                </div>
              </div>
            </Card>

            {/* Block 6: Upcoming events */}
            {today.upcoming_events && today.upcoming_events.length > 0 && (
              <div>
                <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">
                  📅 {lang === "ru" ? "Ближайшие события" : "Upcoming Events"}
                </p>
                <div className="flex gap-2 overflow-x-auto pb-2">
                  {today.upcoming_events.map((ev, i) => {
                    const isToday = ev.days_until === 0;
                    const isSoon = ev.days_until <= 2;
                    return (
                      <div key={i} className="shrink-0 w-36 rounded-xl px-3 py-2.5 flex flex-col gap-1"
                        style={{
                          background: "rgba(107,78,255,0.06)",
                          border: isToday ? "1px solid rgba(201,168,76,0.5)"
                            : isSoon ? "1px solid rgba(107,78,255,0.3)"
                            : "1px solid rgba(107,78,255,0.1)",
                        }}>
                        <div className="flex items-center gap-1.5">
                          <span className="text-sm">{ev.icon}</span>
                          <span className="text-text-primary text-[10px] font-display leading-tight">{ev.title}</span>
                        </div>
                        <p className="text-text-faint text-[9px]">{ev.date}</p>
                        <p className="text-[9px]" style={{ color: isToday ? "#C9A84C" : isSoon ? "#9B8AFF" : "#9B8FBB" }}>
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
            <Card>
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">
                💎 {lang === "ru" ? "Камни дня" : "Day Stones"}
              </p>
              <p className="text-text-muted text-xs">{today.stones}</p>
            </Card>

            {/* Block 7: Month calendar */}
            <Card>
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">{t("lunar.calendar")}</p>
              <div className="grid grid-cols-7 gap-1 text-center">
                {weekdays.map(d => (
                  <span key={d} className="text-text-faint text-[9px] pb-1">{d}</span>
                ))}
                {Array.from({ length: firstDay }).map((_, i) => <div key={`e${i}`} />)}
                {month.map(day => {
                  const dayNum = parseInt(day.date.split("-")[2]);
                  const isToday = day.date === todayStr;
                  return (
                    <div key={day.date} className="flex flex-col items-center py-1 rounded-lg"
                      style={{ background: isToday ? "rgba(107,78,255,0.2)" : "transparent",
                               border: isToday ? "1px solid rgba(107,78,255,0.4)" : "1px solid transparent" }}>
                      <span className={`text-[10px] ${isToday ? "text-text-primary font-bold" : "text-text-muted"}`}>{dayNum}</span>
                      <span className="text-[8px] leading-none">{day.phase_icon}</span>
                      <span className="w-1.5 h-1.5 rounded-full mt-0.5" style={{ background: ENERGY_COLORS[day.energy] || "#9B8FBB" }} />
                    </div>
                  );
                })}
              </div>
            </Card>

            {/* Block 8: AI recommendation (Pro) */}
            <Card>
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">
                🔮 {lang === "ru" ? "AI рекомендация" : "AI Recommendation"}
                {user?.tier !== "pro" && <span className="ml-1" style={{ color: "#C9A84C" }}>Pro</span>}
              </p>
              <input className={inputCls + " mb-2"} value={question} onChange={e => setQuestion(e.target.value)}
                placeholder={lang === "ru" ? "Задай вопрос лунному календарю..." : "Ask the lunar calendar..."} />
              {aiText ? (
                <p className="text-text-muted text-xs leading-relaxed mb-2">
                  {aiText}{aiLoading && <span className="animate-pulse">▍</span>}
                </p>
              ) : null}
              <Button variant="primary" size="sm" className="w-full" onClick={handleAI} disabled={aiLoading}>
                {aiLoading ? "..." : (lang === "ru" ? "Получить рекомендацию ✦" : "Get recommendation ✦")}
              </Button>
            </Card>
          </>
        )}
      </main>

      <BottomNav active="moon" onNavigate={onNavigate} />
      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
    </div>
  );
}
