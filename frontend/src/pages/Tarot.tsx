import { useState } from "react";
import { useTranslation } from "react-i18next";
import { PaywallSheet } from "../components/PaywallSheet";
import { TarotCard } from "../components/tarot/TarotCard";
import { BottomNav, Button, Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { TarotCardData, drawCards } from "../data/tarot";
import { streamRequest } from "../utils/api";

interface TarotProps {
  onNavigate: (page: string) => void;
}

export function Tarot({ onNavigate }: TarotProps) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const [cards, setCards] = useState<TarotCardData[]>(() => drawCards(3));
  const [revealed, setRevealState] = useState([false, false, false]);
  const [isReading, setIsReading] = useState(false);
  const [interpretation, setInterpretation] = useState("");
  const [showPaywall, setShowPaywall] = useState(false);

  function revealCard(i: number) {
    setRevealState(prev => {
      const next = [...prev];
      next[i] = true;
      return next;
    });
  }

  function newSpread() {
    setCards(drawCards(3));
    setRevealState([false, false, false]);
    setInterpretation("");
    setIsReading(false);
  }

  async function handleInterpret() {
    setIsReading(true);
    setInterpretation("");
    try {
      await streamRequest(
        "/tarot/interpret",
        {
          cards: cards.map(c => c.name_ru),
          positions: [t("tarot.past"), t("tarot.present"), t("tarot.future")],
          lang: user?.lang ?? "ru",
        },
        (chunk) => setInterpretation(prev => prev + chunk),
        () => setIsReading(false),
        token ?? undefined
      );
    } catch (e: unknown) {
      const err = e as { code?: string };
      if (err.code === "FREE_LIMIT_REACHED") {
        setShowPaywall(true);
      } else {
        setInterpretation(t("tarot.error"));
      }
      setIsReading(false);
    }
  }

  const allRevealed = revealed.every(Boolean);
  const rotations = [-8, 0, 8];

  return (
    <div className="flex flex-col min-h-screen bg-bg-deep">

      <header
        className="flex items-center justify-between px-4 shrink-0 backdrop-blur-sm"
        style={{ height: 46, background: "rgba(6,4,20,0.75)" }}
      >
        <button
          className="text-text-muted text-lg w-8"
          onClick={() => onNavigate("home")}
        >
          ‹
        </button>
        <span className="font-display text-text-primary text-base tracking-widest">✦ Mystral</span>
        <div className="w-8" />
      </header>

      <main className="flex-1 px-4 pt-6 pb-24 overflow-y-auto">

        <p className="text-text-faint text-[10px] uppercase tracking-widest mb-1">
          {t("tarot.title")}
        </p>
        <p className="font-display text-xl text-text-primary font-light mb-6">
          {t("tarot.spread")}
        </p>

        <div className="flex justify-center gap-3 mb-8" style={{ perspective: "800px" }}>
          {cards.map((card, i) => (
            <div
              key={card.id}
              style={{ transform: `rotate(${rotations[i]}deg)`, marginTop: i === 1 ? 0 : 8 }}
              onClick={() => revealCard(i)}
            >
              <TarotCard card={card} revealed={revealed[i]} delay={0} />
              {revealed[i] && (
                <div style={{ textAlign: "center", marginTop: 6 }}>
                  <span style={{ fontSize: 9, color: "rgba(200,180,255,0.6)", fontFamily: "serif", letterSpacing: "0.05em" }}>
                    {card.name_ru}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>

        {!allRevealed && (
          <p className="text-text-faint text-xs text-center mb-6">
            {t("tarot.tap_hint")}
          </p>
        )}

        {allRevealed && !isReading && !interpretation && (
          <Button variant="primary" className="w-full mb-4" onClick={handleInterpret}>
            {t("tarot.interpret")}
          </Button>
        )}

        {interpretation && (
          <Card className="mb-4">
            <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">
              {t("tarot.interpretation_label")}
            </p>
            <p className="text-text-muted text-xs leading-relaxed">
              {interpretation}
              {isReading && <span className="animate-pulse">▍</span>}
            </p>
          </Card>
        )}

        {allRevealed && !isReading && (
          <Button variant="ghost" className="w-full" onClick={newSpread}>
            {t("tarot.new_spread")}
          </Button>
        )}

      </main>

      <BottomNav active="tarot" onNavigate={onNavigate} />

      <PaywallSheet
        open={showPaywall}
        onClose={() => setShowPaywall(false)}
      />
    </div>
  );
}
