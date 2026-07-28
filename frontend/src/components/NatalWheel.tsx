import { useMemo, useState } from "react";

export type WheelPlanet = {
  /** Raw backend key ("sun", "true_node"). Doubles as the join key against
   *  aspects[].planet1/planet2 and as the lookup for the glyph and colour
   *  tables below, so it must not be a display name. */
  name: string;
  /** What the tooltip shows — already localized by the caller. */
  label?: string;
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
  /** Absolute degree of the Ascendant. The whole wheel is rotated so this
   *  lands on the left horizon — see the rotation note below. */
  ascendant?: number;
  /** Absolute degree of the Midheaven, for the MC/IC axis labels. */
  midheaven?: number;
  size?: number;
};

const ZODIAC_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"];

// Fire / Earth / Air / Water repeating every sign, starting at Aries.
const SIGN_ELEMENT_COLOR = [
  "rgba(196,84,84,.15)", "rgba(110,154,138,.15)", "rgba(138,127,192,.15)", "rgba(75,120,192,.15)",
  "rgba(196,84,84,.15)", "rgba(110,154,138,.15)", "rgba(138,127,192,.15)", "rgba(75,120,192,.15)",
  "rgba(196,84,84,.15)", "rgba(110,154,138,.15)", "rgba(138,127,192,.15)", "rgba(75,120,192,.15)",
];

// Chiron was the only body drawn as letters ("Ch") instead of its glyph.
// These are the standard astronomical/astrological code points, matching what
// the reference charts use (TZ-103 step 0).
const PLANET_SYMBOLS: Record<string, string> = {
  sun: "☉", moon: "☽", mercury: "☿", venus: "♀", mars: "♂",
  jupiter: "♃", saturn: "♄", uranus: "♅", neptune: "♆", pluto: "♇",
  chiron: "⚷", lilith: "⚸", true_node: "☊", north_node: "☊", south_node: "☋",
  ceres: "⚳", pallas: "⚴", juno: "⚵", vesta: "⚶", part_of_fortune: "⊗",
};

const PLANET_COLORS: Record<string, string> = {
  sun: "#E8CD7E", moon: "#C0C8D0", mercury: "#A99BE0", venus: "#D98A8A",
  mars: "#C95050", jupiter: "#C9A84C", saturn: "#8A8170", uranus: "#6E9A8A",
  neptune: "#4B7CB5", pluto: "#8A6E2E",
  // Points and asteroids read as a quieter second tier so they don't compete
  // with the ten planets.
  true_node: "#9C93C4", north_node: "#9C93C4", south_node: "#9C93C4",
  chiron: "#8FA8A0", lilith: "#7E6FA8",
  ceres: "#8A9A78", pallas: "#8A9A78", juno: "#8A9A78", vesta: "#8A9A78",
  part_of_fortune: "#B39A5C",
};

// TZ-103 step 0 — the reference software's convention, not ours: red for the
// tense group, blue for the harmonious one, green for the minors. Conjunction
// stays neutral gold; it takes the character of whatever it joins.
const ASPECT_STYLE: Record<string, { color: string; width: number; dash?: string }> = {
  conjunction: { color: "rgba(201,168,76,.5)", width: 1.2 },
  trine: { color: "rgba(90,140,210,.55)", width: 1 },
  sextile: { color: "rgba(90,140,210,.4)", width: 0.8 },
  square: { color: "rgba(206,74,74,.5)", width: 1 },
  opposition: { color: "rgba(206,74,74,.4)", width: 0.9 },
  semisextile: { color: "rgba(96,158,116,.45)", width: 0.6, dash: "3 3" },
  semisquare: { color: "rgba(96,158,116,.45)", width: 0.6, dash: "3 3" },
  quintile: { color: "rgba(96,158,116,.45)", width: 0.6, dash: "3 3" },
  sesquiquadrate: { color: "rgba(96,158,116,.45)", width: 0.6, dash: "3 3" },
  biquintile: { color: "rgba(96,158,116,.45)", width: 0.6, dash: "3 3" },
  quincunx: { color: "rgba(96,158,116,.45)", width: 0.6, dash: "3 3" },
};

const MINOR_ASPECT_TYPES = new Set([
  "semisextile", "semisquare", "quintile", "sesquiquadrate", "biquintile", "quincunx",
]);

// Planets closer than this (ecliptic degrees) get radially separated so their
// glyphs don't merge into an unreadable blob.
const COLLISION_THRESHOLD_DEG = 4;
const RADIAL_STEP_PX = 15;

// Screen placement for an already-rotated degree: 0 sits at 9 o'clock and the
// value increases counterclockwise, which is the western tropical direction.
//
// TZ-103 step 0: the direction was right but the *anchor* was wrong. This used
// to be fed raw ecliptic degrees, which pinned 0° Aries to the left horizon —
// so the chart came out rotated by an arbitrary amount versus every reference
// drawing, where the left horizon is the Ascendant. Callers now pass
// `degree - ascendant`, which is exactly the offset the reference
// implementation applies (it rotates by the Descendant, putting the AC 180°
// away, i.e. on the left).
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

