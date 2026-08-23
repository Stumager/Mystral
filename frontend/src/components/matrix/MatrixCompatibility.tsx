import { useState } from "react";
import { useTranslation } from "react-i18next";
import { PartnerPicker, Partner } from "../PartnerPicker";
import { useAuth } from "../../context/AuthContext";
import { apiGet, streamRequest } from "../../utils/api";
import { stripMarkdown } from "../../utils/markdown";

interface CompatResult {
  partner: { id: string; name: string; birth_date: string };
  centre: { arcana: number; arcana_name: string; light: string; shadow: string };
  karmic_tail: { t1: number; t2: number; t3: number; code: string; name: string; essence: string; task: string };
}

const CARD = {
  borderRadius: 18,
  background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))",
  border: "1px solid rgba(201,168,76,.13)",
  padding: "16px 18px",
};

// TZ-119: reuses PartnerPicker as-is (the ticket's explicit ask — the same
// selector as the regular Compatibility section, backed by the same
// UserPartner rows per TZ-118 task 4), then the two v1 indicators from
// matrix_compatibility.py: the combined centre arcana and the couple's
// karmic tail.
export function MatrixCompatibility({ onPaywall, onBack }: { onPaywall: () => void; onBack: () => void }) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const lang = user?.lang ?? "ru";
  const isPro = user?.tier === "pro";

  const [result, setResult] = useState<CompatResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [reading, setReading] = useState<string | undefined>(undefined);
  const [streaming, setStreaming] = useState(false);
  const [readingError, setReadingError] = useState("");

  async function selectPartner(p: Partner) {
    if (!isPro) { onPaywall(); return; }
    setLoading(true);
    setError("");
    setResult(null);
    setReading(undefined);
    try {
      const d = await apiGet<CompatResult>(`/matrix/compatibility/${p.id}?lang=${lang}`, token ?? undefined);
      setResult(d);
    } catch {
      setError(t("matrixCompatibility.error"));
    } finally { setLoading(false); }
  }

  async function interpret() {
    if (!result || streaming || reading !== undefined) return;
    if (!isPro) { onPaywall(); return; }
    setStreaming(true);
    setReadingError("");
    setReading("");
    try {
      await streamRequest(
        `/matrix/compatibility/${result.partner.id}/interpret`,
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
      else setReadingError(err.message || t("matrixCompatibility.error"));
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <button onClick={onBack} className="text-left text-xs" style={{ color: "#C9A84C" }}>
        ‹ {t("common.back")}
      </button>

      {!result && !loading && (
        <>
          <p className="text-[12px] text-center" style={{ color: "#A89E8B" }}>{t("matrixCompatibility.select_partner_hint")}</p>
          <PartnerPicker token={token} lang={lang} onSelect={selectPartner} onPaywall={onPaywall} />
        </>
      )}

      {loading && (
        <p className="text-[12px] text-center animate-pulse" style={{ color: "#A89E8B" }}>{t("matrix.calculating")}</p>
      )}

      {error && (
        <p className="text-[12px] text-center" style={{ color: "#D98A8A" }}>{error}</p>
      )}

      {result && (
        <>
          <p className="font-cormorant text-center" style={{ fontSize: 22, color: "#F0E9DA" }}>{result.partner.name}</p>

          {/* п.3: the "no verdict" framing must be a visible intro block,
              not only baked into the AI prompt — original wording, see
              matrixCompatibility.intro in the locale files. */}
          <div style={{ padding: "12px 14px", borderRadius: 14, background: "rgba(75,60,134,.08)", border: "1px solid rgba(138,127,192,.2)" }}>
            <p className="text-[12px] text-center" style={{ color: "#C8C0E8", lineHeight: 1.55 }}>
              {t("matrixCompatibility.intro")}
            </p>
          </div>

          <div style={CARD}>
            <p className="font-cinzel uppercase" style={{ fontSize: 9, letterSpacing: ".22em", color: "#C9A84C" }}>
              {t("matrixCompatibility.centre_label")}
            </p>
            <p className="font-cormorant" style={{ fontSize: 30, color: "#E8CD7E", lineHeight: 1.15, marginTop: 2 }}>
              {result.centre.arcana} · {result.centre.arcana_name}
            </p>
            <div className="flex flex-col gap-2 mt-3">
              <div style={{ padding: "9px 12px", borderRadius: 12, background: "rgba(201,168,76,.06)", border: "1px solid rgba(201,168,76,.16)" }}>
                <span className="block text-[10px] uppercase font-cinzel" style={{ letterSpacing: ".18em", color: "#C9A84C" }}>{t("matrix.light")}</span>
                <span className="block text-[12.5px] mt-0.5" style={{ color: "#EDE7DA" }}>{result.centre.light}</span>
              </div>
              <div style={{ padding: "9px 12px", borderRadius: 12, background: "rgba(75,60,134,.10)", border: "1px solid rgba(138,127,192,.22)" }}>
                <span className="block text-[10px] uppercase font-cinzel" style={{ letterSpacing: ".18em", color: "#B3A9E0" }}>{t("matrix.shadow")}</span>
                <span className="block text-[12.5px] mt-0.5" style={{ color: "#EDE7DA" }}>{result.centre.shadow}</span>
              </div>
            </div>
          </div>

          <div style={CARD}>
            <p className="font-cinzel uppercase" style={{ fontSize: 9, letterSpacing: ".22em", color: "#C9A84C" }}>
              {t("matrixCompatibility.karmic_tail_label")}
            </p>
            <p className="font-cormorant" style={{ fontSize: 26, color: "#E8CD7E", lineHeight: 1.15, marginTop: 2 }}>
              {result.karmic_tail.name}
            </p>
            <p className="text-[10.5px] mt-0.5" style={{ color: "#8A8170" }}>{result.karmic_tail.code}</p>
            <div className="flex flex-col gap-2 mt-3">
              <div style={{ padding: "9px 12px", borderRadius: 12, background: "rgba(255,255,255,.03)", border: "1px solid rgba(201,168,76,.13)" }}>
                <span className="block text-[10px] uppercase font-cinzel" style={{ letterSpacing: ".18em", color: "#C9A84C" }}>{t("karmicTail.essence_label")}</span>
                <span className="block text-[12.5px] mt-0.5" style={{ color: "#EDE7DA" }}>{result.karmic_tail.essence}</span>
              </div>
              <div style={{ padding: "9px 12px", borderRadius: 12, background: "rgba(75,60,134,.10)", border: "1px solid rgba(138,127,192,.22)" }}>
                <span className="block text-[10px] uppercase font-cinzel" style={{ letterSpacing: ".18em", color: "#B3A9E0" }}>{t("karmicTail.task_label")}</span>
                <span className="block text-[12.5px] mt-0.5" style={{ color: "#EDE7DA" }}>{result.karmic_tail.task}</span>
              </div>
            </div>

            {reading !== undefined ? (
              <div className="mt-3" style={{ padding: "12px 14px", borderRadius: 14, background: "rgba(255,255,255,.03)", border: "1px solid rgba(201,168,76,.13)" }}>
                <p className="font-cinzel uppercase mb-1.5" style={{ fontSize: 9, letterSpacing: ".22em", color: "#C9A84C" }}>
                  {t("matrixCompatibility.interpret")}
                </p>
                {reading ? (
                  <p className="text-[13px] whitespace-pre-wrap" style={{ color: "#D8D0C2", lineHeight: 1.65 }}>
                    {stripMarkdown(reading)}
                    {streaming && <span className="animate-pulse">▍</span>}
                  </p>
                ) : (
                  <p className="text-[12px] animate-pulse" style={{ color: "#A89E8B" }}>{t("matrixCompatibility.loading")}</p>
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
                {t("matrixCompatibility.interpret")}
              </button>
            )}

            {readingError && (
              <p className="text-[12px] mt-2 text-center" style={{ color: "#D98A8A" }}>{readingError}</p>
            )}
          </div>

          <button onClick={() => { setResult(null); setReading(undefined); }} className="text-center text-xs" style={{ color: "#8A8170" }}>
            {t("matrixCompatibility.another_partner")}
          </button>
        </>
      )}
    </div>
  );
}
