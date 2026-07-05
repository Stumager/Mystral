import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Share2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { streamRequest } from "../utils/api";
import { stripMarkdown } from "../utils/markdown";
import { ShareCard } from "./ShareCard";
import { PaywallSheet } from "./PaywallSheet";

interface Planet {
  name: string;
  name_ru: string;
  sign: string;
  sign_ru: string;
  degree: number;
  abs_pos: number;
}

interface Aspect {
  planet1: string;
  planet1_ru: string;
  planet2: string;
  planet2_ru: string;
  type: string;
  orb: number;
}

interface CompositeData {
  planets: Planet[];
  aspects: Aspect[];
  summary: {
    element_balance: Record<string, number>;
    modality_balance: Record<string, number>;
  };
  partner_name: string;
  error?: string;
}

interface Props {
  partnerId: string;
  partnerName: string;
  onClose: () => void;
}

const ASPECT_LABELS: Record<string, string> = {
  conjunction: "Соединение",
  trine: "Трин",
  sextile: "Секстиль",
  square: "Квадрат",
  opposition: "Оппозиция",
};
const ASPECT_LABELS_EN: Record<string, string> = {
  conjunction: "Conjunction",
  trine: "Trine",
  sextile: "Sextile",
  square: "Square",
  opposition: "Opposition",
};

type Section = "overview" | "planets" | "aspects" | "advice";

