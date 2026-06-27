import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Logo } from "../components/Logo";
import { PaywallSheet } from "../components/PaywallSheet";
import { ZodiacGlyph } from "../components/ZodiacGlyph";
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
  { id: "tarot",  icon: "☰",  label_ru: "Таро",          label_en: "Tarot",        desc_ru: "Расклады на любой вопрос",  desc_en: "Spreads for any question" },
  { id: "moon",   icon: "☽",  label_ru: "Лунный день",   label_en: "Moon Day",     desc_ru: "Лунный календарь",          desc_en: "Lunar calendar" },
  { id: "compat", icon: "♡",  label_ru: "Совместимость", label_en: "Compatibility", desc_ru: "Анализ пары",               desc_en: "Couple analysis" },
  { id: "natal",  icon: "◎",  label_ru: "Натальная",     label_en: "Natal Chart",   desc_ru: "Карта рождения",            desc_en: "Birth chart" },
  { id: "numero", icon: "#",  label_ru: "Нумерология",   label_en: "Numerology",    desc_ru: "Числа судьбы",              desc_en: "Destiny numbers" },
  { id: "runes",  icon: "ᚱ",  label_ru: "Руны",          label_en: "Runes",         desc_ru: "Древние знаки",             desc_en: "Ancient signs" },
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
  const [scores, setScores] = useState<{ love: number; career: number; health: number } | null>(null);
  const [showPaywall, setShowPaywall] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const called = useRef(false);

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

      const today = new Date().toISOString().slice(0, 10);
      fetch(`/api/v1/horoscope/scores?sign=${sign}&date=${today}`).then(r => r.json()).then(setScores).catch(() => {});

      streamRequest("/horoscope/stream", { sign, lang, date: today },
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

  const bars = [
    { label: ru ? "Любовь" : "Love", value: scores?.love ?? 0, color: "#C9A84C" },
    { label: ru ? "Карьера" : "Career", value: scores?.career ?? 0, color: "#8A7FC0" },
    { label: ru ? "Здоровье" : "Health", value: scores?.health ?? 0, color: "#6E9A8A" },
  ];

  function ProgressBar({ label, value, color }: { label: string; value: number; color: string }) {
    const loading = value === 0;
    return (
      <div>
        <div className="flex justify-between" style={{ fontSize: 12, marginBottom: 4 }}>
          <span style={{ color: "#B6AC98" }}>{label}</span>
          <span style={{ color: loading ? "#6E6757" : color }}>{loading ? "—" : `${value}%`}</span>
        </div>
        <div style={{ height: 6, borderRadius: 99, background: "rgba(255,255,255,.07)", overflow: "hidden" }}>
          {loading
            ? <div style={{ width: "60%", height: "100%", borderRadius: 99, background: "rgba(255,255,255,.06)", animation: "mystral-breathe 1.5s ease-in-out infinite" }} />
            : <div style={{ width: `${value}%`, height: "100%", borderRadius: 99, background: `linear-gradient(90deg,${color}99,${color})`, boxShadow: `0 0 12px ${color}80`, transition: "width .6s ease" }} />
          }
        </div>
      </div>
    );
  }

  return (
    <div style={{ animation: "mystral-fadeup .3s ease-out" }}>
      {/* Header — mobile only */}
      <header className="lg:hidden" style={{ padding: "18px 22px 6px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div className="flex items-center gap-2.5">
          <Logo size={26} />
          <span className="font-cinzel" style={{ fontSize: 14, letterSpacing: ".3em", color: "#E8CD7E" }}>MYSTRAL</span>
        </div>
        <div className="flex items-center gap-2.5">
          <button onClick={() => onNavigate("profile")} style={{ height: 34, padding: "0 14px", borderRadius: 99, background: "rgba(255,255,255,.04)", border: "1px solid rgba(201,168,76,.2)", display: "flex", alignItems: "center", gap: 6, cursor: "pointer", color: "#C9A84C", fontSize: 14 }}>
            🔔 <span style={{ width: 5, height: 5, borderRadius: "50%", background: "#C9A84C", boxShadow: "0 0 6px rgba(201,168,76,.8)" }} />
          </button>
          {!isPro && (
            <button onClick={() => setShowPaywall(true)} className="font-sans" style={{ height: 38, padding: "0 14px", borderRadius: 11, background: "linear-gradient(100deg,#A9882F,#E8CD7E)", color: "#1A1206", fontSize: 12, fontWeight: 600, letterSpacing: ".04em", display: "flex", alignItems: "center", gap: 4, border: "none" }}>PRO</button>
          )}
        </div>
      </header>

      <div style={{ padding: "6px 22px 0" }}>
        <p className="font-cinzel italic" style={{ fontSize: 14, color: "#A89E8B" }}>{dayName} · {getTimeOfDay(lang)}</p>
        <p className="font-cormorant" style={{ fontSize: 31, color: "#F0E9DA", lineHeight: 1.08, marginTop: 2 }}>
          {getGreetingWord(lang)}, {user?.name ?? t("profile.guest")}
        </p>
      </div>

      {/* Zodiac + Horoscope — grid on desktop */}
      <div className="lg:grid lg:gap-5" style={{ marginTop: 12, padding: "0 22px" }} >
        <style>{`.lg\\:grid { grid-template-columns: 300px 1fr; } @media(max-width:1023px) { .lg\\:grid { display:block !important; } }`}</style>

        {/* Zodiac — hero level */}
        <div className="lg:rounded-3xl lg:p-5 lg:text-center" style={{ position: "relative", padding: "6px 0 2px", textAlign: "center", background: "radial-gradient(140% 100% at 50% 0%, #1C1650 0%, #0F0A2E 40%, transparent 100%)", borderRadius: 22, border: "1px solid rgba(201,168,76,.28)", boxShadow: "0 0 80px rgba(75,60,134,.25), 0 0 40px rgba(201,168,76,.08)" }}>
          <ZodiacGlyph sign={userSign} size={200} />
          <div style={{ marginTop: -8 }}>
            <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".34em", color: "#C9A84C" }}>{ru ? "ВАШ ЗНАК" : "YOUR SIGN"}</p>
            <p className="font-cormorant" style={{ fontSize: 42, color: "#F0E9DA", lineHeight: 1.02 }}>{zodiacLabel ?? t("home.zodiac_fallback")}</p>
            {meta && <p style={{ fontSize: 12, color: "#8A8170", letterSpacing: ".04em", marginTop: 2 }}>{ru ? meta.element_ru : meta.element_en} · {ru ? meta.modality_ru : meta.modality_en} · {meta.dates}</p>}
          </div>
        </div>

        {/* Horoscope */}
        <div style={{ padding: 22, borderRadius: 22, background: "linear-gradient(160deg,rgba(255,255,255,.055),rgba(255,255,255,.015))", border: "1px solid rgba(201,168,76,.16)", backdropFilter: "blur(12px)" }}>
        <div className="flex items-center justify-between">
          <span className="font-cinzel uppercase" style={{ fontSize: 10.5, letterSpacing: ".28em", color: "#C9A84C" }}>{t("home.daily_horoscope")}</span>
          <span style={{ fontSize: 11, color: "#6E6757" }}>{now.toLocaleDateString(ru ? "ru-RU" : "en-US", { day: "numeric", month: "short" })}</span>
        </div>
        <div style={{ marginTop: 13, fontSize: 14.5, lineHeight: 1.72, color: "#D7CFBE", overflow: "hidden", maxHeight: expanded ? "none" : 105 }}>
          {horoscopeLoading && !horoscope
            ? <p className="animate-pulse" style={{ color: "#8A8170" }}>{t("home.stars_loading")}</p>
            : <>{horoscope}{horoscopeLoading && <span className="animate-pulse">▍</span>}</>}
        </div>
        <div className="flex flex-col lg:grid lg:grid-cols-3" style={{ marginTop: 18, gap: 11 }}>
          {bars.map(b => <ProgressBar key={b.label} {...b} />)}
        </div>
        {horoscope.length > 200 && !expanded && (
          <button onClick={() => setExpanded(true)} style={{ marginTop: 18, width: "100%", height: 46, borderRadius: 13, border: "1px solid rgba(201,168,76,.4)", background: "rgba(201,168,76,.06)", color: "#E8CD7E", fontWeight: 500, fontSize: 13.5 }}>
            {ru ? "Читать полностью" : "Read full"}
          </button>
        )}
      </div>
      </div>{/* end grid wrapper */}

      {/* Tarot CTA */}
      <button onClick={() => onNavigate("tarot")} className="w-full text-left" style={{ margin: "12px 22px 0", width: "calc(100% - 44px)", padding: "16px 20px", borderRadius: 18, display: "flex", alignItems: "center", gap: 14, background: "linear-gradient(100deg, rgba(75,60,134,.2), rgba(201,168,76,.08))", border: "1px solid rgba(201,168,76,.2)", cursor: "pointer" }}>
        <span style={{ fontSize: 28, color: "#C9A84C", filter: "drop-shadow(0 0 8px rgba(201,168,76,.4))", flexShrink: 0 }}>☰</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <p className="font-cormorant" style={{ fontSize: 18, color: "#F0E9DA" }}>{ru ? "Расклад дня" : "Daily spread"}</p>
          <p style={{ fontSize: 12, color: "#8A8170" }}>{ru ? "Узнай что говорят карты" : "See what the cards say"}</p>
        </div>
        <span style={{ color: "#6E6757", marginLeft: "auto" }}>›</span>
      </button>

      {/* Lunar — mobile only */}
      <button onClick={() => onNavigate("moon")} className="w-full text-left lg:hidden" style={{ margin: "14px 22px 0", width: "calc(100% - 44px)", padding: "18px 20px", borderRadius: 22, display: "flex", alignItems: "center", gap: 18, background: "linear-gradient(160deg,rgba(58,76,134,.22),rgba(255,255,255,.012))", border: "1px solid rgba(138,127,192,.24)" }}>
        <div style={{ animation: "mystral-pulse-glow 3.6s ease-in-out infinite", borderRadius: "50%", flexShrink: 0, width: 52, height: 52, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28, color: "#A99BE0" }}>
          {lunar?.phase_icon ?? "☽"}
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
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-3" style={{ gap: 12, marginTop: 14 }}>
          {SECTIONS.map(s => (
            <button key={s.id} onClick={() => onNavigate(s.id)} className="text-left" style={{ padding: 16, borderRadius: 18, background: "rgba(255,255,255,.02)", border: "1px solid rgba(255,255,255,.06)", display: "flex", alignItems: "center", gap: 12 }}>
              <span style={{ fontSize: 20, color: "#C9A84C", flexShrink: 0 }}>{s.icon}</span>
              <span className="font-cormorant" style={{ fontSize: 18, color: "#F0E9DA" }}>{ru ? s.label_ru : s.label_en}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Natal banner — mobile only */}
      <button onClick={() => onNavigate("natal")} className="w-full text-left lg:hidden" style={{ margin: "20px 22px 24px", width: "calc(100% - 44px)", position: "relative", overflow: "hidden", padding: 24, borderRadius: 22, background: "linear-gradient(120deg,#1B1546,#0C0A22)", border: "1px solid rgba(201,168,76,.24)" }}>
        <div style={{ position: "absolute", top: -30, right: -10, width: 140, height: 140, borderRadius: "50%", background: "radial-gradient(circle,rgba(201,168,76,.16),transparent 68%)" }} />
        <p className="font-cinzel uppercase" style={{ fontSize: 10.5, letterSpacing: ".28em", color: "#C9A84C", position: "relative" }}>{ru ? "НАТАЛЬНАЯ КАРТА" : "NATAL CHART"}</p>
        <p className="font-cormorant" style={{ fontSize: 25, color: "#F0E9DA", margin: "6px 0 10px", lineHeight: 1.15, position: "relative" }}>{ru ? "Ваша карта рождения готова" : "Your birth chart is ready"}</p>
        <p style={{ fontSize: 13, lineHeight: 1.6, color: "#A89E8B", margin: "0 0 16px", maxWidth: "90%", position: "relative" }}>{ru ? "Большая тройка, планеты и аспекты — всё, что записали звёзды в момент вашего рождения." : "Big three, planets and aspects — everything the stars wrote at your birth."}</p>
        <span style={{ display: "inline-flex", alignItems: "center", gap: 8, height: 44, padding: "0 20px", borderRadius: 12, background: "linear-gradient(100deg,#A9882F,#E8CD7E)", color: "#1A1206", fontWeight: 600, fontSize: 13.5, position: "relative" }}>{ru ? "Открыть карту" : "Open chart"}</span>
      </button>

      <div className="pb-20 lg:pb-8" />

      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
    </div>
  );
}
