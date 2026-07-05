import { useMemo, useState } from "react";

export type WheelPlanet = {
  name: string;
  sign: string;
  degree: number; // absolute degree 0-360
  retrograde: boolean;
};

export type WheelHouse = {
  number: number; // 1-12
  degree: number; // absolute cusp degree 0-360
};

export type WheelAspect = {
  planet1: string;
  planet2: string;
  type: string; // conjunction, trine, square, sextile, opposition
  orb: number;
};

export type NatalWheelProps = {
  planets: WheelPlanet[];
  houses: WheelHouse[];
  aspects: WheelAspect[];
  size?: number;
};

const ZODIAC_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"];

// Fire / Earth / Air / Water repeating every sign, starting at Aries.
const SIGN_ELEMENT_COLOR = [
  "rgba(196,84,84,.15)", "rgba(110,154,138,.15)", "rgba(138,127,192,.15)", "rgba(75,120,192,.15)",
  "rgba(196,84,84,.15)", "rgba(110,154,138,.15)", "rgba(138,127,192,.15)", "rgba(75,120,192,.15)",
  "rgba(196,84,84,.15)", "rgba(110,154,138,.15)", "rgba(138,127,192,.15)", "rgba(75,120,192,.15)",
];

const PLANET_SYMBOLS: Record<string, string> = {
  sun: "☉", moon: "☽", mercury: "☿", venus: "♀", mars: "♂",
  jupiter: "♃", saturn: "♄", uranus: "♅", neptune: "♆", pluto: "♇",
  chiron: "Ch", true_node: "☊", north_node: "☊", south_node: "☋",
};

const PLANET_COLORS: Record<string, string> = {
  sun: "#E8CD7E", moon: "#C0C8D0", mercury: "#A99BE0", venus: "#D98A8A",
  mars: "#C95050", jupiter: "#C9A84C", saturn: "#8A8170", uranus: "#6E9A8A",
  neptune: "#4B7CB5", pluto: "#8A6E2E",
};

const ASPECT_STYLE: Record<string, { color: string; width: number }> = {
  conjunction: { color: "rgba(201,168,76,.5)", width: 1.2 },
  trine: { color: "rgba(110,154,138,.5)", width: 1 },
  sextile: { color: "rgba(138,127,192,.4)", width: 0.8 },
  square: { color: "rgba(196,84,84,.45)", width: 1 },
  opposition: { color: "rgba(196,84,84,.35)", width: 0.8 },
};

// Astrological 0° (Aries) sits at 9 o'clock, increasing counterclockwise.
function degToXY(degree: number, radius: number, cx: number, cy: number) {
  const rad = ((180 - degree) * Math.PI) / 180;
  return { x: cx + radius * Math.cos(rad), y: cy + radius * Math.sin(rad) };
}

function sectorPath(startDeg: number, endDeg: number, rOuter: number, rInner: number, cx: number, cy: number) {
  const outerStart = degToXY(startDeg, rOuter, cx, cy);
  const outerEnd = degToXY(endDeg, rOuter, cx, cy);
  const innerEnd = degToXY(endDeg, rInner, cx, cy);
  const innerStart = degToXY(startDeg, rInner, cx, cy);
  const largeArc = endDeg - startDeg > 180 ? 1 : 0;
  return [
    `M ${outerStart.x} ${outerStart.y}`,
    `A ${rOuter} ${rOuter} 0 ${largeArc} 0 ${outerEnd.x} ${outerEnd.y}`,
    `L ${innerEnd.x} ${innerEnd.y}`,
    `A ${rInner} ${rInner} 0 ${largeArc} 1 ${innerStart.x} ${innerStart.y}`,
    "Z",
  ].join(" ");
}

function angularDiff(a: number, b: number) {
  const diff = Math.abs(a - b);
  return diff > 180 ? 360 - diff : diff;
}

function houseMidAngle(startDeg: number, endDeg: number) {
  const end = endDeg < startDeg ? endDeg + 360 : endDeg;
  return ((startDeg + end) / 2) % 360;
}

function findHouseForDegree(degree: number, houses: WheelHouse[]): number | null {
  if (houses.length === 0) return null;
  const sorted = [...houses].sort((a, b) => a.degree - b.degree);
  for (let i = 0; i < sorted.length; i++) {
    const start = sorted[i].degree;
    const end = sorted[(i + 1) % sorted.length].degree;
    const inRange = end > start ? degree >= start && degree < end : degree >= start || degree < end;
    if (inRange) return sorted[i].number;
  }
  return sorted[0].number;
}

