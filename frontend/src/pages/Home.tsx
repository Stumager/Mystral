import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Logo } from "../components/Logo";
import { PaywallSheet } from "../components/PaywallSheet";
import { ZodiacGlyph } from "../components/ZodiacGlyph";
import { BottomNav } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { streamRequest } from "../utils/api";
import { getZodiacSign, ZodiacInfo } from "../utils/zodiac";

interface HomeProps { onNavigate: (page: string) => void; }

interface LunarToday {
  lunar_day: number; phase_name: string; phase_icon: string; moon_sign: string; illumination: number;
}

const ZODIAC_META: Record<string, { element_ru: string; element_en: string; modality_ru: string; modality_en: string; dates: string }> = {
  Aries:       { element_ru: "Огонь", element_en: "Fire", modality_ru: "Кардинальный", modality_en: "Cardinal", dates: "21.03 – 19.04" },
  Taurus:      { element_ru: "Земля", element_en: "Earth", modality_ru: "Фиксированный", modality_en: "Fixed", dates: "20.04 – 20.05" },
  Gemini:      { element_ru: "Воздух", element_en: "Air", modality_ru: "Мутабельный", modality_en: "Mutable", dates: "21.05 – 20.06" },
  Cancer:      { element_ru: "Вода", element_en: "Water", modality_ru: "Кардинальный", modality_en: "Cardinal", dates: "21.06 – 22.07" },
  Leo:         { element_ru: "Огонь", element_en: "Fire", modality_ru: "Фиксированный", modality_en: "Fixed", dates: "23.07 – 22.08" },
  Virgo:       { element_ru: "Земля", element_en: "Earth", modality_ru: "Мутабельный", modality_en: "Mutable", dates: "23.08 – 22.09" },
  Libra:       { element_ru: "Воздух", element_en: "Air", modality_ru: "Кардинальный", modality_en: "Cardinal", dates: "23.09 – 22.10" },
  Scorpio:     { element_ru: "Вода", element_en: "Water", modality_ru: "Фиксированный", modality_en: "Fixed", dates: "23.10 – 21.11" },
  Sagittarius: { element_ru: "Огонь", element_en: "Fire", modality_ru: "Мутабельный", modality_en: "Mutable", dates: "22.11 – 21.12" },
  Capricorn:   { element_ru: "Земля", element_en: "Earth", modality_ru: "Кардинальный", modality_en: "Cardinal", dates: "22.12 – 19.01" },
  Aquarius:    { element_ru: "Воздух", element_en: "Air", modality_ru: "Фиксированный", modality_en: "Fixed", dates: "20.01 – 18.02" },
  Pisces:      { element_ru: "Вода", element_en: "Water", modality_ru: "Мутабельный", modality_en: "Mutable", dates: "19.02 – 20.03" },
};

const SECTIONS = [
  { id: "tarot",  icon: "🂠", label_ru: "Таро",          label_en: "Tarot",        desc_ru: "Расклады на любой вопрос",  desc_en: "Spreads for any question" },
  { id: "moon",   icon: "☽",  label_ru: "Лунный день",   label_en: "Moon Day",     desc_ru: "Лунный календарь",          desc_en: "Lunar calendar" },
  { id: "compat", icon: "♡",  label_ru: "Совместимость", label_en: "Compatibility", desc_ru: "Анализ пары",               desc_en: "Couple analysis" },
  { id: "natal",  icon: "◎",  label_ru: "Натальная",     label_en: "Natal Chart",   desc_ru: "Карта рождения",            desc_en: "Birth chart" },
  { id: "numero", icon: "#",  label_ru: "Нумерология",   label_en: "Numerology",    desc_ru: "Числа судьбы",              desc_en: "Destiny numbers" },
  { id: "runes",  icon: "ᚱ",  label_ru: "Руны",          label_en: "Runes",         desc_ru: "Древние знаки",             desc_en: "Ancient signs" },
];

