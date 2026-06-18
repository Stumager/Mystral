import { useState } from "react";
import "./i18n";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { Home } from "./pages/Home";
import { LoginScreen } from "./pages/LoginScreen";
import { NatalChart } from "./pages/NatalChart";
import { Profile } from "./pages/Profile";
import { Tarot } from "./pages/Tarot";

type Page = "home" | "tarot" | "moon" | "natal" | "profile";

function AppInner() {
  const [page, setPage] = useState<Page>("home");
  const { user, isLoading } = useAuth();

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

  if (page === "tarot") return <Tarot onNavigate={navigate} />;
  if (page === "natal")    return <NatalChart onNavigate={navigate} />;
  if (page === "profile")  return <Profile    onNavigate={navigate} />;
  return <Home onNavigate={navigate} />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppInner />
    </AuthProvider>
  );
}
