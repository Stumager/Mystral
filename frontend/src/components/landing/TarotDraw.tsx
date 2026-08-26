import { useCallback, useEffect, useRef, useState } from "react";
import { ARCANA_READINGS } from "../../data/landingArcana";
import { MAJOR_ARCANA } from "../../data/tarot";
import { usePrefersReducedMotion } from "../../utils/motion";
import { SparkIcon } from "../icons/AstroIcons";
import { TarotCardBack } from "../tarot/TarotCardBack";

/** Matches the 1109:1920 aspect of the source art, so nothing is cropped. */
const CARD_W = 130;
const CARD_H = 225;

/** Landing-sized WebP derivatives — ~63 KB each vs ~850 KB for the originals. */
const cardImage = (id: number) => `/tarot/landing/${id}.webp`;

/** Fan geometry for the face-down deck: angle and offset per card. */
const FAN = [-21, -14, -7, 0, 7, 14, 21].map((angle, i, arr) => {
  const mid = (arr.length - 1) / 2;
  const t = (i - mid) / mid; // -1 .. 1
  return { angle, x: t * 78, y: Math.abs(t) * 16, z: i };
});
const FAN_CENTER = 3;

type Phase = "idle" | "lift" | "flip" | "done";

/** Timings must stay in step with the CSS transitions below. */
const LIFT_MS = 620;
const FLIP_MS = 700;

interface Props { ru: boolean; onOpenApp: () => void; }

