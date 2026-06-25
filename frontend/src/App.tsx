import { useState } from "react";
import "./i18n";
import { AppLayout } from "./components/layout/AppLayout";
import { Logo } from "./components/Logo";
import { MergeAccountPrompt } from "./components/MergeAccountPrompt";
import { OnboardingModal } from "./components/OnboardingModal";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { Admin } from "./pages/Admin";
import { Compatibility } from "./pages/Compatibility";
import { Home } from "./pages/Home";
import { LoginScreen } from "./pages/LoginScreen";
import { LunarCalendar } from "./pages/LunarCalendar";
import { NatalChart } from "./pages/NatalChart";
import { Numerology } from "./pages/Numerology";
import { Profile } from "./pages/Profile";
import { Runes } from "./pages/Runes";
import { Tarot } from "./pages/Tarot";

type Page = "home" | "tarot" | "moon" | "natal" | "profile" | "lunar" | "compat" | "numerology" | "numero" | "runes" | "admin";

function AppInner() {
  const [page, setPage] = useState<Page>("home");
  const { user, isLoading, pendingMerge, dismissMerge, updateUser } = useAuth();
  const [onboardingDismissed, setOnboardingDismissed] = useState(false);

  const navigate = (p: string) => setPage(p as Page);

  if (isLoading) {
    return (
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100vh", background: "#07060F", gap: 20 }}>
        <div style={{ filter: "drop-shadow(0 0 32px rgba(201,168,76,.6))", animation: "mystral-pulse-glow 1.8s ease-in-out infinite" }}>
          <Logo size={80} />
        </div>
        <span className="font-cinzel" style={{ fontSize: 13, letterSpacing: ".4em", color: "#E8CD7E", marginTop: 8 }}>MYSTRAL</span>
        <div style={{ display: "flex", gap: 6, marginTop: 16 }}>
          {[0, 0.2, 0.4].map((d, i) => (
            <span key={i} style={{ width: 6, height: 6, borderRadius: "50%", background: "#C9A84C", animation: `mystral-fadeup .6s ease-out infinite ${d}s` }} />
          ))}
        </div>
      </div>
    );
  }

  if (page === "admin" || window.location.hash.replace(/\/+$/, "") === "#admin") return <Admin />;

  if (!user) return <LoginScreen />;

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
      {content}
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
