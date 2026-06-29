import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import { getZodiacSign } from "../../utils/zodiac";
import { Logo } from "../Logo";

interface Props {
  activePage: string;
  onNavigate: (page: string) => void;
}

const NAV_ITEMS = [
  { id: "home",       icon: "⌂",  key: "nav.home" },
  { id: "tarot",      icon: "☰",  key: "nav.tarot" },
  { id: "moon",       icon: "☽",  key: "nav.moon" },
  { id: "compat",     icon: "♡",  key: "nav.compat" },
  { id: "natal",      icon: "◎",  key: "nav.natal" },
  { id: "numerology", icon: "#",  key: "nav.numerology" },
  { id: "runes",      icon: "ᚱ",  key: "nav.runes" },
  { id: "profile",    icon: "○",  key: "nav.profile" },
];

export function DesktopSidebar({ activePage, onNavigate }: Props) {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const ru = (user?.lang ?? "ru") === "ru";
  const isPro = user?.tier === "pro";
  const firstLetter = (user?.name ?? "?")[0]?.toUpperCase() ?? "?";

  const [zodiacLabel, setZodiacLabel] = useState<string | null>(null);
  const loaded = useRef(false);

  useEffect(() => {
    if (loaded.current || !token) return;
    loaded.current = true;
    fetch("/api/v1/profile", { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(d => {
        if (d.birth_date) {
          const z = getZodiacSign(d.birth_date);
          setZodiacLabel(ru ? z.sign : z.en);
        }
      }).catch(() => {});
  }, [token]);

  const active = activePage === "lunar" ? "moon" : activePage === "numero" ? "numerology" : activePage;

  return (
    <aside style={{ flex: "none", width: 240, height: "100%", display: "flex", flexDirection: "column", padding: "24px 16px", borderRight: "1px solid rgba(201,168,76,.12)", background: "rgba(7,6,15,.55)" }}>
      <div style={{ padding: "0 8px 22px", display: "flex", alignItems: "center", gap: 10 }}>
        <Logo size={30} />
        <span className="font-cinzel" style={{ fontSize: 16, letterSpacing: ".28em", color: "#E8CD7E" }}>MYSTRAL</span>
      </div>

      <nav style={{ display: "flex", flexDirection: "column", gap: 3, flex: 1 }}>
        {NAV_ITEMS.map(n => {
          const isActive = active === n.id;
          return (
            <button key={n.id} onClick={() => onNavigate(n.id)} style={{
              display: "flex", alignItems: "center", gap: 13, padding: "11px 14px", borderRadius: 12,
              cursor: "pointer", transition: ".15s", textAlign: "left",
              background: isActive ? "linear-gradient(100deg,rgba(201,168,76,.16),rgba(201,168,76,.04))" : "transparent",
              border: isActive ? "1px solid rgba(201,168,76,.3)" : "1px solid transparent",
              color: isActive ? "#E8CD7E" : "#A89E8B", fontWeight: isActive ? 600 : 400,
            }}>
              <span style={{ fontSize: 20, width: 20, textAlign: "center" }}>{n.icon}</span>
              <span style={{ fontSize: 13.5 }}>{t(n.key)}</span>
            </button>
          );
        })}
      </nav>

      <div style={{ marginTop: "auto", borderTop: "1px solid rgba(255,255,255,.07)", padding: "14px 10px 4px", display: "flex", flexDirection: "column", gap: 10 }}>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <div style={{ width: 40, height: 40, borderRadius: "50%", background: "linear-gradient(135deg,#4B3C86,#C9A84C)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <span className="font-cormorant" style={{ fontSize: 19, color: "#0C0A18", fontWeight: 600 }}>{firstLetter}</span>
          </div>
          <div>
            <div style={{ fontSize: 13.5, color: "#F0E9DA", fontWeight: 500 }}>{user?.name ?? t("profile.guest")}</div>
            <div style={{ fontSize: 11, color: "#C9A84C" }}>{zodiacLabel ?? "—"} · {isPro ? "Pro" : "Free"}</div>
          </div>
        </div>
        <div style={{ fontSize: 11, color: "#6E6757", paddingLeft: 2 }}>
          <a href="/privacy" style={{ color: "#6E6757", textDecoration: "none" }}>{t("legal.privacy")}</a>
          {" · "}
          <a href="/terms" style={{ color: "#6E6757", textDecoration: "none" }}>{t("legal.terms")}</a>
        </div>
      </div>
    </aside>
  );
}
