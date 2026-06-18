import { useState } from "react";
import { TarotCard } from "../components/tarot/TarotCard";
import { BottomNav, Button, Card } from "../components/ui";
import { TarotCardData, drawCards } from "../data/tarot";
import { streamRequest } from "../utils/api";

interface TarotProps {
  onNavigate: (page: string) => void;
}

export function Tarot({ onNavigate }: TarotProps) {
  const [cards, setCards] = useState<TarotCardData[]>(() => drawCards(3));
  const [revealed, setRevealState] = useState([false, false, false]);
  const [isReading, setIsReading] = useState(false);
  const [interpretation, setInterpretation] = useState("");

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
          positions: ["прошлое", "настоящее", "будущее"],
          lang: "ru",
        },
        (chunk) => setInterpretation(prev => prev + chunk),
        () => setIsReading(false)
      );
    } catch {
      setInterpretation("Ошибка соединения. Попробуй ещё раз.");
      setIsReading(false);
    }
  }

  const allRevealed = revealed.every(Boolean);
  const rotations = [-8, 0, 8];

  return (
    <div className="flex flex-col min-h-screen bg-bg-deep max-w-[390px] mx-auto">

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
          Расклад дня
        </p>
        <p className="font-display text-xl text-text-primary font-light mb-6">
          Прошлое · Настоящее · Будущее
        </p>

        <div className="flex justify-center gap-3 mb-8" style={{ perspective: "800px" }}>
          {cards.map((card, i) => (
            <div
              key={card.id}
              style={{ transform: `rotate(${rotations[i]}deg)`, marginTop: i === 1 ? 0 : 8 }}
              onClick={() => revealCard(i)}
            >
              <TarotCard card={card} revealed={revealed[i]} delay={0} />
            </div>
          ))}
        </div>

        {!allRevealed && (
          <p className="text-text-faint text-xs text-center mb-6">
            Коснись карты чтобы открыть
          </p>
        )}

        {allRevealed && !isReading && !interpretation && (
          <Button variant="primary" className="w-full mb-4" onClick={handleInterpret}>
            Получить толкование ✦
          </Button>
        )}

        {interpretation && (
          <Card className="mb-4">
            <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">
              Толкование · AI
            </p>
            <p className="text-text-muted text-xs leading-relaxed">
              {interpretation}
              {isReading && <span className="animate-pulse">▍</span>}
            </p>
          </Card>
        )}

        {allRevealed && !isReading && (
          <Button variant="ghost" className="w-full" onClick={newSpread}>
            Новый расклад
          </Button>
        )}

      </main>

      <BottomNav active="tarot" onNavigate={onNavigate} />
    </div>
  );
}
