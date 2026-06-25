import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../utils/api";
import { Logo } from "./Logo";

interface PaywallSheetProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

const twa = () => (window as any).Telegram?.WebApp;
const isTMA = () => Boolean(twa()?.initData);

const BENEFITS_RU = [
  { icon: "*", title: "Безлимитные расклады Таро", desc: "Все колоды и развороты без ограничений" },
  { icon: "◎", title: "Полная натальная карта", desc: "Аспекты, дома и AI-интерпретация" },
  { icon: "♡", title: "Глубокая совместимость", desc: "Синастрия по всем планетам" },
  { icon: "🔔", title: "Персональные прогнозы", desc: "Уведомления по вашей карте каждый день" },
  { icon: "☽", title: "Лунный календарь Pro", desc: "Детальные рекомендации на каждый день" },
];
const BENEFITS_EN = [
  { icon: "*", title: "Unlimited Tarot spreads", desc: "All decks and spreads without limits" },
  { icon: "◎", title: "Full natal chart", desc: "Aspects, houses and AI interpretation" },
  { icon: "♡", title: "Deep compatibility", desc: "Synastry across all planets" },
  { icon: "🔔", title: "Personal forecasts", desc: "Daily notifications based on your chart" },
  { icon: "☽", title: "Lunar calendar Pro", desc: "Detailed daily recommendations" },
];

