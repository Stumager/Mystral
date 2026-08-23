export type MatrixPointPos =
  | "left" | "top" | "right" | "bottom" | "centre"
  | "top-left" | "top-right" | "bottom-right" | "bottom-left";

export type MatrixPoint = {
  id: string;
  pos: MatrixPointPos;
  square: "personal" | "ancestral";
  // TZ-119: Children's Matrix free tier sends locked points with arcana:
  // null instead of omitting them, so the octagram still draws all nine
  // positions — just with a lock glyph instead of a number.
  arcana: number | null;
  arcana_name: string | null;
  // Not every module has light/shadow keywords (money line/karmic tail
  // don't) — optional rather than dropped, since the octagram itself
  // never reads these fields anyway (only the detail card below it does).
  light?: string;
  shadow?: string;
  locked?: boolean;
};

type Props = {
  points: MatrixPoint[];
  selected: string | null;
  onSelect: (id: string) => void;
  size?: number;
};

const VIEW = 320;
const C = VIEW / 2;
const R = 116;
// Both squares are inscribed in the same circle, one rotated 45° against the
// other — that's what makes the outline a regular eight-pointed star rather
// than two squares that happen to overlap.
const D = R / Math.SQRT2;

const COORDS: Record<MatrixPointPos, [number, number]> = {
  left:           [C - R, C],
  top:            [C, C - R],
  right:          [C + R, C],
  bottom:         [C, C + R],
  centre:         [C, C],
  "top-left":     [C - D, C - D],
  "top-right":    [C + D, C - D],
  "bottom-right": [C + D, C + D],
  "bottom-left":  [C - D, C + D],
};

const GOLD = "#C9A84C";
const GOLD_LIGHT = "#E8CD7E";
const INDIGO = "#8A7FC0";

const poly = (positions: MatrixPointPos[]) =>
  positions.map(p => COORDS[p].join(",")).join(" ");

export function DestinyOctagram({ points, selected, onSelect, size = 320 }: Props) {
  const byPos = new Map(points.map(p => [p.pos, p]));

  return (
    <svg
      viewBox={`0 0 ${VIEW} ${VIEW}`}
      width={size}
      height={size}
      style={{ maxWidth: "100%", height: "auto", display: "block", margin: "0 auto", overflow: "visible" }}
      role="img"
      aria-label="Octagram"
    >
      <defs>
        <radialGradient id="mx-core" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="rgba(201,168,76,.30)" />
          <stop offset="100%" stopColor="rgba(201,168,76,0)" />
        </radialGradient>
      </defs>

      <circle cx={C} cy={C} r={R} fill="none" stroke="rgba(201,168,76,.10)" strokeWidth="1" />
      <circle cx={C} cy={C} r={R * 0.62} fill="url(#mx-core)" />

      {/* Ancestral square sits underneath — it's the inherited layer the
          personal square is drawn over, which is also how the method itself
          describes the two. */}
      <polygon
        points={poly(["top-left", "top-right", "bottom-right", "bottom-left"])}
        fill="rgba(75,60,134,.10)" stroke="rgba(138,127,192,.42)" strokeWidth="1.1"
      />
      <polygon
        points={poly(["left", "top", "right", "bottom"])}
        fill="rgba(201,168,76,.05)" stroke="rgba(201,168,76,.5)" strokeWidth="1.1"
      />

      {(Object.keys(COORDS) as MatrixPointPos[])
        .filter(pos => pos !== "centre")
        .map(pos => (
          <line
            key={`spoke-${pos}`}
            x1={C} y1={C} x2={COORDS[pos][0]} y2={COORDS[pos][1]}
            stroke="rgba(201,168,76,.10)" strokeWidth="1"
          />
        ))}

      {(Object.keys(COORDS) as MatrixPointPos[]).map(pos => {
        const p = byPos.get(pos);
        if (!p) return null;
        const [x, y] = COORDS[pos];
        const isCentre = pos === "centre";
        const isSel = selected === p.id;
        const accent = p.square === "personal" ? GOLD : INDIGO;
        const r = isCentre ? 25 : 20;

        const isLocked = p.arcana === null;

        return (
          <g
            key={p.id}
            onClick={() => onSelect(p.id)}
            style={{ cursor: "pointer" }}
            role="button"
            tabIndex={0}
            aria-label={isLocked ? "Pro" : `${p.arcana_name} — ${p.arcana}`}
            onKeyDown={e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onSelect(p.id); } }}
          >
            {isSel && <circle cx={x} cy={y} r={r + 6} fill="none" stroke={accent} strokeWidth="1" opacity=".45" />}
            <circle
              cx={x} cy={y} r={r}
              fill={isCentre ? "rgba(201,168,76,.16)" : "rgba(7,6,15,.92)"}
              stroke={isSel ? GOLD_LIGHT : accent}
              strokeWidth={isSel ? 2 : 1.3}
              opacity={isLocked ? 0.45 : 1}
            />
            <text
              x={x} y={y} textAnchor="middle" dominantBaseline="central"
              className="font-cinzel"
              style={{
                fontSize: isLocked ? 13 : isCentre ? 20 : 17,
                fill: isLocked ? "#8A8170" : isSel ? GOLD_LIGHT : isCentre ? GOLD_LIGHT : "#EDE7DA",
                letterSpacing: ".02em",
                userSelect: "none",
              }}
            >
              {isLocked ? "🔒" : p.arcana}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
