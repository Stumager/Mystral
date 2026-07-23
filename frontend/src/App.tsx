import { lazy, Suspense, useState } from "react";
import { useTranslation } from "react-i18next";
import "./i18n";
import { AppLayout } from "./components/layout/AppLayout";
import { Logo } from "./components/Logo";
import { MergeAccountPrompt } from "./components/MergeAccountPrompt";
import { OnboardingModal } from "./components/OnboardingModal";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { Home } from "./pages/Home";
import { LoginScreen } from "./pages/LoginScreen";

// TZ-090: these used to be eager imports, so every page's code shipped in
// the single main bundle (370 KB / 103 KB gzip) even though only one of
// them ever renders per session before the user navigates. Home and
// LoginScreen stay eager — one of the two is always the first paint.
const Admin = lazy(() => import("./pages/Admin").then(m => ({ default: m.Admin })));
const Compatibility = lazy(() => import("./pages/Compatibility").then(m => ({ default: m.Compatibility })));
const ForgotPassword = lazy(() => import("./pages/ForgotPassword").then(m => ({ default: m.ForgotPassword })));
const ResetPassword = lazy(() => import("./pages/ResetPassword").then(m => ({ default: m.ResetPassword })));
const LunarCalendar = lazy(() => import("./pages/LunarCalendar").then(m => ({ default: m.LunarCalendar })));
const Privacy = lazy(() => import("./pages/Privacy").then(m => ({ default: m.Privacy })));
const Terms = lazy(() => import("./pages/Terms").then(m => ({ default: m.Terms })));
const NatalChart = lazy(() => import("./pages/NatalChart").then(m => ({ default: m.NatalChart })));
const Numerology = lazy(() => import("./pages/Numerology").then(m => ({ default: m.Numerology })));
const PaymentReturn = lazy(() => import("./pages/PaymentReturn").then(m => ({ default: m.PaymentReturn })));
const Profile = lazy(() => import("./pages/Profile").then(m => ({ default: m.Profile })));
const Runes = lazy(() => import("./pages/Runes").then(m => ({ default: m.Runes })));
const Tarot = lazy(() => import("./pages/Tarot").then(m => ({ default: m.Tarot })));

type Page = "home" | "tarot" | "moon" | "natal" | "profile" | "lunar" | "compat" | "numerology" | "numero" | "runes" | "admin";

function PageFallback() {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh", background: "#07060F" }}>
      <span style={{ width: 28, height: 28, border: "2px solid rgba(201,168,76,.3)", borderTopColor: "#C9A84C", borderRadius: "50%", display: "inline-block" }} className="animate-spin" />
    </div>
  );
}

