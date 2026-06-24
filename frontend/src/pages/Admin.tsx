import { useCallback, useEffect, useState } from "react";
import { Logo } from "../components/Logo";

interface Stats { total_users: number; pro_users: number; new_7days: number; new_30days: number; }
interface UserRow {
  id: string; email: string | null; display_name: string | null;
  telegram_id: string | null; tier: string;
  subscription_expires_at: string | null; created_at: string | null;
}
interface UsersRes { users: UserRow[]; total: number; page: number; pages: number; }

const API = "/api/v1";

function adminHeaders(): Record<string, string> {
  return { "Content-Type": "application/json", "X-Admin-Token": sessionStorage.getItem("admin_token") || "" };
}

async function apiFetch<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, { ...opts, headers: { ...adminHeaders(), ...opts?.headers } });
  if (res.status === 403) throw new Error("forbidden");
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export function Admin() {
  const [authed, setAuthed] = useState(!!sessionStorage.getItem("admin_token"));
  const [tokenInput, setTokenInput] = useState("");
  const [loginError, setLoginError] = useState("");
  const [stats, setStats] = useState<Stats | null>(null);
  const [users, setUsers] = useState<UserRow[]>([]);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(1);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [searchDebounced, setSearchDebounced] = useState("");

  useEffect(() => {
    const t = setTimeout(() => setSearchDebounced(search), 400);
    return () => clearTimeout(t);
  }, [search]);

  const loadStats = useCallback(async () => {
    try { setStats(await apiFetch<Stats>("/admin/stats")); } catch {}
  }, []);

  const loadUsers = useCallback(async () => {
    try {
      const d = await apiFetch<UsersRes>(`/admin/users?page=${page}&limit=50&search=${encodeURIComponent(searchDebounced)}`);
      setUsers(d.users); setTotal(d.total); setPages(d.pages);
    } catch {}
  }, [page, searchDebounced]);

  useEffect(() => { if (authed) { loadStats(); loadUsers(); } }, [authed, loadStats, loadUsers]);

  async function handleLogin() {
    sessionStorage.setItem("admin_token", tokenInput);
    try {
      await apiFetch("/admin/stats");
      setAuthed(true); setLoginError("");
    } catch {
      sessionStorage.removeItem("admin_token");
      setLoginError("Неверный токен");
    }
  }

  async function grantPro(id: string, days: number) {
    await apiFetch(`/admin/users/${id}/grant-pro`, { method: "POST", body: JSON.stringify({ days }) });
    loadUsers(); loadStats();
  }
  async function revokePro(id: string) {
    await apiFetch(`/admin/users/${id}/revoke-pro`, { method: "POST" });
    loadUsers(); loadStats();
  }
  async function deleteUser(id: string, label: string) {
    if (!window.confirm(`Удалить пользователя ${label}?`)) return;
    await apiFetch(`/admin/users/${id}`, { method: "DELETE" });
    loadUsers(); loadStats();
  }

  function logout() { sessionStorage.removeItem("admin_token"); location.reload(); }

  const cs: React.CSSProperties = { background: "var(--gradient-page)", minHeight: "100vh", color: "#F0E9DA", fontFamily: "'Inter', sans-serif" };

  // ============= LOGIN =============
  if (!authed) {
    return (
      <div style={{ ...cs, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
        <Logo size={60} />
        <p className="font-cinzel" style={{ fontSize: 18, letterSpacing: ".3em", color: "#E8CD7E", marginTop: 20 }}>MYSTRAL ADMIN</p>
        <div style={{ width: "100%", maxWidth: 340, marginTop: 32 }}>
          <input type="password" placeholder="Admin token" value={tokenInput}
            onChange={e => setTokenInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleLogin()}
            style={{ width: "100%", padding: "14px 18px", borderRadius: 14, background: "rgba(255,255,255,.04)", border: "1px solid rgba(201,168,76,.22)", color: "#F0E9DA", fontSize: 15, outline: "none" }} />
          {loginError && <p style={{ color: "#D98A8A", fontSize: 13, marginTop: 8, textAlign: "center" }}>{loginError}</p>}
          <button onClick={handleLogin} style={{ width: "100%", marginTop: 12, height: 50, borderRadius: 14, background: "linear-gradient(100deg,#A9882F,#C9A84C 50%,#E8CD7E)", color: "#1A1206", fontWeight: 600, fontSize: 15, border: "none", cursor: "pointer" }}>
            Войти
          </button>
        </div>
      </div>
    );
  }

  // ============= PANEL =============
  const statCards = [
    { label: "Всего", value: stats?.total_users ?? "—" },
    { label: "Pro", value: stats?.pro_users ?? "—" },
    { label: "7 дней", value: stats?.new_7days ?? "—" },
    { label: "30 дней", value: stats?.new_30days ?? "—" },
  ];

  const gridCols = "2fr 1.5fr 1fr 1fr 1.5fr 180px";

  return (
    <div style={cs}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "20px 32px", borderBottom: "1px solid rgba(201,168,76,.12)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <Logo size={24} />
          <span className="font-cinzel" style={{ fontSize: 13, letterSpacing: ".3em", color: "#E8CD7E" }}>MYSTRAL ADMIN</span>
        </div>
        <button onClick={logout} style={{ padding: "6px 14px", borderRadius: 8, background: "transparent", border: "1px solid rgba(255,255,255,.1)", color: "#B6AC98", fontSize: 12, cursor: "pointer" }}>
          Выйти
        </button>
      </div>

      <div style={{ maxWidth: 1200, margin: "0 auto", padding: 32 }}>
        {/* Stats */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16, marginBottom: 32 }}>
          {statCards.map(s => (
            <div key={s.label} style={{ padding: 20, borderRadius: 16, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)" }}>
              <div className="font-cinzel" style={{ fontSize: 10, letterSpacing: ".2em", color: "#C9A84C", textTransform: "uppercase" }}>{s.label}</div>
              <div className="font-cormorant" style={{ fontSize: 38, color: "#F0E9DA", lineHeight: 1, marginTop: 8 }}>{s.value}</div>
            </div>
          ))}
        </div>

        {/* Search */}
        <input placeholder="Поиск по email или Telegram..." value={search} onChange={e => { setSearch(e.target.value); setPage(1); }}
          style={{ width: 360, padding: "12px 18px", borderRadius: 12, background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,.1)", color: "#F0E9DA", fontSize: 14, outline: "none", marginBottom: 20 }} />
        <span style={{ marginLeft: 16, fontSize: 13, color: "#6E6757" }}>{total} users</span>

        {/* Table */}
        <div style={{ borderRadius: 18, overflow: "hidden", border: "1px solid rgba(201,168,76,.13)" }}>
          {/* Header row */}
          <div style={{ display: "grid", gridTemplateColumns: gridCols, padding: "12px 20px", background: "rgba(201,168,76,.06)" }}>
            {["ID", "Email / Telegram", "Имя", "Тир", "Дата рег.", "Действия"].map(h => (
              <span key={h} className="font-cinzel" style={{ fontSize: 10, letterSpacing: ".15em", color: "#C9A84C", textTransform: "uppercase" }}>{h}</span>
            ))}
          </div>

          {/* Rows */}
          {users.map(u => (
            <div key={u.id} style={{ display: "grid", gridTemplateColumns: gridCols, padding: "14px 20px", alignItems: "center", borderTop: "1px solid rgba(255,255,255,.06)" }}>
              <span style={{ fontSize: 11, color: "#6E6757", fontFamily: "monospace", overflow: "hidden", textOverflow: "ellipsis" }}>{u.id.slice(0, 8)}</span>
              <div>
                {u.email && <div style={{ fontSize: 14, color: "#F0E9DA" }}>{u.email}</div>}
                {u.telegram_id && <div style={{ fontSize: 12, color: "#A89E8B" }}>TG: {u.telegram_id}</div>}
                {!u.email && !u.telegram_id && <span style={{ color: "#6E6757" }}>—</span>}
              </div>
              <span style={{ fontSize: 13, color: "#B6AC98" }}>{u.display_name || "—"}</span>
              <div>
                <span className="font-cinzel" style={{
                  fontSize: 11, padding: "3px 10px", borderRadius: 99,
                  background: u.tier === "pro" ? "rgba(201,168,76,.15)" : "rgba(255,255,255,.05)",
                  border: u.tier === "pro" ? "1px solid rgba(201,168,76,.3)" : "none",
                  color: u.tier === "pro" ? "#E8CD7E" : "#6E6757",
                }}>{u.tier.toUpperCase()}</span>
                {u.tier === "pro" && u.subscription_expires_at && (
                  <div style={{ fontSize: 10, color: "#6E6757", marginTop: 2 }}>
                    до {new Date(u.subscription_expires_at).toLocaleDateString("ru-RU")}
                  </div>
                )}
              </div>
              <span style={{ fontSize: 12, color: "#6E6757" }}>{u.created_at ? new Date(u.created_at).toLocaleDateString("ru-RU") : "—"}</span>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                {u.tier !== "pro" ? (
                  <>
                    <button onClick={() => grantPro(u.id, 30)} style={actionBtn()}>+30д</button>
                    <button onClick={() => grantPro(u.id, 365)} style={actionBtn()}>+1г</button>
                  </>
                ) : (
                  <button onClick={() => revokePro(u.id)} style={actionBtn("#D98A8A", "rgba(196,84,84,.3)")}>Убрать</button>
                )}
                <button onClick={() => deleteUser(u.id, u.email || u.telegram_id || u.id)} style={actionBtn("#D98A8A", "rgba(196,84,84,.3)")}>✕</button>
              </div>
            </div>
          ))}

          {users.length === 0 && (
            <div style={{ padding: "40px 20px", textAlign: "center", color: "#6E6757" }}>Нет пользователей</div>
          )}
        </div>

        {/* Pagination */}
        {pages > 1 && (
          <div style={{ display: "flex", justifyContent: "center", gap: 8, marginTop: 24 }}>
            {Array.from({ length: pages }, (_, i) => i + 1).map(p => (
              <button key={p} onClick={() => setPage(p)} style={{
                width: 36, height: 36, borderRadius: 10, border: "none", cursor: "pointer",
                background: p === page ? "rgba(201,168,76,.15)" : "rgba(255,255,255,.04)",
                color: p === page ? "#E8CD7E" : "#A89E8B", fontSize: 13,
              }}>{p}</button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function actionBtn(color = "#E8CD7E", borderColor = "rgba(201,168,76,.3)"): React.CSSProperties {
  return {
    height: 28, padding: "0 10px", borderRadius: 8, fontSize: 11,
    background: "transparent", border: `1px solid ${borderColor}`,
    color, cursor: "pointer",
  };
}
