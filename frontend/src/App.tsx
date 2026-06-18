import { useState } from "react";
import "./i18n";
import { Home } from "./pages/Home";
import { Tarot } from "./pages/Tarot";

type Page = "home" | "tarot" | "moon" | "profile";

export default function App() {
  const [page, setPage] = useState<Page>("home");

  const navigate = (p: string) => setPage(p as Page);

  if (page === "tarot") return <Tarot onNavigate={navigate} />;
  return <Home onNavigate={navigate} />;
}
