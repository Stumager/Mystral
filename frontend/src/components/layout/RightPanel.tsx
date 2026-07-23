import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import { getZodiacSign, signLabel } from "../../utils/zodiac";

interface LunarInfo {
  lunar_day: number;
  phase_name: string;
  phase_icon: string;
  moon_sign: string;
  energy: string;
}

export function RightPanel() {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const [lunar, setLunar] = useState<LunarInfo | null>(null);
  const [birthDate, setBirthDate] = useState<string | null>(null);
  const loaded = useRef(false);

  useEffect(() => {
    if (loaded.current) return;
    loaded.current = true;
    const lang = user?.lang ?? "ru";

    fetch(`/api/v1/lunar/today?lang=${lang}`).then(r => r.json()).then(setLunar).catch(() => {});

    if (token) {
      fetch("/api/v1/profile", { headers: { Authorization: `Bearer ${token}` } })
        .then(r => r.json())
        .then(d => { if (d.birth_date) setBirthDate(d.birth_date); })
        .catch(() => {});
    }
  }, []);

  const zodiac = birthDate ? getZodiacSign(birthDate) : null;
  const zodiacLabel = zodiac ? signLabel(zodiac, user?.lang ?? "ru") : null;

  return (
    <aside
      className="w-[220px] shrink-0 sticky top-0 h-screen overflow-y-auto py-6 px-4 flex flex-col gap-4"
      style={{ borderLeft: "1px solid rgba(140,110,255,0.08)" }}
    >
      {/* Lunar today */}
      {lunar && (
        <div
          className="rounded-xl px-3 py-3 flex flex-col gap-1.5"
          style={{ background: "rgba(107,78,255,0.06)", border: "0.5px solid rgba(107,78,255,0.12)" }}
        >
          <div className="flex items-center gap-2">
            <span className="text-xl">{lunar.phase_icon}</span>
            <div>
              <p className="text-text-primary text-sm font-display">
                {lunar.lunar_day} {t("lunar.lunar_day_label")}
              </p>
              <p className="text-text-faint text-[10px]">{lunar.phase_name}</p>
            </div>
          </div>
          <p className="text-text-faint text-[10px]">
            {t("lunar.moon_in")} {lunar.moon_sign}
          </p>
          <p className="text-text-faint text-[10px]">
            {t("lunar.energy")}: <span style={{ color: "#C9A84C" }}>{lunar.energy}</span>
          </p>
        </div>
      )}

      {/* Zodiac sign */}
      {zodiac ? (
        <div
          className="rounded-xl px-3 py-3 flex items-center gap-3"
          style={{ background: "rgba(107,78,255,0.06)", border: "0.5px solid rgba(107,78,255,0.12)" }}
        >
          <span className="text-2xl">{zodiac.symbol}</span>
          <div>
            <p className="text-text-primary text-sm font-display">{zodiacLabel}</p>
            <p className="text-text-faint text-[10px]">
              {user?.lang === "en" ? "Your sign" : "Твой знак"}
            </p>
          </div>
        </div>
      ) : (
        <div
          className="rounded-xl px-3 py-3"
          style={{ background: "rgba(107,78,255,0.06)", border: "0.5px solid rgba(107,78,255,0.12)" }}
        >
          <p className="text-text-faint text-xs">{t("home.zodiac_fallback")}</p>
        </div>
      )}

      {/* Pro badge */}
      {user?.tier === "pro" ? (
        <div
          className="rounded-xl px-3 py-2.5 flex items-center gap-2"
          style={{ background: "rgba(201,168,76,0.08)", border: "0.5px solid rgba(201,168,76,0.2)" }}
        >
          <span style={{ color: "#C9A84C" }}>Pro</span>
          <span className="text-xs font-display" style={{ color: "#C9A84C" }}>Mystral Pro</span>
        </div>
      ) : (
        <div
          className="rounded-xl px-3 py-2.5"
          style={{ background: "rgba(107,78,255,0.06)", border: "0.5px solid rgba(107,78,255,0.12)" }}
        >
          <p className="text-text-faint text-[10px]">{t("profile.free_plan")}</p>
        </div>
      )}
    </aside>
  );
}
