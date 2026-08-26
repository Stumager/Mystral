import { useEffect, useRef, useState } from "react";
import { onScrollThrottled, usePrefersReducedMotion } from "../../utils/motion";
import { PlanetIcon, ZODIAC_ORDER, ZodiacIcon } from "../icons/AstroIcons";

/**
 * A representative chart, not a live calculation.
 *
 * The section exists to show what the app draws, so the geometry has to be
 * plausible rather than accurate for any particular birth: twelve equal
 * houses off a fixed Ascendant, ten bodies at fixed ecliptic degrees, and
 * the aspects that actually hold between those degrees.
 */
const ASCENDANT = 22;
const HOUSES = Array.from({ length: 12 }, (_, i) => ({ number: i + 1, degree: (ASCENDANT + i * 30) % 360 }));

const PLANETS = [
  { name: "sun", degree: 138, color: "#E8CD7E" },
  { name: "moon", degree: 47, color: "#C0C8D0" },
  { name: "mercury", degree: 155, color: "#A99BE0" },
  { name: "venus", degree: 112, color: "#D98A8A" },
  { name: "mars", degree: 268, color: "#C95050" },
  { name: "jupiter", degree: 8, color: "#C9A84C" },
  { name: "saturn", degree: 305, color: "#8A8170" },
  { name: "uranus", degree: 218, color: "#6E9A8A" },
  { name: "neptune", degree: 342, color: "#4B7CB5" },
  { name: "pluto", degree: 195, color: "#8A6E2E" },
];

const ASPECTS = [
  { a: "sun", b: "venus", kind: "sextile" },
  { a: "sun", b: "mercury", kind: "conjunction" },
  { a: "moon", b: "mars", kind: "square" },
  { a: "jupiter", b: "uranus", kind: "trine" },
  { a: "saturn", b: "moon", kind: "trine" },
  { a: "mars", b: "neptune", kind: "square" },
  { a: "pluto", b: "sun", kind: "opposition" },
  { a: "venus", b: "saturn", kind: "sextile" },
];

const ASPECT_STYLE: Record<string, { color: string; width: number }> = {
  conjunction: { color: "rgba(201,168,76,.6)", width: 1.2 },
  trine: { color: "rgba(90,140,210,.6)", width: 1 },
  sextile: { color: "rgba(90,140,210,.42)", width: .9 },
  square: { color: "rgba(206,74,74,.55)", width: 1 },
  opposition: { color: "rgba(206,74,74,.45)", width: .9 },
};

// Fire / Earth / Air / Water, repeating from Aries.
const ELEMENT_FILL = ["rgba(196,84,84,.13)", "rgba(110,154,138,.13)", "rgba(138,127,192,.13)", "rgba(75,120,192,.13)"];

const SIZE = 460;
const C = SIZE / 2;
const R_OUTER = C * 0.95;
const R_SIGN = C * 0.79;
const R_HOUSE = C * 0.68;
const R_INNER = C * 0.36;
const R_PLANET = C * 0.55;

/** 0° sits at 9 o'clock and increases counterclockwise — western tropical. */
function xy(deg: number, radius: number) {
  const rad = ((180 - deg) * Math.PI) / 180;
  return { x: C + radius * Math.cos(rad), y: C + radius * Math.sin(rad) };
}

function sector(startDeg: number, endDeg: number, rOuter: number, rInner: number) {
  const a = xy(startDeg, rOuter), b = xy(endDeg, rOuter);
  const c = xy(endDeg, rInner), d = xy(startDeg, rInner);
  return `M ${a.x} ${a.y} A ${rOuter} ${rOuter} 0 0 0 ${b.x} ${b.y} L ${c.x} ${c.y} A ${rInner} ${rInner} 0 0 1 ${d.x} ${d.y} Z`;
}

/** Maps a global 0..1 progress onto one stage's own 0..1 range. */
function stage(p: number, from: number, to: number) {
  return Math.min(1, Math.max(0, (p - from) / (to - from)));
}

const STAGES = [
  { ru: { t: "Круг эклиптики", d: "Двенадцать секторов по 30° — знаки зодиака в момент вашего рождения." },
    en: { t: "The ecliptic", d: "Twelve 30° sectors — the zodiac as it stood at the moment you were born." } },
  { ru: { t: "Дома", d: "Двенадцать домов от Асцендента: сферы жизни, на которые ложатся планеты." },
    en: { t: "The houses", d: "Twelve houses from the Ascendant: the areas of life the planets fall into." } },
  { ru: { t: "Планеты", d: "Десять тел с точностью до градуса — по эфемеридам, а не по знаку целиком." },
    en: { t: "The planets", d: "Ten bodies to the degree — from ephemeris, not from your sign as a whole." } },
  { ru: { t: "Аспекты", d: "Углы между планетами: сеть, которая и делает карту вашей, а не общей." },
    en: { t: "The aspects", d: "The angles between planets: the web that makes the chart yours, not everyone's." } },
];

