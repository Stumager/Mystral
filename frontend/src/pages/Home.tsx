import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { ZodiacOrb } from "../components/three/ZodiacOrb";
import { BottomNav, Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { streamRequest } from "../utils/api";
import { getZodiacSign, ZodiacInfo } from "../utils/zodiac";

interface HomeProps {
  onNavigate: (page: string) => void;
}

function getGreeting(t: (k: string) => string): string {
  const h = new Date().getHours();
  if (h >= 5 && h < 12) return t("home.greeting_morning");
  if (h >= 12 && h < 18) return t("home.greeting_afternoon");
  if (h >= 18 && h < 23) return t("home.greeting_evening");
  return t("home.greeting_night");
}

export function Home({ onNavigate }: HomeProps) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const [horoscope, setHoroscope] = useState("");
  const [horoscopeLoading, setHoroscopeLoading] = useState(true);
  const [zodiac, setZodiac] = useState<ZodiacInfo | null>(null);
  const [lunarDay, setLunarDay] = useState<number | null>(null);

  const called = useRef(false);

  const tools = [
    { id: "tarot",  icon: "🃏", label: t("home.tool_tarot") },
    { id: "moon",   icon: "🌙", label: t("home.tool_moon") },
    { id: "natal",  icon: "🌟", label: t("home.tool_natal") },
    { id: "compat", icon: "💑", label: t("home.tool_compat") },
    { id: "numero", icon: "🔢", label: t("home.tool_numero") },
    { id: "runes",  icon: "ᚱ",  label: t("home.tool_runes") },
  ];

  useEffect(() => {
    if (called.current) return;
    called.current = true;

    const lang = user?.lang ?? "ru";

    async function load() {
      let sign = "aries";

      fetch(`/api/v1/lunar/today?lang=${lang}`)
        .then(r => r.json())
        .then(d => setLunarDay(d.lunar_day))
        .catch(() => {});

      if (token) {
        try {
          const res = await fetch("/api/v1/profile", {
            headers: { Authorization: `Bearer ${token}` },
          });
          const data = await res.json();
          if (data.birth_date) {
            const z = getZodiacSign(data.birth_date);
            setZodiac(z);
            sign = z.en.toLowerCase();
          }
        } catch {}
      }

      streamRequest(
        "/horoscope/stream",
        { sign, lang, date: new Date().toISOString().slice(0, 10) },
        (chunk) => setHoroscope(prev => prev + chunk),
        () => setHoroscopeLoading(false),
      ).catch(() => {
        setHoroscope(t("home.stars_unavailable"));
        setHoroscopeLoading(false);
      });
    }

    load();
  }, []);

  const zodiacLabel = zodiac
    ? (user?.lang === "en" ? zodiac.en : zodiac.sign)
    : null;
  const dateFmt = user?.lang === "en" ? "en-US" : "ru-RU";

  return (
    <div className="flex flex-col min-h-screen relative overflow-hidden" style={{ background: "var(--gradient-page)" }}>

      <header
        className="flex items-center justify-between px-4 shrink-0 backdrop-blur-md"
        style={{ height: 46, background: "var(--bg-header)", borderBottom: "1px solid var(--border-gold)" }}
      >
        <button className="text-text-muted text-lg w-8">‹</button>
        <span className="font-cinzel text-sm tracking-[.25em]" style={{ color: "#E8CD7E" }}>✦ Mystral</span>
        <div className="w-8 flex justify-end">
          <span className="w-2 h-2 rounded-full bg-violet-600 animate-pulse" />
        </div>
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-4 pb-20">

        <div className="mb-4">
          <p className="text-text-faint text-xs uppercase tracking-widest mb-1">
            {getGreeting(t)}
          </p>
          <p className="text-text-primary font-display text-2xl font-light">
            {user?.name ?? t("profile.guest")} ✨
          </p>
          <p className="text-text-muted text-xs mt-1">
            {zodiacLabel
              ? `${zodiacLabel}${lunarDay ? ` · ${lunarDay} ${t("home.lunar_day")}` : ""}`
              : t("home.zodiac_fallback")}
          </p>
        </div>

        <div className="flex justify-center mb-5">
          <ZodiacOrb
            sign={zodiacLabel ?? "Mystral"}
            symbol={zodiac?.symbol ?? "✦"}
          />
        </div>

        <Card className="mb-4 relative overflow-hidden">
          <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">
            {new Date().toLocaleDateString(dateFmt, { day: "numeric", month: "long", year: "numeric" })} · {t("home.daily_horoscope")}
          </p>
          {horoscopeLoading && !horoscope
            ? <p className="text-text-muted text-xs animate-pulse">{t("home.stars_loading")}</p>
            : <p className="text-text-muted text-xs leading-relaxed">
                {horoscope}
                {horoscopeLoading && <span className="animate-pulse">▍</span>}
              </p>
          }
          <span className="absolute top-3 right-3 text-[9px] px-2 py-0.5
            rounded-full bg-violet-600/10 text-violet-400 border
            border-violet-600/20">AI</span>
        </Card>

        <div className="grid grid-cols-3 gap-2">
          {tools.map(tool => (
            <Card
              key={tool.id}
              className="flex flex-col items-center py-3 px-1 gap-1
                cursor-pointer hover:border-border-medium transition-all
                active:scale-95"
              onClick={() => onNavigate(tool.id)}
            >
              <span className="text-2xl">{tool.icon}</span>
              <span className="text-text-muted text-[10px] text-center leading-tight">
                {tool.label}
              </span>
            </Card>
          ))}
        </div>

      </main>

      <BottomNav active="home" onNavigate={onNavigate} />
    </div>
  );
}
