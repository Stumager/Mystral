import { useState } from "react";
import "./i18n";
import { MergeAccountPrompt } from "./components/MergeAccountPrompt";
import { OnboardingModal } from "./components/OnboardingModal";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { Home } from "./pages/Home";
import { LoginScreen } from "./pages/LoginScreen";
import { NatalChart } from "./pages/NatalChart";
import { Profile } from "./pages/Profile";
import { Tarot } from "./pages/Tarot";

type Page = "home" | "tarot" | "moon" | "natal" | "profile";

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
  if (page === "tarot")        content = <Tarot     onNavigate={navigate} />;
  else if (page === "natal")   content = <NatalChart onNavigate={navigate} />;
  else if (page === "profile") content = <Profile    onNavigate={navigate} />;
  else                         content = <Home       onNavigate={navigate} />;

  return (
    <>
      {content}
      {pendingMerge && <MergeAccountPrompt onClose={dismissMerge} />}
      {showOnboarding && !pendingMerge && (
        <OnboardingModal onClose={() => {
          setOnboardingDismissed(true);
          updateUser({ has_birth_date: true });
        }} />
      )}
    </>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppInner />
    </AuthProvider>
  );
}
