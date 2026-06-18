import React, { createContext, useContext, useEffect, useState } from "react";

interface UserData {
  id: string;
  name: string | null;
  lang: string;
}

interface AuthContextType {
  user: UserData | null;
  token: string | null;
  isLoading: boolean;
  login: (token: string, user: UserData) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserData | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  function login(newToken: string, userData: UserData) {
    setToken(newToken);
    setUser(userData);
    localStorage.setItem("mystral_token", newToken);
    setIsLoading(false);
  }

  function logout() {
    setToken(null);
    setUser(null);
    localStorage.removeItem("mystral_token");
  }

  useEffect(() => {
    async function init() {
      // 1. Попытка через TMA
      const initData = window.Telegram?.WebApp?.initData;
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
            return;
          }
        } catch {}
      }

      // 2. Восстановить сессию из localStorage
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
            return;
          }
        } catch {}
        localStorage.removeItem("mystral_token");
      }
    }

    init().finally(() => setIsLoading(false));
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
