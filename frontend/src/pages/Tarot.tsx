import { useState } from "react";
import { useTranslation } from "react-i18next";
import { PaywallSheet } from "../components/PaywallSheet";
import { ShareCard } from "../components/ShareCard";
import { TarotCard } from "../components/tarot/TarotCard";
import { BottomNav, Button } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { SPREADS, SpreadType } from "../data/spreads";
import { apiRequest, streamRequest } from "../utils/api";

interface TarotProps {
  onNavigate: (page: string) => void;
}

interface DrawnCard {
  id: number;
  name: string;
  name_ru: string;
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
  const [error, setError] = useState("");
  const [showPaywall, setShowPaywall] = useState(false);
  const [showShareCard, setShowShareCard] = useState(false);

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
    setError("");
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
      else setError(t("tarot.error"));
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
        (msg) => { setInterpretation(msg); setIsReading(false); },
      );
    } catch (e: unknown) {
      const err = e as { code?: string; message?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setInterpretation(err.message || t("tarot.error"));
      setIsReading(false);
    }
  }

  function reset() {
    setStep("select");
    setSpread(null);
    setCards([]);
    setInterpretation("");
    setError("");
  }

  const allRevealed = revealed.length > 0 && revealed.every(Boolean);

  const inputCls =
    "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 " +
    "text-text-primary text-sm placeholder:text-text-faint " +
    "focus:outline-none focus:border-violet-600 transition-colors";

  return (
    <div className="flex flex-col min-h-screen" style={{ background: "var(--gradient-page)", animation: "mystral-fadeup .3s ease-out" }}>
      <header
        className="flex items-center justify-between px-4 shrink-0 backdrop-blur-md lg:hidden"
        style={{ height: 46, background: "var(--bg-header)", borderBottom: "1px solid var(--border-gold)" }}
      >
        <button
          className="text-text-muted text-lg w-8"
          onClick={() => step === "select" ? onNavigate("home") : reset()}
        >
          ‹
        </button>
        <span className="font-cinzel" style={{ fontSize: 13, letterSpacing: ".26em", color: "#E8CD7E" }}>
          {t("tarot.header")}
        </span>
        <div className="w-8" />
      </header>

      <main className="flex-1 px-4 pt-6 pb-24 overflow-y-auto">

        {/* Step 1: Spread selection */}
        {step === "select" && (
          <div className="flex flex-col gap-3">
            <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C", marginBottom: 8 }}>
              {t("tarot.choose_spread")}
            </p>
            <div className="flex flex-col gap-2.5">
              {SPREADS.map(s => {
                const accents: Record<string, string> = {
                  card_of_day: "rgba(201,168,76,.15)", three_cards: "rgba(75,60,134,.2)",
                  celtic_cross: "rgba(138,127,192,.15)", horseshoe: "rgba(110,154,138,.15)",
                  relationship: "rgba(196,84,84,.12)", yes_no: "rgba(201,168,76,.1)",
                  two_choices: "rgba(75,60,134,.15)", person: "rgba(138,127,192,.12)", year: "rgba(110,154,138,.12)",
                };
                const accent = accents[s.id] || "rgba(255,255,255,.03)";
                return (
                <div
                  key={s.id}
                  className="cursor-pointer transition-all active:scale-[0.98]"
                  style={{
                    padding: "18px 20px",
                    borderRadius: "0 18px 18px 0",
                    background: accent,
                    border: "1px solid rgba(201,168,76,.13)",
                    borderLeft: `3px solid ${accent.replace(/[\d.]+\)$/, ".6)")}`,
                  }}
                  onClick={() => selectSpread(s)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <span className="shrink-0" style={{ width: 44, height: 44, borderRadius: 12, background: "rgba(201,168,76,.08)", border: "1px solid rgba(201,168,76,.2)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20, color: "#C9A84C" }}>{s.icon}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-cormorant text-text-primary" style={{ fontSize: 16 }}>
                            {lang === "ru" ? s.name_ru : s.name_en}
                          </span>
                          {s.tier === "pro" && (
                            <span className="text-[8px] px-1.5 py-0.5 rounded-full shrink-0" style={{ background: "#C9A84C", color: "#0D0B1F" }}>Pro</span>
                          )}
                          {s.tier === "free" && (
                            <span className="text-[8px] px-1.5 py-0.5 rounded-full shrink-0" style={{ background: "rgba(201,168,76,.1)", color: "#C9A84C" }}>Free</span>
                          )}
                        </div>
                        <p className="text-text-faint text-[11px] leading-tight mt-0.5">{lang === "ru" ? s.desc_ru : s.desc_en}</p>
                        <span className="text-text-faint text-[9px] mt-1 inline-block">{s.count} {t("tarot.cards_label")}</span>
                      </div>
                    </div>
                    <span className="text-text-faint text-sm ml-2 shrink-0" style={{ color: "rgba(201,168,76,.4)" }}>{"›"}</span>
                  </div>
                </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Step 2: Question */}
        {step === "question" && spread && (
          <div className="flex flex-col gap-4">
            <p className="font-cormorant text-text-primary font-light text-center" style={{ fontSize: 22, color: "#F0E9DA" }}>
              {lang === "ru" ? spread.name_ru : spread.name_en}
            </p>

            {spread.schemes && (
              <div className="flex flex-col gap-1.5">
                <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                  {t("tarot.position_scheme")}
                </p>
                {spread.schemes.map((scheme, i) => (
                  <button
                    key={i}
                    onClick={() => setSchemeIdx(i)}
                    className="text-left px-3 py-2 text-xs transition-colors"
                    style={{
                      borderRadius: 14,
                      background: schemeIdx === i ? "rgba(201,168,76,.15)" : "transparent",
                      color: schemeIdx === i ? "#E8CD7E" : "#9B8FBB",
                      border: `1px solid ${schemeIdx === i ? "rgba(201,168,76,.3)" : "rgba(201,168,76,.08)"}`,
                    }}
                  >
                    {(lang === "ru" ? scheme.ru : scheme.en).join(" · ")}
                  </button>
                ))}
              </div>
            )}

            <div>
              <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C", marginBottom: 6 }}>
                {t("tarot.your_question")}
              </p>
              <textarea
                className={inputCls + " min-h-[60px] resize-none"}
                placeholder={t("tarot.question_placeholder")}
                value={question}
                onChange={e => setQuestion(e.target.value)}
              />
              <p className="text-text-faint text-[10px] mt-1">{t("tarot.question_hint")}</p>
            </div>

            {error && <p className="text-red-400 text-xs text-center">{error}</p>}

            <Button variant="primary" className="w-full" style={{ height: 50, borderRadius: 14 }} onClick={handleProceed} disabled={loading}>
              {loading ? "..." : t("tarot.draw_cards")}
            </Button>
          </div>
        )}

        {/* Step 3: Cards */}
        {step === "spread" && (
          <div className="flex flex-col gap-4">
            {spread && (
              <p className="font-cormorant text-text-primary font-light text-center mb-2" style={{ fontSize: 22, color: "#F0E9DA" }}>
                {lang === "ru" ? spread.name_ru : spread.name_en}
              </p>
            )}

            <div className="flex flex-wrap justify-center gap-3" style={{ perspective: "800px" }}>
              {cards.map((card, i) => (
                <div key={i} onClick={() => revealCard(i)} className="flex flex-col items-center">
                  <TarotCard
                    cardId={card.id}
                    name={(lang === "ru" ? card.name_ru : card.name) || card.name}
                    revealed={revealed[i]}
                    reversed={card.reversed}
                    delay={i * 100}
                  />
                  {revealed[i] && (
                    <div className="mt-1.5 text-center max-w-[88px]">
                      <p style={{ fontSize: 8, color: "rgba(200,180,255,0.6)", fontFamily: "serif" }}>{(lang === "ru" ? card.name_ru : card.name) || card.name}</p>
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
              <Button variant="primary" className="w-full" style={{ height: 50, borderRadius: 14 }} onClick={handleInterpret}>
                {t("tarot.interpret")}
              </Button>
            )}

            {interpretation && (
              <div
                className="p-4"
                style={{
                  borderRadius: 18,
                  background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))",
                  border: "1px solid rgba(201,168,76,.13)",
                }}
              >
                <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C", marginBottom: 8 }}>
                  {t("tarot.interpretation_label")}
                </p>
                {question && (
                  <p className="text-text-faint text-[10px] italic mb-2">"{question}"</p>
                )}
                <p className="text-text-muted text-xs leading-relaxed">
                  {interpretation}
                  {isReading && <span className="animate-pulse">{"▍"}</span>}
                </p>
              </div>
            )}

            {interpretation && !isReading && (
              <button onClick={() => setShowShareCard(true)}
                style={{ width: "100%", height: 44, marginTop: 12, borderRadius: 14, border: "1px solid rgba(201,168,76,.25)", background: "transparent", color: "#C9A84C", fontSize: 13, cursor: "pointer" }}>
                {t("share.share_btn")}
              </button>
            )}

            {allRevealed && !isReading && (
              <Button variant="gold" className="w-full" style={{ height: 50, borderRadius: 14 }} onClick={reset}>
                {t("tarot.new_spread")}
              </Button>
            )}
          </div>
        )}

      </main>

      <BottomNav active="tarot" onNavigate={onNavigate} />
      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
      {showShareCard && spread && (
        <ShareCard
          type="tarot"
          title={lang === "ru" ? spread.name_ru : spread.name_en}
          cards={cards.slice(0, 5)}
          onClose={() => setShowShareCard(false)}
        />
      )}
    </div>
  );
}
