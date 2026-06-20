import React from "react";
import { useTranslation } from "react-i18next";
import { RightPanel } from "./RightPanel";

interface UserData {
  tier: string;
}

interface AppLayoutProps {
  page: string;
  onNavigate: (page: string) => void;
  user: UserData | null;
  children: React.ReactNode;
}

const NAV_ITEMS = [
  { id: "home",       emoji: "🏠", key: "nav.home" },
  { id: "tarot",      emoji: "🃏", key: "nav.tarot" },
  { id: "moon",       emoji: "🌙", key: "nav.moon" },
  { id: "compat",     emoji: "💑", key: "nav.compat" },
  { id: "natal",      emoji: "🌟", key: "nav.natal" },
  { id: "numerology", emoji: "🔢", key: "nav.numerology" },
  { id: "runes",      emoji: "ᚱ",  key: "nav.runes" },
  { id: "profile",    emoji: "☽",  key: "nav.profile" },
];

export function AppLayout({ page, onNavigate, user, children }: AppLayoutProps) {
  const { t } = useTranslation();

  const activePage = page === "lunar" ? "moon" : page === "numero" ? "numerology" : page;

  return (
    <div className="min-h-screen bg-bg-deep flex justify-center">
      {/* Left panel — desktop only */}
      <aside
        className="hidden md:flex w-[220px] shrink-0 sticky top-0 h-screen flex-col py-6 px-4"
        style={{ borderRight: "1px solid rgba(140,110,255,0.08)" }}
      >
        {/* Logo */}
        <div className="mb-8 px-2">
          <span className="font-display text-xl tracking-widest" style={{ color: "#C9A84C" }}>
            ✦ Mystral
          </span>
        </div>

        {/* Nav items */}
        <nav className="flex flex-col gap-1 flex-1">
          {NAV_ITEMS.map(({ id, emoji, key }) => {
            const isActive = activePage === id;
            return (
              <button
                key={id}
                onClick={() => onNavigate(id)}
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors text-left"
                style={{
                  background: isActive ? "rgba(107,78,255,0.15)" : "transparent",
                  color: isActive ? "#9B8AFF" : "#9B8FBB",
                }}
              >
                <span className="text-base w-5 text-center">{emoji}</span>
                <span>{t(key)}</span>
              </button>
            );
          })}
        </nav>

        {/* Tier badge */}
        <div className="px-2 mt-4">
          {user?.tier === "pro" ? (
            <div className="flex items-center gap-2">
              <span style={{ color: "#C9A84C" }}>✦</span>
              <span className="text-xs font-display" style={{ color: "#C9A84C" }}>Pro</span>
            </div>
          ) : (
            <span className="text-text-faint text-[10px]">{t("profile.free_plan")}</span>
          )}
        </div>
      </aside>

      {/* Center — mobile screen */}
      <div
        className="w-full md:w-[390px] md:shrink-0 relative"
        style={{ borderLeft: "1px solid rgba(140,110,255,0.08)", borderRight: "1px solid rgba(140,110,255,0.08)" }}
      >
        {children}
      </div>

      {/* Right panel — desktop only */}
      <div className="hidden md:block">
        <RightPanel />
      </div>
    </div>
  );
}
