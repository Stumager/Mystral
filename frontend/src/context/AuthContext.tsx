import React, { createContext, useContext, useEffect, useState } from "react";
import i18n from "../i18n";
import { isTMA } from "../utils/telegram";

interface UserData {
  id: string;
  name: string | null;
  lang: string;
  tier: string;
  has_birth_date: boolean;
}

interface AuthContextType {
  user: UserData | null;
  token: string | null;
  isLoading: boolean;
  pendingMerge: boolean;
  login: (token: string, user: UserData) => void;
  logout: () => void;
  updateUser: (patch: Partial<UserData>) => void;
  dismissMerge: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserData | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [pendingMerge, setPendingMerge] = useState(false);

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
            if (data.is_new) setPendingMerge(true);
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
    <AuthContext.Provider value={{ user, token, isLoading, pendingMerge, login, logout, updateUser, dismissMerge }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