const NAV_ITEMS = [
  { id: "home",       label_ru: "Главная",        label_en: "Home",          icon: "⌂" },
  { id: "tarot",      label_ru: "Таро",           label_en: "Tarot",         icon: "🂠" },
  { id: "moon",       label_ru: "Луна",           label_en: "Moon",          icon: "☽" },
  { id: "compat",     label_ru: "Совместимость",  label_en: "Compatibility", icon: "♡" },
  { id: "natal",      label_ru: "Натальная карта", label_en: "Natal Chart",   icon: "◎" },
  { id: "numerology", label_ru: "Нумерология",    label_en: "Numerology",    icon: "#" },
  { id: "runes",      label_ru: "Руны",           label_en: "Runes",         icon: "ᚱ" },
  { id: "profile",    label_ru: "Профиль",        label_en: "Profile",       icon: "☽" },
];

function getTimeOfDay(lang: string): string {
  const h = new Date().getHours();
  if (lang === "ru") return h >= 6 && h < 12 ? "утро" : h >= 12 && h < 18 ? "день" : h >= 18 ? "вечер" : "ночь";
  return h >= 6 && h < 12 ? "morning" : h >= 12 && h < 18 ? "afternoon" : h >= 18 ? "evening" : "night";
}

function getGreetingWord(lang: string): string {
  const h = new Date().getHours();
  if (lang === "ru") return h >= 6 && h < 12 ? "Доброе утро" : h >= 12 && h < 18 ? "Добрый день" : h >= 18 ? "Добрый вечер" : "Доброй ночи";
  return h >= 6 && h < 12 ? "Good morning" : h >= 12 && h < 18 ? "Good afternoon" : h >= 18 ? "Good evening" : "Good night";
}

