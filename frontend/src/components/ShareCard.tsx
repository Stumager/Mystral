import { useRef, useMemo } from "react";
import { useTranslation } from "react-i18next";
import { Logo } from "./Logo";
import { useShareCard } from "../hooks/useShareCard";

interface ShareCardProps {
  type: "tarot" | "runes" | "numerology" | "natal" | "compat" | "lunar" | "composite";
  title: string;
  subtitle?: string;
  cards?: { id: number; name: string; name_ru: string; reversed: boolean }[];
  runes?: { id: string; name: string; symbol: string; reversed: boolean }[];
  number?: number;
  numberLabel?: string;
  natalName?: string;
  bigThree?: { label: string; sign: string; degree: number }[];
  score?: number;
  scoreLabel?: string;
  aspectLabel?: string;
  description?: string;
  lunarDay?: number;
  lunarPhase?: string;
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
  type, title, subtitle, cards, runes, number, numberLabel,
  natalName, bigThree, score, scoreLabel, aspectLabel, description,
  lunarDay, lunarPhase, onClose,
}: ShareCardProps) {
  const { t, i18n } = useTranslation();
  const cardRef = useRef<HTMLDivElement>(null);
  const { share, shareToTelegram, isLoading, feedback } = useShareCard(cardRef);
  const lang = i18n.language;

  const stars = useMemo(() => {
    const rng = seededRandom(42);
    return Array.from({ length: 25 }, (_, i) => ({
      key: i, left: rng() * 100, top: rng() * 100,
      size: 1 + rng() * 2, opacity: 0.15 + rng() * 0.35,
    }));
  }, []);

  const typeLabels: Record<string, string> = {
    tarot: t("share.type_tarot"), runes: t("share.type_runes"),
    numerology: t("share.type_numerology"), natal: t("share.type_natal"),
    compat: t("share.type_compat"), lunar: t("share.type_lunar"),
    composite: t("share.type_composite"),
  };

  const showCards = cards?.slice(0, 5) ?? [];
  const cardW = showCards.length <= 3 ? 80 : showCards.length <= 4 ? 72 : 62;

  return (
    <div
      onClick={e => e.target === e.currentTarget && onClose()}
      style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,.85)", backdropFilter: "blur(12px)", zIndex: 200, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", overflowY: "auto", padding: 20 }}
    >
      <button onClick={onClose} style={{ position: "fixed", top: 16, right: 16, background: "none", border: "none", color: "#A89E8B", fontSize: 24, cursor: "pointer", zIndex: 201 }}>✕</button>

      {/* PNG card */}
      <div ref={cardRef} style={{ width: "100%", maxWidth: 400, background: "linear-gradient(160deg, #0F0A26 0%, #07060F 60%, #120820 100%)", border: "1px solid rgba(201,168,76,.28)", borderRadius: 24, padding: "26px 22px 22px", boxShadow: "0 0 60px rgba(75,60,134,.4), 0 0 120px rgba(201,168,76,.1)", position: "relative", overflow: "hidden" }}>

        {stars.map(s => (
          <div key={s.key} style={{ position: "absolute", left: `${s.left}%`, top: `${s.top}%`, width: s.size, height: s.size, borderRadius: "50%", background: "#F0E9DA", opacity: s.opacity, pointerEvents: "none" }} />
        ))}

        {[
          { top: 10, left: 10, borderTop: "1px solid rgba(201,168,76,.25)", borderLeft: "1px solid rgba(201,168,76,.25)" },
          { top: 10, right: 10, borderTop: "1px solid rgba(201,168,76,.25)", borderRight: "1px solid rgba(201,168,76,.25)" },
          { bottom: 10, left: 10, borderBottom: "1px solid rgba(201,168,76,.25)", borderLeft: "1px solid rgba(201,168,76,.25)" },
          { bottom: 10, right: 10, borderBottom: "1px solid rgba(201,168,76,.25)", borderRight: "1px solid rgba(201,168,76,.25)" },
        ].map((s, i) => <div key={i} style={{ position: "absolute", width: 14, height: 14, ...s } as React.CSSProperties} />)}

        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18, position: "relative" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Logo size={26} />
            <span className="font-cinzel" style={{ fontSize: 11, letterSpacing: ".35em", color: "#E8CD7E" }}>MYSTRAL</span>
          </div>
          <span className="font-cinzel" style={{ fontSize: 9, letterSpacing: ".18em", color: "#A99BE0", textTransform: "uppercase" }}>{typeLabels[type]}</span>
        </div>

        {/* Title */}
        <div className="font-cormorant" style={{ fontSize: 24, color: "#F0E9DA", lineHeight: 1.15, marginBottom: 4, position: "relative" }}>{title}</div>
        {subtitle && <div style={{ fontSize: 12, color: "#8A8170", marginBottom: 6, position: "relative" }}>{subtitle}</div>}

        {/* Divider */}
        <div style={{ height: 1, background: "linear-gradient(90deg, transparent, rgba(201,168,76,.25), transparent)", margin: "10px 0 16px", position: "relative" }} />

        {/* Visual */}
        <div style={{ display: "flex", justifyContent: "center", gap: showCards.length > 3 ? 5 : 8, flexWrap: "wrap", marginBottom: 16, position: "relative" }}>

          {type === "tarot" && showCards.map(card => (
            <div key={card.id} style={{ textAlign: "center", width: cardW }}>
              <img src={`/tarot/${card.id}.jpg?v=2`} width={cardW}
                style={{ borderRadius: 6, border: "1px solid rgba(201,168,76,.2)", transform: card.reversed ? "rotate(180deg)" : undefined, display: "block" }}
                alt={card.name} crossOrigin="anonymous" />
              <div className="font-cinzel" style={{ fontSize: cardW > 70 ? 8 : 7, color: card.reversed ? "#D98A8A" : "#C9A84C", marginTop: 3, lineHeight: 1.15 }}>
                {lang === "ru" ? card.name_ru : card.name}
              </div>
            </div>
          ))}

          {type === "runes" && runes?.slice(0, 5).map(rune => (
            <div key={rune.id} style={{ textAlign: "center" }}>
              <div style={{ width: 54, height: 54, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(75,60,134,.22)", border: "1px solid rgba(138,127,192,.24)", borderRadius: 12 }}>
                <span style={{ fontSize: 26, color: "#A99BE0", transform: rune.reversed ? "rotate(180deg)" : undefined, display: "inline-block" }}>{rune.symbol}</span>
              </div>
              <div className="font-cinzel" style={{ fontSize: 8, color: rune.reversed ? "#D98A8A" : "#8A7FC0", marginTop: 3 }}>{rune.name}</div>
            </div>
          ))}
          {type === "runes" && runes?.some(r => r.reversed) && (
            <div style={{ flexBasis: "100%", textAlign: "center", fontSize: 9, color: "#6E6757", marginTop: 4 }}>
              {t("share.reversed_hint")}
            </div>
          )}

          {type === "numerology" && (
            <div style={{ textAlign: "center", padding: "8px 0" }}>
              <div className="font-cormorant" style={{ fontSize: 72, color: "#F0E9DA", filter: "drop-shadow(0 0 20px rgba(201,168,76,.4))", lineHeight: 1 }}>{number}</div>
              {numberLabel && <div className="font-cinzel" style={{ fontSize: 10, letterSpacing: ".2em", color: "#C9A84C", textTransform: "uppercase", marginTop: 6 }}>{numberLabel}</div>}
            </div>
          )}

          {type === "natal" && bigThree && bigThree.length > 0 && (
            <div style={{ width: "100%", padding: "4px 0" }}>
              {natalName && (
                <div className="font-cormorant" style={{ fontSize: 20, color: "#F0E9DA", textAlign: "center", marginBottom: 10 }}>
                  {natalName}
                </div>
              )}
              <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                {bigThree.map((b, i) => (
                  <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", padding: "6px 0", borderBottom: i < bigThree.length - 1 ? "1px solid rgba(255,255,255,.06)" : "none" }}>
                    <span style={{ fontSize: 13, color: "#A89E8B" }}>{b.label}</span>
                    <span className="font-cormorant" style={{ fontSize: 16, color: "#C9A84C" }}>
                      {b.sign} <span style={{ fontSize: 11, color: "#8A8170" }}>{b.degree}°</span>
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {type === "composite" && (
            <div style={{ textAlign: "center", padding: "8px 0" }}>
              {aspectLabel && (
                <div className="font-cormorant" style={{ fontSize: 22, color: "#F0E9DA" }}>{aspectLabel}</div>
              )}
              {description && (
                <div style={{ fontSize: 12, color: "#8A8170", marginTop: 8, lineHeight: 1.5 }}>{description}</div>
              )}
            </div>
          )}

          {type === "compat" && score != null && (
            <div style={{ textAlign: "center", padding: "8px 0" }}>
              <div className="font-cormorant" style={{ fontSize: 64, color: score >= 75 ? "#C9A84C" : score >= 50 ? "#A99BE0" : "#D98A8A", filter: "drop-shadow(0 0 16px rgba(201,168,76,.3))", lineHeight: 1 }}>
                {score}%
              </div>
              {scoreLabel && <div style={{ fontSize: 13, color: "#8A8170", marginTop: 6 }}>{scoreLabel}</div>}
            </div>
          )}

          {type === "lunar" && lunarDay != null && (
            <div style={{ textAlign: "center", padding: "8px 0" }}>
              <div style={{ fontSize: 48, lineHeight: 1 }}>🌙</div>
              <div className="font-cormorant" style={{ fontSize: 36, color: "#F0E9DA", marginTop: 4 }}>{lunarDay}</div>
              {lunarPhase && <div style={{ fontSize: 12, color: "#A99BE0", marginTop: 4 }}>{lunarPhase}</div>}
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", position: "relative", paddingTop: 10, borderTop: "1px solid rgba(201,168,76,.12)" }}>
          <div>
            <div className="font-cinzel" style={{ fontSize: 10, color: "#C9A84C", letterSpacing: ".15em" }}>mystral.space</div>
            <div style={{ fontSize: 10, color: "#6E6757", marginTop: 2 }}>{t("share.your_reading")}</div>
          </div>
          <div className="font-cinzel" style={{ fontSize: 8, color: "#6E6757", letterSpacing: ".1em", textAlign: "right" }}>
            {t("share.try_free")}
          </div>
        </div>
      </div>

      {/* Buttons */}
      <div style={{ display: "flex", gap: 12, marginTop: 16, flexWrap: "wrap", justifyContent: "center" }}>
        <button onClick={() => share()} disabled={isLoading}
          style={{ height: 46, padding: "0 24px", borderRadius: 14, border: "none", background: "linear-gradient(135deg, #C9A84C, #A9882F)", color: "#07060F", fontWeight: 600, fontSize: 14, cursor: isLoading ? "not-allowed" : "pointer", opacity: isLoading ? 0.7 : 1 }}>
          {isLoading ? "..." : t("share.download")}
        </button>
        <button onClick={() => shareToTelegram(t("share.tg_text"))} disabled={isLoading}
          style={{ height: 46, padding: "0 24px", borderRadius: 14, border: "1px solid rgba(201,168,76,.3)", background: "rgba(201,168,76,.08)", color: "#C9A84C", fontWeight: 500, fontSize: 14, cursor: isLoading ? "not-allowed" : "pointer", opacity: isLoading ? 0.7 : 1 }}>
          Telegram
        </button>
      </div>
      {feedback && (
        <p style={{ fontSize: 12, color: "#C9A84C", textAlign: "center", marginTop: 12, maxWidth: 320, lineHeight: 1.5 }}>{feedback}</p>
      )}
      <p style={{ fontSize: 11, color: "#6E6757", textAlign: "center", marginTop: 10 }}>{t("share.promo")}</p>
    </div>
  );
}
