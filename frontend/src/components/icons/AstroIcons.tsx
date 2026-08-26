/**
 * Hand-drawn SVG glyph set for the marketing landing.
 *
 * Everything here is stroke-based line art on a 24x24 grid using
 * `currentColor`, deliberately replacing the text symbols used elsewhere in
 * the app (♈, ☉, 🃏). Those code points are rendered by whatever symbol font
 * the device happens to ship, so they arrive at different weights per
 * platform and several of them (🃏 🌙 ⚡ ⭐) render as full-colour emoji on
 * iOS/Android — which reads as clip-art next to the gold-on-ink palette.
 * Drawn paths keep one stroke weight across every platform and inherit the
 * surrounding colour.
 */

interface GlyphProps {
  size?: number;
  strokeWidth?: number;
  className?: string;
  style?: React.CSSProperties;
}

function Glyph({ size = 24, strokeWidth = 1.5, className, style, children }: GlyphProps & { children: React.ReactNode }) {
  return (
    <svg
      width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={strokeWidth}
      strokeLinecap="round" strokeLinejoin="round"
      className={className} style={style} aria-hidden focusable="false"
    >
      {children}
    </svg>
  );
}

// ── Zodiac ────────────────────────────────────────────────────────────────

export const ZODIAC_GLYPHS: Record<string, (p: GlyphProps) => JSX.Element> = {
  aries: p => (
    <Glyph {...p}>
      <path d="M12 20V11" />
      <path d="M12 11c0-4.5-2.2-6.5-4.4-6.5S4 6.2 4 8.2c0 1.6.8 2.8 1.8 3.4" />
      <path d="M12 11c0-4.5 2.2-6.5 4.4-6.5S20 6.2 20 8.2c0 1.6-.8 2.8-1.8 3.4" />
    </Glyph>
  ),
  taurus: p => (
    <Glyph {...p}>
      <circle cx="12" cy="15.2" r="5" />
      <path d="M6.2 4.4a6.6 6.6 0 0 0 11.6 0" />
    </Glyph>
  ),
  gemini: p => (
    <Glyph {...p}>
      <path d="M7.5 4.8v14.4M16.5 4.8v14.4" />
      <path d="M4.8 4.2c2.6-1.2 11.8-1.2 14.4 0" />
      <path d="M4.8 19.8c2.6 1.2 11.8 1.2 14.4 0" />
    </Glyph>
  ),
  cancer: p => (
    <Glyph {...p}>
      <path d="M4 11c0-3.4 3.8-5.2 8-5.2 3 0 5.6.9 7 2.3" />
      <path d="M20 13c0 3.4-3.8 5.2-8 5.2-3 0-5.6-.9-7-2.3" />
      <circle cx="17.4" cy="11" r="2.2" />
      <circle cx="6.6" cy="13" r="2.2" />
    </Glyph>
  ),
  leo: p => (
    <Glyph {...p}>
      <circle cx="8.2" cy="15.4" r="3.9" />
      <path d="M12.1 15.4c0-3.4-1.4-5.6.4-8 1.7-2.3 5-1.5 5.5 1.2.4 2.2-.9 3.7-2.3 4.6-1.4 1-1 3.5 1.8 4.9" />
    </Glyph>
  ),
  virgo: p => (
    <Glyph {...p}>
      <path d="M4 17.5V8.4C4 6.6 6.6 6.4 6.9 8.4V17" />
      <path d="M6.9 8.4C7.2 6.6 9.8 6.4 10.1 8.4V17" />
      <path d="M10.1 8.4c.3-1.8 2.9-2 3.2 0v5.2" />
      <path d="M13.3 12.6c1.6-2 4.6-1.3 5.1 1.3.5 2.7-2 5-4.6 5.4 2.3.2 4.4 1.2 5.2 2.2" />
    </Glyph>
  ),
  libra: p => (
    <Glyph {...p}>
      <path d="M4 19.6h16" />
      <path d="M4 14.6h4.2a4.2 4.2 0 0 1 7.6 0H20" />
    </Glyph>
  ),
  scorpio: p => (
    <Glyph {...p}>
      <path d="M3.6 17.5V8.4c0-1.8 2.6-2 2.9 0V17" />
      <path d="M6.5 8.4c.3-1.8 2.9-2 3.2 0V17" />
      <path d="M9.7 8.4c.3-1.8 2.9-2 3.2 0v8.4l4.9 4.2" />
      <path d="M17.8 20.9l1-4.3M17.8 20.9l-4.3-.7" />
    </Glyph>
  ),
  sagittarius: p => (
    <Glyph {...p}>
      <path d="M5 19.4L18.6 5.8" />
      <path d="M18.6 5.8h-6M18.6 5.8v6" />
      <path d="M8.2 11.2l5.2 5.2" />
    </Glyph>
  ),
  capricorn: p => (
    <Glyph {...p}>
      <path d="M4.4 6.2c1 3.6 2.6 8.6 5 8.6 1.8 0 2.6-2.2 2.6-4.4" />
      <path d="M12 10.4c0-2.8 2.2-4 3.9-2.9 1.9 1.3 1.4 4.6-1.4 5.3 2.8.4 4.6 2.4 3.6 4.8-.8 1.9-3.2 2.4-4.6 1.3" />
    </Glyph>
  ),
  aquarius: p => (
    <Glyph {...p}>
      <path d="M4 10.6l3.3-2.8 3.4 2.8 3.3-2.8 3.4 2.8L20 7.8" />
      <path d="M4 16.4l3.3-2.8 3.4 2.8 3.3-2.8 3.4 2.8L20 13.6" />
    </Glyph>
  ),
  pisces: p => (
    <Glyph {...p}>
      <path d="M8.8 4C4.6 8 4.6 16 8.8 20" />
      <path d="M15.2 4c4.2 4 4.2 12 0 16" />
      <path d="M5 12h14" />
    </Glyph>
  ),
};

