import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { DestinyOctagram, MatrixPoint } from "../DestinyOctagram";
import { Button } from "../ui";
import { useAuth } from "../../context/AuthContext";
import { apiGet, apiRequest, streamRequest } from "../../utils/api";
import { stripMarkdown } from "../../utils/markdown";
import { validateDay, validateMonth, validateYear, validateDateExists } from "../../utils/validate";

interface Child { id: string; name: string; birth_date: string; }

interface ChildPoint extends MatrixPoint {
  strength: string | null;
  support: string | null;
}

interface ChildMatrixData {
  child: Child;
  points: ChildPoint[];
  ancestral_centre: number;
}

const CARD = {
  borderRadius: 18,
  background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))",
  border: "1px solid rgba(201,168,76,.13)",
  padding: "16px 18px",
};

const inputCls = "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 text-text-primary text-sm placeholder:text-text-faint focus:outline-none focus:border-violet-600 transition-colors";

// TZ-119: sub-view mounted inside DestinyMatrix.tsx (not a new top-level
// page/route — the ticket's explicit ask was to nest this inside the
// existing /app/matrix screen, since it needs a list-then-detail flow
// unlike the karmic tail/money line cards).
export function MatrixChildren({ onPaywall, onBack }: { onPaywall: () => void; onBack: () => void }) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const lang = user?.lang ?? "ru";
  const isPro = user?.tier === "pro";

  const [children, setChildren] = useState<Child[]>([]);
  const [loadingList, setLoadingList] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [addForm, setAddForm] = useState({ name: "", day: "", month: "", year: "" });
  const [addErrors, setAddErrors] = useState<Record<string, string>>({});
  const [adding, setAdding] = useState(false);

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ChildMatrixData | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState("");

  const [selectedPoint, setSelectedPoint] = useState<string | null>(null);
  const [readings, setReadings] = useState<Record<string, string>>({});
  const [readingError, setReadingError] = useState("");
  const [streaming, setStreaming] = useState(false);

  const loaded = useRef(false);
  useEffect(() => {
    if (loaded.current || !token) return;
    loaded.current = true;
    loadChildren();
  }, [token]);

  async function loadChildren() {
    setLoadingList(true);
    try {
      const data = await apiGet<Child[]>("/children", token ?? undefined);
      setChildren(Array.isArray(data) ? data : []);
    } catch { setChildren([]); }
    finally { setLoadingList(false); }
  }

  async function handleAddChild() {
    const errs: Record<string, string> = {};
    if (!addForm.name.trim()) errs.name = t("childrensMatrix.name_required");
    const de = validateDay(addForm.day); if (de) errs.day = de;
    const me = validateMonth(addForm.month); if (me) errs.month = me;
    const ye = validateYear(addForm.year); if (ye) errs.year = ye;
    if (!de && !me && !ye) { const dx = validateDateExists(addForm.day, addForm.month, addForm.year); if (dx) errs.date = dx; }
    if (Object.values(errs).some(Boolean)) { setAddErrors(errs); return; }

    setAdding(true);
    try {
      const bd = `${addForm.year}-${addForm.month.padStart(2, "0")}-${addForm.day.padStart(2, "0")}`;
      await apiRequest("/children", { name: addForm.name, birth_date: bd }, token ?? undefined);
      await loadChildren();
      setShowAddForm(false);
      setAddForm({ name: "", day: "", month: "", year: "" });
    } catch {
      setAddErrors({ name: t("childrensMatrix.error") });
    } finally { setAdding(false); }
  }

  async function handleDeleteChild(id: string) {
    try {
      await fetch(`/api/v1/children/${id}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
      setChildren(prev => prev.filter(c => c.id !== id));
      if (selectedId === id) { setSelectedId(null); setDetail(null); }
    } catch {}
  }

  async function selectChild(id: string) {
    setSelectedId(id);
    setDetail(null);
    setDetailError("");
    setSelectedPoint(null);
    setReadings({});
    setDetailLoading(true);
    try {
      const d = await apiGet<ChildMatrixData>(`/matrix/child/${id}?lang=${lang}`, token ?? undefined);
      setDetail(d);
    } catch {
      setDetailError(t("childrensMatrix.error"));
    } finally { setDetailLoading(false); }
  }

  function selectPoint(id: string) {
    const p = detail?.points.find(pt => pt.id === id);
    if (p?.locked) { onPaywall(); return; }
    setSelectedPoint(prev => (prev === id ? null : id));
    setReadingError("");
  }

  const point = detail?.points.find(p => p.id === selectedPoint) ?? null;

  async function interpret() {
    if (!point || !detail || streaming) return;
    if (!isPro) { onPaywall(); return; }
    const id = point.id;
    setStreaming(true);
    setReadingError("");
    setReadings(prev => ({ ...prev, [id]: "" }));
    let failed = false;
    try {
      await streamRequest(
        `/matrix/child/${detail.child.id}/interpret`,
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
      if (err.code === "FREE_LIMIT_REACHED") onPaywall();
      else setReadingError(err.message || t("childrensMatrix.error"));
    } finally {
      if (failed) setReadings(prev => { const next = { ...prev }; delete next[id]; return next; });
    }
  }

  const reading = point ? readings[point.id] : undefined;

  // ---- Detail view for one child ----
  if (selectedId) {
    return (
      <div className="flex flex-col gap-4">
        <button onClick={() => { setSelectedId(null); setDetail(null); }} className="text-left text-xs" style={{ color: "#C9A84C" }}>
          ‹ {t("common.back")}
        </button>

        {detailLoading ? (
          <p className="text-[12px] text-center animate-pulse" style={{ color: "#A89E8B" }}>{t("matrix.calculating")}</p>
        ) : detailError ? (
          <p className="text-[12px] text-center" style={{ color: "#D98A8A" }}>{detailError}</p>
        ) : detail ? (
          <>
            <div style={CARD}>
              <p className="font-cormorant text-center" style={{ fontSize: 22, color: "#F0E9DA" }}>{detail.child.name}</p>
              <DestinyOctagram points={detail.points} selected={selectedPoint} onSelect={selectPoint} />
              {!isPro && (
                <p className="text-center text-[11px] mt-3" style={{ color: "#A89E8B" }}>
                  {t("childrensMatrix.free_hint")}
                </p>
              )}
            </div>

            {point && !point.locked && (
              <div style={CARD}>
                <p className="font-cinzel uppercase" style={{ fontSize: 9, letterSpacing: ".22em", color: "#C9A84C" }}>
                  {t(`matrix.point_${point.id}`)}
                </p>
                <p className="font-cormorant" style={{ fontSize: 30, color: "#E8CD7E", lineHeight: 1.15, marginTop: 2 }}>
                  {point.arcana} · {point.arcana_name}
                </p>

                <div className="flex flex-col gap-2 mt-3">
                  <div style={{ padding: "9px 12px", borderRadius: 12, background: "rgba(201,168,76,.06)", border: "1px solid rgba(201,168,76,.16)" }}>
                    <span className="block text-[10px] uppercase font-cinzel" style={{ letterSpacing: ".18em", color: "#C9A84C" }}>{t("childrensMatrix.strength_label")}</span>
                    <span className="block text-[12.5px] mt-0.5" style={{ color: "#EDE7DA" }}>{point.strength}</span>
                  </div>
                  <div style={{ padding: "9px 12px", borderRadius: 12, background: "rgba(75,60,134,.10)", border: "1px solid rgba(138,127,192,.22)" }}>
                    <span className="block text-[10px] uppercase font-cinzel" style={{ letterSpacing: ".18em", color: "#B3A9E0" }}>{t("childrensMatrix.support_label")}</span>
                    <span className="block text-[12.5px] mt-0.5" style={{ color: "#EDE7DA" }}>{point.support}</span>
                  </div>
                </div>

                {reading !== undefined ? (
                  <div className="mt-3" style={{ padding: "12px 14px", borderRadius: 14, background: "rgba(255,255,255,.03)", border: "1px solid rgba(201,168,76,.13)" }}>
                    <p className="font-cinzel uppercase mb-1.5" style={{ fontSize: 9, letterSpacing: ".22em", color: "#C9A84C" }}>
                      {t("childrensMatrix.interpret")}
                    </p>
                    {reading ? (
                      <p className="text-[13px] whitespace-pre-wrap" style={{ color: "#D8D0C2", lineHeight: 1.65 }}>
                        {stripMarkdown(reading)}
                        {streaming && <span className="animate-pulse">▍</span>}
                      </p>
                    ) : (
                      <p className="text-[12px] animate-pulse" style={{ color: "#A89E8B" }}>{t("childrensMatrix.loading")}</p>
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
                    {t("childrensMatrix.interpret")}
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
          </>
        ) : null}
      </div>
    );
  }

  // ---- List view ----
  return (
    <div className="flex flex-col gap-3">
      <button onClick={onBack} className="text-left text-xs" style={{ color: "#C9A84C" }}>
        ‹ {t("common.back")}
      </button>

      <p className="font-cinzel uppercase mb-1" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
        {t("childrensMatrix.title")}
      </p>

      {loadingList ? (
        <p className="text-[12px] text-center animate-pulse" style={{ color: "#A89E8B" }}>{t("matrix.calculating")}</p>
      ) : children.length === 0 && !showAddForm ? (
        <p className="text-[12px] text-center" style={{ color: "#A89E8B" }}>{t("childrensMatrix.no_children")}</p>
      ) : (
        children.map(c => (
          <div key={c.id} className="cursor-pointer active:scale-[0.98] transition-all"
            style={{ display: "flex", gap: 14, alignItems: "center", justifyContent: "space-between", ...CARD }}
            onClick={() => selectChild(c.id)}>
            <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
              <div className="font-cormorant" style={{ width: 40, height: 40, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, color: "#F0E9DA", background: "linear-gradient(135deg,#4B3C86,#C9A84C)" }}>
                {c.name[0]?.toUpperCase()}
              </div>
              <p className="text-text-primary text-sm">{c.name}</p>
            </div>
            <button className="text-text-faint text-xs px-2" onClick={e => { e.stopPropagation(); handleDeleteChild(c.id); }}>x</button>
          </div>
        ))
      )}

      {showAddForm ? (
        <div style={CARD}>
          <div className="flex flex-col gap-2">
            <input className={inputCls} placeholder={t("childrensMatrix.name_placeholder")} value={addForm.name}
              onChange={e => { setAddForm(p => ({ ...p, name: e.target.value })); setAddErrors(p => ({ ...p, name: "" })); }} />
            {addErrors.name && <p className="text-red-400 text-[10px]">{addErrors.name}</p>}
            <div className="grid grid-cols-3 gap-2">
              <input className={inputCls} placeholder={t("childrensMatrix.day")} type="number" value={addForm.day}
                onChange={e => { setAddForm(p => ({ ...p, day: e.target.value })); setAddErrors(p => ({ ...p, day: "", date: "" })); }} />
              <input className={inputCls} placeholder={t("childrensMatrix.month")} type="number" value={addForm.month}
                onChange={e => { setAddForm(p => ({ ...p, month: e.target.value })); setAddErrors(p => ({ ...p, month: "", date: "" })); }} />
              <input className={inputCls} placeholder={t("childrensMatrix.year")} type="number" value={addForm.year}
                onChange={e => { setAddForm(p => ({ ...p, year: e.target.value })); setAddErrors(p => ({ ...p, year: "", date: "" })); }} />
            </div>
            {(addErrors.day || addErrors.month || addErrors.year || addErrors.date) && (
              <p className="text-red-400 text-[10px]">{addErrors.day || addErrors.month || addErrors.year || addErrors.date}</p>
            )}
            <div className="flex gap-2">
              <Button variant="primary" size="sm" className="flex-1" onClick={handleAddChild} disabled={adding}>
                {adding ? "..." : t("childrensMatrix.add")}
              </Button>
              <Button variant="ghost" size="sm" className="flex-1" onClick={() => setShowAddForm(false)}>
                {t("childrensMatrix.cancel")}
              </Button>
            </div>
          </div>
        </div>
      ) : (
        <button className="w-full py-3 text-sm transition-colors" onClick={() => setShowAddForm(true)}
          style={{ borderRadius: 14, border: "1px solid rgba(201,168,76,.4)", color: "#E8CD7E", background: "transparent" }}>
          {t("childrensMatrix.add_child")} +
        </button>
      )}
    </div>
  );
}
