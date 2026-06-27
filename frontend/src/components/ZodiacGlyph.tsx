import { useMemo } from "react";

interface ZodiacGlyphProps {
  sign: string;
  size?: number;
}

interface ConstellationData {
  points: [number, number][];
  lines: [number, number][];
  bright: number[];
}

const CONSTELLATIONS: Record<string, ConstellationData> = {
  aries: {
    points: [[30,65],[42,52],[55,28],[80,48]],
    lines: [[0,1],[1,2],[2,3]],
    bright: [2],
  },
  taurus: {
    points: [[18,22],[44,35],[48,50],[52,60],[38,42],[82,15],[56,52]],
    lines: [[0,4],[4,1],[1,2],[2,3],[3,6],[4,5]],
    bright: [3,5],
  },
  gemini: {
    points: [[20,80],[28,68],[38,75],[42,52],[56,58],[58,35],[68,18],[78,25]],
    lines: [[0,3],[3,5],[5,6],[2,4],[4,5],[5,7]],
    bright: [6,7],
  },
  cancer: {
    points: [[28,68],[50,50],[46,32],[74,60]],
    lines: [[0,1],[1,2],[1,3]],
    bright: [0],
  },
  leo: {
    points: [[28,22],[30,32],[36,40],[42,48],[45,68],[38,55],[62,38],[68,50],[82,30]],
    lines: [[0,1],[1,2],[2,3],[3,5],[5,4],[3,6],[6,7],[7,8]],
    bright: [4,8],
  },
  virgo: {
    points: [[22,30],[34,40],[45,52],[52,78],[58,42],[65,28]],
    lines: [[0,1],[1,2],[2,3],[2,4],[4,5]],
    bright: [3],
  },
  libra: {
    points: [[30,62],[45,35],[65,40],[38,72],[62,70]],
    lines: [[0,1],[1,2],[0,3],[3,4],[4,2]],
    bright: [1],
  },
  scorpio: {
    points: [[28,22],[35,28],[42,35],[48,42],[52,50],[56,58],[54,66],[48,74],[42,80],[36,82],[30,78],[26,72]],
    lines: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,8],[8,9],[9,10],[10,11]],
    bright: [3,11],
  },
  sagittarius: {
    points: [[28,30],[35,48],[30,60],[50,30],[62,26],[72,38],[68,54],[55,58],[22,65]],
    lines: [[0,1],[1,2],[2,8],[0,3],[3,4],[4,5],[5,6],[6,7],[7,2],[1,7]],
    bright: [2,4],
  },
  capricorn: {
    points: [[20,42],[28,48],[38,68],[48,72],[60,65],[68,45],[75,40],[55,40]],
    lines: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,0]],
    bright: [6],
  },
  aquarius: {
    points: [[22,30],[38,25],[52,30],[60,40],[75,55],[46,48],[52,55],[46,38]],
    lines: [[0,1],[1,7],[7,2],[2,3],[1,5],[5,6],[6,4],[3,4]],
    bright: [1,2],
  },
  pisces: {
    points: [[20,35],[22,22],[30,18],[38,25],[30,40],[22,45],[52,58],[55,40],[65,22],[75,32],[78,45],[70,52],[60,50]],
    lines: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,0],[5,6],[6,7],[7,8],[8,9],[9,10],[10,11],[11,12],[12,6]],
    bright: [3,6,9],
  },
};

const NAME_MAP: Record<string, string> = {
  "овен": "aries", "телец": "taurus", "близнецы": "gemini", "рак": "cancer",
  "лев": "leo", "дева": "virgo", "весы": "libra", "скорпион": "scorpio",
  "стрелец": "sagittarius", "козерог": "capricorn", "водолей": "aquarius", "рыбы": "pisces",
};

function resolveKey(sign: string): string {
  const s = sign.toLowerCase().trim();
  return CONSTELLATIONS[s] ? s : NAME_MAP[s] ?? "leo";
}

export function ZodiacGlyph({ sign, size = 236 }: ZodiacGlyphProps) {
  const key = resolveKey(sign);
  const c = CONSTELLATIONS[key] ?? CONSTELLATIONS.leo;

  const stars = useMemo(() => {
    const arr: { x: number; y: number; sz: number; delay: number; opacity: number }[] = [];
    for (let i = 0; i < 46; i++) {
      const angle = Math.random() * Math.PI * 2;
      const r = 42 + Math.random() * 108;
      arr.push({
        x: 50 + Math.cos(angle) * r / 3.2,
        y: 50 + Math.sin(angle) * r / 3.2,
        sz: Math.random() * 2.2 + 0.6,
        delay: Math.random() * 4,
        opacity: Math.random() * 0.6 + 0.3,
      });
    }
    return arr;
  }, [key]);

  return (
    <div style={{ position: "relative", width: size, height: size, margin: "0 auto" }}>

      {/* Layer 1 — rings */}
      <div style={{ position: "absolute", inset: 0, animation: "mystral-spin 90s linear infinite" }}>
        <svg viewBox="0 0 100 100" width={size} height={size} fill="none">
          <circle cx="50" cy="50" r="47" stroke="rgba(201,168,76,.16)" strokeWidth=".5" strokeDasharray="1 6" />
          <circle cx="50" cy="50" r="40" stroke="rgba(201,168,76,.1)" strokeWidth=".5" />
        </svg>
      </div>
      <div style={{ position: "absolute", inset: 0, animation: "mystral-spin-rev 120s linear infinite" }}>
        <svg viewBox="0 0 100 100" width={size} height={size} fill="none">
          <circle cx="50" cy="50" r="33" stroke="rgba(138,127,192,.18)" strokeWidth=".5" strokeDasharray="2 5" />
        </svg>
      </div>

      {/* Layer 2 — star particles */}
      {stars.map((s, i) => (
        <span key={i} style={{
          position: "absolute",
          left: `${s.x}%`, top: `${s.y}%`,
          width: s.sz, height: s.sz,
          borderRadius: "50%",
          background: "#F0E9DA",
          boxShadow: "0 0 6px rgba(240,233,218,.8)",
          opacity: s.opacity,
          animation: `mystral-twinkle ${2.5 + s.delay}s ease-in-out infinite ${s.delay}s`,
        }} />
      ))}

      {/* Layer 3 — center glow */}
      <div style={{
        position: "absolute", inset: "18%", borderRadius: "50%",
        background: "radial-gradient(circle, rgba(201,168,76,.22), transparent 68%)",
      }} />

      {/* Layer 4 — constellation */}
      <div style={{ position: "absolute", inset: 0, animation: "mystral-float 7s ease-in-out infinite" }}>
        <svg viewBox="0 0 100 100" width={size} height={size} fill="none"
          style={{ filter: "drop-shadow(0 0 5px rgba(240,214,128,.6))" }}>
          {c.lines.map(([a, b], i) => (
            <line key={`l${i}`} x1={c.points[a][0]} y1={c.points[a][1]} x2={c.points[b][0]} y2={c.points[b][1]}
              stroke="rgba(201,168,76,.5)" strokeWidth="1" />
          ))}
          {c.points.map((p, i) => {
            const isBright = c.bright.includes(i);
            return (
              <g key={`p${i}`}>
                <circle cx={p[0]} cy={p[1]} r={isBright ? 7 : 5} fill="none" stroke="rgba(240,214,128,.25)" strokeWidth={isBright ? 1.2 : .8} opacity={isBright ? .3 : .2} />
                <circle cx={p[0]} cy={p[1]} r={isBright ? 2.8 : 1.6} fill="#F0D680" />
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
