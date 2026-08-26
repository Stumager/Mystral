import { useEffect, useState } from "react";
import { MoonIcon } from "../icons/AstroIcons";

interface LunarData {
  lunar_day: number;
  phase_name: string;
  phase_icon: string;
  moon_sign: string;
  illumination: number;
}

/**
 * Moon disc drawn at an actual illuminated fraction.
 *
 * `/lunar/today` returns a `phase_icon`, but it is an emoji (🌒🌓🌔) — colour
 * platform artwork that cannot inherit the gold palette. This derives the
 * terminator geometrically instead: the lit region is bounded by a half
 * circle on the lit limb and by an ellipse of semi-minor axis R·|1−2f|
 * through both poles. The formula degenerates correctly at both ends — f=0
 * traces zero area, f=1 traces the full disc.
 */
function MoonPhase({ illumination, waxing, size = 96 }: { illumination: number; waxing: boolean; size?: number }) {
  const f = Math.min(1, Math.max(0, illumination / 100));
  const R = size / 2 - 2;
  const c = size / 2;
  const rx = R * Math.abs(1 - 2 * f);
  const outerSweep = waxing ? 1 : 0;
  const innerSweep = f < 0.5 ? (waxing ? 0 : 1) : (waxing ? 1 : 0);
  const litPath = `M ${c} ${c - R} A ${R} ${R} 0 0 ${outerSweep} ${c} ${c + R} A ${rx} ${R} 0 0 ${innerSweep} ${c} ${c - R} Z`;

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden focusable="false" style={{ overflow: "visible" }}>
      <defs>
        <radialGradient id="moon-lit" cx="0.4" cy="0.35">
          <stop offset="0" stopColor="#FBF3D8" />
          <stop offset="0.7" stopColor="#E8CD7E" />
          <stop offset="1" stopColor="#C9A84C" />
        </radialGradient>
      </defs>
      <circle cx={c} cy={c} r={R} fill="rgba(255,255,255,.035)" stroke="rgba(201,168,76,.22)" strokeWidth="1" />
      <path d={litPath} fill="url(#moon-lit)" style={{ filter: "drop-shadow(0 0 14px rgba(201,168,76,.45))" }} />
    </svg>
  );
}

interface Props { ru: boolean; }

/**
 * Live "today" strip: the real lunar day, phase and moon sign, pulled from
 * the same public endpoint the app's home screen uses.
 *
 * Deliberately renders nothing at all when the request fails. A marketing
 * page must not show an error box or a permanent skeleton to a first-time
 * visitor — the section simply is not there if the data is not.
 */
export function LunarToday({ ru }: Props) {
  const [data, setData] = useState<LunarData | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let alive = true;
    fetch(`/api/v1/lunar/today?lang=${ru ? "ru" : "en"}`)
      .then(r => { if (!r.ok) throw new Error(String(r.status)); return r.json(); })
      .then((d: LunarData) => { if (alive) setData(d); })
      .catch(() => { if (alive) setFailed(true); });
    return () => { alive = false; };
  }, [ru]);

  if (failed) return null;

  const locale = ru ? "ru-RU" : "en-US";
  const todayLabel = new Date().toLocaleDateString(locale, { day: "numeric", month: "long" });

  return (
    <div style={{
      position: "relative", overflow: "hidden",
      padding: "28px 30px", borderRadius: 24,
      background: "linear-gradient(150deg,rgba(58,76,134,.24),rgba(255,255,255,.012))",
      border: "1px solid rgba(138,127,192,.26)",
    }}>
      <div aria-hidden style={{
        position: "absolute", top: -70, right: -40, width: 220, height: 220, borderRadius: "50%",
        background: "radial-gradient(circle,rgba(169,155,224,.14),transparent 70%)",
      }} />

      <div style={{ position: "relative", display: "flex", alignItems: "center", gap: 26, flexWrap: "wrap" }}>
        <div style={{ animation: "mystral-float 8s ease-in-out infinite", flexShrink: 0 }}>
          {data
            ? <MoonPhase illumination={data.illumination} waxing={data.lunar_day <= 15} />
            : <span style={{ color: "rgba(169,155,224,.45)", display: "flex", width: 96, height: 96, alignItems: "center", justifyContent: "center" }}>
                <MoonIcon size={62} strokeWidth={1.1} />
              </span>}
        </div>

        <div style={{ flex: "1 1 220px", minWidth: 200 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
            <span className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".26em", color: "#A99BE0" }}>
              {ru ? "Прямо сейчас" : "Right now"}
            </span>
            <span style={{
              fontSize: 10.5, padding: "3px 9px", borderRadius: 99,
              background: "rgba(169,155,224,.12)", border: "1px solid rgba(169,155,224,.3)", color: "#A99BE0",
            }}>
              {todayLabel}
            </span>
          </div>

          <p className="font-cormorant" style={{ fontSize: 34, color: "#F0E9DA", lineHeight: 1.08, marginTop: 8 }}>
            {data
              ? `${data.lunar_day} ${ru ? "лунный день" : "lunar day"}`
              : <span style={{ opacity: .45 }}>{ru ? "Загружаем…" : "Loading…"}</span>}
          </p>

          {data && (
            <p style={{ fontSize: 14, color: "#9890B8", marginTop: 6 }}>
              {data.phase_name} · {ru ? "Луна в" : "Moon in"} {data.moon_sign} · {Math.round(data.illumination)}% {ru ? "освещения" : "lit"}
            </p>
          )}

          <p style={{ fontSize: 12.5, lineHeight: 1.6, color: "#6E6757", marginTop: 12, maxWidth: 400 }}>
            {ru
              ? "Не картинка для красоты — реальный расчёт на сегодня, тот же, что видят пользователи внутри. Завтра здесь будет другое число."
              : "Not decoration — the real calculation for today, the same one users see inside. Tomorrow this shows a different number."}
          </p>
        </div>
      </div>
    </div>
  );
}