// Sorts planets by degree, groups consecutive ones within COLLISION_THRESHOLD_DEG
// of each other (wrapping across the 0°/360° seam), and stacks each group
// inward in RADIAL_STEP_PX steps so close conjunctions stay legible.
function resolveCollisions(planets: WheelPlanet[], baseRadius: number) {
  const sorted = [...planets].sort((a, b) => a.degree - b.degree);
  const n = sorted.length;
  if (n === 0) return [];

  const groupOf = new Array(n).fill(0);
  for (let i = 1; i < n; i++) {
    const gap = sorted[i].degree - sorted[i - 1].degree;
    groupOf[i] = gap < COLLISION_THRESHOLD_DEG ? groupOf[i - 1] : groupOf[i - 1] + 1;
  }
  // A cluster straddling the 0°/360° seam ends up split between the first and
  // last groups — merge them when the wrap-around gap is also tight.
  const wrapGap = 360 - sorted[n - 1].degree + sorted[0].degree;
  if (n > 1 && wrapGap < COLLISION_THRESHOLD_DEG) {
    const lastGroup = groupOf[n - 1];
    for (let i = 0; i < n; i++) if (groupOf[i] === lastGroup) groupOf[i] = groupOf[0];
  }

  const groupSizes = new Map<number, number>();
  groupOf.forEach((g: number) => groupSizes.set(g, (groupSizes.get(g) ?? 0) + 1));

  const seen = new Map<number, number>();
  return sorted.map((p, i) => {
    const g = groupOf[i];
    const k = seen.get(g) ?? 0;
    seen.set(g, k + 1);
    const size = groupSizes.get(g)!;
    return { ...p, radius: size > 1 ? baseRadius - k * RADIAL_STEP_PX : baseRadius, collided: size > 1 };
  });
}

