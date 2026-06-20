import { useState } from "react";
import "./i18n";
import { AppLayout } from "./components/layout/AppLayout";
import { MergeAccountPrompt } from "./components/MergeAccountPrompt";
import { OnboardingModal } from "./components/OnboardingModal";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { Compatibility } from "./pages/Compatibility";
import { Home } from "./pages/Home";
import { LoginScreen } from "./pages/LoginScreen";
import { LunarCalendar } from "./pages/LunarCalendar";
import { NatalChart } from "./pages/NatalChart";
import { Numerology } from "./pages/Numerology";
import { Profile } from "./pages/Profile";
import { Runes } from "./pages/Runes";
import { Tarot } from "./pages/Tarot";

type Page = "home" | "tarot" | "moon" | "natal" | "profile" | "lunar" | "compat" | "numerology" | "numero" | "runes";

function AppInner() {
  const [page, setPage] = useState<Page>("home");
  const { user, isLoading, pendingMerge, dismissMerge, updateUser } = useAuth();
  const [onboardingDismissed, setOnboardingDismissed] = useState(false);

  const navigate = (p: string) => setPage(p as Page);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-bg-deep flex items-center justify-center">
        <span
          className="font-display text-4xl font-light tracking-widest animate-pulse"
          style={{ color: "#F0EAFF" }}
        >
          ✦ Mystral
        </span>
      </div>
    );
  }

  if (!user) return <LoginScreen />;

  const showOnboarding = !onboardingDismissed && !user.has_birth_date;

  let content;
  if (page === "tarot")           content = <Tarot         onNavigate={navigate} />;
  else if (page === "natal")      content = <NatalChart    onNavigate={navigate} />;
  else if (page === "profile")    content = <Profile       onNavigate={navigate} />;
  else if (page === "moon" || page === "lunar")
                                  content = <LunarCalendar onNavigate={navigate} />;
  else if (page === "compat")     content = <Compatibility onNavigate={navigate} />;
  else if (page === "numerology" || page === "numero")
                                  content = <Numerology    onNavigate={navigate} />;
  else if (page === "runes")      content = <Runes         onNavigate={navigate} />;
  else                            content = <Home          onNavigate={navigate} />;

  return (
    <AppLayout page={page} onNavigate={navigate} user={user}>
      {content}
      {pendingMerge && <MergeAccountPrompt onClose={dismissMerge} />}
      {showOnboarding && !pendingMerge && (
        <OnboardingModal onClose={() => {
          setOnboardingDismissed(true);
          updateUser({ has_birth_date: true });
        }} />
      )}
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
