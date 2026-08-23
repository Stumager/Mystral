import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import { apiGet, streamRequest } from "../../utils/api";
import { stripMarkdown } from "../../utils/markdown";

interface MoneyPosition {
  id: "entry" | "source" | "block";
  arcana: number;
  flow: string;
  block: string;
}

interface MoneyLineData {
  positions: MoneyPosition[];
}

const CARD = {
  borderRadius: 18,
  background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))",
  border: "1px solid rgba(201,168,76,.13)",
  padding: "16px 18px",
};

// TZ-119: same collapse/reveal/interpret shape as MatrixKarmicTail — see
// its comment. Money line has no per-arcana name (money_line.py's Step 0:
// no source gives it a named-archetype table), so each position shows its
// bare arcana number plus its flow/block keywords instead of a title.
export function MatrixMoneyLine({ onPaywall }: { onPaywall: () => void }) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const lang = user?.lang ?? "ru";
  const isPro = user?.tier === "pro";

  const [open, setOpen] = useState(false);
  const [data, setData] = useState<MoneyLineData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [reading, setReading] = useState<string | undefined>(undefined);
  const [streaming, setStreaming] = useState(false);
  const [readingError, setReadingError] = useState("");

  async function toggle() {
    if (!isPro) { onPaywall(); return; }
    if (open) { setOpen(false); return; }
    setOpen(true);
    if (data || loading) return;
    setLoading(true);
    setError("");
    try {
      const d = await apiGet<MoneyLineData>(`/matrix/money-line?lang=${lang}`, token ?? undefined);
      setData(d);
    } catch {
      setError(t("moneyLine.error"));
    } finally {
      setLoading(false);
    }
  }

  async function interpret() {
    if (streaming || reading !== undefined) return;
    if (!isPro) { onPaywall(); return; }
    setStreaming(true);
    setReadingError("");
    setReading("");
    try {
      await streamRequest(
        "/matrix/money-line/interpret",
        { lang },
        (c) => setReading(prev => (prev ?? "") + c),
        () => setStreaming(false),
        token ?? undefined,
        (msg) => { setReadingError(msg); setStreaming(false); setReading(undefined); },
      );
    } catch (e: unknown) {
      const err = e as { code?: string; message?: string };
      setStreaming(false);
      setReading(undefined);
      if (err.code === "FREE_LIMIT_REACHED") onPaywall();
      else setReadingError(err.message || t("moneyLine.error"));
    }
  }

  return (
    <div style={CARD}>
      <button
        onClick={toggle}
        className="w-full flex items-center justify-between text-left"
        style={{ background: "transparent", border: "none", cursor: "pointer", padding: 0 }}
      >
        <span className="flex items-center gap-2">
          <span className="font-cinzel uppercase" style={{ fontSize: 12, letterSpacing: ".14em", color: "#F0E9DA" }}>
            {t("moneyLine.title")}
          </span>
          {!isPro && (
            <span className="font-cinzel" style={{ fontSize: 8.5, letterSpacing: ".16em", padding: "2px 6px", borderRadius: 99, background: "rgba(201,168,76,.16)", border: "1px solid rgba(201,168,76,.32)", color: "#E8CD7E" }}>
              PRO
            </span>
          )}
        </span>
        <span style={{ color: "#C9A84C", fontSize: 14, opacity: .6, transform: open ? "rotate(90deg)" : "none", transition: "transform .15s" }}>›</span>
      </button>

      {open && (
        <div className="mt-3">
          {loading ? (
            <p className="text-[12px] text-center animate-pulse" style={{ color: "#A89E8B" }}>{t("matrix.calculating")}</p>
          ) : error ? (
            <p className="text-[12px] text-center" style={{ color: "#D98A8A" }}>{error}</p>
          ) : data ? (
            <>
              <div className="flex flex-col gap-2">
                {data.positions.map(pos => (
                  <div key={pos.id} style={{ padding: "9px 12px", borderRadius: 12, background: "rgba(255,255,255,.03)", border: "1px solid rgba(201,168,76,.13)" }}>
                    <div className="flex items-center justify-between">
                      <span className="font-cinzel uppercase" style={{ fontSize: 10, letterSpacing: ".16em", color: "#C9A84C" }}>
                        {t(`moneyLine.position_${pos.id}`)}
                      </span>
                      <span className="font-cormorant" style={{ fontSize: 18, color: "#E8CD7E" }}>{pos.arcana}</span>
                    </div>
                    <p className="text-[12px] mt-1" style={{ color: "#EDE7DA" }}>
                      <span style={{ color: "#8A8170" }}>{t("moneyLine.flow_label")}: </span>{pos.flow}
                    </p>
                    <p className="text-[12px] mt-0.5" style={{ color: "#EDE7DA" }}>
                      <span style={{ color: "#8A8170" }}>{t("moneyLine.block_label")}: </span>{pos.block}
                    </p>
                  </div>
                ))}
              </div>

              {reading !== undefined ? (
                <div className="mt-3" style={{ padding: "12px 14px", borderRadius: 14, background: "rgba(255,255,255,.03)", border: "1px solid rgba(201,168,76,.13)" }}>
                  <p className="font-cinzel uppercase mb-1.5" style={{ fontSize: 9, letterSpacing: ".22em", color: "#C9A84C" }}>
                    {t("moneyLine.interpret")}
                  </p>
                  {reading ? (
                    <p className="text-[13px] whitespace-pre-wrap" style={{ color: "#D8D0C2", lineHeight: 1.65 }}>
                      {stripMarkdown(reading)}
                      {streaming && <span className="animate-pulse">▍</span>}
                    </p>
                  ) : (
                    <p className="text-[12px] animate-pulse" style={{ color: "#A89E8B" }}>{t("moneyLine.loading")}</p>
                  )}
                </div>
              ) : (
                <button
                  onClick={interpret}
                  disabled={streaming}
                  className="w-full mt-3 flex items-center justify-center gap-2"
                  style={{
                    padding: "11px 16px", borderRadius: 14, cursor: streaming ? "default" : "pointer",
                    background: "linear-gradient(100deg, rgba(75,60,134,.28), rgba(201,168,76,.14))",
                    border: "1px solid rgba(201,168,76,.32)", color: "#E8CD7E", fontSize: 13,
                  }}
                >
                  {t("moneyLine.interpret")}
                </button>
              )}

              {readingError && (
                <p className="text-[12px] mt-2 text-center" style={{ color: "#D98A8A" }}>{readingError}</p>
              )}
            </>
          ) : null}
        </div>
      )}
    </div>
  );
}
