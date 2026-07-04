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

const ZODIAC_META: Record<string, { element: string; modality: string; dates: string }> = {
  Aries:       { element: "fire", modality: "cardinal", dates: "21.03 – 19.04" },
  Taurus:      { element: "earth", modality: "fixed", dates: "20.04 – 20.05" },
  Gemini:      { element: "air", modality: "mutable", dates: "21.05 – 20.06" },
  Cancer:      { element: "water", modality: "cardinal", dates: "21.06 – 22.07" },
  Leo:         { element: "fire", modality: "fixed", dates: "23.07 – 22.08" },
  Virgo:       { element: "earth", modality: "mutable", dates: "23.08 – 22.09" },
  Libra:       { element: "air", modality: "cardinal", dates: "23.09 – 22.10" },
  Scorpio:     { element: "water", modality: "fixed", dates: "23.10 – 21.11" },
  Sagittarius: { element: "fire", modality: "mutable", dates: "22.11 – 21.12" },
  Capricorn:   { element: "earth", modality: "cardinal", dates: "22.12 – 19.01" },
  Aquarius:    { element: "air", modality: "fixed", dates: "20.01 – 18.02" },
  Pisces:      { element: "water", modality: "mutable", dates: "19.02 – 20.03" },
};

const SECTIONS = [
  { id: "tarot",  icon: "☰",  labelKey: "home.section_tarot",  descKey: "home.section_desc_tarot" },
  { id: "moon",   icon: "☽",  labelKey: "home.section_moon",   descKey: "home.section_desc_moon" },
  { id: "compat", icon: "♡",  labelKey: "home.section_compat", descKey: "home.section_desc_compat" },
  { id: "natal",  icon: "◎",  labelKey: "home.section_natal",  descKey: "home.section_desc_natal" },
  { id: "numero", icon: "#",  labelKey: "home.section_numero", descKey: "home.section_desc_numero" },
  { id: "runes",  icon: "ᚱ",  labelKey: "home.section_runes",  descKey: "home.section_desc_runes" },
];

function getTimeOfDayKey(): string {
  const h = new Date().getHours();
  if (h >= 6 && h < 12) return "home.time_morning";
  if (h >= 12 && h < 18) return "home.time_afternoon";
  if (h >= 18) return "home.time_evening";
  return "home.time_night";
}

