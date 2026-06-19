import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "./ui";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../utils/api";

interface PaywallSheetProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const twa = () => (window as any).Telegram?.WebApp;
const isTMA = () => Boolean(twa()?.initData);

export function PaywallSheet({ open, onClose, onSuccess }: PaywallSheetProps) {
  const { t } = useTranslation();
  const { token, updateUser } = useAuth();
  const [loading, setLoading] = useState<string | null>(null);
  const [toast, setToast] = useState("");

  if (!open) return null;

  const features = [
    t("paywall.feature_tarot"),
    t("paywall.feature_natal"),
    t("paywall.feature_priority"),
    t("paywall.feature_personal"),
  ];

  function showToast(msg: string) {
    setToast(msg);
    setTimeout(() => setToast(""), 3000);
  }

  async function handleStars(product: "pro_month" | "pro_year") {
    setLoading(product);
    try {
      const data = await apiRequest<{ invoice_link: string; payload: string }>(
        "/payments/stars/create",
        { product },
        token ?? undefined
      );

      const webApp = twa();
      if (!webApp?.openInvoice) {
        showToast(t("paywall.open_tg"));
        setLoading(null);
        return;
      }

      webApp.openInvoice(data.invoice_link, async (status: string) => {
        if (status === "paid") {
          await apiRequest("/payments/stars/confirm", { payload: data.payload }, token ?? undefined);
          updateUser({ tier: "pro" });
          showToast(t("paywall.activated"));
          setTimeout(() => {
            onClose();
            onSuccess?.();
          }, 1500);
        }
        setLoading(null);
      });
    } catch {
      showToast(t("paywall.error"));
      setLoading(null);
    }
  }

  async function handleYukassa() {
    setLoading("yukassa");
    try {
      const data = await apiRequest<{ payment_url: string }>(
        "/payments/yukassa/create",
        { product: "pro_month" },
        token ?? undefined
      );
      window.open(data.payment_url, "_blank");
    } catch {
      showToast(t("paywall.error"));
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center max-w-[390px] mx-auto">
      <div
        className="absolute inset-0"
        style={{ background: "rgba(6,4,20,0.75)" }}
        onClick={onClose}
      />

      <div
        className="relative w-full rounded-t-2xl px-5 pt-5 pb-8 flex flex-col gap-4"
        style={{ background: "#0D0B1F", border: "0.5px solid rgba(107,78,255,0.2)" }}
      >
        <div className="w-10 h-1 rounded-full bg-border-subtle mx-auto -mt-1" />

        <div className="flex items-center justify-between">
          <span className="font-display text-xl text-text-primary tracking-widest">
            ✦ Mystral Pro
          </span>
          <button className="text-text-muted text-xl w-8" onClick={onClose}>×</button>
        </div>

        <div className="flex flex-col gap-2">
          {features.map(f => (
            <div key={f} className="flex items-start gap-2">
              <span className="text-violet-400 text-xs mt-0.5">✦</span>
              <span className="text-text-muted text-xs">{f}</span>
            </div>
          ))}
        </div>

        <div className="w-full h-px" style={{ background: "rgba(107,78,255,0.15)" }} />

        <Button variant="gold" className="w-full" onClick={() => handleStars("pro_month")} disabled={loading !== null}>
          {loading === "pro_month" ? t("paywall.loading") : t("paywall.stars_month")}
        </Button>

        <Button variant="ghost" className="w-full" onClick={() => handleStars("pro_year")} disabled={loading !== null}>
          {loading === "pro_year" ? t("paywall.loading") : t("paywall.stars_year")}
        </Button>

        {!isTMA() && (
          <Button variant="ghost" size="sm" className="w-full" onClick={handleYukassa} disabled={loading !== null}>
            {loading === "yukassa" ? "..." : t("paywall.pay_card")}
          </Button>
        )}

        {toast && (
          <p className="text-center text-xs" style={{ color: "#C9A84C" }}>
            {toast}
          </p>
        )}
      </div>
    </div>
  );
}
