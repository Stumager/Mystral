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

        {/* Лицевая сторона — Rider-Waite изображение */}
        <div
          style={{
            backfaceVisibility: "hidden",
            transform: "rotateY(180deg)",
            position: "absolute",
            inset: 0,
            borderRadius: 10,
            overflow: "hidden",
            border: "1px solid rgba(140,110,255,0.35)",
            background: "linear-gradient(160deg, #1E0E50, #0D0520)",
          }}
        >
          <img
            src={`/tarot/${card.id}.jpg`}
            alt={card.name_ru}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
            }}
            onError={(e) => {
              e.currentTarget.style.display = "none";
            }}
          />
          <div
            style={{
              position: "absolute",
              bottom: 0,
              left: 0,
              right: 0,
              background: "rgba(0,0,0,0.6)",
              padding: "4px 6px",
              textAlign: "center",
            }}
          >
            <span
              style={{
                fontSize: 9,
                color: "rgba(232,224,255,0.9)",
                fontFamily: "serif",
              }}
            >
              {card.name_ru}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