export function TarotDraw({ ru, onOpenApp }: Props) {
  const [phase, setPhase] = useState<Phase>("idle");
  const [cardId, setCardId] = useState<number | null>(null);
  const reduced = usePrefersReducedMotion();
  const timers = useRef<number[]>([]);

  // Phase advances on timers; if the visitor navigates away mid-draw the
  // component unmounts and those callbacks must not fire into a dead tree.
  useEffect(() => () => { timers.current.forEach(clearTimeout); }, []);

  const draw = useCallback(() => {
    if (phase === "lift" || phase === "flip") return;
    timers.current.forEach(clearTimeout);
    timers.current = [];

    const pool = ARCANA_READINGS.filter(r => r.id !== cardId);
    const next = pool[Math.floor(Math.random() * pool.length)];

    // Start fetching the art now, during the lift. The flip takes ~1.3s, so
    // by the time the face turns towards the viewer the image is normally
    // decoded and there is no blank card.
    const preload = new Image();
    preload.src = cardImage(next.id);

    setCardId(next.id);

    if (reduced) { setPhase("done"); return; }

    // Reset to face-down before lifting, so a second draw replays the whole
    // sequence rather than flipping an already-revealed card back and forth.
    setPhase("idle");
    timers.current.push(window.setTimeout(() => setPhase("lift"), 30));
    timers.current.push(window.setTimeout(() => setPhase("flip"), 30 + LIFT_MS));
    timers.current.push(window.setTimeout(() => setPhase("done"), 30 + LIFT_MS + FLIP_MS));
  }, [phase, cardId, reduced]);

  const reading = cardId !== null ? ARCANA_READINGS.find(r => r.id === cardId) ?? null : null;
  const meta = cardId !== null ? MAJOR_ARCANA.find(c => c.id === cardId) ?? null : null;
  const copy = reading ? (ru ? reading.ru : reading.en) : null;

  const drawn = phase !== "idle";
  const flipped = phase === "flip" || phase === "done";
  const busy = phase === "lift" || phase === "flip";

  return (
    <div className="td-grid">
      <style>{`
        .td-grid { display: grid; gap: 30px; align-items: center; grid-template-columns: 1fr; }
        @media (min-width: 900px) { .td-grid { grid-template-columns: 420px 1fr; gap: 48px; } }
        .td-stage { height: 360px; }
        @media (max-width: 420px) { .td-stage { transform: scale(.82); height: 300px; } }
        .td-deck-card { transition: transform .5s cubic-bezier(.22,.9,.3,1); }
        .td-stage:hover .td-deck-card { transform: var(--hover-transform); }
        @media (prefers-reduced-motion: reduce) {
          .td-deck-card, .td-stage:hover .td-deck-card { transition: none; transform: var(--rest-transform); }
        }
      `}</style>

      {/* ── Stage ─────────────────────────────────────────────────────── */}
      <div className="td-stage" style={{
        position: "relative", display: "flex",
        alignItems: "center", justifyContent: "center", perspective: 1400,
      }}>
        {/* Glow pool under the deck */}
        <div aria-hidden style={{
          position: "absolute", bottom: 30, width: 260, height: 60, borderRadius: "50%",
          background: "radial-gradient(ellipse,rgba(201,168,76,.22),transparent 70%)",
          filter: "blur(6px)",
        }} />

        {/* Face-down fan */}
        {FAN.map((f, i) => {
          const rest = `translate(${f.x}px, ${f.y}px) rotate(${f.angle}deg)`;
          return (
            <div key={i} aria-hidden className="td-deck-card" style={{
              position: "absolute", width: CARD_W, height: CARD_H,
              transform: rest,
              ["--rest-transform" as string]: rest,
              ["--hover-transform" as string]: `translate(${f.x * 1.12}px, ${f.y * 1.12 - 6}px) rotate(${f.angle * 1.08}deg)`,
              zIndex: f.z,
              opacity: drawn && i === FAN_CENTER ? 0 : 1,
            }}>
              <TarotCardBack logoSize={54} animateLogo={false} />
            </div>
          );
        })}

        {/* The drawn card — rises out of the middle of the fan, then flips. */}
        <div style={{
          position: "absolute", width: CARD_W, height: CARD_H, zIndex: 20,
          transform: drawn ? "translateY(-52px) scale(1.14)" : "translateY(0) scale(1)",
          opacity: drawn ? 1 : 0,
          transition: `transform ${LIFT_MS}ms cubic-bezier(.22,.9,.3,1), opacity 200ms ease`,
          pointerEvents: "none",
        }}>
          {/* No `filter` anywhere on this subtree: a filter forces the group
              to render flattened, which silently cancels `preserve-3d` and
              leaves the back face showing through the whole flip. */}
          <div style={{
            position: "relative", width: "100%", height: "100%",
            transformStyle: "preserve-3d",
            transform: flipped ? "rotateY(180deg)" : "rotateY(0deg)",
            transition: `transform ${FLIP_MS}ms cubic-bezier(.4,.05,.2,1)`,
          }}>
            <div style={{ position: "absolute", inset: 0, backfaceVisibility: "hidden", WebkitBackfaceVisibility: "hidden" }}>
              <TarotCardBack logoSize={54} animateLogo={false} />
            </div>
            <div style={{
              position: "absolute", inset: 0, borderRadius: 16, overflow: "hidden",
              backfaceVisibility: "hidden", WebkitBackfaceVisibility: "hidden",
              transform: "rotateY(180deg)",
              border: "2px solid rgba(201,168,76,.35)", background: "#0A0818",
              boxShadow: "0 20px 40px rgba(0,0,0,.6)",
            }}>
              {meta && copy && (
                <img
                  src={cardImage(meta.id)}
                  // The visible caption beside the card already names it, so
                  // the alt text carries the arcanum number the art shows.
                  alt={`${copy.name} — ${meta.number}`}
                  width={CARD_W} height={CARD_H} decoding="async"
                  style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
                />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── Reading ───────────────────────────────────────────────────── */}
      <div>
        {/* Announced politely so a screen reader hears the drawn card without
            the focus being yanked away from the draw button. */}
        <div aria-live="polite">
          {phase === "done" && copy && meta ? (
            <div key={cardId} style={{ animation: "mystral-fadeup .5s ease-out" }}>
              <span className="font-cinzel uppercase" style={{ fontSize: 10.5, letterSpacing: ".26em", color: "#C9A84C" }}>
                {meta.number} · {copy.keyword}
              </span>
              <p className="font-cormorant" style={{ fontSize: 30, color: "#F0E9DA", lineHeight: 1.1, marginTop: 6 }}>
                {copy.name}
              </p>
              <p style={{ fontSize: 15, lineHeight: 1.7, color: "#B6AC98", marginTop: 12, maxWidth: 420 }}>
                {copy.text}
              </p>
            </div>
          ) : (
            <div>
              <p className="font-cormorant" style={{ fontSize: 30, color: "#F0E9DA", lineHeight: 1.15 }}>
                {ru ? "Вытяните карту дня" : "Draw your card of the day"}
              </p>
              <p style={{ fontSize: 15, lineHeight: 1.7, color: "#8A8170", marginTop: 10, maxWidth: 420 }}>
                {ru
                  ? "22 Старших Аркана, одна карта — прямо здесь, без регистрации. В приложении доступна полная колода из 78 карт и расклады на несколько позиций."
                  : "22 Major Arcana, one card — right here, no sign-up. The app opens the full 78-card deck and multi-position spreads."}
              </p>
            </div>
          )}
        </div>

        <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginTop: 22 }}>
          <button onClick={draw} disabled={busy} className="ml-focus" style={{
            display: "inline-flex", alignItems: "center", gap: 8,
            height: 48, padding: "0 24px", borderRadius: 14, border: "none",
            background: "linear-gradient(100deg,#A9882F,#C9A84C 50%,#E8CD7E)", color: "#1A1206",
            fontWeight: 600, fontSize: 14.5,
            cursor: busy ? "default" : "pointer",
            opacity: busy ? 0.72 : 1,
            boxShadow: "0 14px 34px -12px rgba(201,168,76,.6)",
            transition: "opacity .2s ease",
          }}>
            <SparkIcon size={17} strokeWidth={1.6} />
            {phase === "done"
              ? (ru ? "Вытянуть ещё" : "Draw again")
              : (ru ? "Вытянуть карту" : "Draw a card")}
          </button>

          {phase === "done" && (
            <button onClick={onOpenApp} className="ml-focus" style={{
              height: 48, padding: "0 22px", borderRadius: 14,
              background: "rgba(255,255,255,.04)", color: "#F0E9DA",
              border: "1px solid rgba(201,168,76,.28)", fontSize: 14.5, cursor: "pointer",
              animation: "mystral-fadein .4s ease-out",
            }}>
              {ru ? "Расклад на 78 картах" : "Full 78-card spread"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
