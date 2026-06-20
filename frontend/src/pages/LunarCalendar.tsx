import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { BottomNav, Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";

interface LunarCalendarProps {
  onNavigate: (page: string) => void;
}

interface LunarToday {
  lunar_day: number;
  phase_name: string;
  phase_icon: string;
  moon_sign: string;
  recommendations: string[];
  energy: string;
}

interface MonthDay {
  date: string;
  lunar_day: number;
  phase_icon: string;
}

export function LunarCalendar({ onNavigate }: LunarCalendarProps) {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [today, setToday] = useState<LunarToday | null>(null);
  const [month, setMonth] = useState<MonthDay[]>([]);
  const loaded = useRef(false);

  useEffect(() => {
    if (loaded.current) return;
    loaded.current = true;
    const lang = user?.lang ?? "ru";

    Promise.all([
      fetch(`/api/v1/lunar/today?lang=${lang}`).then(r => r.json()),
      fetch("/api/v1/lunar/month").then(r => r.json()),
    ])
      .then(([t, m]) => { setToday(t); setMonth(m); })
      .catch(() => {});
  }, []);

  const todayStr = new Date().toISOString().slice(0, 10);
  const weekdays = t("lunar.weekdays").split(",");

  const firstDayOfMonth = month.length > 0
    ? (new Date(month[0].date).getDay() + 6) % 7
    : 0;

  return (
    <div className="flex flex-col min-h-screen bg-bg-deep relative">
      <header
        className="flex items-center justify-between px-4 shrink-0 backdrop-blur-sm"
        style={{ height: 46, background: "rgba(6,4,20,0.75)" }}
      >
        <button className="text-text-muted text-lg w-8" onClick={() => onNavigate("home")}>‹</button>
        <span className="font-display text-text-primary text-base tracking-widest">{t("lunar.title")}</span>
        <div className="w-8" />
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-6 pb-24 flex flex-col gap-5">
        {!today ? (
          <p className="text-text-muted text-xs text-center animate-pulse">{t("lunar.loading")}</p>
        ) : (
          <>
            {/* Moon orb */}
            <div className="flex flex-col items-center gap-3">
              <div
                className="w-28 h-28 rounded-full flex items-center justify-center text-5xl"
                style={{
                  background: "radial-gradient(circle at 35% 35%, rgba(255,255,255,0.15), rgba(107,78,255,0.08))",
                  border: "1px solid rgba(255,255,255,0.1)",
                  boxShadow: "0 0 40px rgba(107,78,255,0.2)",
                }}
              >
                {today.phase_icon}
              </div>
              <p className="font-display text-3xl text-text-primary">{today.lunar_day}</p>
              <p className="text-text-muted text-xs">{today.lunar_day} {t("lunar.lunar_day_label")}</p>
              <p className="text-text-faint text-xs">
                {today.phase_name} · {t("lunar.moon_in")} {today.moon_sign}
              </p>
              <div className="flex items-center gap-2">
                <span className="text-text-faint text-[10px]">{t("lunar.energy")}:</span>
                <span className="text-xs font-display" style={{ color: "#C9A84C" }}>{today.energy}</span>
              </div>
            </div>

            {/* Recommendations */}
            <Card>
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">
                {t("lunar.recommendations")}
              </p>
              <div className="flex flex-col gap-2.5">
                {today.recommendations.map((r, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <span className="text-violet-400 text-xs mt-0.5">✦</span>
                    <span className="text-text-muted text-xs">{r}</span>
                  </div>
                ))}
              </div>
            </Card>

            {/* Month calendar */}
            <Card>
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">
                {t("lunar.calendar")}
              </p>
              <div className="grid grid-cols-7 gap-1 text-center">
                {weekdays.map(d => (
                  <span key={d} className="text-text-faint text-[9px] pb-1">{d}</span>
                ))}
                {Array.from({ length: firstDayOfMonth }).map((_, i) => (
                  <div key={`e${i}`} />
                ))}
                {month.map(day => {
                  const dayNum = parseInt(day.date.split("-")[2]);
                  const isToday = day.date === todayStr;
                  return (
                    <div
                      key={day.date}
                      className="flex flex-col items-center py-1 rounded-lg"
                      style={{
                        background: isToday ? "rgba(107,78,255,0.2)" : "transparent",
                        border: isToday ? "1px solid rgba(107,78,255,0.4)" : "1px solid transparent",
                      }}
                    >
                      <span className={`text-[10px] ${isToday ? "text-text-primary font-bold" : "text-text-muted"}`}>
                        {dayNum}
                      </span>
                      <span className="text-[10px] leading-none">{day.phase_icon}</span>
                    </div>
                  );
                })}
              </div>
            </Card>
          </>
        )}
      </main>

      <BottomNav active="moon" onNavigate={onNavigate} />
    </div>
  );
}
