import { useEffect, useState } from "react";
import { Logo } from "../Logo";

interface TarotCardProps {
  cardId: number;
  name: string;
  revealed: boolean;
  reversed?: boolean;
  delay?: number;
}

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
        width: 88, height: 144, borderRadius: 14, overflow: "hidden", position: "relative",
        border: reversed ? "2px solid rgba(217,138,138,.5)" : "1px solid rgba(201,168,76,.28)",
        boxShadow: "0 8px 32px rgba(0,0,0,.6)",
      }}>
        <img src={`/tarot/${cardId}.jpg?v=2`} alt={name}
          style={{ width: "100%", height: "100%", objectFit: "cover", transform: reversed ? "rotate(180deg)" : "none" }}
          onError={e => { (e.target as HTMLImageElement).style.display = "none"; }} />
        {reversed && (
          <div style={{ position: "absolute", top: 4, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
            <span style={{ fontSize: 7, color: "#fff", background: "rgba(217,138,138,.8)", padding: "1px 5px", borderRadius: 4 }}>REV</span>
          </div>
        )}
      </div>
    );
  }

  return (
    <div style={{ perspective: 600, width: 88, height: 144 }}>
      <div style={{
        width: "100%", height: "100%", position: "relative",
        transformStyle: "preserve-3d", transition: "transform 0.7s ease",
        transform: flipped ? "rotateY(180deg)" : "rotateY(0deg)",
        borderRadius: 14,
      }}>
        {/* Back */}
        <div style={{
          backfaceVisibility: "hidden", WebkitBackfaceVisibility: "hidden",
          position: "absolute", inset: 0, borderRadius: 14,
          background: "linear-gradient(160deg,#0F0A2E,#1A1246,#0A0818)",
          border: "1px solid rgba(201,168,76,.28)",
          boxShadow: "0 8px 32px rgba(0,0,0,.6)",
          display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 8,
          overflow: "hidden",
        }}>
          {/* Inner border */}
          <div style={{ position: "absolute", inset: 8, border: "1px solid rgba(201,168,76,.15)", borderRadius: 10, pointerEvents: "none" }} />
          {/* Corner decorations */}
          {[
            { top: 12, left: 12, borderTop: "1.5px solid rgba(201,168,76,.3)", borderLeft: "1.5px solid rgba(201,168,76,.3)" },
            { top: 12, right: 12, borderTop: "1.5px solid rgba(201,168,76,.3)", borderRight: "1.5px solid rgba(201,168,76,.3)" },
            { bottom: 12, left: 12, borderBottom: "1.5px solid rgba(201,168,76,.3)", borderLeft: "1.5px solid rgba(201,168,76,.3)" },
            { bottom: 12, right: 12, borderBottom: "1.5px solid rgba(201,168,76,.3)", borderRight: "1.5px solid rgba(201,168,76,.3)" },
          ].map((s, i) => <div key={i} style={{ position: "absolute", width: 12, height: 12, ...s } as React.CSSProperties} />)}

          <div style={{ filter: "drop-shadow(0 0 18px rgba(201,168,76,.6))", animation: "mystral-float 6s ease-in-out infinite" }}>
            <Logo size={40} />
          </div>
          <span className="font-cinzel" style={{ fontSize: 7, letterSpacing: ".38em", color: "#E8CD7E", marginTop: 2 }}>MYSTRAL</span>
        </div>

        {/* Face */}
        <div style={{
          backfaceVisibility: "hidden", WebkitBackfaceVisibility: "hidden",
          transform: "rotateY(180deg)", position: "absolute", inset: 0, borderRadius: 14,
          overflow: "hidden", border: "1px solid rgba(201,168,76,.28)", background: "#0A0818",
        }}>
          <img src={`/tarot/${cardId}.jpg?v=2`} alt={name}
            style={{ width: "100%", height: "100%", objectFit: "cover", transform: reversed ? "rotate(180deg)" : "none" }}
            onError={e => { (e.target as HTMLImageElement).style.display = "none"; }} />
        </div>
      </div>
    </div>
  );
}