export function CompositeChart({ partnerId, partnerName, onClose }: Props) {
  const { user, token } = useAuth();
  const { i18n } = useTranslation();
  const lang = user?.lang ?? i18n.language ?? "ru";
  const ru = lang === "ru";

  const [data, setData] = useState<CompositeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<Section>("overview");
  const [interpretation, setInterpretation] = useState("");
  const [interpretLoading, setInterpretLoading] = useState(false);
  const [loadedTabs, setLoadedTabs] = useState<Set<Section>>(new Set());
  const [showShare, setShowShare] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);
  const [profileFullName, setProfileFullName] = useState<string | null>(null);
  const loaded = useRef(false);
  const profileLoaded = useRef(false);
  const requestIdRef = useRef(0);

  useEffect(() => {
    if (profileLoaded.current || !token) return;
    profileLoaded.current = true;
    fetch("/api/v1/profile", { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(profileData => setProfileFullName(profileData.full_name || null))
      .catch(() => {});
  }, [token]);

  useEffect(() => {
    if (loaded.current || !token) return;
    loaded.current = true;
    fetchComposite();
  }, [token]);

  async function fetchComposite() {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/compatibility/composite", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ partner_id: partnerId, lang }),
      });
      if (res.status === 402) { setShowPaywall(true); setLoading(false); return; }
      if (!res.ok) { setError(ru ? "Ошибка расчёта" : "Calculation error"); setLoading(false); return; }
      const json = await res.json();
      if (json.error) { setError(json.message || json.error); setLoading(false); return; }
      setData(json);
      loadInterpretation("overview", json);
    } catch {
      setError(ru ? "Ошибка соединения" : "Connection error");
    } finally {
      setLoading(false);
    }
  }

  async function loadInterpretation(section: Section, chartData?: CompositeData) {
    const d = chartData ?? data;
    if (!d) return;
    setActiveTab(section);
    if (loadedTabs.has(section)) return;

    // Guards against a still-running stream from a previously selected tab
    // appending its late chunks into this tab's text (visible as duplicated
    // / mixed-up content when switching tabs before a stream finishes).
    const requestId = ++requestIdRef.current;
    const isStale = () => requestIdRef.current !== requestId;

    setInterpretLoading(true);
    setInterpretation("");
    try {
      await streamRequest(
        "/compatibility/composite/interpret",
        { partner_id: partnerId, section, lang },
        (chunk) => { if (!isStale()) setInterpretation(prev => prev + chunk); },
        () => {
          if (isStale()) return;
          setInterpretLoading(false);
          setLoadedTabs(prev => new Set([...prev, section]));
        },
        token ?? undefined,
        (msg) => { if (!isStale()) { setInterpretation(msg); setInterpretLoading(false); } },
      );
    } catch (e: unknown) {
      if (isStale()) return;
      const err = e as { code?: string };
      if (err.code === "FREE_LIMIT_REACHED") setShowPaywall(true);
      setInterpretLoading(false);
    }
  }

  function handleTabClick(section: Section) {
    if (section === activeTab && loadedTabs.has(section)) return;
    if (section !== activeTab) setInterpretation("");
    loadInterpretation(section);
  }

  const aspectColor = (type: string) => {
    if (type === "trine" || type === "sextile") return "#6E9A8A";
    if (type === "square" || type === "opposition") return "#D98A8A";
    return "#C9A84C";
  };

  const aspectLabel = (type: string) =>
    ru ? (ASPECT_LABELS[type] ?? type) : (ASPECT_LABELS_EN[type] ?? type);

  // Prefer the name entered for astrological calculations (profile.full_name)
  // over the account's display_name, which can be a Telegram handle/login
  // rather than a real name — same priority the backend uses for this chart.
  const userName = profileFullName || user?.name || "?";
  const partnerInitial = partnerName[0]?.toUpperCase() ?? "?";
  const userInitial = userName[0]?.toUpperCase() ?? "?";

  const mainAspect = data?.aspects?.[0];
  const mainAspectText = mainAspect
    ? `${ru ? mainAspect.planet1_ru : mainAspect.planet1} ${aspectLabel(mainAspect.type)} ${ru ? mainAspect.planet2_ru : mainAspect.planet2}`
    : undefined;
  const shareDescription = interpretation
    ? (() => {
        const clean = stripMarkdown(interpretation);
        return clean.length > 140 ? `${clean.slice(0, 140)}…` : clean;
      })()
    : undefined;

  const TABS: { id: Section; label: string }[] = [
    { id: "overview", label: ru ? "Обзор" : "Overview" },
    { id: "planets", label: ru ? "Планеты" : "Planets" },
    { id: "aspects", label: ru ? "Аспекты" : "Aspects" },
    { id: "advice", label: ru ? "Советы" : "Advice" },
  ];

  const topAspects = (data?.aspects ?? []).slice(0, 5);

  return (
    <div style={{ maxWidth: 480, margin: "0 auto", padding: "20px 16px 32px" }}>
      {/* Partner avatars */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 0, margin: "0 0 8px" }}>
        <div className="font-cormorant" style={{ width: 52, height: 52, borderRadius: "50%", background: "linear-gradient(135deg,#4B3C86,#C9A84C)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22, color: "#0C0A18", fontWeight: 600, zIndex: 2, position: "relative" }}>
          {userInitial}
        </div>
        <div style={{ fontSize: 28, color: "#C9A84C", margin: "0 -4px", zIndex: 3, position: "relative", lineHeight: 1 }}>∞</div>
        <div className="font-cormorant" style={{ width: 52, height: 52, borderRadius: "50%", background: "linear-gradient(135deg,#2D3B6E,#8A5CC4)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22, color: "#0C0A18", fontWeight: 600, zIndex: 2, position: "relative" }}>
          {partnerInitial}
        </div>
      </div>
      <p className="font-cormorant" style={{ textAlign: "center", fontSize: 18, color: "#A89E8B", fontStyle: "italic", marginBottom: 24 }}>
        {ru ? "Карта отношений" : "Relationship Chart"}
      </p>

      {loading && (
        <p className="text-text-muted text-xs text-center animate-pulse" style={{ marginTop: 40 }}>
          {ru ? "Расчёт композитной карты..." : "Calculating composite chart..."}
        </p>
      )}

      {error && !loading && (
        <p style={{ color: "#D98A8A", fontSize: 13, textAlign: "center", marginTop: 40 }}>{error}</p>
      )}

      {data && !loading && (
        <>
          {/* Planets table */}
          <p className="font-cinzel" style={{ fontSize: 10, letterSpacing: ".2em", color: "#C9A84C", textTransform: "uppercase", margin: "0 0 12px" }}>
            {ru ? "Планеты композитной карты" : "Composite Planets"}
          </p>
          <div style={{ marginBottom: 20 }}>
            {data.planets.map(p => (
              <div key={p.name} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 0", borderBottom: "1px solid rgba(255,255,255,.06)" }}>
                <span style={{ fontSize: 14, color: "#F0E9DA" }}>{ru ? p.name_ru : p.name}</span>
                <span style={{ fontSize: 13, color: "#C9A84C" }}>{ru ? p.sign_ru : p.sign} {p.degree}°</span>
              </div>
            ))}
          </div>

          {/* Aspects top-5 */}
          {topAspects.length > 0 && (
            <>
              <p className="font-cinzel" style={{ fontSize: 10, letterSpacing: ".2em", color: "#C9A84C", textTransform: "uppercase", margin: "0 0 12px" }}>
                {ru ? "Ключевые аспекты" : "Key Aspects"}
              </p>
              <div style={{ marginBottom: 20 }}>
                {topAspects.map((a, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 0", borderBottom: "1px solid rgba(255,255,255,.06)" }}>
                    <span style={{ fontSize: 14, color: "#F0E9DA" }}>
                      {ru ? a.planet1_ru : a.planet1} · {ru ? a.planet2_ru : a.planet2}
                    </span>
                    <span style={{ fontSize: 13, color: aspectColor(a.type) }}>
                      {aspectLabel(a.type)} {a.orb}°
                    </span>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* AI tabs */}
          <div style={{ display: "flex", gap: 6, marginBottom: 16, flexWrap: "wrap" }}>
            {TABS.map(tab => (
              <button key={tab.id} onClick={() => handleTabClick(tab.id)}
                style={{ padding: "6px 14px", borderRadius: 99, border: "none", cursor: "pointer", fontSize: 12, fontWeight: 500, transition: "all .2s",
                  background: activeTab === tab.id ? "#C9A84C" : "rgba(255,255,255,.06)",
                  color: activeTab === tab.id ? "#07060F" : "#A89E8B" }}>
                {tab.label}
              </button>
            ))}
          </div>

          {(interpretation || interpretLoading) && (
            <div style={{ borderRadius: 14, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "14px 16px", marginBottom: 16 }}>
              <p style={{ fontSize: 9, letterSpacing: ".18em", color: "#C9A84C", textTransform: "uppercase", marginBottom: 8 }}>AI</p>
              <p style={{ fontSize: 13, color: "#BEB5A6", lineHeight: 1.6 }}>
                {stripMarkdown(interpretation)}{interpretLoading && <span className="animate-pulse">▍</span>}
              </p>
            </div>
          )}

          {/* Share */}
          <button onClick={() => setShowShare(true)}
            style={{ width: "100%", height: 44, marginTop: 8, borderRadius: 14, border: "1px solid rgba(201,168,76,.25)", background: "transparent", color: "#C9A84C", fontSize: 13, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}>
            <Share2 size={16} />
            {ru ? "Поделиться картой" : "Share chart"}
          </button>
        </>
      )}

      <PaywallSheet open={showPaywall} onClose={() => { setShowPaywall(false); onClose(); }} />

      {showShare && data && (
        <ShareCard
          type="composite"
          title={`${userName} & ${partnerName}`}
          subtitle={ru ? "Композитная карта" : "Composite Chart"}
          aspectLabel={mainAspectText}
          description={shareDescription}
          onClose={() => setShowShare(false)}
        />
      )}
    </div>
  );
}
