/**
 * Line-art emblems for the 22 Major Arcana, drawn to sit on the landing's
 * card faces.
 *
 * `data/tarot.ts` carries a `symbol` per card, but those are emoji (🃏 ⚡ 🌙
 * 🌩 📯 🌍) — they render as full-colour platform artwork, which is exactly
 * what a hand-illustrated deck must not look like. These share one 32x32
 * grid and one stroke weight so a card face looks drawn rather than
 * assembled from whatever glyphs the OS provides.
 */

export interface ArcanaEmblemProps {
  size?: number;
  strokeWidth?: number;
  style?: React.CSSProperties;
}

function E({ size = 64, strokeWidth = 1, style, children }: ArcanaEmblemProps & { children: React.ReactNode }) {
  return (
    <svg
      width={size} height={size} viewBox="0 0 32 32" fill="none"
      stroke="currentColor" strokeWidth={strokeWidth}
      strokeLinecap="round" strokeLinejoin="round"
      style={style} aria-hidden focusable="false"
    >
      {children}
    </svg>
  );
}

/** Indexed by Major Arcana number (0–21), matching MAJOR_ARCANA[].id. */
export const ARCANA_EMBLEMS: Array<(p: ArcanaEmblemProps) => JSX.Element> = [
  // 0 — The Fool: a traveller's staff and bundle stepping off the edge.
  p => (<E {...p}>
    <path d="M9 27L20 8" />
    <path d="M20 8l3.6-2.4" />
    <path d="M23.6 5.6c2.4.6 3.6 2.4 3 4.4-.6 2-2.8 2.8-4.6 1.8" />
    <circle cx="7.4" cy="27.6" r="1.4" />
  </E>),
  // 1 — The Magician: lemniscate over an upright wand.
  p => (<E {...p}>
    <path d="M16 12c2-2.6 5.6-2.6 6.8 0 1.2 2.6-1.4 4.6-3.4 3.2-2-1.4-1.4-4.4-3.4-3.2z" />
    <path d="M16 12c-2-2.6-5.6-2.6-6.8 0-1.2 2.6 1.4 4.6 3.4 3.2 2-1.4 1.4-4.4 3.4-3.2z" />
    <path d="M16 17.4V27M12.4 27h7.2" />
  </E>),
  // 2 — High Priestess: crescent between the two temple pillars.
  p => (<E {...p}>
    <path d="M8 6v20M24 6v20" />
    <path d="M20.4 15.6a5.4 5.4 0 1 1-6.6-6.6 4.3 4.3 0 0 0 6.6 6.6z" />
  </E>),
  // 3 — The Empress: the sign of Venus.
  p => (<E {...p}>
    <circle cx="16" cy="12" r="6" />
    <path d="M16 18v9M12.2 23h7.6" />
  </E>),
  // 4 — The Emperor: the sign of Mars.
  p => (<E {...p}>
    <circle cx="13.4" cy="18.6" r="6" />
    <path d="M17.8 14.2L26 6M20.4 6H26v5.6" />
  </E>),
  // 5 — The Hierophant: the triple cross.
  p => (<E {...p}>
    <path d="M16 4v24" />
    <path d="M10 10h12M11.6 16h8.8M13.2 22h5.6" />
  </E>),
  // 6 — The Lovers: two rings bound together.
  p => (<E {...p}>
    <circle cx="12.4" cy="16" r="6.4" />
    <circle cx="19.6" cy="16" r="6.4" />
  </E>),
  // 7 — The Chariot: canopy and two wheels.
  p => (<E {...p}>
    <path d="M7 12h18l-2 8H9z" />
    <path d="M9 12l3-5h8l3 5" />
    <circle cx="11.4" cy="24" r="2.6" />
    <circle cx="20.6" cy="24" r="2.6" />
  </E>),
  // 8 — Strength: lemniscate above a steady arc.
  p => (<E {...p}>
    <path d="M16 11c2.2-3 6.2-3 7.6 0 1.4 3-1.6 5.2-3.8 3.6C17.6 13 18.2 8 16 11z" />
    <path d="M16 11c-2.2-3-6.2-3-7.6 0-1.4 3 1.6 5.2 3.8 3.6C14.4 13 13.8 8 16 11z" />
    <path d="M7.6 22c4.8 4.2 12 4.2 16.8 0" />
  </E>),
  // 9 — The Hermit: the raised lantern.
  p => (<E {...p}>
    <path d="M11 12h10l1.6 12H9.4z" />
    <path d="M13 12V9.4a3 3 0 0 1 6 0V12" />
    <path d="M16 15.4v5.2M13.6 18h4.8" />
  </E>),
  // 10 — Wheel of Fortune: the eight-spoked wheel.
  p => (<E {...p}>
    <circle cx="16" cy="16" r="11" />
    <circle cx="16" cy="16" r="3.4" />
    <path d="M16 5v7.6M16 19.4V27M5 16h7.6M19.4 16H27" />
    <path d="M8.2 8.2l5.4 5.4M18.4 18.4l5.4 5.4M23.8 8.2l-5.4 5.4M13.6 18.4l-5.4 5.4" />
  </E>),
  // 11 — Justice: the balanced scales.
  p => (<E {...p}>
    <path d="M16 6v21M10 27h12" />
    <path d="M7 11h18" />
    <path d="M7 11l-3 6a3.4 3.4 0 0 0 6 0z" />
    <path d="M25 11l3 6a3.4 3.4 0 0 1-6 0z" />
  </E>),
  // 12 — The Hanged Man: suspended, inverted.
  p => (<E {...p}>
    <path d="M6 6h20M16 6v7" />
    <circle cx="16" cy="16" r="3" />
    <path d="M16 19v4l-4.6 4M16 23l4.6 4" />
  </E>),
  // 13 — Death: the scythe.
  p => (<E {...p}>
    <path d="M22 27L11 9" />
    <path d="M11 9C6 10 3.6 14.6 5 19c3.4-4.8 9-6.4 14-4" />
  </E>),
  // 14 — Temperance: fire and water, interlocked.
  p => (<E {...p}>
    <path d="M16 5l8.6 14.8H7.4z" />
    <path d="M16 27L7.4 12.2h17.2z" />
  </E>),
  // 15 — The Devil: the inverted pentagram.
  p => (<E {...p}>
    <path d="M16 28L5.6 10.4h20.8z" />
    <path d="M5.6 10.4l20.8 8.4M26.4 10.4L5.6 18.8M16 28V6.6" />
  </E>),
  // 16 — The Tower: struck by lightning.
  p => (<E {...p}>
    <path d="M9.4 28V13l6.6-5 6.6 5v15z" />
    <path d="M17.6 12.4L13 19h5l-3.4 6.4" />
  </E>),
  // 17 — The Star: the eight-pointed star over water.
  p => (<E {...p}>
    <path d="M16 3.6l2.8 8.4 8.4 2.8-8.4 2.8L16 26l-2.8-8.4-8.4-2.8 8.4-2.8z" />
    <path d="M6 28.4c2.6-1.6 5.2-1.6 7.8 0M18.2 28.4c2.6-1.6 5.2-1.6 7.8 0" />
  </E>),
  // 18 — The Moon: crescent with falling dew.
  p => (<E {...p}>
    <path d="M22.6 16.4A8.6 8.6 0 1 1 12.2 5.8a6.8 6.8 0 0 0 10.4 10.6z" />
    <path d="M10 24.6v1.8M16 26v1.8M22 24.6v1.8" />
  </E>),
  // 19 — The Sun: rayed disc.
  p => (<E {...p}>
    <circle cx="16" cy="16" r="6" />
    <path d="M16 4v3.6M16 24.4V28M4 16h3.6M24.4 16H28" />
    <path d="M7.6 7.6l2.6 2.6M21.8 21.8l2.6 2.6M24.4 7.6l-2.6 2.6M10.2 21.8l-2.6 2.6" />
  </E>),
  // 20 — Judgement: the trumpet's call.
  p => (<E {...p}>
    <path d="M5.4 19.6l16-8.4v10.6z" />
    <path d="M21.4 12.4l5.2-2.6v13l-5.2-2.6" />
    <path d="M9.6 21.2l1.4 5.4" />
  </E>),
  // 21 — The World: the closing wreath.
  p => (<E {...p}>
    <ellipse cx="16" cy="16" rx="7.4" ry="11" />
    <path d="M16 5c-3 2.6-3 19.4 0 22M16 5c3 2.6 3 19.4 0 22" />
    <path d="M8.6 16h14.8" />
  </E>),
];