export function Home({ onNavigate }: HomeProps) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const lang = user?.lang ?? "ru";
  const ru = lang === "ru";

  const [horoscope, setHoroscope] = useState("");
  const [horoscopeLoading, setHoroscopeLoading] = useState(true);
  const [zodiac, setZodiac] = useState<ZodiacInfo | null>(null);
  const [lunar, setLunar] = useState<LunarToday | null>(null);
  const [showPaywall, setShowPaywall] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [isDesktop, setIsDesktop] = useState(window.innerWidth >= 1024);

  const called = useRef(false);

  useEffect(() => {
    const onResize = () => setIsDesktop(window.innerWidth >= 1024);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  useEffect(() => {
    if (called.current) return;
    called.current = true;

    async function load() {
      let sign = "aries";
      fetch(`/api/v1/lunar/today?lang=${lang}`).then(r => r.json()).then((d: LunarToday) => setLunar(d)).catch(() => {});

      if (token) {
        try {
          const res = await fetch("/api/v1/profile", { headers: { Authorization: `Bearer ${token}` } });
          const data = await res.json();
          if (data.birth_date) { const z = getZodiacSign(data.birth_date); setZodiac(z); sign = z.en.toLowerCase(); }
        } catch {}
      }

      streamRequest("/horoscope/stream", { sign, lang, date: new Date().toISOString().slice(0, 10) },
        (chunk) => setHoroscope(prev => prev + chunk), () => setHoroscopeLoading(false),
      ).catch(() => { setHoroscope(t("home.stars_unavailable")); setHoroscopeLoading(false); });
    }
    load();
  }, []);

  const zodiacLabel = zodiac ? (ru ? zodiac.sign : zodiac.en) : null;
  const userSign = zodiac?.en ?? "Leo";
  const meta = zodiac ? ZODIAC_META[zodiac.en] : null;
  const isPro = user?.tier === "pro";
  const now = new Date();
  const dayName = now.toLocaleDateString(ru ? "ru-RU" : "en-US", { weekday: "long", day: "numeric", month: "long" });
  const firstLetter = (user?.name ?? "?")[0]?.toUpperCase() ?? "?";

  const barsMobile = [
    { label: ru ? "Любовь" : "Love", value: 78, color: "#C9A84C" },
    { label: ru ? "Карьера" : "Career", value: 64, color: "#C9A84C" },
    { label: ru ? "Здоровье" : "Health", value: 82, color: "#C9A84C" },
  ];
  const barsDesktop = [
    { label: ru ? "Любовь" : "Love", value: 88, color: "#C9A84C" },
    { label: ru ? "Карьера" : "Career", value: 72, color: "#8A7FC0" },
    { label: ru ? "Здоровье" : "Health", value: 64, color: "#6E9A8A" },
  ];

  function ProgressBar({ label, value, color }: { label: string; value: number; color: string }) {
    return (
      <div>
        <div className="flex justify-between" style={{ fontSize: 12, marginBottom: 4 }}>
          <span style={{ color: "#B6AC98" }}>{label}</span>
          <span style={{ color }}>{value}%</span>
        </div>
        <div style={{ height: 6, borderRadius: 99, background: "rgba(255,255,255,.07)", overflow: "hidden" }}>
          <div style={{ width: `${value}%`, height: "100%", borderRadius: 99, background: `linear-gradient(90deg,${color}99,${color})`, boxShadow: `0 0 12px ${color}80` }} />
        </div>
      </div>
    );
  }

  // ======================== DESKTOP ========================
  if (isDesktop) {
    return (
      <div style={{ display: "flex", height: "100vh", overflow: "hidden", background: "radial-gradient(130% 60% at 50% -5%,#0F0A26 0%,#07060F 55%)" }}>

        {/* LEFT SIDEBAR */}
        <aside style={{ flex: "none", width: 240, height: "100%", display: "flex", flexDirection: "column", padding: "24px 16px", borderRight: "1px solid rgba(201,168,76,.12)", background: "rgba(7,6,15,.55)" }}>
          <div style={{ padding: "0 8px 22px", display: "flex", alignItems: "center", gap: 10 }}>
            <Logo size={30} />
            <span className="font-cinzel" style={{ fontSize: 16, letterSpacing: ".28em", color: "#E8CD7E" }}>MYSTRAL</span>
          </div>

          <nav style={{ display: "flex", flexDirection: "column", gap: 3, flex: 1 }}>
            {NAV_ITEMS.map(n => {
              const active = n.id === "home";
              return (
                <button key={n.id} onClick={() => onNavigate(n.id)} style={{
                  display: "flex", alignItems: "center", gap: 13, padding: "11px 14px", borderRadius: 12,
                  cursor: "pointer", transition: ".15s", textAlign: "left",
                  background: active ? "linear-gradient(100deg,rgba(201,168,76,.16),rgba(201,168,76,.04))" : "transparent",
                  border: active ? "1px solid rgba(201,168,76,.3)" : "1px solid transparent",
                  color: active ? "#E8CD7E" : "#A89E8B", fontWeight: active ? 600 : 400,
                }}>
                  <span style={{ fontSize: 20, width: 20, textAlign: "center" }}>{n.icon}</span>
                  <span style={{ fontSize: 13.5 }}>{ru ? n.label_ru : n.label_en}</span>
                </button>
              );
            })}
          </nav>

          <div style={{ marginTop: "auto", borderTop: "1px solid rgba(255,255,255,.07)", padding: "14px 10px 4px", display: "flex", gap: 12, alignItems: "center" }}>
            <div style={{ width: 40, height: 40, borderRadius: "50%", background: "linear-gradient(135deg,#4B3C86,#C9A84C)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <span className="font-cormorant" style={{ fontSize: 19, color: "#0C0A18", fontWeight: 600 }}>{firstLetter}</span>
            </div>
            <div>
              <div style={{ fontSize: 13.5, color: "#F0E9DA", fontWeight: 500 }}>{user?.name ?? "Guest"}</div>
              <div style={{ fontSize: 11, color: "#C9A84C" }}>{zodiacLabel ?? "—"} · {isPro ? "Pro" : "Free"}</div>
            </div>
          </div>
        </aside>

        {/* CENTER */}
        <div style={{ flex: 1, overflowY: "auto", padding: "30px 34px 44px" }}>
          {/* Greeting + bell */}
          <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between" }}>
            <div>
              <p className="font-cormorant italic" style={{ fontSize: 15, color: "#A89E8B" }}>{dayName} · {getTimeOfDay(lang)}</p>
              <p className="font-cormorant" style={{ fontSize: 36, color: "#F0E9DA", lineHeight: 1.05, marginTop: 2 }}>
                {getGreetingWord(lang)}, {user?.name ?? t("profile.guest")}
              </p>
            </div>
            <button style={{ width: 42, height: 42, borderRadius: 12, background: "rgba(255,255,255,.04)", border: "1px solid rgba(201,168,76,.16)", color: "#C9A84C", fontSize: 20, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              🔔
            </button>
          </div>

          {/* Grid: zodiac card | horoscope card */}
          <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: 20, marginTop: 24 }}>
            {/* Zodiac card */}
            <div style={{ borderRadius: 24, background: "radial-gradient(120% 90% at 50% 0%,#15102E,#0A0818)", border: "1px solid rgba(201,168,76,.16)", padding: "18px 18px 22px", textAlign: "center", overflow: "hidden" }}>
              <ZodiacGlyph sign={userSign} size={260} />
              <div style={{ marginTop: -6 }}>
                <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".3em", color: "#C9A84C" }}>{ru ? "ВАШ ЗНАК" : "YOUR SIGN"}</p>
                <p className="font-cormorant" style={{ fontSize: 38, color: "#F0E9DA", lineHeight: 1 }}>{zodiacLabel ?? "—"}</p>
                {meta && <p style={{ fontSize: 11, color: "#8A8170", marginTop: 2 }}>{ru ? meta.element_ru : meta.element_en} · {ru ? meta.modality_ru : meta.modality_en}</p>}
              </div>
            </div>

            {/* Horoscope card */}
            <div style={{ padding: 26, borderRadius: 24, background: "linear-gradient(160deg,rgba(255,255,255,.05),rgba(255,255,255,.012))", border: "1px solid rgba(201,168,76,.16)" }}>
              <p className="font-cinzel uppercase" style={{ fontSize: 10.5, letterSpacing: ".28em", color: "#C9A84C" }}>{t("home.daily_horoscope")}</p>
              <div style={{ fontSize: 15.5, lineHeight: 1.75, color: "#D7CFBE", marginTop: 13 }}>
                {horoscopeLoading && !horoscope
                  ? <p className="animate-pulse" style={{ color: "#8A8170" }}>{t("home.stars_loading")}</p>
                  : <>{horoscope}{horoscopeLoading && <span className="animate-pulse">▍</span>}</>}
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 18, marginTop: 20 }}>
                {barsDesktop.map(b => <ProgressBar key={b.label} {...b} />)}
              </div>
            </div>
          </div>

          {/* Sections */}
          <p className="font-cormorant" style={{ fontSize: 26, color: "#F0E9DA", margin: "30px 0 14px" }}>{ru ? "Разделы" : "Sections"}</p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 16 }}>
            {SECTIONS.map(s => (
              <button key={s.id} onClick={() => onNavigate(s.id)} className="text-left" style={{ position: "relative", overflow: "hidden", padding: 20, borderRadius: 20, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", cursor: "pointer", transition: ".2s" }}>
                <div style={{ position: "absolute", top: -22, right: -20, width: 96, height: 96, borderRadius: "50%", background: "radial-gradient(circle,rgba(201,168,76,.12),transparent 70%)" }} />
                <span style={{ fontSize: 25, color: "#C9A84C", filter: "drop-shadow(0 0 6px rgba(201,168,76,.32))", position: "relative" }}>{s.icon}</span>
                <p className="font-cormorant" style={{ fontSize: 22, color: "#F0E9DA", marginTop: 16, position: "relative" }}>{ru ? s.label_ru : s.label_en}</p>
                <p style={{ fontSize: 12, color: "#8A8170", marginTop: 2, position: "relative" }}>{ru ? s.desc_ru : s.desc_en}</p>
              </button>
            ))}
          </div>
        </div>

        {/* RIGHT SIDEBAR */}
        <aside style={{ flex: "none", width: 312, overflowY: "auto", padding: "26px 22px", borderLeft: "1px solid rgba(201,168,76,.12)", background: "rgba(7,6,15,.45)", display: "flex", flexDirection: "column", gap: 18 }}>
          {/* Lunar day */}
          <div style={{ padding: 20, borderRadius: 20, textAlign: "center", background: "linear-gradient(160deg,rgba(58,76,134,.22),rgba(255,255,255,.012))", border: "1px solid rgba(138,127,192,.24)" }}>
            <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".26em", color: "#A99BE0", marginBottom: 14 }}>{ru ? "ЛУННЫЙ ДЕНЬ" : "LUNAR DAY"}</p>
            <div style={{ display: "flex", justifyContent: "center" }}>
              <div style={{ width: "fit-content", borderRadius: "50%", animation: "mystral-pulse-glow 3.6s ease-in-out infinite", fontSize: 48, lineHeight: 1, padding: 12, color: "#A99BE0" }}>
                {lunar?.phase_icon ?? "🌙"}
              </div>
            </div>
            <p className="font-cormorant" style={{ fontSize: 28, color: "#F0E9DA", marginTop: 14 }}>
              {lunar ? `${lunar.lunar_day} ${ru ? "лунный день" : "lunar day"}` : "..."}
            </p>
            {lunar && <p style={{ fontSize: 12, color: "#9890B8", marginTop: 4 }}>{ru ? "Луна в" : "Moon in"} {lunar.moon_sign}</p>}
          </div>

          {/* Sign of the day */}
          <div style={{ padding: 20, borderRadius: 20, background: "linear-gradient(160deg,rgba(255,255,255,.05),rgba(255,255,255,.012))", border: "1px solid rgba(201,168,76,.16)" }}>
            <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".26em", color: "#C9A84C", marginBottom: 8 }}>{ru ? "ВАШ ЗНАК" : "YOUR SIGN"}</p>
            <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
              <ZodiacGlyph sign={userSign} size={80} />
              <div>
                <p className="font-cormorant" style={{ fontSize: 24, color: "#F0E9DA", lineHeight: 1 }}>{zodiacLabel ?? "—"}</p>
                {meta && <p style={{ fontSize: 12, color: "#8A8170", marginTop: 4 }}>{ru ? meta.element_ru : meta.element_en} · {meta.dates}</p>}
              </div>
            </div>
          </div>

          {/* Pro button */}
          {!isPro && (
            <button onClick={() => setShowPaywall(true)} style={{ position: "relative", overflow: "hidden", height: 54, borderRadius: 14, background: "linear-gradient(100deg,#A9882F,#C9A84C 50%,#E8CD7E)", boxShadow: "0 10px 28px -8px rgba(201,168,76,.55)", display: "flex", alignItems: "center", justifyContent: "center", gap: 8, cursor: "pointer", border: "none", width: "100%" }}>
              <span style={{ position: "absolute", inset: 0, background: "linear-gradient(100deg,transparent 30%,rgba(255,255,255,.5) 50%,transparent 70%)", backgroundSize: "200% 100%", animation: "mystral-shimmer 2.8s linear infinite" }} />
              <span style={{ position: "relative", color: "#1A1206", fontWeight: 600, fontSize: 14 }}>✦ {ru ? "Открыть Mystral Pro" : "Unlock Mystral Pro"}</span>
            </button>
          )}
        </aside>

        <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
      </div>
    );
  }

  // ======================== MOBILE ========================
  return (
    <div className="flex flex-col min-h-screen relative" style={{ background: "var(--gradient-page)" }}>
      {/* Header */}
      <header className="flex items-center justify-between shrink-0" style={{ padding: "18px 22px 6px" }}>
        <div className="flex items-center gap-2.5">
          <Logo size={26} />
          <span className="font-cinzel" style={{ fontSize: 14, letterSpacing: ".3em", color: "#E8CD7E" }}>MYSTRAL</span>
        </div>
        <div className="flex items-center gap-2.5">
          <button style={{ width: 38, height: 38, borderRadius: 11, background: "rgba(255,255,255,.04)", border: "1px solid rgba(201,168,76,.16)", color: "#C9A84C", fontSize: 18, display: "flex", alignItems: "center", justifyContent: "center" }}>🔔</button>
          {!isPro && (
            <button onClick={() => setShowPaywall(true)} className="font-sans" style={{ height: 38, padding: "0 14px", borderRadius: 11, background: "linear-gradient(100deg,#A9882F,#E8CD7E)", color: "#1A1206", fontSize: 12, fontWeight: 600, letterSpacing: ".04em", display: "flex", alignItems: "center", gap: 4, border: "none" }}>✦ PRO</button>
          )}
        </div>
      </header>

      <main className="flex-1 overflow-y-auto pb-20">
        {/* Greeting */}
        <div style={{ padding: "10px 22px 0" }}>
          <p className="font-cinzel italic" style={{ fontSize: 14, color: "#A89E8B" }}>{dayName} · {getTimeOfDay(lang)}</p>
          <p className="font-cormorant" style={{ fontSize: 31, color: "#F0E9DA", lineHeight: 1.08, marginTop: 2 }}>
            {getGreetingWord(lang)}, {user?.name ?? t("profile.guest")}
          </p>
        </div>

        {/* Zodiac */}
        <div style={{ position: "relative", padding: "6px 0 2px", textAlign: "center" }}>
          <ZodiacGlyph sign={userSign} size={236} />
          <div style={{ marginTop: -8 }}>
            <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".34em", color: "#C9A84C" }}>{ru ? "ВАШ ЗНАК" : "YOUR SIGN"}</p>
            <p className="font-cormorant" style={{ fontSize: 42, color: "#F0E9DA", lineHeight: 1.02 }}>{zodiacLabel ?? t("home.zodiac_fallback")}</p>
            {meta && <p style={{ fontSize: 12, color: "#8A8170", letterSpacing: ".04em", marginTop: 2 }}>{ru ? meta.element_ru : meta.element_en} · {ru ? meta.modality_ru : meta.modality_en} · {meta.dates}</p>}
          </div>
        </div>

        {/* Horoscope */}
        <div style={{ margin: "16px 22px 0", padding: 22, borderRadius: 22, background: "linear-gradient(160deg,rgba(255,255,255,.055),rgba(255,255,255,.015))", border: "1px solid rgba(201,168,76,.16)", backdropFilter: "blur(12px)" }}>
          <div className="flex items-center justify-between">
            <span className="font-cinzel uppercase" style={{ fontSize: 10.5, letterSpacing: ".28em", color: "#C9A84C" }}>{t("home.daily_horoscope")}</span>
            <span style={{ fontSize: 11, color: "#6E6757" }}>{now.toLocaleDateString(ru ? "ru-RU" : "en-US", { day: "numeric", month: "short" })}</span>
          </div>
          <div style={{ marginTop: 13, fontSize: 14.5, lineHeight: 1.72, color: "#D7CFBE", overflow: "hidden", maxHeight: expanded ? "none" : 105 }}>
            {horoscopeLoading && !horoscope
              ? <p className="animate-pulse" style={{ color: "#8A8170" }}>{t("home.stars_loading")}</p>
              : <>{horoscope}{horoscopeLoading && <span className="animate-pulse">▍</span>}</>}
          </div>
          <div className="flex flex-col" style={{ marginTop: 18, gap: 11 }}>
            {barsMobile.map(b => (
              <div key={b.label} className="flex items-center gap-2">
                <span style={{ width: 72, fontSize: 12.5, color: "#B6AC98" }}>{b.label}</span>
                <div className="flex-1" style={{ height: 6, borderRadius: 99, background: "rgba(255,255,255,.07)" }}>
                  <div style={{ width: `${b.value}%`, height: "100%", borderRadius: 99, background: "linear-gradient(90deg,#8A6E2E,#E8CD7E)", boxShadow: "0 0 12px rgba(201,168,76,.5)" }} />
                </div>
                <span style={{ width: 34, textAlign: "right", fontSize: 11, color: "#C9A84C" }}>{b.value}%</span>
              </div>
            ))}
          </div>
          {!expanded && horoscope && (
            <button onClick={() => setExpanded(true)} style={{ marginTop: 18, width: "100%", height: 46, borderRadius: 13, border: "1px solid rgba(201,168,76,.4)", background: "rgba(201,168,76,.06)", color: "#E8CD7E", fontWeight: 500, fontSize: 13.5 }}>
              {ru ? "Читать полностью" : "Read full"}
            </button>
          )}
        </div>

        {/* Lunar day */}
        <button onClick={() => onNavigate("moon")} className="w-full text-left" style={{ margin: "14px 22px 0", width: "calc(100% - 44px)", padding: "18px 20px", borderRadius: 22, display: "flex", alignItems: "center", gap: 18, background: "linear-gradient(160deg,rgba(58,76,134,.22),rgba(255,255,255,.012))", border: "1px solid rgba(138,127,192,.24)" }}>
          <div style={{ animation: "mystral-pulse-glow 3.6s ease-in-out infinite", borderRadius: "50%", flexShrink: 0, width: 52, height: 52, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28, color: "#A99BE0" }}>
            {lunar?.phase_icon ?? "🌙"}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".26em", color: "#A99BE0" }}>{ru ? "ЛУННЫЙ ДЕНЬ" : "LUNAR DAY"}</p>
            <p className="font-cormorant" style={{ fontSize: 26, color: "#F0E9DA", lineHeight: 1.15, marginTop: 3 }}>
              {lunar ? `${lunar.lunar_day} ${ru ? "лунный день" : "lunar day"}` : "..."}
            </p>
            {lunar && <p style={{ fontSize: 12, color: "#9890B8", marginTop: 4 }}>{lunar.phase_name} · {ru ? "Луна в" : "Moon in"} {lunar.moon_sign}</p>}
          </div>
          <span style={{ marginLeft: "auto", color: "#6E6757", fontSize: 18 }}>›</span>
        </button>

        {/* Sections */}
        <div style={{ padding: "24px 22px 0" }}>
          <div className="flex items-center justify-between">
            <span className="font-cormorant" style={{ fontSize: 24, color: "#F0E9DA" }}>{ru ? "Разделы" : "Sections"}</span>
            <span style={{ fontSize: 12, color: "#C9A84C" }}>{ru ? "Все" : "All"}</span>
          </div>
          <div className="grid grid-cols-2" style={{ gap: 12, marginTop: 14 }}>
            {SECTIONS.map(s => (
              <button key={s.id} onClick={() => onNavigate(s.id)} className="text-left" style={{ position: "relative", overflow: "hidden", padding: 16, borderRadius: 18, minHeight: 104, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)" }}>
                <div style={{ position: "absolute", top: -22, right: -20, width: 84, height: 84, borderRadius: "50%", background: "radial-gradient(circle,rgba(201,168,76,.13),transparent 70%)" }} />
                <span style={{ fontSize: 22, color: "#C9A84C", filter: "drop-shadow(0 0 6px rgba(201,168,76,.32))" }}>{s.icon}</span>
                <p className="font-cormorant" style={{ fontSize: 20, color: "#F0E9DA", marginTop: 14, lineHeight: 1.1 }}>{ru ? s.label_ru : s.label_en}</p>
                <p style={{ fontSize: 11, color: "#8A8170", marginTop: 2 }}>{ru ? s.desc_ru : s.desc_en}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Natal banner */}
        <button onClick={() => onNavigate("natal")} className="w-full text-left" style={{ margin: "20px 22px 24px", width: "calc(100% - 44px)", position: "relative", overflow: "hidden", padding: 24, borderRadius: 22, background: "linear-gradient(120deg,#1B1546,#0C0A22)", border: "1px solid rgba(201,168,76,.24)" }}>
          <div style={{ position: "absolute", top: -30, right: -10, width: 140, height: 140, borderRadius: "50%", background: "radial-gradient(circle,rgba(201,168,76,.16),transparent 68%)" }} />
          <p className="font-cinzel uppercase" style={{ fontSize: 10.5, letterSpacing: ".28em", color: "#C9A84C", position: "relative" }}>{ru ? "НАТАЛЬНАЯ КАРТА" : "NATAL CHART"}</p>
          <p className="font-cormorant" style={{ fontSize: 25, color: "#F0E9DA", margin: "6px 0 10px", lineHeight: 1.15, position: "relative" }}>{ru ? "Ваша карта рождения готова" : "Your birth chart is ready"}</p>
          <p style={{ fontSize: 13, lineHeight: 1.6, color: "#A89E8B", margin: "0 0 16px", maxWidth: "90%", position: "relative" }}>{ru ? "Большая тройка, планеты и аспекты — всё, что записали звёзды в момент вашего рождения." : "Big three, planets and aspects — everything the stars wrote at your birth."}</p>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 8, height: 44, padding: "0 20px", borderRadius: 12, background: "linear-gradient(100deg,#A9882F,#E8CD7E)", color: "#1A1206", fontWeight: 600, fontSize: 13.5, position: "relative" }}>{ru ? "Открыть карту →" : "Open chart →"}</span>
        </button>
      </main>

      <BottomNav active="home" onNavigate={onNavigate} />
      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
    </div>
  );
}
