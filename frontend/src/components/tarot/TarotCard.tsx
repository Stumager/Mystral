import { useEffect, useState } from "react";
import { Logo } from "../Logo";

interface TarotCardProps {
  cardId: number;
  name: string;
  revealed: boolean;
  reversed?: boolean;
  delay?: number;
}

const W = 120;
const H = 200;

export function TarotCard({ cardId, name, revealed, reversed, delay = 0 }: TarotCardProps) {
  const [flipped, setFlipped] = useState(false);
  const [flat, setFlat] = useState(false);

  useEffect(() => {
    if (!revealed) { setFlipped(false); setFlat(false); return; }
    const t1 = setTimeout(() => setFlipped(true), delay);
    const t2 = setTimeout(() => setFlat(true), delay + 800);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, [revealed, delay]);

  if (flat) {
    return (
      <div style={{
        width: W, height: H, borderRadius: 16, overflow: "hidden", position: "relative",
        border: reversed ? "2px solid rgba(217,138,138,.5)" : "2px solid rgba(201,168,76,.35)",
        boxShadow: "0 8px 32px rgba(0,0,0,.7)",
      }}>
        <img src={`/tarot/${cardId}.jpg?v=2`} alt={name} loading="lazy"
          style={{ width: "100%", height: "100%", objectFit: "cover", transform: reversed ? "rotate(180deg)" : "none" }}
          onError={e => { (e.target as HTMLImageElement).style.display = "none"; }} />
        {reversed && (
          <div style={{ position: "absolute", top: 4, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
            <span style={{ fontSize: 8, color: "#fff", background: "rgba(217,138,138,.8)", padding: "2px 6px", borderRadius: 4 }}>REV</span>
          </div>
        )}
      </div>
    );
  }

  return (
    <div style={{ perspective: 600, width: W, height: H }}>
      <div style={{
        width: "100%", height: "100%", position: "relative",
        transformStyle: "preserve-3d", transition: "transform 0.7s ease",
        transform: flipped ? "rotateY(180deg)" : "rotateY(0deg)",
        borderRadius: 16,
      }}>
        {/* Back */}
        <div style={{
          backfaceVisibility: "hidden", WebkitBackfaceVisibility: "hidden",
          position: "absolute", inset: 0, borderRadius: 16, overflow: "hidden",
          background: "linear-gradient(165deg, #16123F 0%, #1E1754 45%, #0D0B2E 100%)",
          border: "2px solid rgba(201,168,76,.35)",
          boxShadow: "0 0 40px rgba(75,60,134,.35), 0 12px 40px rgba(0,0,0,.8), inset 0 1px 0 rgba(201,168,76,.25)",
          display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
        }}>
          <div style={{ position: "absolute", inset: 0, opacity: .07, pointerEvents: "none",
            background: "repeating-linear-gradient(45deg, rgba(201,168,76,.4) 0px, rgba(201,168,76,.4) 1px, transparent 1px, transparent 14px), repeating-linear-gradient(-45deg, rgba(201,168,76,.4) 0px, rgba(201,168,76,.4) 1px, transparent 1px, transparent 14px)",
          }} />
          <div style={{ position: "absolute", inset: 7, border: "1px solid rgba(201,168,76,.22)", borderRadius: 10, pointerEvents: "none" }} />
          {([
            { top: 12, left: 12, borderTop: "1.5px solid rgba(201,168,76,.5)", borderLeft: "1.5px solid rgba(201,168,76,.5)" },
            { top: 12, right: 12, borderTop: "1.5px solid rgba(201,168,76,.5)", borderRight: "1.5px solid rgba(201,168,76,.5)" },
            { bottom: 12, left: 12, borderBottom: "1.5px solid rgba(201,168,76,.5)", borderLeft: "1.5px solid rgba(201,168,76,.5)" },
            { bottom: 12, right: 12, borderBottom: "1.5px solid rgba(201,168,76,.5)", borderRight: "1.5px solid rgba(201,168,76,.5)" },
          ] as React.CSSProperties[]).map((s, i) => <span key={i} style={{ position: "absolute", width: 12, height: 12, ...s }} />)}
          <div style={{ position: "relative", zIndex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
            <div style={{ filter: "drop-shadow(0 0 20px rgba(201,168,76,.9)) drop-shadow(0 0 40px rgba(201,168,76,.4))", animation: "mystral-float 5s ease-in-out infinite" }}>
              <Logo size={56} />
            </div>
            <span className="font-cinzel" style={{ fontSize: 8.5, letterSpacing: ".44em", color: "rgba(232,205,126,.65)" }}>MYSTRAL</span>
          </div>
        </div>

        {/* Face */}
        <div style={{
          backfaceVisibility: "hidden", WebkitBackfaceVisibility: "hidden",
          transform: "rotateY(180deg)", position: "absolute", inset: 0, borderRadius: 16,
          overflow: "hidden", border: "2px solid rgba(201,168,76,.35)", background: "#0A0818",
        }}>
          <img src={`/tarot/${cardId}.jpg?v=2`} alt={name} loading="lazy"
            style={{ width: "100%", height: "100%", objectFit: "cover", transform: reversed ? "rotate(180deg)" : "none" }}
            onError={e => { (e.target as HTMLImageElement).style.display = "none"; }} />
        </div>
      </div>
    </div>
  );
}