// Pairwise pass: planets within 7° of an already-placed planet at the same
// radius get nudged to an alternate radius so their symbols don't overlap.
function resolveCollisions(planets: WheelPlanet[], baseRadius: number, shift: number) {
  const placed = planets.map(p => ({ ...p, radius: baseRadius }));
  for (let i = 0; i < placed.length; i++) {
    for (let j = 0; j < i; j++) {
      if (angularDiff(placed[i].degree, placed[j].degree) < 7 && placed[i].radius === placed[j].radius) {
        placed[i].radius = placed[j].radius === baseRadius ? baseRadius + shift : baseRadius;
      }
    }
  }
  return placed;
}

export function NatalWheel({ planets, houses, aspects, size = 520 }: NatalWheelProps) {
  const [hovered, setHovered] = useState<number | null>(null);

  const cx = size / 2;
  const cy = size / 2;
  const R = size / 2;
  const R_outer = R * 0.95;
  const R_sign = R * 0.82;
  const R_house = R * 0.72;
  const R_inner = R * 0.38;
  const R_planet = R * 0.6;
  const R_center = R_inner * 0.15;

  const sortedHouses = useMemo(() => [...houses].sort((a, b) => a.number - b.number), [houses]);

  const positionedPlanets = useMemo(
    () => resolveCollisions(planets, R_planet, size * 0.07),
    [planets, R_planet, size],
  );

  const planetByName = useMemo(() => {
    const map = new Map<string, WheelPlanet>();
    planets.forEach(p => map.set(p.name.toLowerCase(), p));
    return map;
  }, [planets]);

  const visibleAspects = useMemo(
    () => aspects.filter(a =>
      a.orb < 5 && planetByName.has(a.planet1.toLowerCase()) && planetByName.has(a.planet2.toLowerCase())),
    [aspects, planetByName],
  );

  const degreeTicks = useMemo(() => Array.from({ length: 36 }, (_, i) => i * 10), []);

  const hoveredPlanet = hovered !== null ? positionedPlanets[hovered] : null;
  const hoveredPos = hoveredPlanet ? degToXY(hoveredPlanet.degree, hoveredPlanet.radius, cx, cy) : null;
  const hoveredHouse = hoveredPlanet ? findHouseForDegree(hoveredPlanet.degree, houses) : null;

  return (
    <div style={{ position: "relative", width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ overflow: "visible" }}>
        {/* Layer 1 — zodiac belt */}
        <g>
          {ZODIAC_SYMBOLS.map((symbol, i) => {
            const start = i * 30;
            const end = start + 30;
            const labelPos = degToXY(start + 15, (R_outer + R_sign) / 2, cx, cy);
            return (
              <g key={`sign-${i}`}>
                <path d={sectorPath(start, end, R_outer, R_sign, cx, cy)} fill={SIGN_ELEMENT_COLOR[i]}
                  stroke="rgba(201,168,76,.3)" strokeWidth={0.5} />
                <text x={labelPos.x} y={labelPos.y} fontSize={size * 0.04} fill="rgba(201,168,76,.8)"
                  fontFamily="Segoe UI Symbol, Apple Symbols, Noto Sans Symbols"
                  textAnchor="middle" dominantBaseline="central">{symbol}</text>
              </g>
            );
          })}
        </g>

        {/* Layer 2 — house lines + numbers */}
        <g>
          {sortedHouses.map((h, i) => {
            const isAngle = h.number === 1 || h.number === 4 || h.number === 7 || h.number === 10;
            const outer = degToXY(h.degree, R_house, cx, cy);
            const inner = degToXY(h.degree, R_inner, cx, cy);
            const next = sortedHouses[(i + 1) % sortedHouses.length];
            const mid = houseMidAngle(h.degree, next.degree);
            const labelPos = degToXY(mid, (R_house + R_inner) / 2, cx, cy);
            return (
              <g key={`house-${h.number}`}>
                <line x1={inner.x} y1={inner.y} x2={outer.x} y2={outer.y}
                  stroke={isAngle ? "rgba(201,168,76,.6)" : "rgba(255,255,255,.2)"}
                  strokeWidth={isAngle ? 1.5 : 0.5} />
                <text x={labelPos.x} y={labelPos.y} fontSize={size * 0.025} fill="rgba(176,172,152,.6)"
                  fontFamily="Inter" textAnchor="middle" dominantBaseline="central">{h.number}</text>
              </g>
            );
          })}
        </g>

        {/* Layer 3 — aspect lines */}
        <g style={{ animation: "mystral-fadein 1s ease-out .4s both" }}>
          {visibleAspects.map((a, i) => {
            const p1 = planetByName.get(a.planet1.toLowerCase())!;
            const p2 = planetByName.get(a.planet2.toLowerCase())!;
            const pos1 = degToXY(p1.degree, R_inner * 0.95, cx, cy);
            const pos2 = degToXY(p2.degree, R_inner * 0.95, cx, cy);
            const style = ASPECT_STYLE[a.type] ?? ASPECT_STYLE.conjunction;
            return (
              <line key={`aspect-${i}`} x1={pos1.x} y1={pos1.y} x2={pos2.x} y2={pos2.y}
                stroke={style.color} strokeWidth={style.width} />
            );
          })}
        </g>

        {/* Layer 4 — planets */}
        <g>
          {positionedPlanets.map((p, i) => {
            const pos = degToXY(p.degree, p.radius, cx, cy);
            const houseEdge = degToXY(p.degree, R_house, cx, cy);
            const key = p.name.toLowerCase();
            const color = PLANET_COLORS[key] ?? "#C9A84C";
            const symbol = PLANET_SYMBOLS[key] ?? p.name.slice(0, 2);
            return (
              <g key={`planet-${i}`}
                style={{ animation: `mystral-fadeup .6s ease-out ${i * 0.05}s both`, cursor: "pointer" }}
                onMouseEnter={() => setHovered(i)}
                onMouseLeave={() => setHovered(null)}>
                <line x1={pos.x} y1={pos.y} x2={houseEdge.x} y2={houseEdge.y} stroke="rgba(255,255,255,.1)" />
                <circle cx={pos.x} cy={pos.y} r={size * 0.022} fill="rgba(7,6,15,.9)" stroke={color} />
                <text x={pos.x} y={pos.y} fontSize={size * 0.028} fill={color}
                  textAnchor="middle" dominantBaseline="central">{symbol}</text>
                {p.retrograde && (
                  <text x={pos.x + size * 0.02} y={pos.y - size * 0.02} fontSize={size * 0.016}
                    fill="rgba(196,84,84,.8)">R</text>
                )}
              </g>
            );
          })}
        </g>

        {/* Layer 5 — degree ticks */}
        <g>
          {degreeTicks.map(deg => {
            const outer = degToXY(deg, R_outer, cx, cy);
            const tickInner = degToXY(deg, R_outer - size * 0.015, cx, cy);
            const labelPos = degToXY(deg, R_outer - size * 0.045, cx, cy);
            return (
              <g key={`tick-${deg}`}>
                <line x1={tickInner.x} y1={tickInner.y} x2={outer.x} y2={outer.y}
                  stroke="rgba(255,255,255,.25)" strokeWidth={0.5} />
                <text x={labelPos.x} y={labelPos.y} fontSize={size * 0.02} fill="rgba(255,255,255,.25)"
                  textAnchor="middle" dominantBaseline="central">{deg % 30}</text>
              </g>
            );
          })}
        </g>

        {/* Layer 6 — center circle */}
        <circle cx={cx} cy={cy} r={R_center} fill="rgba(201,168,76,.08)" stroke="rgba(201,168,76,.2)" />
      </svg>

      {hoveredPlanet && hoveredPos && (
        <div style={{
          position: "absolute", left: hoveredPos.x, top: hoveredPos.y, transform: "translate(-50%, -140%)",
          background: "rgba(7,6,15,.95)", border: "1px solid rgba(201,168,76,.3)",
          borderRadius: 10, padding: "8px 12px", fontSize: 12, color: "#F0E9DA",
          whiteSpace: "nowrap", pointerEvents: "none", zIndex: 10,
        }}>
          {hoveredPlanet.name} в {hoveredPlanet.sign} {Math.round((hoveredPlanet.degree % 30) * 10) / 10}°
          {" · "}{hoveredHouse ?? "?"} дом{hoveredPlanet.retrograde ? " (R)" : ""}
        </div>
      )}
    </div>
  );
}