export const ZODIAC_ORDER = [
  "aries", "taurus", "gemini", "cancer", "leo", "virgo",
  "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
] as const;

export function ZodiacIcon({ sign, ...rest }: GlyphProps & { sign: string }) {
  const Component = ZODIAC_GLYPHS[sign.toLowerCase()] ?? ZODIAC_GLYPHS.aries;
  return <Component {...rest} />;
}

// ── Planets ───────────────────────────────────────────────────────────────

/**
 * Keyed to match the backend's planet names, so a wheel can look a glyph up
 * straight from an API payload without a translation table.
 */
export const PLANET_GLYPHS: Record<string, (p: GlyphProps) => JSX.Element> = {
  sun: p => (<Glyph {...p}><circle cx="12" cy="12" r="8.2" /><circle cx="12" cy="12" r="1.5" fill="currentColor" /></Glyph>),
  moon: p => (<Glyph {...p}><path d="M19.4 14.6A8.2 8.2 0 1 1 9.4 4.6a6.5 6.5 0 0 0 10 10z" /></Glyph>),
  mercury: p => (<Glyph {...p}>
    <circle cx="12" cy="11.6" r="4.6" />
    <path d="M8.4 4.2a5 5 0 0 0 7.2 0" />
    <path d="M12 16.2V21M9.4 18.6h5.2" />
  </Glyph>),
  venus: p => (<Glyph {...p}><circle cx="12" cy="9.4" r="5.4" /><path d="M12 14.8V21M9.2 18.2h5.6" /></Glyph>),
  mars: p => (<Glyph {...p}>
    <circle cx="10.6" cy="13.8" r="5.4" />
    <path d="M14.6 10L20 4.6M15.4 4.6H20v4.6" />
  </Glyph>),
  jupiter: p => (<Glyph {...p}>
    <path d="M6.6 6.6c0-2.4 3.4-3 4.6-1.2 1.2 1.8.6 4.4-.6 7-1 2.2-2.2 4.4-2.2 6.6h9.4" />
    <path d="M15.4 4.6v15.6" />
  </Glyph>),
  saturn: p => (<Glyph {...p}>
    <path d="M7 6.4h5.4M9.7 3.4v7.2" />
    <path d="M9.7 10.6c2.6-1.6 5.6-.4 6.2 2.6.7 3.4-1.4 6.6-4.8 7.4" />
  </Glyph>),
  uranus: p => (<Glyph {...p}>
    <circle cx="12" cy="18.4" r="3" />
    <path d="M12 15.4V3.4M8 6.6v6M16 6.6v6M8 9.6h8" />
  </Glyph>),
  neptune: p => (<Glyph {...p}>
    <path d="M6 4.6v5.2c0 3.4 2.7 6 6 6s6-2.6 6-6V4.6" />
    <path d="M12 8.4V21M8.8 18.6h6.4" />
  </Glyph>),
  pluto: p => (<Glyph {...p}>
    <path d="M6.6 21v-9.4h4.2a3.7 3.7 0 0 0 0-7.4H6.6" />
    <circle cx="15.6" cy="8.4" r="3.2" />
  </Glyph>),
};

export function PlanetIcon({ planet, ...rest }: GlyphProps & { planet: string }) {
  const Component = PLANET_GLYPHS[planet.toLowerCase()] ?? PLANET_GLYPHS.sun;
  return <Component {...rest} />;
}

// ── Section icons ─────────────────────────────────────────────────────────

