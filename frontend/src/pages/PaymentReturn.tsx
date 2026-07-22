import { useEffect, useState } from "react";
import { Logo } from "../components/Logo";
import { useAuth } from "../context/AuthContext";
import { apiGet, apiRequest } from "../utils/api";

type Status = "checking" | "succeeded" | "canceled" | "pending" | "error";

export function PaymentReturn() {
  const { token, user, updateUser } = useAuth();
  const ru = (user?.lang ?? "ru") === "ru";
  const [status, setStatus] = useState<Status>("checking");
  const [product, setProduct] = useState<string | null>(null);
  const [retrying, setRetrying] = useState(false);

  const paymentId = new URLSearchParams(window.location.search).get("payment_id") || "";

  useEffect(() => {
    if (!paymentId) { setStatus("error"); return; }
    let cancelled = false;

    async function poll() {
      for (let i = 0; i < 5; i++) {
        const res = await apiGet<{ status: string; tier: string; product?: string }>(
          `/payments/yukassa/status/${paymentId}`, token ?? undefined,
        ).catch(() => null);
        if (cancelled) return;
        if (res?.product) setProduct(res.product);
        if (res?.status === "succeeded") {
          updateUser({ tier: "pro" });
          setStatus("succeeded");
          return;
        }
        if (res?.status === "canceled") { setStatus("canceled"); return; }
        await new Promise(r => setTimeout(r, 2000));
      }
      if (!cancelled) setStatus("pending");
    }
    poll();
    return () => { cancelled = true; };
  }, [paymentId]);

  function goHome() { window.location.search = ""; }

  // QA-040: leaving YuKassa's page without finishing (closing the tab, hitting
  // back) leaves the payment "pending" on their side too, often for a long
  // time — our poll can't wait that out. Retrying starts a brand new payment
  // for the same plan rather than re-checking the stuck one, so the user has
  // a real way out instead of "reload" re-running the same doomed poll.
  async function handleRetry() {
    if (!product) { goHome(); return; }
    setRetrying(true);
    try {
      const data = await apiRequest<{ payment_url: string; payment_id: string }>(
        "/payments/yukassa/create", { product }, token ?? undefined,
      );
      window.location.href = data.payment_url;
    } catch {
      setRetrying(false);
    }
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "0 24px", background: "var(--gradient-page)" }}>
      <div style={{ animation: "mystral-float 7s ease-in-out infinite", filter: "drop-shadow(0 0 30px rgba(201,168,76,.5))" }}>
        <Logo size={64} />
      </div>

      {status === "checking" && (
        <>
          <p className="font-cormorant" style={{ fontSize: 28, color: "#F0E9DA", marginTop: 24 }}>
            {ru ? "Проверяем платёж…" : "Checking payment…"}
          </p>
          <p style={{ fontSize: 14, color: "#A89E8B", marginTop: 8 }}>
            {ru ? "Это займёт несколько секунд" : "This takes a few seconds"}
          </p>
        </>
      )}

      {status === "succeeded" && (
        <>
          <p style={{ fontSize: 48, color: "#C9A84C", marginTop: 24 }}>✓</p>
          <p className="font-cormorant" style={{ fontSize: 28, color: "#F0E9DA", marginTop: 12 }}>
            {ru ? "Оплата прошла успешно" : "Payment successful"}
          </p>
          <p style={{ fontSize: 14, color: "#A89E8B", marginTop: 8, textAlign: "center" }}>
            {ru ? "Поздравляем, у вас Mystral Pro!" : "Congratulations, you have Mystral Pro!"}
          </p>
          <button onClick={goHome} style={btnStyle}>{ru ? "На главную" : "Go home"}</button>
        </>
      )}

      {status === "canceled" && (
        <>
          <p className="font-cormorant" style={{ fontSize: 28, color: "#F0E9DA", marginTop: 24 }}>
            {ru ? "Оплата не завершена" : "Payment not completed"}
          </p>
          <p style={{ fontSize: 14, color: "#A89E8B", marginTop: 8, textAlign: "center" }}>
            {ru ? "Платёж был отменён. Вы можете попробовать снова." : "The payment was canceled. You can try again."}
          </p>
          <div style={{ display: "flex", gap: 12, marginTop: 20 }}>
            <button onClick={goHome} style={ghostBtnStyle}>{ru ? "На главную" : "Go home"}</button>
            {product && (
              <button onClick={handleRetry} disabled={retrying} style={{ ...btnStyle, marginTop: 0 }}>
                {retrying ? "…" : (ru ? "Попробовать снова" : "Try again")}
              </button>
            )}
          </div>
        </>
      )}

      {status === "pending" && (
        <>
          <p className="font-cormorant" style={{ fontSize: 28, color: "#F0E9DA", marginTop: 24 }}>
            {ru ? "Платёж пока не подтверждён" : "Payment not confirmed yet"}
          </p>
          <p style={{ fontSize: 14, color: "#A89E8B", marginTop: 8, textAlign: "center", maxWidth: 320 }}>
            {ru
              ? "Если вы уже оплатили — Pro активируется в течение минуты, просто вернитесь позже. Если вы закрыли окно оплаты, не завершив её, попробуйте оплатить снова."
              : "If you already paid, Pro will activate within a minute — just check back later. If you closed the payment window without finishing, try paying again."}
          </p>
          <div style={{ display: "flex", gap: 12, marginTop: 20 }}>
            <button onClick={goHome} style={ghostBtnStyle}>{ru ? "На главную" : "Go home"}</button>
            {product && (
              <button onClick={handleRetry} disabled={retrying} style={{ ...btnStyle, marginTop: 0 }}>
                {retrying ? "…" : (ru ? "Попробовать снова" : "Try again")}
              </button>
            )}
          </div>
        </>
      )}

      {status === "error" && (
        <>
          <p className="font-cormorant" style={{ fontSize: 28, color: "#F0E9DA", marginTop: 24 }}>
            {ru ? "Платёж не найден" : "Payment not found"}
          </p>
          <button onClick={goHome} style={btnStyle}>{ru ? "На главную" : "Go home"}</button>
        </>
      )}
    </div>
  );
}

const btnStyle: React.CSSProperties = {
  marginTop: 20, height: 48, padding: "0 32px", borderRadius: 14,
  background: "linear-gradient(100deg,#A9882F,#C9A84C,#E8CD7E)",
  color: "#1A1206", fontWeight: 600, fontSize: 14, border: "none", cursor: "pointer",
};

const ghostBtnStyle: React.CSSProperties = {
  height: 48, padding: "0 28px", borderRadius: 14,
  background: "transparent", border: "1px solid rgba(201,168,76,.35)",
  color: "#C9A84C", fontWeight: 600, fontSize: 14, cursor: "pointer",
};