export function PaywallSheet({ open, onClose, onSuccess }: PaywallSheetProps) {
  const { t } = useTranslation();
  const { token, user, updateUser } = useAuth();
  const ru = (user?.lang ?? "ru") === "ru";
  const [plan, setPlan] = useState<"year" | "month">("year");
  const [loading, setLoading] = useState<string | null>(null);
  const [toast, setToast] = useState("");
  const [isDesktop, setIsDesktop] = useState(window.innerWidth >= 1024);

  useEffect(() => {
    const h = () => setIsDesktop(window.innerWidth >= 1024);
    window.addEventListener("resize", h);
    return () => window.removeEventListener("resize", h);
  }, []);

  if (!open) return null;

  const benefits = ru ? BENEFITS_RU : BENEFITS_EN;

  function showToast(msg: string) { setToast(msg); setTimeout(() => setToast(""), 3000); }

  async function handleBuy() {
    const product = plan === "year" ? "pro_year" : "pro_month";
    setLoading(product);
    try {
      const data = await apiRequest<{ invoice_link: string; payload: string }>(
        "/payments/stars/create", { product }, token ?? undefined,
      );
      const webApp = twa();
      if (!webApp?.openInvoice) { showToast(t("paywall.open_tg")); setLoading(null); return; }
      webApp.openInvoice(data.invoice_link, async (status: string) => {
        if (status === "paid") {
          await apiRequest("/payments/stars/confirm", { payload: data.payload }, token ?? undefined);
          updateUser({ tier: "pro" });
          showToast(t("paywall.activated"));
          setTimeout(() => { onClose(); onSuccess?.(); }, 1500);
        }
        setLoading(null);
      });
    } catch { showToast(t("paywall.error")); setLoading(null); }
  }

  async function handleYukassa() {
    setLoading("yukassa");
    try {
      const data = await apiRequest<{ payment_url: string }>("/payments/yukassa/create", { product: "pro_month" }, token ?? undefined);
      window.open(data.payment_url, "_blank");
    } catch { showToast(t("paywall.error")); }
    finally { setLoading(null); }
  }

  const price = plan === "year" ? "1500" : "190";
  const period = plan === "year" ? (ru ? "12 месяцев" : "12 months") : (ru ? "1 месяц" : "1 month");

  function PlanCard({ type, label, priceVal, sub, badge }: { type: "year" | "month"; label: string; priceVal: string; sub: string; badge?: string }) {
    const active = plan === type;
    return (
      <button onClick={() => setPlan(type)} style={{
        position: "relative", flex: 1, padding: "20px 16px", borderRadius: 16, cursor: "pointer", textAlign: "left",
        background: active ? "linear-gradient(155deg,rgba(201,168,76,.12),rgba(201,168,76,.04))" : "rgba(255,255,255,.04)",
        border: `1.5px solid ${active ? "rgba(201,168,76,.5)" : "rgba(255,255,255,.1)"}`,
      }}>
        {badge && (
          <span style={{ position: "absolute", top: -9, left: 16, fontSize: 9.5, letterSpacing: ".12em", fontWeight: 600, background: "linear-gradient(100deg,#A9882F,#E8CD7E)", color: "#1A1206", padding: "3px 9px", borderRadius: 99 }}>
            {badge}
          </span>
        )}
        <div style={{ fontSize: 13, color: "#B6AC98" }}>{label}</div>
        <div style={{ display: "flex", alignItems: "center", gap: 5, marginTop: 6, lineHeight: 1 }}>
          <span style={{ fontSize: 18, color: "#C9A84C" }}>⭐</span>
          <span className="font-cormorant" style={{ fontSize: 34, color: "#F0E9DA" }}>{priceVal}</span>
        </div>
        <div style={{ fontSize: 11, color: "#6E6757", marginTop: 3 }}>{sub}</div>
      </button>
    );
  }

  function BuyButton() {
    return (
      <button onClick={handleBuy} disabled={loading !== null} style={{ position: "relative", overflow: "hidden", width: "100%", height: 56, borderRadius: 16, cursor: loading ? "default" : "pointer", background: "linear-gradient(100deg,#A9882F,#C9A84C 50%,#E8CD7E)", display: "flex", alignItems: "center", justifyContent: "center", gap: 9, boxShadow: "0 12px 32px -8px rgba(201,168,76,.6)", border: "none" }}>
        <span style={{ position: "absolute", inset: 0, background: "linear-gradient(100deg,transparent 30%,rgba(255,255,255,.5) 50%,transparent 70%)", backgroundSize: "200% 100%", animation: "mystral-shimmer 2.6s linear infinite" }} />
        <span style={{ position: "relative", color: "#1A1206", fontWeight: 600, fontSize: 15.5, display: "flex", alignItems: "center", gap: 8 }}>
          ⭐ {loading ? "..." : (ru ? `Оформить за ${price} Stars` : `Subscribe for ${price} Stars`)}
        </span>
      </button>
    );
  }

  function Footnote() {
    return (
      <>
        <p style={{ textAlign: "center", fontSize: 12, color: "#6E6757", marginTop: 14 }}>
          {ru ? `Оплата через Telegram Stars · ${period} · отмена в любой момент` : `Payment via Telegram Stars · ${period} · cancel anytime`}
        </p>
        {!isTMA() && (
          <button onClick={handleYukassa} disabled={loading !== null} style={{ width: "100%", marginTop: 10, padding: "10px 0", borderRadius: 12, background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,.08)", color: "#B6AC98", fontSize: 13, cursor: "pointer" }}>
            {loading === "yukassa" ? "..." : (ru ? "Оплатить картой" : "Pay with card")}
          </button>
        )}
        {toast && <p style={{ textAlign: "center", fontSize: 13, color: "#C9A84C", marginTop: 10 }}>{toast}</p>}
      </>
    );
  }

  // =================== DESKTOP ===================
  if (isDesktop) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: "rgba(0,0,0,.7)", backdropFilter: "blur(6px)" }} onClick={e => e.target === e.currentTarget && onClose()}>
        <div style={{ width: "100%", maxWidth: 1060, padding: "10px 40px 50px", display: "grid", gridTemplateColumns: "1fr 420px", gap: 40, alignItems: "start", background: "radial-gradient(120% 60% at 50% -6%, #1C1433 0%, #07060F 52%)", borderRadius: 28, border: "1px solid rgba(201,168,76,.18)", maxHeight: "90vh", overflowY: "auto" }}>

          {/* Header across both columns */}
          <div style={{ gridColumn: "1 / -1", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "18px 0" }}>
            <div />
            <button onClick={onClose} style={{ width: 40, height: 40, display: "flex", alignItems: "center", justifyContent: "center", borderRadius: 12, background: "rgba(255,255,255,.05)", border: "1px solid rgba(255,255,255,.1)", color: "#B6AC98", cursor: "pointer", fontSize: 18 }}>✕</button>
          </div>

          {/* Left */}
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
              <div style={{ filter: "drop-shadow(0 0 34px rgba(201,168,76,.5))", animation: "mystral-float 7s ease-in-out infinite" }}>
                <Logo size={80} />
              </div>
              <div>
                <p className="font-cinzel" style={{ fontSize: 30, letterSpacing: ".24em", color: "#E8CD7E" }}>MYSTRAL PRO</p>
                <p className="font-cormorant italic" style={{ fontSize: 20, color: "#A89E8B", marginTop: 6 }}>
                  {ru ? "Полный доступ к языку звёзд" : "Full access to the language of stars"}
                </p>
              </div>
            </div>

            <div style={{ marginTop: 30, display: "flex", flexDirection: "column", gap: 16 }}>
              {benefits.map(b => (
                <div key={b.title} style={{ display: "flex", gap: 16, alignItems: "flex-start", padding: "16px 18px", borderRadius: 16, background: "linear-gradient(155deg,rgba(255,255,255,.04),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.12)" }}>
                  <div style={{ width: 36, height: 36, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", borderRadius: 11, background: "rgba(201,168,76,.1)", border: "1px solid rgba(201,168,76,.26)", color: "#C9A84C", fontSize: 16 }}>{b.icon}</div>
                  <div>
                    <div style={{ fontSize: 15, color: "#F0E9DA", fontWeight: 500 }}>{b.title}</div>
                    <div style={{ fontSize: 13, color: "#8A8170", marginTop: 1 }}>{b.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right — sticky */}
          <div style={{ position: "sticky", top: 10, padding: 28, borderRadius: 24, background: "radial-gradient(120% 80% at 50% 0%, #1A1440, #0C0A20)", border: "1px solid rgba(201,168,76,.24)" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <PlanCard type="year" label={ru ? "Год" : "Year"} priceVal="1500" sub={ru ? "всего 125 Stars в месяц" : "only 125 Stars/month"} badge={ru ? "ВЫГОДНО −34%" : "SAVE −34%"} />
              <PlanCard type="month" label={ru ? "Месяц" : "Month"} priceVal="190" sub={ru ? "гибкая отмена" : "flexible cancel"} />
            </div>
            <div style={{ marginTop: 20 }}><BuyButton /></div>
            <Footnote />
          </div>
        </div>
      </div>
    );
  }

  // =================== MOBILE ===================
  return (
    <div className="fixed inset-0 z-50" style={{ background: "radial-gradient(120% 60% at 50% -6%, #1C1433 0%, #07060F 52%)", overflowY: "auto", overflowX: "hidden" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "18px 22px" }}>
        <button onClick={onClose} style={{ width: 40, height: 40, display: "flex", alignItems: "center", justifyContent: "center", borderRadius: 12, background: "rgba(255,255,255,.05)", border: "1px solid rgba(255,255,255,.1)", color: "#B6AC98", cursor: "pointer", fontSize: 18 }}>✕</button>
        <span style={{ fontSize: 18, color: "#6E6757", cursor: "pointer" }}>↗</span>
      </div>

      <div style={{ padding: "6px 24px 40px", maxWidth: 560, margin: "0 auto" }}>
        {/* Logo + title */}
        <div style={{ textAlign: "center" }}>
          <div style={{ width: 96, height: 96, margin: "0 auto", filter: "drop-shadow(0 0 34px rgba(201,168,76,.5))", animation: "mystral-float 7s ease-in-out infinite" }}>
            <Logo size={96} />
          </div>
          <p className="font-cinzel" style={{ fontSize: 26, letterSpacing: ".26em", color: "#E8CD7E", marginTop: 20 }}>MYSTRAL PRO</p>
          <p className="font-cormorant italic" style={{ fontSize: 19, color: "#A89E8B", marginTop: 8 }}>
            {ru ? "Полный доступ к языку звёзд" : "Full access to the language of stars"}
          </p>
        </div>

        {/* Benefits */}
        <div style={{ marginTop: 28, display: "flex", flexDirection: "column", gap: 14 }}>
          {benefits.map(b => (
            <div key={b.title} style={{ display: "flex", gap: 14, alignItems: "flex-start" }}>
              <div style={{ width: 34, height: 34, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", borderRadius: 10, background: "rgba(201,168,76,.1)", border: "1px solid rgba(201,168,76,.26)", color: "#C9A84C", fontSize: 14 }}>{b.icon}</div>
              <div>
                <div style={{ fontSize: 14.5, color: "#F0E9DA", fontWeight: 500 }}>{b.title}</div>
                <div style={{ fontSize: 12.5, color: "#8A8170", marginTop: 1 }}>{b.desc}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Plan selector */}
        <div style={{ marginTop: 26, display: "flex", gap: 12 }}>
          <PlanCard type="year" label={ru ? "Год" : "Year"} priceVal="1500" sub={ru ? "125 Stars в месяц" : "125 Stars/month"} badge={ru ? "ВЫГОДНО −34%" : "SAVE −34%"} />
          <PlanCard type="month" label={ru ? "Месяц" : "Month"} priceVal="190" sub={ru ? "гибкая отмена" : "flexible cancel"} />
        </div>

        {/* Buy button */}
        <div style={{ marginTop: 20 }}><BuyButton /></div>
        <Footnote />
      </div>
    </div>
  );
}
