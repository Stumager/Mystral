import { useState } from "react";
import { useTranslation } from "react-i18next";
import { PaywallSheet } from "../components/PaywallSheet";
import { BottomNav, Button, Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { apiRequest, streamRequest } from "../utils/api";

interface RunesProps {
  onNavigate: (page: string) => void;
}

interface Rune {
  id: string;
  name: string;
  symbol: string;
  reversed: boolean;
  meaning: string;
}

export function Runes({ onNavigate }: RunesProps) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const [mode, setMode] = useState<"idle" | "drawing" | "result">("idle");
  const [count, setCount] = useState(1);
  const [runes, setRunes] = useState<Rune[]>([]);
  const [loading, setLoading] = useState(false);
  const [interpretation, setInterpretation] = useState("");
  const [interpretLoading, setInterpretLoading] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);
  const [error, setError] = useState("");

  async function handleDraw() {
    setLoading(true);
    setError("");
    setMode("drawing");
    try {
      const data = await apiRequest<{ runes: Rune[] }>(
        "/runes/draw",
        { count, lang: user?.lang ?? "ru" },
        token ?? undefined,
      );
      setTimeout(() => {
        setRunes(data.runes);
        setMode("result");
        setLoading(false);
      }, 800);
    } catch (e: unknown) {
      const err = e as { code?: string };
      if (err.code === "FREE_LIMIT_REACHED") {
        setShowPaywall(true);
        setMode("idle");
      } else {
        setError(t("runes.error"));
        setMode("idle");
      }
      setLoading(false);
    }
  }

  async function handleInterpret() {
    setInterpretLoading(true);
    setInterpretation("");
    try {
      await streamRequest(
        "/runes/interpret",
        { runes: runes.map(r => ({ name: r.name, reversed: r.reversed })), lang: user?.lang ?? "ru" },
        (chunk) => setInterpretation(prev => prev + chunk),
        () => setInterpretLoading(false),
        token ?? undefined,
      );
    } catch {
      setInterpretation(t("runes.error"));
      setInterpretLoading(false);
    }
  }

  function reset() {
    setMode("idle");
    setRunes([]);
    setInterpretation("");
    setError("");
  }

  const isPro = user?.tier === "pro";

  return (
    <div className="flex flex-col min-h-screen bg-bg-deep relative">
      <header
        className="flex items-center justify-between px-4 shrink-0 backdrop-blur-sm"
        style={{ height: 46, background: "rgba(6,4,20,0.75)" }}
      >
        <button className="text-text-muted text-lg w-8" onClick={() => onNavigate("home")}>‹</button>
        <span className="font-display text-text-primary text-base tracking-widest">{t("runes.title")}</span>
        <div className="w-8" />
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-6 pb-24">
        {mode === "idle" && (
          <div className="flex flex-col items-center gap-6 pt-8">
            <p className="text-text-muted text-sm text-center">{t("runes.focus")}</p>

            <div className="flex gap-3">
              <button
                onClick={() => setCount(1)}
                className="px-5 py-2.5 rounded-xl text-sm transition-all"
                style={{
                  background: count === 1 ? "rgba(107,78,255,0.2)" : "transparent",
                  border: `1px solid ${count === 1 ? "rgba(107,78,255,0.5)" : "rgba(107,78,255,0.15)"}`,
                  color: count === 1 ? "#9B8AFF" : "#9B8FBB",
                }}
              >
                {t("runes.one_rune")}
              </button>
              <button
                onClick={() => isPro ? setCount(3) : setShowPaywall(true)}
                className="px-5 py-2.5 rounded-xl text-sm transition-all relative"
                style={{
                  background: count === 3 ? "rgba(107,78,255,0.2)" : "transparent",
                  border: `1px solid ${count === 3 ? "rgba(107,78,255,0.5)" : "rgba(107,78,255,0.15)"}`,
                  color: count === 3 ? "#9B8AFF" : "#9B8FBB",
                }}
              >
                {t("runes.three_runes")}
                {!isPro && (
                  <span className="absolute -top-2 -right-2 text-[8px] px-1.5 py-0.5 rounded-full" style={{ background: "#C9A84C", color: "#0D0B1F" }}>
                    {t("runes.pro_only")}
                  </span>
                )}
              </button>
            </div>

            {error && <p className="text-red-400 text-xs">{error}</p>}

            <Button variant="primary" className="w-full max-w-[280px]" onClick={handleDraw} disabled={loading}>
              {t("runes.draw")}
            </Button>
          </div>
        )}

        {mode === "drawing" && (
          <div className="flex justify-center items-center pt-16">
            <div className="flex gap-4">
              {Array.from({ length: count }).map((_, i) => (
                <div
                  key={i}
                  className="w-20 h-28 rounded-xl flex items-center justify-center animate-pulse"
                  style={{
                    background: "rgba(107,78,255,0.15)",
                    border: "1px solid rgba(107,78,255,0.3)",
                    animationDelay: `${i * 200}ms`,
                  }}
                >
                  <span className="text-3xl text-violet-400">?</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {mode === "result" && (
          <div className="flex flex-col gap-4">
            <div className={`flex justify-center gap-4 mb-2 ${runes.length === 1 ? "" : ""}`}>
              {runes.map((rune, i) => (
                <div
                  key={i}
                  className="w-24 rounded-xl flex flex-col items-center py-4 gap-2"
                  style={{
                    background: "rgba(107,78,255,0.1)",
                    border: "1px solid rgba(107,78,255,0.25)",
                    boxShadow: "0 0 20px rgba(107,78,255,0.15)",
                  }}
                >
                  <span
                    className="font-display text-4xl"
                    style={{
                      color: "#9B8AFF",
                      transform: rune.reversed ? "rotate(180deg)" : "none",
                      display: "inline-block",
                    }}
                  >
                    {rune.symbol}
                  </span>
                  <span className="text-text-primary text-xs font-display">{rune.name}</span>
                  <span
                    className="text-[9px] px-2 py-0.5 rounded-full"
                    style={{
                      background: rune.reversed ? "rgba(239,68,68,0.12)" : "rgba(107,78,255,0.12)",
                      color: rune.reversed ? "#f87171" : "#9B8AFF",
                    }}
                  >
                    {rune.reversed ? t("runes.reversed") : t("runes.upright")}
                  </span>
                </div>
              ))}
            </div>

            {runes.map((rune, i) => (
              <Card key={i}>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg" style={{ color: "#9B8AFF" }}>{rune.symbol}</span>
                  <span className="font-display text-sm text-text-primary">{rune.name}</span>
                </div>
                <p className="text-text-muted text-xs leading-relaxed">{rune.meaning}</p>
              </Card>
            ))}

            {interpretation ? (
              <Card>
                <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">{t("runes.interpretation_label")}</p>
                <p className="text-text-muted text-xs leading-relaxed">
                  {interpretation}
                  {interpretLoading && <span className="animate-pulse">▍</span>}
                </p>
              </Card>
            ) : (
              <Button variant="primary" className="w-full" onClick={handleInterpret} disabled={interpretLoading}>
                {interpretLoading ? t("runes.reading") : t("runes.get_interpretation")}
              </Button>
            )}

            <Button variant="ghost" className="w-full" onClick={reset}>
              {t("runes.new_draw")}
            </Button>
          </div>
        )}
      </main>

      <BottomNav active="home" onNavigate={onNavigate} />
      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
    </div>
  );
}
