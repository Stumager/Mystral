import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import i18n from "../i18n";
import { isTMA } from "../utils/telegram";
import { applyStoredReferralCode } from "../utils/api";

interface UserData {
  id: string;
  name: string | null;
  lang: string;
  tier: string;
  has_birth_date: boolean;
}

export type TierStatusMessage = "pro_activated" | "pro_deactivated";

interface AuthContextType {
  user: UserData | null;
  token: string | null;
  isLoading: boolean;
  pendingMerge: boolean;
  login: (token: string, user: UserData) => void;
  logout: () => void;
  updateUser: (patch: Partial<UserData>) => void;
  dismissMerge: () => void;
  refreshUser: () => Promise<void>;
  statusMessage: TierStatusMessage | null;
  clearStatusMessage: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserData | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [pendingMerge, setPendingMerge] = useState(false);
  const [statusMessage, setStatusMessage] = useState<TierStatusMessage | null>(null);
  const tierRef = useRef<string | null>(null);

  useEffect(() => { tierRef.current = user?.tier ?? null; }, [user?.tier]);

  function clearStatusMessage() { setStatusMessage(null); }

  function login(newToken: string, userData: UserData) {
    setToken(newToken);
    setUser(userData);
    localStorage.setItem("mystral_token", newToken);
    if (userData.lang) i18n.changeLanguage(userData.lang);
    setIsLoading(false);
  }

  function logout() {
    if (isTMA()) {
      (window as any).Telegram?.WebApp?.close();
      return;
    }
    // Revoke the token server-side (jti blacklist); local cleanup regardless
    if (token) {
      fetch("/api/v1/auth/logout", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      }).catch(() => {});
    }
    setToken(null);
    setUser(null);
    setPendingMerge(false);
    localStorage.removeItem("mystral_token");
  }

  function updateUser(patch: Partial<UserData>) {
    setUser(prev => prev ? { ...prev, ...patch } : null);
    if (patch.lang) i18n.changeLanguage(patch.lang);
  }

  function dismissMerge() {
    setPendingMerge(false);
  }

  // Authoritative re-fetch of /auth/me — unlike updateUser() (a local optimistic
  // patch), this reflects whatever the server currently has, so it also picks up
  // changes the client had no direct hand in (e.g. a refund processed by an admin
  // while this tab was just sitting open). Detects a tier flip against the last
  // known tier and surfaces it as an explicit statusMessage instead of a silent
  // state change (QA-038).
  async function refreshUser() {
    if (!token) return;
    try {
      const res = await fetch("/api/v1/auth/me", { headers: { Authorization: `Bearer ${token}` } });
      if (!res.ok) return;
      const fresh: UserData = await res.json();
      const prevTier = tierRef.current;
      setUser(fresh);
      if (fresh.lang) i18n.changeLanguage(fresh.lang);
      if (prevTier && prevTier !== fresh.tier) {
        setStatusMessage(fresh.tier === "pro" ? "pro_activated" : "pro_deactivated");
      }
    } catch {}
  }

  // Re-check status whenever the user comes back to this tab — the app has no
  // websocket/push channel for tier changes, so a returning tab is the one
  // reliable moment to poll instead of waiting for a manual reload (QA-038).
  useEffect(() => {
    if (!token) return;
    function onVisible() {
      if (document.visibilityState === "visible") refreshUser();
    }
    document.addEventListener("visibilitychange", onVisible);
    window.addEventListener("focus", onVisible);
    return () => {
      document.removeEventListener("visibilitychange", onVisible);
      window.removeEventListener("focus", onVisible);
    };
  }, [token]);

  useEffect(() => {
    if (!statusMessage) return;
    const timer = setTimeout(() => setStatusMessage(null), 6000);
    return () => clearTimeout(timer);
  }, [statusMessage]);

  useEffect(() => {
    async function init() {
      // 1. TMA auto-login
      const initData = (window as any).Telegram?.WebApp?.initData;
      if (initData) {
        try {
          const res = await fetch("/api/v1/auth/telegram", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ init_data: initData }),
          });
          if (res.ok) {
            const data = await res.json();
            login(data.access_token, data.user);
            if (data.is_new) {
              await applyStoredReferralCode(data.access_token);
              setPendingMerge(true);
            }
            return;
          }
        } catch {}
      }

      // 2. Restore session from localStorage
      const savedToken = localStorage.getItem("mystral_token");
      if (savedToken) {
        try {
          const res = await fetch("/api/v1/auth/me", {
            headers: { Authorization: `Bearer ${savedToken}` },
          });
          if (res.ok) {
            const userData = await res.json();
            setToken(savedToken);
            setUser(userData);
            if (userData.lang) i18n.changeLanguage(userData.lang);
            return;
          }
        } catch {}
        localStorage.removeItem("mystral_token");
      }
    }

    init().finally(() => setIsLoading(false));
  }, []);

  return (
    <AuthContext.Provider value={{
      user, token, isLoading, pendingMerge, login, logout, updateUser, dismissMerge,
      refreshUser, statusMessage, clearStatusMessage,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
