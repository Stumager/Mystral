import { useEffect, useRef, useState } from "react";
import { ArrowRightIcon, TelegramIcon } from "../icons/AstroIcons";

interface Props {
  ru: boolean;
  /** Element whose exit from the viewport arms the bar — normally the hero. */
  watchRef: React.RefObject<HTMLElement>;
  appUrl: string;
}

/**
 * Bottom bar that arms itself once the hero has scrolled away, so the primary
 * action stays reachable through the long middle of the page.
 *
 * Dismissal is remembered for the session only. Persisting it would mean a
 * returning visitor never sees the main call to action again, which is a
 * worse trade than showing the bar once per visit.
 */
export function StickyCta({ ru, watchRef, appUrl }: Props) {
  const [armed, setArmed] = useState(false);
  const [dismissed, setDismissed] = useState(() => {
    try { return sessionStorage.getItem("mystral_cta_dismissed") === "1"; } catch { return false; }
  });
  const barRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = watchRef.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([entry]) => setArmed(!entry.isIntersecting),
      { rootMargin: "-120px 0px 0px 0px" },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [watchRef]);

  function dismiss() {
    setDismissed(true);
    try { sessionStorage.setItem("mystral_cta_dismissed", "1"); } catch { /* private mode */ }
  }

  const visible = armed && !dismissed;

  return (
    <div ref={barRef} style={{
      position: "fixed", left: 0, right: 0, bottom: 0, zIndex: 60,
      transform: visible ? "translateY(0)" : "translateY(110%)",
      opacity: visible ? 1 : 0,
      transition: "transform .45s cubic-bezier(.22,.9,.3,1), opacity .3s ease",
      pointerEvents: visible ? "auto" : "none",
      padding: "0 16px 16px",
    }}>
      {/* Everything below stays on one line down to 320px: a bar that wraps
          to two rows eats a third of a phone screen and hides the content it
          is meant to sit beside. */}
      <style>{`
        .sc-bar { padding: 14px 16px 14px 22px; gap: 16px; }
        .sc-title { font-size: 20px; }
        .sc-sub { font-size: 12.5px; }
        .sc-btn { height: 46px; padding: 0 22px; }
        .sc-title-short { display: none; }
        @media (max-width: 560px) {
          .sc-bar { padding: 11px 11px 11px 16px; gap: 10px; }
          .sc-title { font-size: 16.5px; }
          .sc-sub { display: none; }
          .sc-btn { height: 42px; padding: 0 15px; }
          .sc-btn-arrow { display: none; }
          /* The full sentence wraps to two lines below ~380px, which doubles
             the bar's height. Swap in a short label instead of truncating. */
          .sc-title-long { display: none; }
          .sc-title-short { display: inline; }
        }
        @media (max-width: 400px) {
          .sc-bar { padding: 10px 10px 10px 14px; gap: 8px; }
          .sc-title { font-size: 15px; }
          .sc-btn { padding: 0 13px; font-size: 14px; }
          .sc-close { width: 34px; height: 34px; margin-left: 6px; }
        }
        /* The dismiss control is visually small, so the tap area is grown
           past its bounds instead — a 36px box is under the 44px guidance
           and this costs no layout. */
        .sc-close { position: relative; }
        .sc-close::after {
          content: ""; position: absolute; top: 50%; left: 50%;
          transform: translate(-50%, -50%);
          width: 44px; height: 44px;
        }
      `}</style>

      <div className="sc-bar" style={{
        maxWidth: 940, margin: "0 auto",
        display: "flex", alignItems: "center", flexWrap: "nowrap",
        borderRadius: 18,
        background: "rgba(12,10,32,.9)", backdropFilter: "blur(16px)",
        border: "1px solid rgba(201,168,76,.3)",
        boxShadow: "0 20px 50px -18px rgba(0,0,0,.85)",
      }}>
        <div style={{ flex: "1 1 auto", minWidth: 0 }}>
          <p className="font-cormorant sc-title" style={{ color: "#F0E9DA", lineHeight: 1.2 }}>
            <span className="sc-title-long">{ru ? "Первый разбор — бесплатно" : "Your first reading is free"}</span>
            <span className="sc-title-short">{ru ? "Разбор бесплатно" : "First reading free"}</span>
          </p>
          <p className="sc-sub" style={{ color: "#8A8170", marginTop: 2 }}>
            {ru ? "Без карты, меньше минуты" : "No card, under a minute"}
          </p>
        </div>

        <a href={appUrl} target="_blank" rel="noopener noreferrer" className="sc-btn" style={{
          display: "inline-flex", alignItems: "center", gap: 8, textDecoration: "none", flexShrink: 0,
          borderRadius: 13,
          background: "linear-gradient(100deg,#A9882F,#C9A84C 50%,#E8CD7E)", color: "#1A1206",
          fontWeight: 600, fontSize: 14.5, whiteSpace: "nowrap",
          boxShadow: "0 12px 28px -10px rgba(201,168,76,.6)",
        }}>
          <TelegramIcon size={17} strokeWidth={1.6} />
          {ru ? "Открыть" : "Open"}
          <span className="sc-btn-arrow" style={{ display: "inline-flex" }}>
            <ArrowRightIcon size={16} strokeWidth={1.7} />
          </span>
        </a>

        <button onClick={dismiss} aria-label={ru ? "Скрыть" : "Dismiss"} className="sc-close" style={{
          width: 36, height: 36, flexShrink: 0, borderRadius: 10, cursor: "pointer", marginLeft: 10,
          background: "rgba(255,255,255,.05)", border: "1px solid rgba(255,255,255,.1)",
          color: "#827A69", display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="2" strokeLinecap="round" aria-hidden>
            <path d="M5 5l14 14M19 5L5 19" />
          </svg>
        </button>
      </div>
    </div>
  );
}