export function ScrollNatalWheel({ ru }: { ru: boolean }) {
  const sectionRef = useRef<HTMLElement>(null);
  const [progress, setProgress] = useState(0);
  const reduced = usePrefersReducedMotion();

  useEffect(() => {
    // Reduced motion gets the finished chart immediately — an un-animated
    // version of this section would otherwise be a blank circle.
    if (reduced) { setProgress(1); return; }
    return onScrollThrottled(() => {
      const el = sectionRef.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const travel = rect.height - window.innerHeight;
      if (travel <= 0) { setProgress(1); return; }
      setProgress(Math.min(1, Math.max(0, -rect.top / travel)));
    });
  }, [reduced]);

  const pRings = stage(progress, 0, 0.16);
  const pSigns = stage(progress, 0.14, 0.40);
  const pHouses = stage(progress, 0.38, 0.58);
  const pPlanets = stage(progress, 0.56, 0.80);
  const pAspects = stage(progress, 0.78, 1);

  const activeStage = pAspects > 0 ? 3 : pPlanets > 0 ? 2 : pHouses > 0 ? 1 : 0;
  const caption = ru ? STAGES[activeStage].ru : STAGES[activeStage].en;

  const planetPos = new Map(PLANETS.map(p => [p.name, xy(p.degree - ASCENDANT, R_INNER * 0.94)]));

  return (
    <section ref={sectionRef} style={{ position: "relative", height: reduced ? "auto" : "300vh" }}>
      <div className="snw-sticky" style={{
        position: reduced ? "relative" : "sticky", top: 0,
        minHeight: reduced ? undefined : "100vh",
        display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
        padding: "40px 24px", gap: 20,
      }}>
        {/* The whole stack has to fit one viewport height, or the sticky
            frame clips its own caption on short laptop screens. */}
        <style>{`
          .snw-wheel { width: min(100%, 420px); }
          @media (max-height: 780px) { .snw-wheel { width: min(100%, 330px); } }
          @media (max-height: 660px) { .snw-wheel { width: min(100%, 270px); } }
        `}</style>

        <div style={{ textAlign: "center", maxWidth: 560 }}>
          <span className="font-cinzel uppercase" style={{ fontSize: 11.5, letterSpacing: ".28em", color: "#C9A84C" }}>
            {ru ? "Натальная карта" : "The natal chart"}
          </span>
          <h2 className="font-cormorant" style={{ fontSize: "clamp(28px,4vw,40px)", color: "#F0E9DA", lineHeight: 1.14, marginTop: 10 }}>
            {ru ? "Собирается слой за слоем" : "Assembled layer by layer"}
          </h2>
        </div>

        <div className="snw-wheel" style={{ position: "relative" }}>
          <svg viewBox={`0 0 ${SIZE} ${SIZE}`} width="100%" style={{ overflow: "visible", display: "block" }} aria-hidden>
            {/* Layer 1 — the rings, drawn on with a dash offset */}
            <g fill="none" stroke="rgba(201,168,76,.45)">
              {[R_OUTER, R_SIGN, R_HOUSE, R_INNER].map((r, i) => {
                const circumference = 2 * Math.PI * r;
                const local = stage(pRings, i * 0.12, 0.6 + i * 0.12);
                return (
                  <circle key={r} cx={C} cy={C} r={r} strokeWidth={i === 0 ? 1.4 : 0.8}
                    strokeDasharray={circumference} strokeDashoffset={circumference * (1 - local)}
                    transform={`rotate(-90 ${C} ${C})`} opacity={i === 0 ? 0.9 : 0.5} />
                );
              })}
            </g>

            {/* Layer 2 — zodiac belt, one sign at a time */}
            <g>
              {ZODIAC_ORDER.map((sign, i) => {
                const local = stage(pSigns, i * 0.055, 0.34 + i * 0.055);
                if (local <= 0) return null;
                const start = i * 30 - ASCENDANT;
                const mid = xy(start + 15, (R_OUTER + R_SIGN) / 2);
                return (
                  <g key={sign} opacity={local}>
                    <path d={sector(start, start + 30, R_OUTER, R_SIGN)}
                      fill={ELEMENT_FILL[i % 4]} stroke="rgba(201,168,76,.28)" strokeWidth={0.5} />
                    <g transform={`translate(${mid.x - 10} ${mid.y - 10}) scale(${0.6 + local * 0.4})`}
                      style={{ color: "rgba(232,205,126,.85)", transformOrigin: "10px 10px" }}>
                      <ZodiacIcon sign={sign} size={20} strokeWidth={1.4} />
                    </g>
                  </g>
                );
              })}
            </g>

            {/* Layer 3 — house cusps */}
            <g>
              {HOUSES.map((h, i) => {
                const local = stage(pHouses, i * 0.05, 0.4 + i * 0.05);
                if (local <= 0) return null;
                const isAngle = [1, 4, 7, 10].includes(h.number);
                const outer = xy(h.degree - ASCENDANT, R_HOUSE);
                const inner = xy(h.degree - ASCENDANT, R_INNER);
                const label = xy(h.degree - ASCENDANT + 15, (R_HOUSE + R_INNER) / 2);
                return (
                  <g key={h.number} opacity={local}>
                    <line x1={inner.x} y1={inner.y}
                      x2={inner.x + (outer.x - inner.x) * local} y2={inner.y + (outer.y - inner.y) * local}
                      stroke={isAngle ? "rgba(201,168,76,.6)" : "rgba(255,255,255,.2)"}
                      strokeWidth={isAngle ? 1.4 : 0.6} />
                    <text x={label.x} y={label.y} fontSize={10} fill="rgba(176,172,152,.55)"
                      fontFamily="Inter, sans-serif" textAnchor="middle" dominantBaseline="central">
                      {h.number}
                    </text>
                  </g>
                );
              })}
            </g>

            {/* Layer 5 — aspects sit under the planet discs */}
            <g>
              {ASPECTS.map((a, i) => {
                const local = stage(pAspects, i * 0.07, 0.45 + i * 0.07);
                if (local <= 0) return null;
                const p1 = planetPos.get(a.a)!, p2 = planetPos.get(a.b)!;
                const style = ASPECT_STYLE[a.kind];
                return (
                  <line key={i}
                    x1={p1.x} y1={p1.y}
                    x2={p1.x + (p2.x - p1.x) * local} y2={p1.y + (p2.y - p1.y) * local}
                    stroke={style.color} strokeWidth={style.width} />
                );
              })}
            </g>

            {/* Layer 4 — planets */}
            <g>
              {PLANETS.map((p, i) => {
                const local = stage(pPlanets, i * 0.06, 0.4 + i * 0.06);
                if (local <= 0) return null;
                const pos = xy(p.degree - ASCENDANT, R_PLANET);
                const hub = planetPos.get(p.name)!;
                return (
                  <g key={p.name} opacity={local}>
                    <line x1={pos.x} y1={pos.y} x2={hub.x} y2={hub.y} stroke="rgba(255,255,255,.12)" strokeWidth={0.6} />
                    <circle cx={pos.x} cy={pos.y} r={11 * (0.6 + local * 0.4)}
                      fill="rgba(7,6,15,.92)" stroke={p.color} strokeWidth={1} />
                    <g transform={`translate(${pos.x - 7} ${pos.y - 7})`} style={{ color: p.color }}>
                      <PlanetIcon planet={p.name} size={14} strokeWidth={1.5} />
                    </g>
                  </g>
                );
              })}
            </g>
          </svg>
        </div>

        {/* Caption tracks the stage the scroll is currently in */}
        <div style={{ textAlign: "center", maxWidth: 460, minHeight: 84 }}>
          <p key={caption.t} className="font-cormorant" style={{ fontSize: 24, color: "#F0E9DA", animation: "mystral-fadein .4s ease-out" }}>
            {caption.t}
          </p>
          <p key={caption.d} style={{ fontSize: 14.5, lineHeight: 1.65, color: "#8A8170", marginTop: 6, animation: "mystral-fadein .4s ease-out" }}>
            {caption.d}
          </p>
          <div style={{ display: "flex", justifyContent: "center", gap: 7, marginTop: 16 }}>
            {STAGES.map((_, i) => (
              <span key={i} style={{
                width: i === activeStage ? 22 : 7, height: 7, borderRadius: 99,
                background: i === activeStage ? "linear-gradient(90deg,#A9882F,#E8CD7E)" : "rgba(255,255,255,.14)",
                transition: "width .35s ease, background .35s ease",
              }} />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
