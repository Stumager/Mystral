import { CSSProperties } from "react";
import { TarotCardData } from "../../data/tarot";

interface TarotCardProps {
  card: TarotCardData;
  revealed: boolean;
  delay?: number;
}

const faceStyle: CSSProperties = {
  position: "absolute",
  top: 0,
  left: 0,
  width: "100%",
  height: "100%",
  borderRadius: 10,
  backfaceVisibility: "hidden",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
};

export function TarotCard({ card, revealed, delay = 0 }: TarotCardProps) {
  return (
    <div style={{ perspective: "600px", width: 88, height: 144 }}>
      <div
        style={{
          width: "100%",
          height: "100%",
          position: "relative",
          transformStyle: "preserve-3d",
          transition: `transform 0.7s ease ${delay}ms`,
          transform: revealed ? "rotateY(180deg)" : "rotateY(0deg)",
        }}
      >
        {/* Рубашка */}
        <div
          style={{
            ...faceStyle,
            background: "linear-gradient(135deg, #1B0C4A, #080316)",
            border: "1px solid rgba(140,110,255,0.3)",
          }}
        >
          <span style={{ fontSize: 24, color: "#C9A84C" }}>✦</span>
          <span
            style={{
              fontSize: 8,
              color: "#C9A84C",
              letterSpacing: "0.15em",
              textTransform: "uppercase",
              marginTop: 6,
            }}
          >
            MYSTRAL
          </span>
        </div>

        {/* Лицевая сторона */}
        <div
          style={{
            ...faceStyle,
            background: "linear-gradient(160deg, #1E0E50, #0D0520)",
            border: "1px solid rgba(140,110,255,0.35)",
            transform: "rotateY(180deg)",
            justifyContent: "space-between",
            padding: "8px 6px",
          }}
        >
          {/* Внутренняя рамка */}
          <div
            style={{
              position: "absolute",
              inset: 3,
              borderRadius: 8,
              border: "0.5px solid rgba(200,160,80,0.18)",
              pointerEvents: "none",
            }}
          />
          <span
            style={{
              fontSize: 10,
              color: "#C9A84C",
              letterSpacing: "0.08em",
              zIndex: 1,
            }}
          >
            {card.number}
          </span>
          <span style={{ fontSize: 32, zIndex: 1 }}>{card.symbol}</span>
          <span
            style={{
              fontSize: 9,
              color: "#9B8FBB",
              textAlign: "center",
              lineHeight: 1.3,
              zIndex: 1,
              padding: "0 4px",
            }}
          >
            {card.name_ru}
          </span>
        </div>
      </div>
    </div>
  );
}
