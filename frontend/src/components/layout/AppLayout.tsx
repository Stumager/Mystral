import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { BottomNav } from "../ui";
import { DesktopRightPanel } from "./DesktopRightPanel";
import { DesktopSidebar } from "./DesktopSidebar";

interface UserData { tier: string; }

interface AppLayoutProps {
  page: string;
  onNavigate: (page: string) => void;
  user: UserData | null;
  children: React.ReactNode;
}

export function AppLayout({ page, onNavigate, children }: AppLayoutProps) {
  const { t } = useTranslation();
  const [isDesktop, setIsDesktop] = useState(window.innerWidth >= 1024);

  useEffect(() => {
    const h = () => setIsDesktop(window.innerWidth >= 1024);
    window.addEventListener("resize", h);
    return () => window.removeEventListener("resize", h);
  }, []);

  void t;

  if (isDesktop) {
    return (
      <div style={{ display: "flex", height: "100vh", overflow: "hidden", background: "radial-gradient(130% 60% at 50% -5%,#0F0A26 0%,#07060F 55%)" }}>
        <DesktopSidebar activePage={page} onNavigate={onNavigate} />
        <div style={{ flex: 1, overflowY: "auto" }}>
          {children}
        </div>
        <DesktopRightPanel />
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-dark)" }}>
      {children}
      <div style={{ textAlign: "center", fontSize: 11, color: "#827A69", padding: "12px 0 80px" }}>
        <a href="/privacy" style={{ color: "#827A69", textDecoration: "none" }}>{t("legal.privacy")}</a>
        {" · "}
        <a href="/terms" style={{ color: "#827A69", textDecoration: "none" }}>{t("legal.terms")}</a>
      </div>
      <BottomNav active={page === "lunar" ? "moon" : page} onNavigate={onNavigate} />
    </div>
  );
}
