import { useState } from "react";
import { useTranslation } from "react-i18next";
import { PaywallSheet } from "../components/PaywallSheet";
import { TarotCard } from "../components/tarot/TarotCard";
import { BottomNav, Button, Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { SPREADS, SpreadType } from "../data/spreads";
import { apiRequest, streamRequest } from "../utils/api";

interface TarotProps {
  onNavigate: (page: string) => void;
}

interface DrawnCard {
  id: number;
  name: string;
  reversed: boolean;
}

type Step = "select" | "question" | "spread" | "reading";

export function Tarot({ onNavigate }: TarotProps) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const lang = user?.lang ?? "ru";

  const [step, setStep] = useState<Step>("select");
  const [spread, setSpread] = useState<SpreadType | null>(null);
  const [schemeIdx, setSchemeIdx] = useState(0);
  const [question, setQuestion] = useState("");
  const [cards, setCards] = useState<DrawnCard[]>([]);
  const [positions, setPositions] = useState<string[]>([]);
  const [revealed, setRevealed] = useState<boolean[]>([]);
  const [interpretation, setInterpretation] = useState("");
  const [isReading, setIsReading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);

  function selectSpread(s: SpreadType) {
    if (s.tier === "pro" && user?.tier !== "pro") {
      setShowPaywall(true);
      return;
    }
    setSpread(s);
    setSchemeIdx(0);
    setQuestion("");
    if (s.id === "card_of_day") {
      doSpread(s, s.positions_ru);
    } else {
      setStep("question");
    }
  }

  async function doSpread(s: SpreadType, pos: string[]) {
    setLoading(true);
    try {
      const data = await apiRequest<{ cards: DrawnCard[] }>(
        "/tarot/spread",
        { spread_id: s.id, positions: pos, question: question || null },
        token ?? undefined,
      );
      setCards(data.cards);
      setPositions(pos);
      setRevealed(new Array(data.cards.length).fill(false));
      setInterpretation("");
      setStep("spread");
    } catch (e: unknown) {
      const err = e as { code?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
    } finally {
      setLoading(false);
    }
  }

  function handleProceed() {
    if (!spread) return;
    const pos = spread.schemes
      ? (lang === "ru" ? spread.schemes[schemeIdx].ru : spread.schemes[schemeIdx].en)
      : (lang === "ru" ? spread.positions_ru : spread.positions_en);
    doSpread(spread, pos);
  }

  function revealCard(i: number) {
    setRevealed(prev => { const n = [...prev]; n[i] = true; return n; });
  }

  async function handleInterpret() {
    if (!spread) return;
    setIsReading(true);
    setInterpretation("");
    try {
      await streamRequest(
        "/tarot/interpret",
        { spread_id: spread.id, cards, positions, question: question || null, lang },
        (chunk) => setInterpretation(prev => prev + chunk),
        () => setIsReading(false),
        token ?? undefined,
      );
    } catch (e: unknown) {
      const err = e as { code?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setInterpretation(t("tarot.error"));
      setIsReading(false);
    }
  }

  function reset() {
    setStep("select");
    setSpread(null);
    setCards([]);
    setInterpretation("");
  }

  const allRevealed = revealed.length > 0 && revealed.every(Boolean);

  const inputCls =
    "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 " +
    "text-text-primary text-sm placeholder:text-text-faint " +
    "focus:outline-none focus:border-violet-600 transition-colors";

  return (
    <div className="flex flex-col min-h-screen bg-bg-deep">
      <header
        className="flex items-center justify-between px-4 shrink-0 backdrop-blur-sm"
        style={{ height: 46, background: "rgba(6,4,20,0.75)" }}
      >
        <button
          className="text-text-muted text-lg w-8"
          onClick={() => step === "select" ? onNavigate("home") : reset()}
        >
          ‹
        </button>
        <span className="font-display text-text-primary text-base tracking-widest">✦ {t("tarot.header")}</span>
        <div className="w-8" />
      </header>

      <main className="flex-1 px-4 pt-6 pb-24 overflow-y-auto">

        {/* Step 1: Spread selection */}
        {step === "select" && (
          <div className="flex flex-col gap-3">
            <p className="text-text-faint text-[10px] uppercase tracking-widest mb-2">{t("tarot.choose_spread")}</p>
            <div className="grid grid-cols-2 gap-2">
              {SPREADS.map(s => (
                <Card
                  key={s.id}
                  className="cursor-pointer hover:border-border-medium transition-all active:scale-[0.98] relative"
                  onClick={() => selectSpread(s)}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg">{s.icon}</span>
                    <span className="text-text-primary text-xs font-display">{lang === "ru" ? s.name_ru : s.name_en}</span>
                  </div>
                  <p className="text-text-faint text-[10px] leading-tight">{lang === "ru" ? s.desc_ru : s.desc_en}</p>
                  <div className="flex items-center gap-1.5 mt-2">
                    <span className="text-text-faint text-[9px]">{s.count} {t("tarot.cards_label")}</span>
                    {s.tier === "pro" && (
                      <span className="text-[8px] px-1.5 py-0.5 rounded-full" style={{ background: "#C9A84C", color: "#0D0B1F" }}>Pro</span>
                    )}
                    {s.tier === "free" && (
                      <span className="text-[8px] px-1.5 py-0.5 rounded-full" style={{ background: "rgba(107,78,255,0.2)", color: "#9B8AFF" }}>Free</span>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Question */}
        {step === "question" && spread && (
          <div className="flex flex-col gap-4">
            <p className="font-display text-xl text-text-primary font-light text-center">
              {lang === "ru" ? spread.name_ru : spread.name_en}
            </p>

            {spread.schemes && (
              <div className="flex flex-col gap-1.5">
                <p className="text-text-faint text-[10px] uppercase tracking-widest">{t("tarot.position_scheme")}</p>
                {spread.schemes.map((scheme, i) => (
                  <button
                    key={i}
                    onClick={() => setSchemeIdx(i)}
                    className="text-left px-3 py-2 rounded-lg text-xs transition-colors"
                    style={{
                      background: schemeIdx === i ? "rgba(107,78,255,0.15)" : "transparent",
                      color: schemeIdx === i ? "#9B8AFF" : "#9B8FBB",
                      border: `1px solid ${schemeIdx === i ? "rgba(107,78,255,0.3)" : "rgba(107,78,255,0.08)"}`,
                    }}
                  >
                    {(lang === "ru" ? scheme.ru : scheme.en).join(" · ")}
                  </button>
                ))}
              </div>
            )}

            <div>
              <p className="text-text-faint text-[10px] uppercase tracking-widest mb-1.5">{t("tarot.your_question")}</p>
              <textarea
                className={inputCls + " min-h-[60px] resize-none"}
                placeholder={t("tarot.question_placeholder")}
                value={question}
                onChange={e => setQuestion(e.target.value)}
              />
              <p className="text-text-faint text-[10px] mt-1">{t("tarot.question_hint")}</p>
            </div>

            <Button variant="primary" className="w-full" onClick={handleProceed} disabled={loading}>
              {loading ? "..." : t("tarot.draw_cards")}
            </Button>
          </div>
        )}

        {/* Step 3: Cards */}
        {step === "spread" && (
          <div className="flex flex-col gap-4">
            {spread && (
              <p className="font-display text-lg text-text-primary font-light text-center mb-2">
                {lang === "ru" ? spread.name_ru : spread.name_en}
              </p>
            )}

            <div className="flex flex-wrap justify-center gap-3" style={{ perspective: "800px" }}>
              {cards.map((card, i) => (
                <div key={i} onClick={() => revealCard(i)} className="flex flex-col items-center">
                  <TarotCard
                    cardId={card.id}
                    name={card.name}
                    revealed={revealed[i]}
                    reversed={card.reversed}
                    delay={i * 100}
                  />
                  {revealed[i] && (
                    <div className="mt-1.5 text-center max-w-[88px]">
                      <p style={{ fontSize: 8, color: "rgba(200,180,255,0.6)", fontFamily: "serif" }}>{card.name}</p>
                      <p className="text-text-faint text-[8px]">{positions[i]}</p>
                      {card.reversed && (
                        <p className="text-[8px]" style={{ color: "#f87171" }}>{t("tarot.reversed")}</p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {!allRevealed && (
              <p className="text-text-faint text-xs text-center">{t("tarot.tap_hint")}</p>
            )}

            {allRevealed && !isReading && !interpretation && (
              <Button variant="primary" className="w-full" onClick={handleInterpret}>
                {t("tarot.interpret")}
              </Button>
            )}

            {interpretation && (
              <Card>
                <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">
                  {t("tarot.interpretation_label")}
                </p>
                {question && (
                  <p className="text-text-faint text-[10px] italic mb-2">"{question}"</p>
                )}
                <p className="text-text-muted text-xs leading-relaxed">
                  {interpretation}
                  {isReading && <span className="animate-pulse">▍</span>}
                </p>
              </Card>
            )}

            {allRevealed && !isReading && (
              <Button variant="ghost" className="w-full" onClick={reset}>
                {t("tarot.new_spread")}
              </Button>
            )}
          </div>
        )}

      </main>

      <BottomNav active="tarot" onNavigate={onNavigate} />
      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
    </div>
  );
}
