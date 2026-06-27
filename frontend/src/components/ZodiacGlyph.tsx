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
    points: [[28,48],[45,38],[68,30]],
    lines: [[0,1],[1,2]],
    bright: [2],
  },
  taurus: {
    points: [[22,20],[40,45],[28,58],[22,52],[50,58],[52,72],[60,40]],
    lines: [[0,1],[1,2],[2,3],[1,4],[4,5],[3,5],[0,6]],
    bright: [0,5],
  },
  gemini: {
    points: [[42,16],[60,18],[38,30],[34,48],[28,65],[64,30],[70,48],[72,65]],
    lines: [[0,1],[0,2],[2,3],[3,4],[1,5],[5,6],[6,7]],
    bright: [0,1],
  },
  cancer: {
    points: [[48,18],[48,38],[54,52],[72,60],[28,72],[50,72]],
    lines: [[0,1],[1,2],[2,3],[2,5],[5,4]],
    bright: [4],
  },
  leo: {
    points: [[78,18],[72,22],[65,32],[60,44],[55,58],[45,70],[58,52],[42,42],[22,38]],
    lines: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,8]],
    bright: [3,5,8],
  },
  virgo: {
    points: [[68,18],[62,32],[48,48],[30,42],[22,28],[32,68],[62,62],[75,72]],
    lines: [[0,1],[1,2],[2,3],[3,4],[3,5],[2,6],[6,7]],
    bright: [2,5],
  },
  libra: {
    points: [[35,28],[62,20],[45,62],[68,55],[20,55]],
    lines: [[0,1],[1,3],[0,4],[0,2],[2,3]],
    bright: [0,2],
  },
  scorpio: {
    points: [[28,22],[42,20],[58,22],[45,32],[35,42],[28,52],[22,62],[20,72],[22,80],[30,86],[40,88],[50,84],[58,78],[65,72],[70,68]],
    lines: [[0,1],[1,2],[1,3],[3,4],[4,5],[5,6],[6,7],[7,8],[8,9],[9,10],[10,11],[11,12],[12,13],[13,14]],
    bright: [4,13],
  },
  sagittarius: {
    points: [[22,50],[28,35],[35,28],[45,35],[32,55],[45,58],[60,52],[68,40],[22,58]],
    lines: [[8,0],[0,4],[4,5],[5,6],[6,7],[0,1],[1,2],[2,3],[3,7],[1,4]],
    bright: [2,4,6],
  },
  capricorn: {
    points: [[25,32],[58,22],[22,55],[45,50],[72,42],[42,68]],
    lines: [[0,1],[1,4],[4,5],[5,2],[2,0],[0,3],[3,4],[2,3]],
    bright: [1,4],
  },
  aquarius: {
    points: [[30,28],[48,22],[65,32],[58,42],[72,55],[42,50],[38,65],[28,58]],
    lines: [[0,1],[1,2],[2,3],[3,4],[3,5],[5,6],[5,7],[1,5]],
    bright: [1,2],
  },
  pisces: {
    points: [[22,62],[15,52],[18,42],[26,36],[34,42],[30,55],[44,58],[55,42],[65,28],[75,25],[80,35],[78,45],[68,52],[56,55]],
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

      {stars.map((s, i) => (
        <span key={i} style={{
          position: "absolute", left: `${s.x}%`, top: `${s.y}%`,
          width: s.sz, height: s.sz, borderRadius: "50%",
          background: "#F0E9DA", boxShadow: "0 0 6px rgba(240,233,218,.8)",
          opacity: s.opacity, animation: `mystral-twinkle ${2.5 + s.delay}s ease-in-out infinite ${s.delay}s`,
        }} />
      ))}

      <div style={{ position: "absolute", inset: "18%", borderRadius: "50%", background: "radial-gradient(circle, rgba(201,168,76,.22), transparent 68%)" }} />

      <div style={{ position: "absolute", inset: 0, animation: "mystral-float 7s ease-in-out infinite" }}>
        <svg viewBox="0 0 100 100" width={size} height={size} fill="none"
          style={{ filter: "drop-shadow(0 0 5px rgba(240,214,128,.6))" }}>
          {c.lines.map(([a, b], i) => (
            <line key={`l${i}`} x1={c.points[a][0]} y1={c.points[a][1]} x2={c.points[b][0]} y2={c.points[b][1]}
              stroke="rgba(201,168,76,.5)" strokeWidth="1" />
          ))}
          {c.points.map((p, i) => {
            const bright = c.bright.includes(i);
            return (
              <g key={`p${i}`}>
                <circle cx={p[0]} cy={p[1]} r={bright ? 8 : 5} fill="none" stroke="rgba(240,214,128,.25)" strokeWidth={bright ? 1.2 : .8} opacity={bright ? .28 : .15} />
                <circle cx={p[0]} cy={p[1]} r={bright ? 2.8 : 1.6} fill="#F0D680" />
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