/** Ornamental card back — a rayed circle inside a double gold frame. */
export function CardBack({ width = 132, height = 200 }: { width?: number; height?: number }) {
  return (
    <svg width={width} height={height} viewBox="0 0 132 200" fill="none" aria-hidden focusable="false">
      <defs>
        <linearGradient id="cb-face" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#171041" />
          <stop offset="0.55" stopColor="#0E0A26" />
          <stop offset="1" stopColor="#1A1246" />
        </linearGradient>
        <linearGradient id="cb-gold" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#8A6E2E" />
          <stop offset="0.5" stopColor="#E8CD7E" />
          <stop offset="1" stopColor="#A9882F" />
        </linearGradient>
      </defs>
      <rect x="1" y="1" width="130" height="198" rx="11" fill="url(#cb-face)" stroke="url(#cb-gold)" strokeWidth="1.6" />
      <rect x="8" y="8" width="116" height="184" rx="7" fill="none" stroke="rgba(201,168,76,.34)" strokeWidth="0.8" />
      <g stroke="url(#cb-gold)" fill="none" strokeLinecap="round">
        <circle cx="66" cy="100" r="30" strokeWidth="1.1" />
        <circle cx="66" cy="100" r="20" strokeWidth="0.7" opacity=".7" />
        <circle cx="66" cy="100" r="6.5" strokeWidth="1.1" />
        {Array.from({ length: 12 }, (_, i) => {
          const a = (i * 30 * Math.PI) / 180;
          return (
            <line key={i}
              x1={66 + Math.cos(a) * 20} y1={100 + Math.sin(a) * 20}
              x2={66 + Math.cos(a) * 30} y2={100 + Math.sin(a) * 30}
              strokeWidth={i % 3 === 0 ? 1.1 : 0.6} opacity={i % 3 === 0 ? 0.95 : 0.5} />
          );
        })}
        {[[66, 26], [66, 174]].map(([cx, cy], i) => (
          <path key={i} d={`M${cx - 7} ${cy} l7 -6 l7 6 l-7 6 z`} strokeWidth="0.8" opacity=".75" />
        ))}
      </g>
    </svg>
  );
}
