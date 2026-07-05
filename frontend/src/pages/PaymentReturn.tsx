import { useEffect, useState } from "react";
import { Logo } from "../components/Logo";
import { useAuth } from "../context/AuthContext";
import { apiGet } from "../utils/api";

type Status = "checking" | "succeeded" | "canceled" | "pending" | "error";

export function PaymentReturn() {
  const { token, user, updateUser } = useAuth();
  const ru = (user?.lang ?? "ru") === "ru";
  const [status, setStatus] = useState<Status>("checking");

  const paymentId = new URLSearchParams(window.location.search).get("payment_id") || "";

  useEffect(() => {
    if (!paymentId) { setStatus("error"); return; }
    let cancelled = false;

    async function poll() {
      for (let i = 0; i < 5; i++) {
        const res = await apiGet<{ status: string; tier: string }>(
          `/payments/yukassa/status/${paymentId}`, token ?? undefined,
        ).catch(() => null);
        if (cancelled) return;
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
            {ru ? "Mystral Pro активирован" : "Mystral Pro is now active"}
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
          <button onClick={goHome} style={btnStyle}>{ru ? "Вернуться к тарифам" : "Back to plans"}</button>
        </>
      )}

      {status === "pending" && (
        <>
          <p className="font-cormorant" style={{ fontSize: 28, color: "#F0E9DA", marginTop: 24 }}>
            {ru ? "Платёж обрабатывается" : "Payment is processing"}
          </p>
          <p style={{ fontSize: 14, color: "#A89E8B", marginTop: 8, textAlign: "center" }}>
            {ru
              ? "Pro активируется в течение минуты. Обновите страницу, чтобы проверить снова."
              : "Pro will activate within a minute. Refresh to check again."}
          </p>
          <button onClick={() => window.location.reload()} style={btnStyle}>
            {ru ? "Проверить снова" : "Check again"}
          </button>
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
