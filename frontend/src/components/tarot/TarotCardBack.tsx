import { Logo } from "../Logo";

interface TarotCardBackProps {
  /** Scales with the card; the in-app deck uses 56 on a 120x200 card. */
  logoSize?: number;
  radius?: number;
  /**
   * The in-app spread shows one card at a time, so its logo drifts. A fanned
   * deck would have seven of them drifting out of sync, so the landing turns
   * it off.
   */
  animateLogo?: boolean;
}

/**
 * The face-down side of a Mystral tarot card.
 *
 * Extracted from TarotCard so the landing's deck and the in-app spread show
 * the same back rather than two different ones — a visitor who draws a card
 * on the landing and then opens the app should recognise the deck.
 *
 * Fills its positioned parent; the parent owns size, 3D transforms and
 * backface-visibility.
 */
export function TarotCardBack({ logoSize = 56, radius = 16, animateLogo = true }: TarotCardBackProps) {
  return (
    <div style={{
      position: "absolute", inset: 0, borderRadius: radius, overflow: "hidden",
      background: "linear-gradient(165deg, #16123F 0%, #1E1754 45%, #0D0B2E 100%)",
      border: "2px solid rgba(201,168,76,.35)",
      boxShadow: "0 0 40px rgba(75,60,134,.35), 0 12px 40px rgba(0,0,0,.8), inset 0 1px 0 rgba(201,168,76,.25)",
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
    }}>
      <div style={{
        position: "absolute", inset: 0, opacity: .07, pointerEvents: "none",
        background: "repeating-linear-gradient(45deg, rgba(201,168,76,.4) 0px, rgba(201,168,76,.4) 1px, transparent 1px, transparent 14px), repeating-linear-gradient(-45deg, rgba(201,168,76,.4) 0px, rgba(201,168,76,.4) 1px, transparent 1px, transparent 14px)",
      }} />
      <div style={{ position: "absolute", inset: 7, border: "1px solid rgba(201,168,76,.22)", borderRadius: radius - 6, pointerEvents: "none" }} />
      {([
        { top: 12, left: 12, borderTop: "1.5px solid rgba(201,168,76,.5)", borderLeft: "1.5px solid rgba(201,168,76,.5)" },
        { top: 12, right: 12, borderTop: "1.5px solid rgba(201,168,76,.5)", borderRight: "1.5px solid rgba(201,168,76,.5)" },
        { bottom: 12, left: 12, borderBottom: "1.5px solid rgba(201,168,76,.5)", borderLeft: "1.5px solid rgba(201,168,76,.5)" },
        { bottom: 12, right: 12, borderBottom: "1.5px solid rgba(201,168,76,.5)", borderRight: "1.5px solid rgba(201,168,76,.5)" },
      ] as React.CSSProperties[]).map((s, i) => (
        <span key={i} style={{ position: "absolute", width: 12, height: 12, ...s }} />
      ))}
      <div style={{ position: "relative", zIndex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
        <div style={{
          filter: "drop-shadow(0 0 20px rgba(201,168,76,.9)) drop-shadow(0 0 40px rgba(201,168,76,.4))",
          animation: animateLogo ? "mystral-float 5s ease-in-out infinite" : undefined,
        }}>
          <Logo size={logoSize} />
        </div>
        <span className="font-cinzel" style={{ fontSize: 8.5, letterSpacing: ".44em", color: "rgba(232,205,126,.65)" }}>MYSTRAL</span>
      </div>
    </div>
  );
}
