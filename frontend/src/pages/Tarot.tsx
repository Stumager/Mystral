import { useState } from "react";
import { useTranslation } from "react-i18next";
import { PaywallSheet } from "../components/PaywallSheet";
import { ShareCard } from "../components/ShareCard";
import { TarotCard } from "../components/tarot/TarotCard";
import { BottomNav, Button } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { SPREADS, SpreadType } from "../data/spreads";
import { apiRequest, streamRequest } from "../utils/api";
import { stripMarkdown } from "../utils/markdown";

interface TarotProps {
  onNavigate: (page: string) => void;
}

interface DrawnCard {
  id: number;
  name: string;
  name_ru: string;
  name_display: string;
  reversed: boolean;
}

type Step = "select" | "question" | "spread" | "reading";

// QA-022: celtic_cross and horseshoe used the same flex-wrap grid as every
// other spread, so nothing on screen hinted at the shape the name promises.
// Percent-based slots (relative to a fixed-height canvas) lay the cards out
// in their traditional geometry; cards are scaled down so a 10-card cross
// still fits mobile width. Every other spread id is untouched — it falls
// through to the existing flex-wrap layout below.
interface SpreadLayout { height: number; scale: number; positions: { x: number; y: number; rotate?: number }[]; }
const NAMED_SPREAD_LAYOUTS: Record<string, SpreadLayout> = {
  celtic_cross: {
    height: 460, scale: 0.5,
    positions: [
      { x: 38, y: 50 },              // 1: situation (center)
      { x: 38, y: 50, rotate: 90 },  // 2: obstacle (crossing)
      { x: 38, y: 14 },              // 3: above / goal
      { x: 38, y: 86 },              // 4: below / foundation
      { x: 14, y: 50 },              // 5: past
      { x: 62, y: 50 },              // 6: future
      { x: 86, y: 86 },              // 7: staff — self
      { x: 86, y: 62 },              // 8: staff — environment
      { x: 86, y: 38 },              // 9: staff — hopes/fears
      { x: 86, y: 14 },              // 10: staff — outcome
    ],
  },
  horseshoe: {
    height: 300, scale: 0.5,
    positions: [
      { x: 6, y: 12 }, { x: 20, y: 42 }, { x: 35, y: 66 }, { x: 50, y: 78 },
      { x: 65, y: 66 }, { x: 80, y: 42 }, { x: 94, y: 12 },
    ],
  },
};

// TZ-097: mirrors the backend's MAX_CLARIFICATIONS_PER_READING (tarot.py) —
// duplicated here only to disable the button early client-side; the backend
// stays the actual source of truth.
const MAX_CLARIFICATIONS = 2;

