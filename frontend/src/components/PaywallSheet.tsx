import { useState } from "react";
import { Button } from "./ui";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../utils/api";

interface PaywallSheetProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

const FEATURES = [
  "Безлимитные расклады Таро каждый день",
  "Натальные карты без ограничений",
  "Приоритетный доступ к новым функциям",
  "Персональные астрологические прогнозы",
];

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const twa = () => (window as any).Telegram?.WebApp;
const isTMA = () => Boolean(twa()?.initData);

export function PaywallSheet({ open, onClose, onSuccess }: PaywallSheetProps) {
  const { token, updateUser } = useAuth();
  const [loading, setLoading] = useState<string | null>(null);
  const [toast, setToast] = useState("");

  if (!open) return null;

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
        showToast("Открой через Telegram");
        setLoading(null);
        return;
      }

      webApp.openInvoice(data.invoice_link, async (status: string) => {
        if (status === "paid") {
          await apiRequest("/payments/stars/confirm", { payload: data.payload }, token ?? undefined);
          updateUser({ tier: "pro" });
          showToast("✦ Mystral Pro активирован");
          setTimeout(() => {
            onClose();
            onSuccess?.();
          }, 1500);
        }
        setLoading(null);
      });
    } catch {
      showToast("Ошибка. Попробуй позже.");
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
      showToast("Ошибка. Попробуй позже.");
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center max-w-[390px] mx-auto">
      {/* Overlay */}
      <div
        className="absolute inset-0"
        style={{ background: "rgba(6,4,20,0.75)" }}
        onClick={onClose}
      />

      {/* Sheet */}
      <div
        className="relative w-full rounded-t-2xl px-5 pt-5 pb-8 flex flex-col gap-4"
        style={{ background: "#0D0B1F", border: "0.5px solid rgba(107,78,255,0.2)" }}
      >
        {/* Handle */}
        <div className="w-10 h-1 rounded-full bg-border-subtle mx-auto -mt-1" />

        {/* Header */}
        <div className="flex items-center justify-between">
          <span className="font-display text-xl text-text-primary tracking-widest">
            ✦ Mystral Pro
          </span>
          <button className="text-text-muted text-xl w-8" onClick={onClose}>×</button>
        </div>

        {/* Features */}
        <div className="flex flex-col gap-2">
          {FEATURES.map(f => (
            <div key={f} className="flex items-start gap-2">
              <span className="text-violet-400 text-xs mt-0.5">✦</span>
              <span className="text-text-muted text-xs">{f}</span>
            </div>
          ))}
        </div>

        <div
          className="w-full h-px"
          style={{ background: "rgba(107,78,255,0.15)" }}
        />

        {/* Buttons */}
        <Button
          variant="gold"
          className="w-full"
          onClick={() => handleStars("pro_month")}
          disabled={loading !== null}
        >
          {loading === "pro_month" ? "Загрузка..." : "300 Stars · Месяц"}
        </Button>

        <Button
          variant="ghost"
          className="w-full"
          onClick={() => handleStars("pro_year")}
          disabled={loading !== null}
        >
          {loading === "pro_year" ? "Загрузка..." : "2400 Stars · Год  —20%"}
        </Button>

        {!isTMA() && (
          <Button
            variant="ghost"
            size="sm"
            className="w-full"
            onClick={handleYukassa}
            disabled={loading !== null}
          >
            {loading === "yukassa" ? "..." : "Оплатить картой"}
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
