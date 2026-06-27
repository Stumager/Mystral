import { useState } from "react";
import { useTranslation } from "react-i18next";

interface BottomNavProps {
  active?: string;
  onNavigate?: (id: string) => void;
}

export function BottomNav({ active: activeProp, onNavigate }: BottomNavProps) {
  const { t } = useTranslation();
  const [internalActive, setInternalActive] = useState(activeProp ?? "home");
  const active = activeProp !== undefined ? activeProp : internalActive;

  const items = [
    { id: "home",    label: t("nav.home"),    icon: "⌂" },
    { id: "tarot",   label: t("nav.tarot"),   icon: "☰" },
    { id: "moon",    label: t("nav.moon"),    icon: "☽" },
    { id: "profile", label: t("nav.profile"), icon: "○" },
  ];

  function handleClick(id: string) {
    if (onNavigate) onNavigate(id);
    else if (activeProp === undefined) setInternalActive(id);
  }

  return (
    <nav className="fixed bottom-0 left-0 right-0 lg:hidden" style={{ padding: "0 16px 20px", background: "linear-gradient(0deg, #07060F 50%, transparent)", pointerEvents: "none", zIndex: 40 }}>
      <div style={{ display: "flex", gap: 4, background: "rgba(15,10,38,.92)", backdropFilter: "blur(24px)", border: "1px solid rgba(201,168,76,.18)", borderRadius: 99, padding: "6px 8px", boxShadow: "0 8px 32px rgba(0,0,0,.5), 0 0 0 1px rgba(255,255,255,.04) inset", pointerEvents: "auto" }}>
        {items.map(({ id, label, icon }) => {
          const isActive = active === id;
          return (
            <button key={id} onClick={() => handleClick(id)}
              style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 3, padding: "8px 4px", borderRadius: 99, cursor: "pointer", transition: ".2s", background: isActive ? "rgba(201,168,76,.15)" : "transparent", border: "none" }}>
              <span style={{ fontSize: 22, lineHeight: 1, color: isActive ? "#E8CD7E" : "#6E6757", filter: isActive ? "drop-shadow(0 0 8px rgba(201,168,76,.5))" : "none" }}>{icon}</span>
              <span className="font-cinzel" style={{ fontSize: 8, letterSpacing: ".1em", color: isActive ? "#E8CD7E" : "#6E6757" }}>{label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