export function SunIcon(p: GlyphProps) {
  return (
    <Glyph {...p}>
      <circle cx="12" cy="12" r="4.2" />
      <path d="M12 2.6v2.6M12 18.8v2.6M2.6 12h2.6M18.8 12h2.6M5.4 5.4l1.9 1.9M16.7 16.7l1.9 1.9M18.6 5.4l-1.9 1.9M7.3 16.7l-1.9 1.9" />
    </Glyph>
  );
}

export function TarotIcon(p: GlyphProps) {
  return (
    <Glyph {...p}>
      <rect x="3.2" y="6.4" width="9.4" height="13.4" rx="1.6" transform="rotate(-12 7.9 13.1)" />
      <rect x="11.4" y="4.2" width="9.4" height="13.4" rx="1.6" transform="rotate(9 16.1 10.9)" />
      <path d="M16 9.2v3.4M14.3 10.9h3.4" />
    </Glyph>
  );
}

export function NatalIcon(p: GlyphProps) {
  return (
    <Glyph {...p}>
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="4.4" />
      <path d="M12 3v3.6M12 17.4V21M3 12h3.6M17.4 12H21" />
      <path d="M5.6 5.6l2.6 2.6M15.8 15.8l2.6 2.6M18.4 5.6l-2.6 2.6M8.2 15.8l-2.6 2.6" />
    </Glyph>
  );
}

export function CompatibilityIcon(p: GlyphProps) {
  return (
    <Glyph {...p}>
      <circle cx="8.8" cy="12" r="5.6" />
      <circle cx="15.2" cy="12" r="5.6" />
    </Glyph>
  );
}

/** The 3x3 Pythagorean square the numerology reading is actually built on. */
export function NumerologyIcon(p: GlyphProps) {
  return (
    <Glyph {...p}>
      <rect x="3.4" y="3.4" width="17.2" height="17.2" rx="2.2" />
      <path d="M9.1 3.4v17.2M14.9 3.4v17.2M3.4 9.1h17.2M3.4 14.9h17.2" />
    </Glyph>
  );
}

export function MoonIcon(p: GlyphProps) {
  return (
    <Glyph {...p}>
      <path d="M20 14.4A8.6 8.6 0 1 1 9.6 4a6.8 6.8 0 0 0 10.4 10.4z" />
    </Glyph>
  );
}

/** Raidō — the rune the app's own spreads lead with. */
export function RuneIcon(p: GlyphProps) {
  return (
    <Glyph {...p}>
      <path d="M6.5 21V3h6.2a4.3 4.3 0 0 1 0 8.6H6.5" />
      <path d="M11.4 11.6L17.5 21" />
    </Glyph>
  );
}

export function MatrixIcon(p: GlyphProps) {
  return (
    <Glyph {...p}>
      <path d="M12 2.4l2.6 6.9 6.9 2.7-6.9 2.7-2.6 6.9-2.6-6.9L2.5 12l6.9-2.7z" />
      <circle cx="12" cy="12" r="2.4" />
    </Glyph>
  );
}

// ── UI accents ────────────────────────────────────────────────────────────

export function SparkIcon(p: GlyphProps) {
  return (
    <Glyph {...p}>
      <path d="M12 3l2.1 5.9L20 11l-5.9 2.1L12 19l-2.1-5.9L4 11l5.9-2.1z" />
    </Glyph>
  );
}

export function CheckIcon(p: GlyphProps) {
  return (
    <Glyph {...p}>
      <path d="M4.5 12.5l5 5 10-11" />
    </Glyph>
  );
}

export function ArrowRightIcon(p: GlyphProps) {
  return (
    <Glyph {...p}>
      <path d="M4 12h15M13 6l6 6-6 6" />
    </Glyph>
  );
}

export function PlusIcon(p: GlyphProps) {
  return (
    <Glyph {...p}>
      <path d="M12 5v14M5 12h14" />
    </Glyph>
  );
}

export function TelegramIcon(p: GlyphProps) {
  return (
    <Glyph {...p}>
      <path d="M21 4.4L2.9 11.2l5.2 1.8 2 6 2.8-3.7 5 3.7z" />
      <path d="M8.1 13l12.9-8.6-8 10.9" />
    </Glyph>
  );
}

export function ShieldIcon(p: GlyphProps) {
  return (
    <Glyph {...p}>
      <path d="M12 2.8l7.4 2.8v5.6c0 4.6-3 8.1-7.4 10-4.4-1.9-7.4-5.4-7.4-10V5.6z" />
    </Glyph>
  );
}

export function StarIcon(p: GlyphProps) {
  return (
    <Glyph {...p}>
      <path d="M12 3.2l2.7 5.6 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z" />
    </Glyph>
  );
}
