import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import { getZodiacSign, ZodiacInfo } from "../../utils/zodiac";
import { ZodiacGlyph } from "../ZodiacGlyph";

interface LunarData {
  lunar_day: number; phase_name: string; phase_icon: string; moon_sign: string;
}

export function DesktopRightPanel() {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const ru = (user?.lang ?? "ru") === "ru";
  const isPro = user?.tier === "pro";

  const [lunar, setLunar] = useState<LunarData | null>(null);
  const [zodiac, setZodiac] = useState<ZodiacInfo | null>(null);
  const loaded = useRef(false);

  useEffect(() => {
    if (loaded.current) return;
    loaded.current = true;
    fetch(`/api/v1/lunar/today?lang=${user?.lang ?? "ru"}`).then(r => r.json()).then(setLunar).catch(() => {});
    if (token) {
      fetch("/api/v1/profile", { headers: { Authorization: `Bearer ${token}` } })
        .then(r => r.json())
        .then(d => { if (d.birth_date) setZodiac(getZodiacSign(d.birth_date)); })
        .catch(() => {});
    }
  }, []);

  const zodiacLabel = zodiac ? (ru ? zodiac.sign : zodiac.en) : null;
  const userSign = zodiac?.en ?? "Leo";

  return (
    <aside style={{ flex: "none", width: 312, overflowY: "auto", padding: "26px 22px", borderLeft: "1px solid rgba(201,168,76,.12)", background: "rgba(7,6,15,.45)", display: "flex", flexDirection: "column", gap: 18 }}>
      {/* Lunar day */}
      <div style={{ padding: 20, borderRadius: 20, textAlign: "center", background: "linear-gradient(160deg,rgba(58,76,134,.22),rgba(255,255,255,.012))", border: "1px solid rgba(138,127,192,.24)" }}>
        <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".26em", color: "#A99BE0", marginBottom: 14 }}>{t("sidebar.lunar_day")}</p>
        <div style={{ display: "flex", justifyContent: "center" }}>
          <div style={{ width: "fit-content", borderRadius: "50%", animation: "mystral-pulse-glow 3.6s ease-in-out infinite", fontSize: 48, lineHeight: 1, padding: 12, color: "#A99BE0" }}>
            {lunar?.phase_icon ?? "☽"}
          </div>
        </div>
        <p className="font-cormorant" style={{ fontSize: 28, color: "#F0E9DA", marginTop: 14 }}>
          {lunar ? `${lunar.lunar_day} ${t("home.lunar_day")}` : "..."}
        </p>
        {lunar && <p style={{ fontSize: 12, color: "#9890B8", marginTop: 4 }}>{t("lunar.moon_in")} {lunar.moon_sign}</p>}
      </div>

      {/* Zodiac sign */}
      <div style={{ padding: 20, borderRadius: 20, background: "linear-gradient(160deg,rgba(255,255,255,.05),rgba(255,255,255,.012))", border: "1px solid rgba(201,168,76,.16)" }}>
        <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".26em", color: "#C9A84C", marginBottom: 8 }}>{t("home.your_sign")}</p>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <ZodiacGlyph sign={userSign} size={80} />
          <div>
            <p className="font-cormorant" style={{ fontSize: 24, color: "#F0E9DA", lineHeight: 1 }}>{zodiacLabel ?? "—"}</p>
            <p style={{ fontSize: 12, color: "#8A8170", marginTop: 4 }}>{t("sidebar.your_sign")}</p>
          </div>
        </div>
      </div>

      {/* Pro button */}
      {!isPro && (
        <button style={{ position: "relative", overflow: "hidden", height: 54, borderRadius: 14, background: "linear-gradient(100deg,#A9882F,#C9A84C 50%,#E8CD7E)", boxShadow: "0 10px 28px -8px rgba(201,168,76,.55)", display: "flex", alignItems: "center", justifyContent: "center", gap: 8, cursor: "pointer", border: "none", width: "100%" }}>
          <span style={{ position: "absolute", inset: 0, background: "linear-gradient(100deg,transparent 30%,rgba(255,255,255,.5) 50%,transparent 70%)", backgroundSize: "200% 100%", animation: "mystral-shimmer 2.8s linear infinite" }} />
          <span style={{ position: "relative", color: "#1A1206", fontWeight: 600, fontSize: 14 }}>{t("sidebar.mystral_pro")}</span>
        </button>
      )}
    </aside>
  );
}
