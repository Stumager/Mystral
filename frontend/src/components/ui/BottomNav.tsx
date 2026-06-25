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
    if (onNavigate) {
      onNavigate(id);
    } else if (activeProp === undefined) {
      setInternalActive(id);
    }
  }

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 flex justify-around items-center md:hidden"
      style={{
        height: 56,
        background: "rgba(7,6,15,0.94)",
        borderTop: "1px solid var(--border-gold)",
        backdropFilter: "blur(18px)",
      }}
    >
      {items.map(({ id, label, icon }) => {
        const isActive = active === id;
        return (
          <button
            key={id}
            onClick={() => handleClick(id)}
            className="flex flex-col items-center justify-center gap-0.5 flex-1 py-1 transition-colors duration-200"
            style={{ color: isActive ? "#E8CD7E" : "var(--text-muted)" }}
          >
            <span className="text-lg leading-none">{icon}</span>
            <span className="text-[10px] font-sans">{label}</span>
            {isActive && (
              <span
                className="rounded-full"
                style={{ width: 4, height: 4, background: "#C9A84C" }}
              />
            )}
          </button>
        );
      })}
    </nav>
  );
}
