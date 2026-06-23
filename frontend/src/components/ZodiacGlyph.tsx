import { useMemo } from "react";

interface ZodiacGlyphProps {
  sign: string;
  size?: number;
}

const CONSTELLATIONS: Record<string, [number, number][]> = {
  aries:       [[38,62],[46,50],[52,38],[60,30],[68,38],[72,50],[65,42],[58,52]],
  taurus:      [[22,58],[32,46],[44,38],[56,38],[66,46],[72,58],[56,52],[44,52],[50,44],[50,62]],
  gemini:      [[28,22],[28,38],[30,52],[28,68],[28,78],[72,22],[72,38],[70,52],[72,68],[72,78]],
  cancer:      [[30,42],[40,30],[54,36],[64,48],[60,62],[46,68],[38,60],[32,66]],
  leo:         [[18,30],[30,24],[44,30],[58,42],[70,40],[82,52],[74,68],[58,72],[50,60],[38,52],[26,46]],
  virgo:       [[36,18],[40,30],[46,44],[40,56],[46,68],[56,74],[64,64],[68,52],[64,40],[56,28],[62,20]],
  libra:       [[22,54],[36,38],[50,28],[64,38],[78,54],[28,68],[72,68],[50,54]],
  scorpio:     [[20,30],[32,24],[46,28],[58,36],[68,40],[78,34],[84,46],[78,56],[72,66],[66,76],[60,82]],
  sagittarius: [[26,72],[38,58],[52,42],[64,30],[50,44],[66,52],[76,44],[64,30],[48,62],[36,68]],
  capricorn:   [[28,34],[38,24],[52,28],[64,36],[68,50],[62,64],[50,70],[38,66],[34,76],[50,80]],
  aquarius:    [[18,46],[32,34],[50,46],[68,34],[82,46],[22,62],[36,52],[54,62],[70,52],[82,62]],
  pisces:      [[28,26],[38,36],[34,50],[40,64],[28,74],[72,26],[62,36],[66,50],[60,64],[72,74],[50,50]],
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
  const pts = CONSTELLATIONS[key] ?? CONSTELLATIONS.leo;

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
          {pts.slice(1).map((p, i) => (
            <line key={`l${i}`} x1={pts[i][0]} y1={pts[i][1]} x2={p[0]} y2={p[1]}
              stroke="rgba(201,168,76,.5)" strokeWidth="1" />
          ))}
          {pts.map((p, i) => (
            <g key={`p${i}`}>
              <circle cx={p[0]} cy={p[1]} r={i === 0 || i === 5 ? 2.6 : 1.7} fill="#F0D680" />
              <circle cx={p[0]} cy={p[1]} r={5} fill="none" stroke="rgba(240,214,128,.25)" strokeWidth="1" />
            </g>
          ))}
        </svg>
      </div>
    </div>
  );
}