function AppInner() {
  const { t } = useTranslation();
  const [page, setPage] = useState<Page>("home");
  const { user, isLoading, pendingMerge, dismissMerge, updateUser, statusMessage, clearStatusMessage } = useAuth();
  const [onboardingDismissed, setOnboardingDismissed] = useState(false);

  const navigate = (p: string) => setPage(p as Page);

  if (isLoading) {
    return (
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100vh", background: "#07060F", gap: 20 }}>
        <div style={{ animation: "mystral-logo-glow 2s ease-in-out infinite" }}>
          <Logo size={80} />
        </div>
        <style>{`@keyframes mystral-logo-glow {
          0%,100% { filter: drop-shadow(0 0 20px rgba(201,168,76,.4)) drop-shadow(0 0 40px rgba(201,168,76,.2)); }
          50% { filter: drop-shadow(0 0 32px rgba(201,168,76,.8)) drop-shadow(0 0 60px rgba(201,168,76,.4)); }
        }`}</style>
        <span className="font-cinzel" style={{ fontSize: 13, letterSpacing: ".4em", color: "#E8CD7E", marginTop: 8 }}>MYSTRAL</span>
        <div style={{ display: "flex", gap: 6, marginTop: 16 }}>
          {[0, 0.2, 0.4].map((d, i) => (
            <span key={i} style={{ width: 6, height: 6, borderRadius: "50%", background: "#C9A84C", animation: `mystral-fadeup .6s ease-out infinite ${d}s` }} />
          ))}
        </div>
      </div>
    );
  }

  // Handle ref links: /ref/CODE or #ref/CODE
  const refMatch = window.location.pathname.match(/\/ref\/(\w+)/) || window.location.hash.match(/#ref\/(\w+)/);
  if (refMatch) {
    localStorage.setItem("mystral_ref_code", refMatch[1]);
    window.history.replaceState(null, "", "/");
  }

  // Public pages (no auth required)
  const path = window.location.pathname;
  if (path === "/privacy") return <Suspense fallback={<PageFallback />}><Privacy /></Suspense>;
  if (path === "/terms") return <Suspense fallback={<PageFallback />}><Terms /></Suspense>;

  if (page === "admin" || window.location.hash.replace(/\/+$/, "") === "#admin")
    return <Suspense fallback={<PageFallback />}><Admin /></Suspense>;

  if (window.location.search.includes("token="))
    return <Suspense fallback={<PageFallback />}><ResetPassword /></Suspense>;

  const hash = window.location.hash.replace(/\/+$/, "");
  if (hash === "#forgot-password")
    return (
      <Suspense fallback={<PageFallback />}>
        <ForgotPassword onBack={() => { window.location.hash = ""; window.location.reload(); }} />
      </Suspense>
    );

  if (!user) return <LoginScreen />;

  if (window.location.search.includes("payment_id="))
    return <Suspense fallback={<PageFallback />}><PaymentReturn /></Suspense>;

  const showOnboarding = !onboardingDismissed && !user.has_birth_date;

  const modals = (
    <>
      {pendingMerge && <MergeAccountPrompt onClose={dismissMerge} />}
      {showOnboarding && !pendingMerge && (
        <OnboardingModal onClose={() => {
          setOnboardingDismissed(true);
          updateUser({ has_birth_date: true });
        }} />
      )}
      {statusMessage && (
        <div className="fixed top-4 left-0 right-0 flex justify-center pointer-events-none" style={{ zIndex: 200, padding: "0 16px" }}>
          <div
            onClick={clearStatusMessage}
            className="pointer-events-auto"
            style={{
              maxWidth: 420, textAlign: "center", fontSize: 13, padding: "10px 18px", borderRadius: 14, cursor: "pointer",
              background: statusMessage === "pro_activated" ? "rgba(201,168,76,.14)" : "rgba(196,84,84,.14)",
              border: `1px solid ${statusMessage === "pro_activated" ? "rgba(201,168,76,.4)" : "rgba(196,84,84,.4)"}`,
              color: statusMessage === "pro_activated" ? "#E8CD7E" : "#D98A8A",
              boxShadow: "0 8px 24px -8px rgba(0,0,0,.5)",
            }}
          >
            {statusMessage === "pro_activated" ? t("common.pro_activated_banner") : t("common.pro_deactivated_banner")}
          </div>
        </div>
      )}
    </>
  );

  let content;
  if (page === "home")            content = <Home          onNavigate={navigate} />;
  else if (page === "tarot")      content = <Tarot         onNavigate={navigate} />;
  else if (page === "natal")      content = <NatalChart    onNavigate={navigate} />;
  else if (page === "profile")    content = <Profile       onNavigate={navigate} />;
  else if (page === "moon" || page === "lunar")
                                  content = <LunarCalendar onNavigate={navigate} />;
  else if (page === "compat")     content = <Compatibility onNavigate={navigate} />;
  else if (page === "numerology" || page === "numero")
                                  content = <Numerology    onNavigate={navigate} />;
  else if (page === "runes")      content = <Runes         onNavigate={navigate} />;
  else                            content = null;

  return (
    <AppLayout page={page} onNavigate={navigate} user={user}>
      <Suspense fallback={<PageFallback />}>{content}</Suspense>
      {modals}
    </AppLayout>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppInner />
    </AuthProvider>
  );
}
