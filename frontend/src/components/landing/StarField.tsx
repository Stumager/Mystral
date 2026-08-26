import { useEffect, useMemo, useRef } from "react";
import { onScrollThrottled, seededRandom, usePrefersReducedMotion } from "../../utils/motion";

interface Star { x: number; y: number; r: number; opacity: number; twinkle: number; delay: number; }

interface Layer { stars: Star[]; depth: number; }

/** Three depth planes: far/dim/small through near/bright/large. */
const LAYER_SPECS = [
  { count: 90, depth: 0.06, minR: 0.6, maxR: 1.1, minO: 0.18, maxO: 0.45 },
  { count: 45, depth: 0.14, minR: 1.0, maxR: 1.7, minO: 0.35, maxO: 0.7 },
  { count: 18, depth: 0.26, minR: 1.6, maxR: 2.6, minO: 0.6, maxO: 1.0 },
];

function buildLayers(): Layer[] {
  const rand = seededRandom(0x4D5953); // "MYS"
  return LAYER_SPECS.map(spec => ({
    depth: spec.depth,
    stars: Array.from({ length: spec.count }, () => ({
      x: rand() * 100,
      y: rand() * 100,
      r: spec.minR + rand() * (spec.maxR - spec.minR),
      opacity: spec.minO + rand() * (spec.maxO - spec.minO),
      twinkle: 2.6 + rand() * 3.4,
      delay: rand() * 4,
    })),
  }));
}

/**
 * Parallax starfield for the landing hero.
 *
 * Each layer translates at its own fraction of scroll distance, so the field
 * gains depth as the page moves. The whole thing is one absolutely-positioned
 * aria-hidden backdrop — it never participates in layout or the a11y tree.
 */
export function StarField({ height = "140%" }: { height?: string }) {
  const layers = useMemo(buildLayers, []);
  const layerRefs = useRef<(HTMLDivElement | null)[]>([]);
  const hostRef = useRef<HTMLDivElement>(null);
  const reduced = usePrefersReducedMotion();

  useEffect(() => {
    if (reduced) return;
    return onScrollThrottled(() => {
      const host = hostRef.current;
      if (!host) return;
      // Offset from this section's own top, not absolute page scroll, so the
      // effect stays anchored once the hero leaves the viewport.
      const offset = -host.getBoundingClientRect().top;
      layers.forEach((layer, i) => {
        const el = layerRefs.current[i];
        if (el) el.style.transform = `translate3d(0, ${offset * layer.depth}px, 0)`;
      });
    });
  }, [layers, reduced]);

  return (
    <div ref={hostRef} aria-hidden style={{ position: "absolute", inset: 0, overflow: "hidden", pointerEvents: "none" }}>
      {layers.map((layer, i) => (
        <div key={i} ref={el => { layerRefs.current[i] = el; }}
          style={{ position: "absolute", left: 0, right: 0, top: 0, height, willChange: "transform" }}>
          {layer.stars.map((s, j) => (
            <span key={j} style={{
              position: "absolute",
              left: `${s.x}%`, top: `${s.y}%`,
              width: s.r * 2, height: s.r * 2,
              borderRadius: "50%",
              background: "#E8CD7E",
              opacity: s.opacity,
              boxShadow: s.r > 1.5 ? `0 0 ${s.r * 3}px rgba(232,205,126,.7)` : undefined,
              animation: reduced ? undefined : `mystral-twinkle ${s.twinkle}s ease-in-out infinite ${s.delay}s`,
            }} />
          ))}
        </div>
      ))}
    </div>
  );
}
