import { useRef, useEffect, useState, useMemo } from "react";
import { useTranslation } from "react-i18next";
import { toDataURL as qrToDataURL } from "qrcode";
import { Logo } from "./Logo";
import { useShareCard } from "../hooks/useShareCard";

interface ShareCardProps {
  type: "tarot" | "runes" | "numerology" | "natal";
  title: string;
  subtitle?: string;
  cards?: { id: number; name: string; name_ru: string; reversed: boolean }[];
  runes?: { id: string; name: string; symbol: string; reversed: boolean }[];
  number?: number;
  numberLabel?: string;
  sign?: string;
  interpretation: string;
  refCode?: string;
  onClose: () => void;
}

function seededRandom(seed: number) {
  let s = seed;
  return () => {
    s = (s * 16807 + 0) % 2147483647;
    return s / 2147483647;
  };
}

export function ShareCard({
  type,
  title,
  subtitle,
  cards,
  runes,
  number,
  numberLabel,
  sign,
  interpretation,
  refCode,
  onClose,
}: ShareCardProps) {
  const { t, i18n } = useTranslation();
  const cardRef = useRef<HTMLDivElement>(null);
  const { share, isLoading } = useShareCard(cardRef);
  const [qrUrl, setQrUrl] = useState<string>("");
  const lang = i18n.language;

  const stars = useMemo(() => {
    const rng = seededRandom(42);
    return Array.from({ length: 30 }, (_, i) => ({
      key: i,
      left: rng() * 100,
      top: rng() * 100,
      size: 1 + rng() * 2,
      opacity: 0.2 + rng() * 0.4,
    }));
  }, []);

  useEffect(() => {
    const url = refCode
      ? `https://mystral.space/ref/${refCode}`
      : "https://mystral.space";
    qrToDataURL(url, {
      width: 104,
      margin: 1,
      color: { dark: "#C9A84C", light: "#07060F" },
    }).then(setQrUrl).catch(() => {});
  }, [refCode]);

  const truncatedText =
    interpretation.length > 280
      ? interpretation.slice(0, 280) + "..."
      : interpretation;

  const typeLabels: Record<string, string> = {
    tarot: t("share.type_tarot"),
    runes: t("share.type_runes"),
    numerology: t("share.type_numerology"),
    natal: t("share.type_natal"),
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,.85)",
        backdropFilter: "blur(12px)",
        zIndex: 200,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        overflowY: "auto",
        padding: "20px 0",
      }}
    >
      {/* Close button */}
      <button
        onClick={onClose}
        style={{
          position: "fixed",
          top: 16,
          right: 16,
          background: "none",
          border: "none",
          color: "#A89E8B",
          fontSize: 24,
          cursor: "pointer",
          zIndex: 201,
          lineHeight: 1,
        }}
      >
        ✕
      </button>

      {/* Card (captured by html2canvas) */}
      <div
        ref={cardRef}
        style={{
          width: 400,
          background:
            "linear-gradient(160deg, #0F0A26 0%, #07060F 60%, #120820 100%)",
          border: "1px solid rgba(201,168,76,.28)",
          borderRadius: 24,
          padding: 28,
          boxShadow:
            "0 0 60px rgba(75,60,134,.4), 0 0 120px rgba(201,168,76,.1)",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Stars background */}
        {stars.map((s) => (
          <div
            key={s.key}
            style={{
              position: "absolute",
              left: `${s.left}%`,
              top: `${s.top}%`,
              width: s.size,
              height: s.size,
              borderRadius: "50%",
              background: "#F0E9DA",
              opacity: s.opacity,
              pointerEvents: "none",
            }}
          />
        ))}

        {/* Corner decorations */}
        <div
          style={{
            position: "absolute",
            top: 12,
            left: 12,
            width: 16,
            height: 16,
            borderTop: "1px solid rgba(201,168,76,.3)",
            borderLeft: "1px solid rgba(201,168,76,.3)",
          }}
        />
        <div
          style={{
            position: "absolute",
            top: 12,
            right: 12,
            width: 16,
            height: 16,
            borderTop: "1px solid rgba(201,168,76,.3)",
            borderRight: "1px solid rgba(201,168,76,.3)",
          }}
        />
        <div
          style={{
            position: "absolute",
            bottom: 12,
            left: 12,
            width: 16,
            height: 16,
            borderBottom: "1px solid rgba(201,168,76,.3)",
            borderLeft: "1px solid rgba(201,168,76,.3)",
          }}
        />
        <div
          style={{
            position: "absolute",
            bottom: 12,
            right: 12,
            width: 16,
            height: 16,
            borderBottom: "1px solid rgba(201,168,76,.3)",
            borderRight: "1px solid rgba(201,168,76,.3)",
          }}
        />

        {/* Header */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 16,
            position: "relative",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Logo size={28} />
            <span
              className="font-cinzel"
              style={{
                fontSize: 12,
                letterSpacing: ".35em",
                color: "#E8CD7E",
              }}
            >
              MYSTRAL
            </span>
          </div>
          <span
            className="font-cinzel"
            style={{
              fontSize: 9,
              letterSpacing: ".2em",
              color: "#A99BE0",
              textTransform: "uppercase",
            }}
          >
            {typeLabels[type]}
          </span>
        </div>

        {/* Title */}
        <div style={{ marginBottom: 16, position: "relative" }}>
          <div
            className="font-cormorant"
            style={{ fontSize: 26, color: "#F0E9DA" }}
          >
            {title}
          </div>
          {subtitle && (
            <div style={{ fontSize: 13, color: "#8A8170", marginTop: 4 }}>
              {subtitle}
            </div>
          )}
        </div>

        {/* Visual block */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: 12,
            marginBottom: 16,
            position: "relative",
          }}
        >
          {type === "tarot" &&
            cards?.slice(0, 3).map((card) => (
              <div key={card.id} style={{ textAlign: "center", width: 80 }}>
                <img
                  src={`/tarot/${String(card.id).padStart(2, "0")}.jpg`}
                  width={80}
                  style={{
                    borderRadius: 8,
                    border: "1px solid rgba(201,168,76,.2)",
                    transform: card.reversed ? "rotate(180deg)" : undefined,
                  }}
                  alt={card.name}
                />
                <div
                  className="font-cinzel"
                  style={{
                    fontSize: 10,
                    color: "#C9A84C",
                    textAlign: "center",
                    marginTop: 4,
                  }}
                >
                  {lang === "ru" ? card.name_ru : card.name}
                </div>
              </div>
            ))}

          {type === "runes" &&
            runes?.slice(0, 3).map((rune) => (
              <div key={rune.id} style={{ textAlign: "center" }}>
                <div
                  style={{
                    width: 60,
                    height: 60,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    background: "rgba(75,60,134,.22)",
                    border: "1px solid rgba(138,127,192,.24)",
                    borderRadius: 12,
                  }}
                >
                  <span
                    style={{
                      fontSize: 28,
                      color: "#A99BE0",
                      transform: rune.reversed ? "rotate(180deg)" : undefined,
                      display: "inline-block",
                    }}
                  >
                    {rune.symbol}
                  </span>
                </div>
                <div
                  className="font-cinzel"
                  style={{ fontSize: 9, color: "#8A7FC0", marginTop: 4 }}
                >
                  {rune.name}
                </div>
              </div>
            ))}

          {type === "numerology" && (
            <div style={{ textAlign: "center" }}>
              <div
                className="font-cormorant"
                style={{
                  fontSize: 72,
                  color: "#F0E9DA",
                  filter: "drop-shadow(0 0 20px rgba(201,168,76,.4))",
                }}
              >
                {number}
              </div>
              {numberLabel && (
                <div
                  className="font-cinzel"
                  style={{
                    fontSize: 10,
                    letterSpacing: ".2em",
                    color: "#C9A84C",
                    textTransform: "uppercase",
                  }}
                >
                  {numberLabel}
                </div>
              )}
            </div>
          )}

          {type === "natal" && (
            <div style={{ textAlign: "center" }}>
              <div
                className="font-cormorant"
                style={{ fontSize: 48, color: "#F0E9DA" }}
              >
                {sign}
              </div>
              {subtitle && (
                <div
                  className="font-cinzel"
                  style={{ fontSize: 11, color: "#C9A84C", marginTop: 4 }}
                >
                  {subtitle}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Interpretation text */}
        <div
          style={{
            fontSize: 13,
            lineHeight: 1.65,
            color: "#B6AC98",
            padding: 14,
            borderRadius: 14,
            background: "rgba(255,255,255,.04)",
            border: "1px solid rgba(255,255,255,.07)",
            marginBottom: 16,
            position: "relative",
          }}
        >
          {truncatedText}
        </div>

        {/* Footer */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            position: "relative",
          }}
        >
          <div>
            <div
              className="font-cinzel"
              style={{ fontSize: 10, color: "#C9A84C" }}
            >
              mystral.space
            </div>
            <div style={{ fontSize: 11, color: "#6E6757", marginTop: 2 }}>
              {t("share.your_reading")}
            </div>
          </div>
          {qrUrl && (
            <img
              src={qrUrl}
              width={52}
              height={52}
              style={{ borderRadius: 6 }}
              alt="QR"
            />
          )}
        </div>
      </div>

      {/* Buttons (outside card ref, not captured in PNG) */}
      <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
        <button
          onClick={share}
          disabled={isLoading}
          style={{
            padding: "10px 24px",
            borderRadius: 12,
            border: "none",
            background: "linear-gradient(135deg, #C9A84C, #A9882F)",
            color: "#07060F",
            fontWeight: 600,
            fontSize: 14,
            cursor: isLoading ? "not-allowed" : "pointer",
            opacity: isLoading ? 0.7 : 1,
          }}
        >
          {isLoading ? "..." : t("share.download")}
        </button>
        <button
          onClick={() =>
            window.open(
              `https://t.me/share/url?url=https://mystral.space/ref/${refCode || ""}&text=${encodeURIComponent(t("share.tg_text"))}`,
              "_blank"
            )
          }
          style={{
            padding: "10px 24px",
            borderRadius: 12,
            border: "1px solid rgba(201,168,76,.3)",
            background: "rgba(201,168,76,.08)",
            color: "#C9A84C",
            fontWeight: 500,
            fontSize: 14,
            cursor: "pointer",
          }}
        >
          Telegram
        </button>
      </div>
      <p
        style={{
          fontSize: 11,
          color: "#6E6757",
          textAlign: "center",
          marginTop: 10,
        }}
      >
        {t("share.promo")}
      </p>
    </div>
  );
}
