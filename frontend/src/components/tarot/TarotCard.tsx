import { TarotCardData } from "../../data/tarot";

interface TarotCardProps {
  card: TarotCardData;
  revealed: boolean;
  delay?: number;
}

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
          boxShadow: revealed
            ? "0 8px 24px rgba(107,78,255,0.3), 0 2px 8px rgba(0,0,0,0.5)"
            : "0 4px 12px rgba(0,0,0,0.4)",
          borderRadius: 10,
        }}
      >
        {/* Рубашка — SVG паттерн */}
        <div
          style={{
            backfaceVisibility: "hidden",
            position: "absolute",
            inset: 0,
            borderRadius: 10,
            background: "linear-gradient(160deg, #1B0C4A, #080316)",
            border: "1px solid rgba(140,110,255,0.4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            overflow: "hidden",
          }}
        >
          <svg width="100%" height="100%" style={{ position: "absolute", inset: 0 }}>
            <defs>
              <pattern id="rub" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                <circle cx="10" cy="10" r="1" fill="rgba(140,110,255,0.15)" />
                <line x1="0" y1="10" x2="20" y2="10" stroke="rgba(140,110,255,0.06)" strokeWidth="0.5" />
                <line x1="10" y1="0" x2="10" y2="20" stroke="rgba(140,110,255,0.06)" strokeWidth="0.5" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#rub)" />
            <rect x="5" y="5" width="78" height="134" rx="6" fill="none" stroke="rgba(200,160,80,0.3)" strokeWidth="1" />
          </svg>
          <div
            style={{
              position: "relative",
              zIndex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 4,
            }}
          >
            <span style={{ fontSize: 28, opacity: 0.9, color: "#C9A84C" }}>✦</span>
            <span
              style={{
                fontSize: 8,
                letterSpacing: "0.2em",
                color: "rgba(200,160,80,0.7)",
                fontFamily: "serif",
              }}
            >
              MYSTRAL
            </span>
          </div>
        </div>

        {/* Лицевая сторона — Rider-Waite */}
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
        </div>
      </div>
    </div>
  );
}
