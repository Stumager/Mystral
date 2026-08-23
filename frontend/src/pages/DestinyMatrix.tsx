import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { DestinyOctagram, MatrixPoint } from "../components/DestinyOctagram";
import { MatrixChildren } from "../components/matrix/MatrixChildren";
import { MatrixCompatibility } from "../components/matrix/MatrixCompatibility";
import { MatrixKarmicTail } from "../components/matrix/MatrixKarmicTail";
import { MatrixMoneyLine } from "../components/matrix/MatrixMoneyLine";
import { PaywallSheet } from "../components/PaywallSheet";
import { BottomNav, Button } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { streamRequest } from "../utils/api";
import { stripMarkdown } from "../utils/markdown";

interface DestinyMatrixProps { onNavigate: (page: string) => void; }

// TZ-119: sub-view state, not a new top-level Page/route — the ticket was
// explicit about nesting these inside the existing /app/matrix screen
// rather than inventing new navigation. "main" is the base matrix (plus
// the karmic tail/money line cards); "children" and "compatibility" swap
// the whole <main> content for their own list-then-detail flow.
type MatrixView = "main" | "children" | "compatibility";

interface MatrixData {
  birth_date: string;
  points: MatrixPoint[];
  ancestral_centre: number;
}

const CARD = {
  borderRadius: 18,
  background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))",
  border: "1px solid rgba(201,168,76,.13)",
  padding: "16px 18px",
};