export function Tarot({ onNavigate }: TarotProps) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const lang = user?.lang ?? "ru";

  const [step, setStep] = useState<Step>("select");
  const [spread, setSpread] = useState<SpreadType | null>(null);
  const [schemeIdx, setSchemeIdx] = useState(0);
  const [question, setQuestion] = useState("");
  const [cards, setCards] = useState<DrawnCard[]>([]);
  const [readingId, setReadingId] = useState<string | null>(null);
  const [positions, setPositions] = useState<string[]>([]);
  const [revealed, setRevealed] = useState<boolean[]>([]);
  const [interpretation, setInterpretation] = useState("");
  const [isReading, setIsReading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showPaywall, setShowPaywall] = useState(false);
  const [showShareCard, setShowShareCard] = useState(false);
  const [clarifications, setClarifications] = useState<{ question: string; answer: string }[]>([]);
  const [clarifyOpen, setClarifyOpen] = useState(false);
  const [clarifyDraft, setClarifyDraft] = useState("");
  const [clarifyLoading, setClarifyLoading] = useState(false);
  const [clarifyError, setClarifyError] = useState("");
  // Distinguishes a real interpretation from streamRequest's error-message
  // fallback, which also lands in `interpretation` (existing pattern) — the
  // clarify feature needs to know the difference, or it'd offer to clarify
  // a reading that was never actually generated.
  const [interpretFailed, setInterpretFailed] = useState(false);

  // Display strings for a spread (name/desc/positions/schemes) live in the
  // locale files under tarot.spreads.<id>, in all 6 languages — i18next
  // already resolves to the active UI language, same as every other t() call.
  const spreadName = (id: string) => t(`tarot.spreads.${id}.name`);
  const spreadDesc = (id: string) => t(`tarot.spreads.${id}.desc`);
  const spreadPositions = (id: string) => t(`tarot.spreads.${id}.positions`, { returnObjects: true }) as string[];
  const spreadSchemes = (id: string) => t(`tarot.spreads.${id}.schemes`, { returnObjects: true }) as string[][];

  function selectSpread(s: SpreadType) {
    if (s.tier === "pro" && user?.tier !== "pro") {
      setShowPaywall(true);
      return;
    }
    setSpread(s);
    setSchemeIdx(0);
    setQuestion("");
    if (s.id === "card_of_day") {
      doSpread(s, spreadPositions(s.id));
    } else {
      setStep("question");
    }
  }

  async function doSpread(s: SpreadType, pos: string[], force = false) {
    setLoading(true);
    setError("");
    try {
      const data = await apiRequest<{ cards: DrawnCard[]; reading_id: string }>(
        "/tarot/spread",
        { spread_id: s.id, positions: pos, question: question || null, lang, force },
        token ?? undefined,
      );
      setCards(data.cards);
      setReadingId(data.reading_id);
      setPositions(pos);
      setRevealed(new Array(data.cards.length).fill(false));
      setInterpretation("");
      setInterpretFailed(false);
      setClarifications([]);
      setClarifyOpen(false);
      setClarifyDraft("");
      setClarifyError("");
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
    const pos = spread.schemeCount ? spreadSchemes(spread.id)[schemeIdx] : spreadPositions(spread.id);
    doSpread(spread, pos);
  }

  function revealCard(i: number) {
    setRevealed(prev => { const n = [...prev]; n[i] = true; return n; });
  }

  async function handleInterpret() {
    if (!spread) return;
    setIsReading(true);
    setInterpretation("");
    setInterpretFailed(false);
    try {
      await streamRequest(
        "/tarot/interpret",
        { spread_id: spread.id, cards, positions, question: question || null, lang, reading_id: readingId },
        (chunk) => setInterpretation(prev => prev + chunk),
        () => setIsReading(false),
        token ?? undefined,
        (msg) => { setInterpretation(msg); setInterpretFailed(true); setIsReading(false); },
      );
    } catch (e: unknown) {
      const err = e as { code?: string; message?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setInterpretation(err.message || t("tarot.error"));
      setInterpretFailed(true);
      setIsReading(false);
    }
  }

  function reset() {
    setStep("select");
    setSpread(null);
    setCards([]);
    setReadingId(null);
    setInterpretation("");
    setInterpretFailed(false);
    setClarifications([]);
    setClarifyOpen(false);
    setClarifyDraft("");
    setClarifyError("");
    setError("");
  }

  function handleClarifyToggle() {
    if (user?.tier !== "pro") { setShowPaywall(true); return; }
    if (clarifications.length >= MAX_CLARIFICATIONS) return;
    setClarifyOpen(o => !o);
  }

  async function submitClarify() {
    const q = clarifyDraft.trim();
    if (!q || !readingId || clarifyLoading) return;
    setClarifyLoading(true);
    setClarifyError("");
    setClarifyOpen(false);
    setClarifyDraft("");
    setClarifications(prev => [...prev, { question: q, answer: "" }]);
    // A failed attempt (thrown HTTP error, or an in-stream error event) never
    // gets persisted server-side (see store_clarification's full_text guard),
    // so it must not occupy a slot in the client-side array either — keeping
    // it would let a transient LLM hiccup silently eat into the per-reading
    // clarify limit.
    let failed = false;
    try {
      await streamRequest(
        "/tarot/clarify",
        { reading_id: readingId, question: q, lang },
        (chunk) => setClarifications(prev => {
          const next = [...prev];
          next[next.length - 1] = { ...next[next.length - 1], answer: next[next.length - 1].answer + chunk };
          return next;
        }),
        () => setClarifyLoading(false),
        token ?? undefined,
        (msg) => { failed = true; setClarifyError(msg); setClarifyLoading(false); },
      );
    } catch (e: unknown) {
      failed = true;
      const err = e as { code?: string; message?: string };
      setClarifyLoading(false);
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setClarifyError(err.message || t("tarot.error"));
    } finally {
      if (failed) setClarifications(prev => prev.slice(0, -1));
    }
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
                            {spreadName(s.id)}
                          </span>
                          {s.tier === "pro" && (
                            <span className="text-[8px] px-1.5 py-0.5 rounded-full shrink-0" style={{ background: "#C9A84C", color: "#0D0B1F" }}>Pro</span>
                          )}
                          {s.tier === "free" && (
                            <span className="text-[8px] px-1.5 py-0.5 rounded-full shrink-0" style={{ background: "rgba(201,168,76,.1)", color: "#C9A84C" }}>Free</span>
                          )}
                        </div>
                        <p className="text-text-faint text-[11px] leading-tight mt-0.5">{spreadDesc(s.id)}</p>
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
              {spreadName(spread.id)}
            </p>

            {spread.schemeCount && (
              <div className="flex flex-col gap-1.5">
                <p className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
                  {t("tarot.position_scheme")}
                </p>
                {spreadSchemes(spread.id).map((scheme, i) => (
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
                    {scheme.join(" · ")}
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
                {spreadName(spread.id)}
              </p>
            )}

            {(() => {
              const layout = spread ? NAMED_SPREAD_LAYOUTS[spread.id] : undefined;
              if (layout && layout.positions.length === cards.length) {
                return (
                  <>
                    <div style={{ position: "relative", height: layout.height, perspective: 800 }}>
                      {cards.map((card, i) => {
                        const p = layout.positions[i];
                        return (
                          <div key={i} onClick={() => revealCard(i)}
                            style={{
                              position: "absolute", left: `${p.x}%`, top: `${p.y}%`,
                              transform: `translate(-50%, -50%) rotate(${p.rotate ?? 0}deg) scale(${layout.scale})`,
                              zIndex: p.rotate ? 2 : 1,
                            }}>
                            {/* QA-023: deal-in wrapper is separate from the
                                positioning div above so the animation's own
                                transform doesn't clobber the card's slot. */}
                            <div style={{ animation: "mystral-deal .5s cubic-bezier(.2,.8,.3,1) both", animationDelay: `${i * 70}ms` }}>
                              <TarotCard
                                cardId={card.id}
                                name={card.name_display || card.name}
                                revealed={revealed[i]}
                                reversed={card.reversed}
                                delay={i * 100}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                    {revealed.some(Boolean) && (
                      <div className="flex flex-col gap-1">
                        {cards.map((card, i) => revealed[i] && (
                          <div key={i} className="flex items-center justify-between text-[10px] gap-2">
                            <span className="text-text-faint shrink-0">{positions[i]}</span>
                            <span style={{ color: "rgba(200,180,255,0.8)", textAlign: "right" }}>
                              {card.name_display || card.name}{card.reversed ? ` (${t("tarot.reversed")})` : ""}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                );
              }
              return (
                <div className="flex flex-wrap justify-center gap-3" style={{ perspective: "800px" }}>
                  {cards.map((card, i) => (
                    <div key={i} onClick={() => revealCard(i)} className="flex flex-col items-center"
                      style={{ animation: "mystral-deal .5s cubic-bezier(.2,.8,.3,1) both", animationDelay: `${i * 70}ms` }}>
                      <TarotCard
                        cardId={card.id}
                        name={card.name_display || card.name}
                        revealed={revealed[i]}
                        reversed={card.reversed}
                        delay={i * 100}
                      />
                      {revealed[i] && (
                        <div className="mt-1.5 text-center max-w-[88px]">
                          <p style={{ fontSize: 8, color: "rgba(200,180,255,0.6)", fontFamily: "serif" }}>{card.name_display || card.name}</p>
                          <p className="text-text-faint text-[8px]">{positions[i]}</p>
                          {card.reversed && (
                            <p className="text-[8px]" style={{ color: "#f87171" }}>{t("tarot.reversed")}</p>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              );
            })()}

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
                  {stripMarkdown(interpretation)}
                  {isReading && <span className="animate-pulse">{"▍"}</span>}
                </p>
              </div>
            )}

            {interpretation && !isReading && !interpretFailed && (
              <div className="flex flex-col gap-2">
                {clarifications.map((c, i) => {
                  const isLast = i === clarifications.length - 1;
                  return (
                    <div key={i} className="p-3" style={{ borderRadius: 14, background: "rgba(255,255,255,.02)", border: "1px solid rgba(201,168,76,.1)" }}>
                      <p className="text-text-faint text-[10px] italic mb-1.5">"{c.question}"</p>
                      {!c.answer && clarifyLoading && isLast ? (
                        <p className="animate-pulse text-text-faint text-xs">{t("tarot.clarify_loading")}</p>
                      ) : (
                        <p className="text-text-muted text-xs leading-relaxed">
                          {stripMarkdown(c.answer)}
                          {clarifyLoading && isLast && <span className="animate-pulse">{"▍"}</span>}
                        </p>
                      )}
                    </div>
                  );
                })}

                {clarifyError && <p className="text-red-400 text-xs text-center">{clarifyError}</p>}

                {clarifyOpen && (
                  <div className="flex flex-col gap-1.5">
                    <textarea
                      className={inputCls + " min-h-[50px] resize-none"}
                      placeholder={t("tarot.clarify_placeholder")}
                      value={clarifyDraft}
                      maxLength={500}
                      onChange={e => setClarifyDraft(e.target.value)}
                    />
                    <div className="flex items-center justify-between">
                      <span className="text-text-faint text-[9px]">{clarifyDraft.length}/500</span>
                      <Button
                        variant="primary"
                        style={{ height: 38, borderRadius: 12, padding: "0 18px" }}
                        onClick={submitClarify}
                        disabled={!clarifyDraft.trim() || clarifyLoading}
                      >
                        {t("tarot.clarify_submit")}
                      </Button>
                    </div>
                  </div>
                )}

                {!clarifyOpen && !clarifyLoading && clarifications.length < MAX_CLARIFICATIONS && (
                  <button onClick={handleClarifyToggle}
                    style={{ width: "100%", height: 44, borderRadius: 14, border: "1px solid rgba(201,168,76,.25)", background: "transparent", color: "#C9A84C", fontSize: 13, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}>
                    {t("tarot.clarify_btn")}
                    {user?.tier !== "pro" && (
                      <span className="text-[8px] px-1.5 py-0.5 rounded-full shrink-0" style={{ background: "#C9A84C", color: "#0D0B1F" }}>Pro</span>
                    )}
                  </button>
                )}

                {!clarifyOpen && clarifications.length >= MAX_CLARIFICATIONS && (
                  <p className="text-text-faint text-[10px] text-center">{t("tarot.clarify_limit_reached")}</p>
                )}
              </div>
            )}

            {allRevealed && !isReading && (
              <Button
                variant="gold"
                className="w-full"
                style={{ height: 50, borderRadius: 14 }}
                onClick={() => spread?.id === "card_of_day" ? doSpread(spread, positions, true) : reset()}
              >
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
          title={spreadName(spread.id)}
          cards={cards.slice(0, 5)}
          onClose={() => setShowShareCard(false)}
        />
      )}
    </div>
  );
}