function getGreetingKey(): string {
  const h = new Date().getHours();
  if (h >= 6 && h < 12) return "home.greeting_morning";
  if (h >= 12 && h < 18) return "home.greeting_afternoon";
  if (h >= 18) return "home.greeting_evening";
  return "home.greeting_night";
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
        token ?? undefined,
      ).catch(() => { setHoroscope(t("home.stars_unavailable")); setHoroscopeLoading(false); });
    }
    load();
  }, []);

  const zodiacLabel = zodiac ? (ru ? zodiac.sign : zodiac.en) : null;
  const userSign = zodiac?.en ?? "Leo";
  const meta = zodiac ? ZODIAC_META[zodiac.en] : null;
  const isPro = user?.tier === "pro";
  const now = new Date();
  const locale = lang === "ru" ? "ru-RU" : lang === "uk" ? "uk-UA" : lang === "es" ? "es-ES" : lang === "pt" ? "pt-BR" : lang === "tr" ? "tr-TR" : "en-US";
  const dayName = now.toLocaleDateString(locale, { weekday: "long", day: "numeric", month: "long" });

  const bars = [
    { label: t("home.score_love"), value: scores?.love ?? 0, color: "#C9A84C" },
    { label: t("home.score_career"), value: scores?.career ?? 0, color: "#8A7FC0" },
    { label: t("home.score_health"), value: scores?.health ?? 0, color: "#6E9A8A" },
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
        <p className="font-cinzel italic" style={{ fontSize: 14, color: "#A89E8B" }}>{dayName} · {t(getTimeOfDayKey())}</p>
        <p className="font-cormorant" style={{ fontSize: 31, color: "#F0E9DA", lineHeight: 1.08, marginTop: 2 }}>
          {t(getGreetingKey())}, {user?.name ?? t("profile.guest")}
        </p>
      </div>

      {/* Zodiac + Horoscope — grid on desktop */}
      <div className="lg:grid lg:gap-5" style={{ marginTop: 12, padding: "0 22px" }} >
        <style>{`.lg\\:grid { grid-template-columns: 300px 1fr; } @media(max-width:1023px) { .lg\\:grid { display:block !important; } }`}</style>

        {/* Zodiac — hero level */}
        <div className="lg:rounded-3xl lg:p-5 lg:text-center" style={{ position: "relative", padding: "6px 0 2px", textAlign: "center", background: "radial-gradient(140% 100% at 50% 0%, #1C1650 0%, #0F0A2E 40%, transparent 100%)", borderRadius: 22, border: "1px solid rgba(201,168,76,.28)", boxShadow: "0 0 80px rgba(75,60,134,.25), 0 0 40px rgba(201,168,76,.08)" }}>
          <ZodiacGlyph sign={userSign} size={200} />
          <div style={{ marginTop: -8 }}>
            <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".34em", color: "#C9A84C" }}>{t("home.your_sign")}</p>
            <p className="font-cormorant" style={{ fontSize: 42, color: "#F0E9DA", lineHeight: 1.02 }}>{zodiacLabel ?? t("home.zodiac_fallback")}</p>
            {meta && <p style={{ fontSize: 12, color: "#8A8170", letterSpacing: ".04em", marginTop: 2 }}>{t(`home.element_${meta.element}`)} · {t(`home.modality_${meta.modality}`)} · {meta.dates}</p>}
          </div>
        </div>

        {/* Horoscope */}
        <div style={{ padding: 22, borderRadius: 22, background: "linear-gradient(160deg,rgba(255,255,255,.055),rgba(255,255,255,.015))", border: "1px solid rgba(201,168,76,.16)", backdropFilter: "blur(12px)" }}>
        <div className="flex items-center justify-between">
          <span className="font-cinzel uppercase" style={{ fontSize: 10.5, letterSpacing: ".28em", color: "#C9A84C" }}>{t("home.daily_horoscope")}</span>
          <span style={{ fontSize: 11, color: "#6E6757" }}>{now.toLocaleDateString(locale, { day: "numeric", month: "short" })}</span>
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
            {t("home.read_full")}
          </button>
        )}
      </div>
      </div>{/* end grid wrapper */}

      {/* Tarot CTA */}
      <button onClick={() => onNavigate("tarot")} className="w-full text-left" style={{ margin: "12px 22px 0", width: "calc(100% - 44px)", padding: "16px 20px", borderRadius: 18, display: "flex", alignItems: "center", gap: 14, background: "linear-gradient(100deg, rgba(75,60,134,.2), rgba(201,168,76,.08))", border: "1px solid rgba(201,168,76,.2)", cursor: "pointer" }}>
        <span style={{ fontSize: 28, color: "#C9A84C", filter: "drop-shadow(0 0 8px rgba(201,168,76,.4))", flexShrink: 0 }}>☰</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <p className="font-cormorant" style={{ fontSize: 18, color: "#F0E9DA" }}>{t("home.daily_spread")}</p>
          <p style={{ fontSize: 12, color: "#8A8170" }}>{t("home.daily_spread_hint")}</p>
        </div>
        <span style={{ color: "#6E6757", marginLeft: "auto" }}>›</span>
      </button>

      {/* Lunar — mobile only */}
      <button onClick={() => onNavigate("moon")} className="w-full text-left lg:hidden" style={{ margin: "14px 22px 0", width: "calc(100% - 44px)", padding: "18px 20px", borderRadius: 22, display: "flex", alignItems: "center", gap: 18, background: "linear-gradient(160deg,rgba(58,76,134,.22),rgba(255,255,255,.012))", border: "1px solid rgba(138,127,192,.24)" }}>
        <div style={{ animation: "mystral-pulse-glow 3.6s ease-in-out infinite", borderRadius: "50%", flexShrink: 0, width: 52, height: 52, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28, color: "#A99BE0" }}>
          {lunar?.phase_icon ?? "☽"}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".26em", color: "#A99BE0" }}>{t("home.lunar_day_title")}</p>
          <p className="font-cormorant" style={{ fontSize: 26, color: "#F0E9DA", lineHeight: 1.15, marginTop: 3 }}>
            {lunar ? `${lunar.lunar_day} ${t("home.lunar_day")}` : "..."}
          </p>
          {lunar && <p style={{ fontSize: 12, color: "#9890B8", marginTop: 4 }}>{lunar.phase_name} · {t("lunar.moon_in")} {lunar.moon_sign}</p>}
        </div>
        <span style={{ marginLeft: "auto", color: "#6E6757", fontSize: 18 }}>›</span>
      </button>

      {/* Sections */}
      <div style={{ padding: "24px 22px 0" }}>
        <div className="flex items-center justify-between">
          <span className="font-cormorant" style={{ fontSize: 24, color: "#F0E9DA" }}>{t("home.sections")}</span>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-3" style={{ gap: 12, marginTop: 14 }}>
          {SECTIONS.map(s => (
            <button key={s.id} onClick={() => onNavigate(s.id)} className="text-left" style={{ padding: 16, borderRadius: 18, background: "rgba(255,255,255,.02)", border: "1px solid rgba(255,255,255,.06)", display: "flex", alignItems: "center", gap: 12 }}>
              <span style={{ fontSize: 20, color: "#C9A84C", flexShrink: 0 }}>{s.icon}</span>
              <span className="font-cormorant" style={{ fontSize: 18, color: "#F0E9DA" }}>{t(s.labelKey)}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Natal banner — mobile only */}
      <button onClick={() => onNavigate("natal")} className="w-full text-left lg:hidden" style={{ margin: "20px 22px 24px", width: "calc(100% - 44px)", position: "relative", overflow: "hidden", padding: 24, borderRadius: 22, background: "linear-gradient(120deg,#1B1546,#0C0A22)", border: "1px solid rgba(201,168,76,.24)" }}>
        <div style={{ position: "absolute", top: -30, right: -10, width: 140, height: 140, borderRadius: "50%", background: "radial-gradient(circle,rgba(201,168,76,.16),transparent 68%)" }} />
        <p className="font-cinzel uppercase" style={{ fontSize: 10.5, letterSpacing: ".28em", color: "#C9A84C", position: "relative" }}>{t("home.natal_title")}</p>
        <p className="font-cormorant" style={{ fontSize: 25, color: "#F0E9DA", margin: "6px 0 10px", lineHeight: 1.15, position: "relative" }}>{t("home.natal_ready")}</p>
        <p style={{ fontSize: 13, lineHeight: 1.6, color: "#A89E8B", margin: "0 0 16px", maxWidth: "90%", position: "relative" }}>{t("home.natal_banner_desc")}</p>
        <span style={{ display: "inline-flex", alignItems: "center", gap: 8, height: 44, padding: "0 20px", borderRadius: 12, background: "linear-gradient(100deg,#A9882F,#E8CD7E)", color: "#1A1206", fontWeight: 600, fontSize: 13.5, position: "relative" }}>{t("home.open_chart")}</span>
      </button>

      <div className="pb-20 lg:pb-8" />

      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
    </div>
  );
}
