import { useState } from "react";

type NavItem = {
  id: string;
  label: string;
  emoji: string;
};

const items: NavItem[] = [
  { id: "home",    label: "Главная", emoji: "🏠" },
  { id: "tarot",   label: "Таро",    emoji: "🃏" },
  { id: "moon",    label: "Луна",    emoji: "🌙" },
  { id: "profile", label: "Профиль", emoji: "☽" },
];

interface BottomNavProps {
  active?: string;
}

export function BottomNav({ active: activeProp }: BottomNavProps) {
  const [internalActive, setInternalActive] = useState(activeProp ?? "home");
  const active = activeProp !== undefined ? activeProp : internalActive;

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 flex justify-around items-center"
      style={{
        height: 56,
        background: "rgba(6,4,20,0.94)",
        borderTop: "0.5px solid rgba(140,110,255,0.10)",
      }}
    >
      {items.map(({ id, label, emoji }) => {
        const isActive = active === id;
        return (
          <button
            key={id}
            onClick={() => { if (activeProp === undefined) setInternalActive(id); }}
            className="flex flex-col items-center justify-center gap-0.5 flex-1 py-1 transition-colors duration-200"
            style={{ color: isActive ? "#9B8AFF" : "#9B8FBB" }}
          >
            <span className="text-lg leading-none">{emoji}</span>
            <span className="text-[10px] font-sans">{label}</span>
            {isActive && (
              <span
                className="rounded-full"
                style={{ width: 4, height: 4, background: "#9B8AFF" }}
              />
            )}
          </button>
        );
      })}
    </nav>
  );
}
