import { ZODIAC_ORDER, ZodiacIcon } from "../icons/AstroIcons";
import { usePrefersReducedMotion } from "../../utils/motion";

const SIGN_NAMES: Record<string, { ru: string; en: string }> = {
  aries: { ru: "Овен", en: "Aries" },
  taurus: { ru: "Телец", en: "Taurus" },
  gemini: { ru: "Близнецы", en: "Gemini" },
  cancer: { ru: "Рак", en: "Cancer" },
  leo: { ru: "Лев", en: "Leo" },
  virgo: { ru: "Дева", en: "Virgo" },
  libra: { ru: "Весы", en: "Libra" },
  scorpio: { ru: "Скорпион", en: "Scorpio" },
  sagittarius: { ru: "Стрелец", en: "Sagittarius" },
  capricorn: { ru: "Козерог", en: "Capricorn" },
  aquarius: { ru: "Водолей", en: "Aquarius" },
  pisces: { ru: "Рыбы", en: "Pisces" },
};

/**
 * Continuous band of the twelve signs drawn as SVG line glyphs.
 *
 * The track holds the twelve signs twice and shifts by exactly -50%, so the
 * second copy is in the first one's starting position when the loop restarts
 * — that is what makes the seam invisible. Duplicating any other number of
 * times, or animating to a pixel value, produces a visible jump.
 */
export function ZodiacMarquee({ ru }: { ru: boolean }) {
  const reduced = usePrefersReducedMotion();
  const items = [...ZODIAC_ORDER, ...ZODIAC_ORDER];

  return (
    <div aria-hidden style={{
      position: "relative", overflow: "hidden", padding: "20px 0",
      borderTop: "1px solid rgba(255,255,255,.06)", borderBottom: "1px solid rgba(255,255,255,.06)",
      // Fades the band into the page background at both ends instead of
      // letting glyphs get chopped mid-stroke by the viewport edge.
      maskImage: "linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent)",
      WebkitMaskImage: "linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent)",
    }}>
      <div style={{
        display: "flex", width: "max-content",
        animation: reduced ? undefined : "mystral-marquee 46s linear infinite",
      }}>
        {items.map((sign, i) => (
          // The spacing lives on each item rather than in a flex `gap`: with
          // `gap` the track is 24 items + 23 gaps, so -50% lands half a gap
          // short of the loop point and the seam visibly stutters.
          <div key={`${sign}-${i}`} style={{ display: "flex", alignItems: "center", gap: 11, flexShrink: 0, marginRight: 52 }}>
            <span style={{ color: "rgba(201,168,76,.75)", display: "flex" }}>
              <ZodiacIcon sign={sign} size={26} strokeWidth={1.3} />
            </span>
            <span className="font-cinzel uppercase" style={{ fontSize: 11.5, letterSpacing: ".22em", color: "rgba(182,172,152,.6)", whiteSpace: "nowrap" }}>
              {ru ? SIGN_NAMES[sign].ru : SIGN_NAMES[sign].en}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