export function DestinyMatrix({ onNavigate }: DestinyMatrixProps) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const lang = user?.lang ?? "ru";
  const isPro = user?.tier === "pro";

  const [data, setData] = useState<MatrixData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [view, setView] = useState<MatrixView>("main");

  const [selected, setSelected] = useState<string | null>(null);
  // Kept per point so re-opening a point the user already paid to generate
  // doesn't fire a second billed request.
  const [readings, setReadings] = useState<Record<string, string>>({});
  const [readingError, setReadingError] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);

  // Keyed on lang rather than a plain "already ran" flag: arcana names come
  // from the server, so a language switch has to refetch them, otherwise
  // they'd stay in the old language while the labels around them changed.
  const fetchedLang = useRef<string | null>(null);

  useEffect(() => {
    if (!token || fetchedLang.current === lang) return;
    fetchedLang.current = lang;
    setLoading(true);
    setError("");
    // Generated readings are language-specific too — drop them rather than
    // show Russian prose under English headings.
    setReadings({});
    setReadingError("");
    fetch(`/api/v1/matrix?lang=${lang}`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async r => {
        if (!r.ok) throw new Error(String(r.status));
        return r.json();
      })
      .then((d: MatrixData) => setData(d))
      .catch(() => setError(t("matrix.need_birth_date")))
      .finally(() => setLoading(false));
  }, [token, lang, t]);

  const point = data?.points.find(p => p.id === selected) ?? null;

  function selectPoint(id: string) {
    setSelected(prev => (prev === id ? null : id));
    setReadingError("");
  }

  async function interpret() {
    if (!point || streaming) return;
    if (!isPro) { setShowPaywall(true); return; }

    const id = point.id;
    setStreaming(true);
    setReadingError("");
    setReadings(prev => ({ ...prev, [id]: "" }));
    let failed = false;
    try {
      await streamRequest(
        "/matrix/interpret",
        { point: id, lang },
        (c) => setReadings(prev => ({ ...prev, [id]: (prev[id] ?? "") + c })),
        () => setStreaming(false),
        token ?? undefined,
        (msg) => { failed = true; setReadingError(msg); setStreaming(false); },
      );
    } catch (e: unknown) {
      failed = true;
      const err = e as { code?: string; message?: string };
      setStreaming(false);
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      else setReadingError(err.message || t("matrix.error"));
    } finally {
      // A failed attempt must not leave an empty card behind that looks like
      // a generated-but-blank reading (TZ-097 lesson) — drop the placeholder
      // and surface the failure through readingError instead.
      if (failed) setReadings(prev => { const next = { ...prev }; delete next[id]; return next; });
    }
  }

  const reading = point ? readings[point.id] : undefined;

  function PointRow({ p }: { p: MatrixPoint }) {
    const active = selected === p.id;
    return (
      <button
        onClick={() => selectPoint(p.id)}
        className="w-full text-left flex items-center gap-3"
        style={{
          padding: "9px 12px", borderRadius: 12, cursor: "pointer",
          background: active ? "rgba(201,168,76,.10)" : "rgba(255,255,255,.03)",
          border: `1px solid ${active ? "rgba(201,168,76,.4)" : "rgba(201,168,76,.12)"}`,
        }}
      >
        <span
          className="font-cinzel shrink-0 flex items-center justify-center"
          style={{
            width: 30, height: 30, borderRadius: 99, fontSize: 13,
            color: p.square === "personal" ? "#E8CD7E" : "#B3A9E0",
            border: `1px solid ${p.square === "personal" ? "rgba(201,168,76,.35)" : "rgba(138,127,192,.4)"}`,
          }}
        >
          {p.arcana}
        </span>
        <span className="min-w-0">
          <span className="block text-[11px]" style={{ color: "#A89E8B" }}>{t(`matrix.point_${p.id}`)}</span>
          <span className="block font-display truncate" style={{ fontSize: 13, color: "#EDE7DA" }}>{p.arcana_name}</span>
        </span>
      </button>
    );
  }

  return (
    <div className="flex flex-col min-h-screen relative" style={{ background: "var(--gradient-page)", animation: "mystral-fadeup .3s ease-out" }}>
      <header className="flex items-center justify-between px-4 shrink-0 backdrop-blur-md lg:hidden" style={{ height: 46, background: "var(--bg-header)", borderBottom: "1px solid var(--border-gold)" }}>
        <button className="text-text-muted text-lg w-8" onClick={() => (view === "main" ? onNavigate("home") : setView("main"))}>&#8249;</button>
        <span className="font-cinzel tracking-[.26em]" style={{ fontSize: 13, color: "#E8CD7E" }}>{t("matrix.title")}</span>
        <div className="w-8" />
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-6 pb-24 flex flex-col gap-4">
        {view === "children" ? (
          <MatrixChildren onPaywall={() => setShowPaywall(true)} onBack={() => setView("main")} />
        ) : view === "compatibility" ? (
          <MatrixCompatibility onPaywall={() => setShowPaywall(true)} onBack={() => setView("main")} />
        ) : loading ? (
          <p className="text-text-muted text-xs text-center animate-pulse">{t("matrix.calculating")}</p>
        ) : error ? (
          <div style={CARD}>
            <p className="text-text-muted text-sm text-center">{error}</p>
            <Button variant="primary" size="sm" className="w-full mt-3" onClick={() => onNavigate("profile")}>
              {t("matrix.open_profile")}
            </Button>
          </div>
        ) : data ? (
          <>
            <div style={CARD}>
              <DestinyOctagram points={data.points} selected={selected} onSelect={selectPoint} />
              <p className="text-center text-[11px] mt-3" style={{ color: "#A89E8B" }}>
                {t("matrix.select_hint")}
              </p>
            </div>

            {/* TZ-119 п.1: karmic tail + money line reuse the already-
                calculated 9 points, no new input — sections right next to
                the octagram rather than a separate screen. */}
            <MatrixKarmicTail onPaywall={() => setShowPaywall(true)} />
            <MatrixMoneyLine onPaywall={() => setShowPaywall(true)} />

            {point && (
              <div style={CARD}>
                <p className="font-cinzel uppercase" style={{ fontSize: 9, letterSpacing: ".22em", color: "#C9A84C" }}>
                  {t(`matrix.point_${point.id}`)}
                </p>
                <p className="font-cormorant" style={{ fontSize: 30, color: "#E8CD7E", lineHeight: 1.15, marginTop: 2 }}>
                  {point.arcana} · {point.arcana_name}
                </p>

                <div className="flex flex-col gap-2 mt-3">
                  <div style={{ padding: "9px 12px", borderRadius: 12, background: "rgba(201,168,76,.06)", border: "1px solid rgba(201,168,76,.16)" }}>
                    <span className="block text-[10px] uppercase font-cinzel" style={{ letterSpacing: ".18em", color: "#C9A84C" }}>{t("matrix.light")}</span>
                    <span className="block text-[12.5px] mt-0.5" style={{ color: "#EDE7DA" }}>{point.light}</span>
                  </div>
                  <div style={{ padding: "9px 12px", borderRadius: 12, background: "rgba(75,60,134,.10)", border: "1px solid rgba(138,127,192,.22)" }}>
                    <span className="block text-[10px] uppercase font-cinzel" style={{ letterSpacing: ".18em", color: "#B3A9E0" }}>{t("matrix.shadow")}</span>
                    <span className="block text-[12.5px] mt-0.5" style={{ color: "#EDE7DA" }}>{point.shadow}</span>
                  </div>
                </div>

                {reading !== undefined ? (
                  <div className="mt-3" style={{ padding: "12px 14px", borderRadius: 14, background: "rgba(255,255,255,.03)", border: "1px solid rgba(201,168,76,.13)" }}>
                    <p className="font-cinzel uppercase mb-1.5" style={{ fontSize: 9, letterSpacing: ".22em", color: "#C9A84C" }}>
                      {t("matrix.interpret")}
                    </p>
                    {reading ? (
                      <p className="text-[13px] whitespace-pre-wrap" style={{ color: "#D8D0C2", lineHeight: 1.65 }}>
                        {stripMarkdown(reading)}
                        {streaming && <span className="animate-pulse">▍</span>}
                      </p>
                    ) : (
                      <p className="text-[12px] animate-pulse" style={{ color: "#A89E8B" }}>{t("matrix.loading")}</p>
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
                    {t("matrix.interpret")}
                    {!isPro && (
                      <span className="font-cinzel" style={{ fontSize: 8.5, letterSpacing: ".16em", padding: "2px 6px", borderRadius: 99, background: "rgba(201,168,76,.16)", border: "1px solid rgba(201,168,76,.32)" }}>
                        PRO
                      </span>
                    )}
                  </button>
                )}

                {readingError && (
                  <p className="text-[12px] mt-2 text-center" style={{ color: "#D98A8A" }}>{readingError}</p>
                )}
              </div>
            )}

            <div style={CARD}>
              <p className="font-cinzel uppercase mb-2" style={{ fontSize: 9, letterSpacing: ".22em", color: "#C9A84C" }}>
                {t("matrix.personal_square")}
              </p>
              <div className="flex flex-col gap-1.5">
                {data.points.filter(p => p.square === "personal").map(p => <PointRow key={p.id} p={p} />)}
              </div>
            </div>

            <div style={CARD}>
              <p className="font-cinzel uppercase mb-2" style={{ fontSize: 9, letterSpacing: ".22em", color: "#B3A9E0" }}>
                {t("matrix.ancestral_square")}
              </p>
              <div className="flex flex-col gap-1.5">
                {data.points.filter(p => p.square === "ancestral").map(p => <PointRow key={p.id} p={p} />)}
              </div>
              <p className="text-[11px] mt-2.5 text-center" style={{ color: "#A89E8B" }}>
                {t("matrix.ancestral_centre")}: <span style={{ color: "#B3A9E0" }}>{data.ancestral_centre}</span>
              </p>
            </div>

            {/* TZ-119 п.2/п.3: children's matrix and compatibility need
                their own list-then-detail flow (CRUD, partner picker), so
                they're a sub-view of this same screen rather than an
                inline section like the two cards above. */}
            <p className="font-cinzel uppercase mt-2" style={{ fontSize: 9, letterSpacing: ".22em", color: "#8A8170" }}>
              {t("matrix.more_readings")}
            </p>
            <button
              onClick={() => setView("children")}
              className="w-full flex items-center justify-between"
              style={{ ...CARD, cursor: "pointer" }}
            >
              <span className="flex items-center gap-2">
                <span className="font-cinzel uppercase" style={{ fontSize: 12, letterSpacing: ".14em", color: "#F0E9DA" }}>
                  {t("childrensMatrix.title")}
                </span>
                {!isPro && (
                  <span className="font-cinzel" style={{ fontSize: 8.5, letterSpacing: ".16em", padding: "2px 6px", borderRadius: 99, background: "rgba(201,168,76,.16)", border: "1px solid rgba(201,168,76,.32)", color: "#E8CD7E" }}>
                    PRO
                  </span>
                )}
              </span>
              <span style={{ color: "#C9A84C", fontSize: 14, opacity: .6 }}>›</span>
            </button>
            <button
              // Unlike Children's Matrix (which has a free sample point),
              // Compatibility's GET is all-or-nothing Pro on the backend
              // too — same immediate-paywall behavior as the karmic
              // tail/money line cards above, not a nav into an empty
              // partner picker a free user can't do anything with.
              onClick={() => (isPro ? setView("compatibility") : setShowPaywall(true))}
              className="w-full flex items-center justify-between"
              style={{ ...CARD, cursor: "pointer" }}
            >
              <span className="flex items-center gap-2">
                <span className="font-cinzel uppercase" style={{ fontSize: 12, letterSpacing: ".14em", color: "#F0E9DA" }}>
                  {t("matrixCompatibility.title")}
                </span>
                {!isPro && (
                  <span className="font-cinzel" style={{ fontSize: 8.5, letterSpacing: ".16em", padding: "2px 6px", borderRadius: 99, background: "rgba(201,168,76,.16)", border: "1px solid rgba(201,168,76,.32)", color: "#E8CD7E" }}>
                    PRO
                  </span>
                )}
              </span>
              <span style={{ color: "#C9A84C", fontSize: 14, opacity: .6 }}>›</span>
            </button>
          </>
        ) : null}
      </main>

      <BottomNav active="home" onNavigate={onNavigate} />
      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
    </div>
  );
}
