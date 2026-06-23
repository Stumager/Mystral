import React from "react";
import { useTranslation } from "react-i18next";
import { Logo } from "../Logo";
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
    <div className="min-h-screen flex justify-center" style={{ background: "var(--bg-dark)" }}>
      {/* Left panel — desktop only */}
      <aside
        className="hidden md:flex w-[220px] shrink-0 sticky top-0 h-screen flex-col py-6 px-4"
        style={{ borderRight: "1px solid var(--border-gold)" }}
      >
        {/* Logo */}
        <div className="mb-8 px-2 flex items-center gap-2.5">
          <Logo size={26} />
          <span className="font-cinzel text-sm tracking-[.3em]" style={{ color: "#E8CD7E" }}>
            MYSTRAL
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
                className="flex items-center gap-3 px-3 py-2 text-sm transition-colors text-left"
                style={{
                  borderRadius: "var(--radius-xs)",
                  background: isActive ? "rgba(75,60,134,.22)" : "transparent",
                  color: isActive ? "var(--gold-light)" : "var(--text-muted)",
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
            <div
              className="flex items-center gap-2 px-3 py-1.5"
              style={{
                borderRadius: "var(--radius-xs)",
                background: "rgba(201,168,76,.08)",
                border: "1px solid var(--border-gold)",
              }}
            >
              <span className="font-cinzel text-xs tracking-widest" style={{ color: "#E8CD7E" }}>
                Mystral Pro
              </span>
            </div>
          ) : (
            <span className="text-xs" style={{ color: "var(--text-dim)" }}>{t("profile.free_plan")}</span>
          )}
        </div>
      </aside>

      {/* Center — mobile screen */}
      <div
        className="w-full md:w-[390px] md:shrink-0 relative"
        style={{
          borderLeft: "1px solid var(--border-gold)",
          borderRight: "1px solid var(--border-gold)",
        }}
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