export function NatalWheel({ planets, houses, aspects, ascendant = 0, midheaven, size = 520 }: NatalWheelProps) {
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

  // Every ecliptic degree goes through here before it becomes a coordinate.
  const rot = (degree: number) => degree - ascendant;

  const sortedHouses = useMemo(() => [...houses].sort((a, b) => a.number - b.number), [houses]);

  const positionedPlanets = useMemo(
    () => resolveCollisions(planets, R_planet),
    [planets, R_planet],
  );

  const planetByName = useMemo(() => {
    const map = new Map<string, WheelPlanet>();
    planets.forEach(p => map.set(p.name.toLowerCase(), p));
    return map;
  }, [planets]);

  // The drawn web is deliberately tighter than the aspect table. With the
  // optional points switched on there are 19 bodies, and at the table's 8°
  // major orb that's ~47 lines inside a circle ~190px across — a grey blob.
  // 3° keeps the aspects that actually carry weight; the rest stay listed
  // below the wheel. Minors are exempt: their orb is 1° at most already.
  const visibleAspects = useMemo(
    () => aspects.filter(a =>
      (MINOR_ASPECT_TYPES.has(a.type) || a.orb < 3)
      && planetByName.has(a.planet1.toLowerCase()) && planetByName.has(a.planet2.toLowerCase())),
    [aspects, planetByName],
  );

  const degreeTicks = useMemo(() => Array.from({ length: 36 }, (_, i) => i * 10), []);

  // AC/DC come straight from the rotation, MC/IC from the actual Midheaven —
  // not from house cusps 10/4, which only coincide with it in the quadrant
  // systems. In Equal houses cusp 10 is just the Ascendant + 270°.
  const axes = useMemo(() => {
    const list = [{ label: "AC", deg: 0 }, { label: "DC", deg: 180 }];
    if (midheaven !== undefined) {
      list.push({ label: "MC", deg: rot(midheaven) }, { label: "IC", deg: rot(midheaven) + 180 });
    }
    return list;
  }, [midheaven, ascendant]);

  const hoveredPlanet = hovered !== null ? positionedPlanets[hovered] : null;
  const hoveredPos = hoveredPlanet ? degToXY(rot(hoveredPlanet.degree), hoveredPlanet.radius, cx, cy) : null;
  const hoveredHouse = hoveredPlanet ? findHouseForDegree(hoveredPlanet.degree, houses) : null;

  return (
    <div style={{ position: "relative", width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ overflow: "visible" }}>
        {/* Layer 1 — zodiac belt */}
        <g>
          {ZODIAC_SYMBOLS.map((symbol, i) => {
            const start = rot(i * 30);
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
            const outer = degToXY(rot(h.degree), R_house, cx, cy);
            const inner = degToXY(rot(h.degree), R_inner, cx, cy);
            const next = sortedHouses[(i + 1) % sortedHouses.length];
            const mid = houseMidAngle(h.degree, next.degree);
            const labelPos = degToXY(rot(mid), (R_house + R_inner) / 2, cx, cy);
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
            const pos1 = degToXY(rot(p1.degree), R_inner * 0.95, cx, cy);
            const pos2 = degToXY(rot(p2.degree), R_inner * 0.95, cx, cy);
            const style = ASPECT_STYLE[a.type] ?? ASPECT_STYLE.conjunction;
            return (
              <line key={`aspect-${i}`} x1={pos1.x} y1={pos1.y} x2={pos2.x} y2={pos2.y}
                stroke={style.color} strokeWidth={style.width} strokeDasharray={style.dash} />
            );
          })}
        </g>

        {/* Layer 4 — planets */}
        <g>
          {positionedPlanets.map((p, i) => {
            const pos = degToXY(rot(p.degree), p.radius, cx, cy);
            const houseEdge = degToXY(rot(p.degree), R_house, cx, cy);
            const outerEdge = degToXY(rot(p.degree), R_outer, cx, cy);
            const key = p.name.toLowerCase();
            const color = PLANET_COLORS[key] ?? "#C9A84C";
            const symbol = PLANET_SYMBOLS[key] ?? p.name.slice(0, 2);
            return (
              <g key={`planet-${i}`}
                style={{ animation: `mystral-fadeup .6s ease-out ${i * 0.05}s both`, cursor: "pointer" }}
                onMouseEnter={() => setHovered(i)}
                onMouseLeave={() => setHovered(null)}>
                <line x1={pos.x} y1={pos.y} x2={houseEdge.x} y2={houseEdge.y} stroke="rgba(255,255,255,.1)" />
                {p.collided && (
                  <line x1={pos.x} y1={pos.y} x2={outerEdge.x} y2={outerEdge.y} stroke="#827A69" strokeWidth={0.5} />
                )}
                <circle cx={pos.x} cy={pos.y} r={size * 0.022} fill="rgba(7,6,15,.9)" stroke={color} />
                <text x={pos.x} y={pos.y} fontSize={size * 0.028} fill={color}
                  textAnchor="middle" dominantBaseline="central">{symbol}</text>
                {p.retrograde && (
                  <text x={pos.x + size * 0.02} y={pos.y - size * 0.02} fontSize={size * 0.016}
                    fill="#A89E8B">℞</text>
                )}
              </g>
            );
          })}
        </g>

        {/* Layer 5 — degree ticks */}
        <g>
          {degreeTicks.map(deg => {
            const outer = degToXY(rot(deg), R_outer, cx, cy);
            const tickInner = degToXY(rot(deg), R_outer - size * 0.015, cx, cy);
            const labelPos = degToXY(rot(deg), R_outer - size * 0.045, cx, cy);
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

        {/* Layer 6 — AC / DC / MC / IC axis labels */}
        <g>
          {/* Labelled inside the empty ring between the house ring and the
              zodiac belt. Outside the rim would match the reference drawings
              more closely, but the wheel is sized to the viewport width on
              mobile, so anything past R_outer gets clipped at the screen edge. */}
          {axes.map(({ label, deg }) => {
            const inner = degToXY(deg, R_house, cx, cy);
            const outer = degToXY(deg, R_sign, cx, cy);
            const labelPos = degToXY(deg, (R_house + R_sign) / 2, cx, cy);
            const primary = label === "AC" || label === "MC";
            return (
              <g key={`axis-${label}`}>
                <line x1={inner.x} y1={inner.y} x2={outer.x} y2={outer.y}
                  stroke="rgba(201,168,76,.55)" strokeWidth={primary ? 1.4 : 0.8} />
                <circle cx={labelPos.x} cy={labelPos.y} r={size * 0.026} fill="rgba(7,6,15,.92)" />
                <text x={labelPos.x} y={labelPos.y} fontSize={size * 0.024}
                  fill={primary ? "#E8CD7E" : "rgba(201,168,76,.65)"}
                  fontFamily="Inter" textAnchor="middle" dominantBaseline="central">{label}</text>
              </g>
            );
          })}
        </g>

        {/* Layer 7 — center circle */}
        <circle cx={cx} cy={cy} r={R_center} fill="rgba(201,168,76,.08)" stroke="rgba(201,168,76,.2)" />
      </svg>

      {hoveredPlanet && hoveredPos && (
        <div style={{
          position: "absolute", left: hoveredPos.x, top: hoveredPos.y, transform: "translate(-50%, -140%)",
          background: "rgba(7,6,15,.95)", border: "1px solid rgba(201,168,76,.3)",
          borderRadius: 10, padding: "8px 12px", fontSize: 12, color: "#F0E9DA",
          whiteSpace: "nowrap", pointerEvents: "none", zIndex: 10,
        }}>
          {/* Symbolic rather than worded: this component is shared by all six
              languages and used to hardcode Russian "в"/"дом" in every one. */}
          {hoveredPlanet.label ?? hoveredPlanet.name} · {hoveredPlanet.sign} {Math.round((hoveredPlanet.degree % 30) * 10) / 10}°
          {" · H"}{hoveredHouse ?? "?"}{hoveredPlanet.retrograde ? " ℞" : ""}
        </div>
      )}
    </div>
  );
}
