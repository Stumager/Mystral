import { useEffect, useState } from "react";

/**
 * True when the visitor asked their OS to reduce motion.
 *
 * The landing leans on scroll-driven animation (parallax starfield, the natal
 * wheel assembling as you scroll, the tarot flip). Every one of those has to
 * degrade to its finished state rather than simply not run — otherwise a
 * reduced-motion visitor gets an empty wheel and a blank card.
 */
export function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = useState(() =>
    typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const handler = (e: MediaQueryListEvent) => setReduced(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  return reduced;
}

/**
 * Deterministic 0..1 generator (mulberry32).
 *
 * The starfield needs a few hundred fixed positions. Math.random() would
 * reshuffle them on every re-render, so the field would visibly jump whenever
 * React re-rendered the hero for an unrelated reason.
 */
export function seededRandom(seed: number): () => number {
  let a = seed;
  return () => {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/**
 * Subscribes to scroll through a single rAF-throttled listener.
 *
 * Several landing sections react to scroll at once; giving each its own
 * unthrottled handler is what turns a parallax hero into a janky one.
 */
export function onScrollThrottled(callback: () => void): () => void {
  let ticking = false;
  const handler = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => { callback(); ticking = false; });
  };
  window.addEventListener("scroll", handler, { passive: true });
  window.addEventListener("resize", handler, { passive: true });
  callback();
  return () => {
    window.removeEventListener("scroll", handler);
    window.removeEventListener("resize", handler);
  };
}
