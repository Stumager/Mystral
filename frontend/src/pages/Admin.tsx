import { useCallback, useEffect, useState } from "react";
import { Logo } from "../components/Logo";

interface Stats { total_users: number; pro_users: number; new_7days: number; new_30days: number; }
interface UserRow {
  id: string; email: string | null; display_name: string | null;
  telegram_id: string | null; tier: string;
  subscription_expires_at: string | null; created_at: string | null;
}
interface UsersRes { users: UserRow[]; total: number; page: number; pages: number; }
interface RefundRow {
  id: string; status: string; reason: string | null; admin_comment: string | null;
  error_detail: string | null; created_at: string | null; resolved_at: string | null;
  user: { id: string | null; email: string | null; display_name: string | null; telegram_id: string | null };
  payment: { provider: string; product: string; amount: string; currency: string; status: string; created_at: string | null } | null;
}
interface RefundsRes { pending: RefundRow[]; resolved: RefundRow[]; }

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
  const [tab, setTab] = useState<"users" | "reviews" | "referrals" | "refunds">("users");
  const [refStats, setRefStats] = useState<{ total_referrals: number; total_bonus_days_given: number; top_referrers: { name: string; email: string; ref_code: string; referral_count: number; bonus_days: number }[]; recent: { referrer_name: string; referred_name: string; bonus_days: number; created_at: string | null }[] } | null>(null);
  const [reviews, setReviews] = useState<{ id: string; user_name: string; user_email: string | null; rating: number; text: string | null; is_published: boolean; created_at: string | null }[]>([]);
  const [refundsPending, setRefundsPending] = useState<RefundRow[]>([]);
  const [refundsResolved, setRefundsResolved] = useState<RefundRow[]>([]);

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

  const loadReviews = useCallback(async () => {
    try { setReviews(await apiFetch("/admin/reviews")); } catch {}
  }, []);

  const loadRefStats = useCallback(async () => {
    try { setRefStats(await apiFetch("/admin/referrals/stats")); } catch {}
  }, []);

  const loadRefunds = useCallback(async () => {
    try {
      const d = await apiFetch<RefundsRes>("/admin/refunds");
      setRefundsPending(d.pending); setRefundsResolved(d.resolved);
    } catch {}
  }, []);

  useEffect(() => { if (authed) { loadStats(); loadUsers(); loadReviews(); loadRefStats(); loadRefunds(); } }, [authed, loadStats, loadUsers, loadReviews, loadRefStats, loadRefunds]);

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

  async function publishReview(id: string) {
    await apiFetch(`/admin/reviews/${id}/publish`, { method: "POST" });
    loadReviews();
  }
  async function deleteReview(id: string) {
    if (!window.confirm("Удалить отзыв?")) return;
    await apiFetch(`/admin/reviews/${id}`, { method: "DELETE" });
    loadReviews();
  }

  async function approveRefund(id: string) {
    if (!window.confirm("Одобрить и вернуть деньги? Возврат будет отправлен провайдеру немедленно.")) return;
    try {
      const res = await apiFetch<{ status: string; error?: string }>(`/admin/refunds/${id}/approve`, { method: "POST" });
      if (res.status === "failed") window.alert(`Возврат не удался: ${res.error || "неизвестная ошибка"}`);
    } catch { window.alert("Ошибка запроса"); }
    loadRefunds(); loadStats(); loadUsers();
  }

  async function rejectRefund(id: string) {
    const comment = window.prompt("Причина отклонения (обязательно):");
    if (!comment || !comment.trim()) return;
    try {
      await apiFetch(`/admin/refunds/${id}/reject`, { method: "POST", body: JSON.stringify({ comment }) });
    } catch { window.alert("Ошибка запроса"); }
    loadRefunds();
  }

  function logout() { sessionStorage.removeItem("admin_token"); location.reload(); }

  const cs: React.CSSProperties = { background: "var(--gradient-page)", minHeight: "100vh", color: "#F0E9DA", fontFamily: "'Inter', sans-serif" };

  // ============= LOGIN =============
  if (!authed) {
    return (
      <div style={{ ...cs, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "0 24px" }}>
        <Logo size={60} />
        <p className="font-cinzel" style={{ fontSize: 18, letterSpacing: ".3em", color: "#E8CD7E", marginTop: 20 }}>MYSTRAL ADMIN</p>
        <div style={{ width: "100%", maxWidth: 340, marginTop: 32 }}>
          <input type="password" placeholder="Admin token" value={tokenInput}
            onChange={e => setTokenInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleLogin()}
            style={{ width: "100%", padding: "14px 18px", borderRadius: 14, background: "rgba(255,255,255,.04)", border: "1px solid rgba(201,168,76,.22)", color: "#F0E9DA", fontSize: 15, outline: "none", boxSizing: "border-box" }} />
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

  function UserCard({ u }: { u: UserRow }) {
    return (
      <div style={{ padding: 16, borderRadius: 14, background: "rgba(255,255,255,.025)", border: "1px solid rgba(255,255,255,.06)", display: "flex", flexDirection: "column", gap: 8 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div style={{ minWidth: 0, flex: 1 }}>
            {u.display_name && <div style={{ fontSize: 14, color: "#F0E9DA", fontWeight: 500 }}>{u.display_name}</div>}
            {u.email && <div style={{ fontSize: 13, color: "#A89E8B", wordBreak: "break-all" }}>{u.email}</div>}
            {u.telegram_id && <div style={{ fontSize: 12, color: "#8A8170" }}>TG: {u.telegram_id}</div>}
          </div>
          <span className="font-cinzel" style={{
            fontSize: 10, padding: "3px 10px", borderRadius: 99, flexShrink: 0, marginLeft: 8,
            background: u.tier === "pro" ? "rgba(201,168,76,.15)" : "rgba(255,255,255,.05)",
            border: u.tier === "pro" ? "1px solid rgba(201,168,76,.3)" : "1px solid rgba(255,255,255,.08)",
            color: u.tier === "pro" ? "#E8CD7E" : "#6E6757",
          }}>{u.tier.toUpperCase()}</span>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontSize: 11, color: "#6E6757" }}>
            {u.created_at ? new Date(u.created_at).toLocaleDateString("ru-RU") : "—"}
            {u.tier === "pro" && u.subscription_expires_at && ` · до ${new Date(u.subscription_expires_at).toLocaleDateString("ru-RU")}`}
          </div>
          <div style={{ fontSize: 10, color: "#6E6757", fontFamily: "monospace" }}>{u.id.slice(0, 8)}</div>
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {u.tier !== "pro" ? (
            <>
              <button onClick={() => grantPro(u.id, 30)} style={actionBtn()}>+30 дней</button>
              <button onClick={() => grantPro(u.id, 365)} style={actionBtn()}>+1 год</button>
            </>
          ) : (
            <button onClick={() => revokePro(u.id)} style={actionBtn("#D98A8A", "rgba(196,84,84,.3)")}>Убрать Pro</button>
          )}
          <button onClick={() => deleteUser(u.id, u.email || u.telegram_id || u.id)} style={{ ...actionBtn("#D98A8A", "rgba(196,84,84,.3)"), marginLeft: "auto" }}>Удалить</button>
        </div>
      </div>
    );
  }

  function RefundCard({ r }: { r: RefundRow }) {
    const statusColor = r.status === "pending" ? "#C9A84C"
      : r.status === "completed" ? "#6E9A8A"
      : r.status === "rejected" || r.status === "failed" ? "#D98A8A"
      : "#6E6757";
    return (
      <div style={{ padding: 16, borderRadius: 14, background: "rgba(255,255,255,.025)", border: "1px solid rgba(255,255,255,.06)", display: "flex", flexDirection: "column", gap: 8 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 8 }}>
          <div style={{ minWidth: 0 }}>
            <div style={{ fontSize: 14, color: "#F0E9DA", fontWeight: 500 }}>{r.user.display_name || r.user.email || r.user.telegram_id || "?"}</div>
            {r.user.email && <div style={{ fontSize: 12, color: "#A89E8B", wordBreak: "break-all" }}>{r.user.email}</div>}
            {r.user.telegram_id && <div style={{ fontSize: 11, color: "#8A8170" }}>TG: {r.user.telegram_id}</div>}
          </div>
          <span className="font-cinzel" style={{ fontSize: 10, padding: "3px 10px", borderRadius: 99, flexShrink: 0, background: "rgba(255,255,255,.05)", color: statusColor, border: `1px solid ${statusColor}55` }}>
            {r.status.toUpperCase()}
          </span>
        </div>
        {r.payment && (
          <div style={{ fontSize: 12, color: "#B6AC98" }}>
            {r.payment.provider === "stars" ? "Stars" : "ЮKassa"} · {r.payment.amount} {r.payment.currency} · {r.payment.product}
            {r.payment.created_at && ` · ${new Date(r.payment.created_at).toLocaleDateString("ru-RU")}`}
          </div>
        )}
        {r.reason && <div style={{ fontSize: 12, color: "#8A8170" }}>Причина: {r.reason}</div>}
        {r.admin_comment && <div style={{ fontSize: 12, color: "#8A8170" }}>Комментарий: {r.admin_comment}</div>}
        {r.error_detail && <div style={{ fontSize: 12, color: "#D98A8A" }}>Ошибка: {r.error_detail}</div>}
        <div style={{ fontSize: 11, color: "#6E6757" }}>
          {r.created_at ? new Date(r.created_at).toLocaleString("ru-RU") : ""}
          {r.resolved_at && ` → ${new Date(r.resolved_at).toLocaleString("ru-RU")}`}
        </div>
        {r.status === "pending" && (
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button onClick={() => approveRefund(r.id)} style={actionBtn("#6E9A8A", "rgba(110,154,138,.4)")}>Одобрить и вернуть</button>
            <button onClick={() => rejectRefund(r.id)} style={actionBtn("#D98A8A", "rgba(196,84,84,.3)")}>Отклонить</button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div style={cs}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 20px", borderBottom: "1px solid rgba(201,168,76,.12)", flexWrap: "wrap", gap: 10 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Logo size={22} />
          <span className="font-cinzel" style={{ fontSize: 11, letterSpacing: ".25em", color: "#E8CD7E" }}>ADMIN</span>
        </div>
        <div style={{ display: "flex", gap: 4 }}>
          {(["users", "reviews", "referrals", "refunds"] as const).map(t => (
            <button key={t} onClick={() => setTab(t)} style={{
              padding: "6px 14px", borderRadius: 8, fontSize: 12, cursor: "pointer",
              background: tab === t ? "rgba(201,168,76,.15)" : "transparent",
              border: tab === t ? "1px solid rgba(201,168,76,.3)" : "1px solid transparent",
              color: tab === t ? "#E8CD7E" : "#A89E8B",
            }}>{t === "users" ? "Пользователи" : t === "reviews" ? "Отзывы" : t === "referrals" ? "Рефералы" : `Возвраты${refundsPending.length ? ` (${refundsPending.length})` : ""}`}</button>
          ))}
        </div>
        <button onClick={logout} style={{ padding: "6px 12px", borderRadius: 8, background: "transparent", border: "1px solid rgba(255,255,255,.1)", color: "#B6AC98", fontSize: 12, cursor: "pointer" }}>
          Выйти
        </button>
      </div>

      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "20px 16px 40px" }}>

        {/* ===== REVIEWS TAB ===== */}
        {tab === "reviews" && (
          <div>
            <p className="font-cinzel" style={{ fontSize: 10, letterSpacing: ".2em", color: "#C9A84C", textTransform: "uppercase", marginBottom: 16 }}>
              На модерации ({reviews.filter(r => !r.is_published).length}) · Опубликовано ({reviews.filter(r => r.is_published).length})
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {reviews.length === 0 && <p style={{ color: "#6E6757", textAlign: "center", padding: 40 }}>Нет отзывов</p>}
              {reviews.map(r => (
                <div key={r.id} style={{ padding: 16, borderRadius: 14, background: "rgba(255,255,255,.025)", border: `1px solid ${r.is_published ? "rgba(110,154,138,.3)" : "rgba(255,255,255,.06)"}`, display: "flex", flexDirection: "column", gap: 8 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
                    <div>
                      <span style={{ fontSize: 14, color: "#F0E9DA", fontWeight: 500 }}>{r.user_name || "?"}</span>
                      {r.user_email && <span style={{ fontSize: 12, color: "#8A8170", marginLeft: 8 }}>{r.user_email}</span>}
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                      {Array.from({ length: 5 }, (_, i) => (
                        <span key={i} style={{ fontSize: 14, color: i < r.rating ? "#C9A84C" : "rgba(201,168,76,.2)" }}>★</span>
                      ))}
                      <span className="font-cinzel" style={{
                        fontSize: 10, padding: "2px 8px", borderRadius: 99, marginLeft: 8,
                        background: r.is_published ? "rgba(110,154,138,.15)" : "rgba(201,168,76,.1)",
                        color: r.is_published ? "#6E9A8A" : "#C9A84C",
                      }}>{r.is_published ? "PUB" : "MOD"}</span>
                    </div>
                  </div>
                  {r.text && <p style={{ fontSize: 13, color: "#B6AC98", lineHeight: 1.5 }}>{r.text}</p>}
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
                    <span style={{ fontSize: 11, color: "#6E6757" }}>{r.created_at ? new Date(r.created_at).toLocaleDateString("ru-RU") : ""}</span>
                    <div style={{ display: "flex", gap: 6 }}>
                      {!r.is_published && (
                        <button onClick={() => publishReview(r.id)} style={actionBtn("#6E9A8A", "rgba(110,154,138,.4)")}>Опубликовать</button>
                      )}
                      <button onClick={() => deleteReview(r.id)} style={actionBtn("#D98A8A", "rgba(196,84,84,.3)")}>Удалить</button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ===== REFERRALS TAB ===== */}
        {tab === "referrals" && refStats && (
          <div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 20 }}>
              <div style={{ padding: "14px 16px", borderRadius: 14, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)" }}>
                <div className="font-cinzel" style={{ fontSize: 9, letterSpacing: ".2em", color: "#C9A84C", textTransform: "uppercase" }}>Рефералов</div>
                <div className="font-cormorant" style={{ fontSize: 32, color: "#F0E9DA", lineHeight: 1, marginTop: 6 }}>{refStats.total_referrals}</div>
              </div>
              <div style={{ padding: "14px 16px", borderRadius: 14, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)" }}>
                <div className="font-cinzel" style={{ fontSize: 9, letterSpacing: ".2em", color: "#C9A84C", textTransform: "uppercase" }}>Дней Pro</div>
                <div className="font-cormorant" style={{ fontSize: 32, color: "#F0E9DA", lineHeight: 1, marginTop: 6 }}>{refStats.total_bonus_days_given}</div>
              </div>
            </div>
            {refStats.top_referrers.length > 0 && (
              <>
                <p className="font-cinzel" style={{ fontSize: 10, letterSpacing: ".2em", color: "#C9A84C", textTransform: "uppercase", marginBottom: 10 }}>Топ рефереров</p>
                <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 24 }}>
                  {refStats.top_referrers.map((r, i) => (
                    <div key={i} style={{ padding: 14, borderRadius: 12, background: "rgba(255,255,255,.025)", border: "1px solid rgba(255,255,255,.06)", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
                      <div>
                        <span style={{ fontSize: 14, color: "#F0E9DA", fontWeight: 500 }}>{r.name || "?"}</span>
                        {r.email && <span style={{ fontSize: 12, color: "#8A8170", marginLeft: 8 }}>{r.email}</span>}
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <span style={{ fontSize: 12, fontFamily: "monospace", background: "rgba(201,168,76,.1)", padding: "2px 8px", borderRadius: 6, color: "#C9A84C" }}>{r.ref_code}</span>
                        <span style={{ fontSize: 13, color: "#F0E9DA" }}>{r.referral_count} чел</span>
                        <span style={{ fontSize: 12, color: "#C9A84C" }}>+{r.bonus_days}д</span>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
            {refStats.recent.length > 0 && (
              <>
                <p className="font-cinzel" style={{ fontSize: 10, letterSpacing: ".2em", color: "#C9A84C", textTransform: "uppercase", marginBottom: 10 }}>Последние</p>
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  {refStats.recent.map((r, i) => (
                    <div key={i} style={{ padding: "10px 14px", borderRadius: 10, background: "rgba(255,255,255,.02)", display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: 13, flexWrap: "wrap", gap: 6 }}>
                      <span style={{ color: "#B6AC98" }}>{r.referrer_name} → {r.referred_name}</span>
                      <span style={{ color: "#6E6757" }}>{r.created_at ? new Date(r.created_at).toLocaleDateString("ru-RU") : ""}</span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        )}

        {/* ===== REFUNDS TAB ===== */}
        {tab === "refunds" && (
          <div>
            <p className="font-cinzel" style={{ fontSize: 10, letterSpacing: ".2em", color: "#C9A84C", textTransform: "uppercase", marginBottom: 16 }}>
              На рассмотрении ({refundsPending.length})
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 28 }}>
              {refundsPending.length === 0 && <p style={{ color: "#6E6757", textAlign: "center", padding: 40 }}>Нет заявок на рассмотрении</p>}
              {refundsPending.map(r => <RefundCard key={r.id} r={r} />)}
            </div>
            <p className="font-cinzel" style={{ fontSize: 10, letterSpacing: ".2em", color: "#C9A84C", textTransform: "uppercase", marginBottom: 16 }}>
              История
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {refundsResolved.length === 0 && <p style={{ color: "#6E6757", textAlign: "center", padding: 40 }}>Пусто</p>}
              {refundsResolved.map(r => <RefundCard key={r.id} r={r} />)}
            </div>
          </div>
        )}

        {/* ===== USERS TAB ===== */}
        {tab === "users" && <>
        {/* Stats — 2 cols on mobile, 4 on desktop */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 10, marginBottom: 20 }} className="admin-stats-grid">
          {statCards.map(s => (
            <div key={s.label} style={{ padding: "14px 16px", borderRadius: 14, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)" }}>
              <div className="font-cinzel" style={{ fontSize: 9, letterSpacing: ".2em", color: "#C9A84C", textTransform: "uppercase" }}>{s.label}</div>
              <div className="font-cormorant" style={{ fontSize: 32, color: "#F0E9DA", lineHeight: 1, marginTop: 6 }}>{s.value}</div>
            </div>
          ))}
        </div>

        {/* Search */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16, flexWrap: "wrap" }}>
          <input placeholder="Поиск..." value={search} onChange={e => { setSearch(e.target.value); setPage(1); }}
            style={{ flex: 1, minWidth: 200, padding: "10px 14px", borderRadius: 12, background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,.1)", color: "#F0E9DA", fontSize: 14, outline: "none", boxSizing: "border-box" }} />
          <span style={{ fontSize: 12, color: "#6E6757", flexShrink: 0 }}>{total} users</span>
        </div>

        {/* Mobile: cards / Desktop: table */}
        <div className="admin-table-desktop" style={{ borderRadius: 18, overflow: "hidden", border: "1px solid rgba(201,168,76,.13)", display: "none" }}>
          <div style={{ display: "grid", gridTemplateColumns: gridCols, padding: "12px 20px", background: "rgba(201,168,76,.06)" }}>
            {["ID", "Email / TG", "Имя", "Тир", "Рег.", "Действия"].map(h => (
              <span key={h} className="font-cinzel" style={{ fontSize: 10, letterSpacing: ".15em", color: "#C9A84C", textTransform: "uppercase" }}>{h}</span>
            ))}
          </div>
          {users.map(u => (
            <div key={u.id} style={{ display: "grid", gridTemplateColumns: gridCols, padding: "14px 20px", alignItems: "center", borderTop: "1px solid rgba(255,255,255,.06)" }}>
              <span style={{ fontSize: 11, color: "#6E6757", fontFamily: "monospace" }}>{u.id.slice(0, 8)}</span>
              <div>
                {u.email && <div style={{ fontSize: 13, color: "#F0E9DA" }}>{u.email}</div>}
                {u.telegram_id && <div style={{ fontSize: 11, color: "#A89E8B" }}>TG: {u.telegram_id}</div>}
                {!u.email && !u.telegram_id && <span style={{ color: "#6E6757" }}>—</span>}
              </div>
              <span style={{ fontSize: 13, color: "#B6AC98" }}>{u.display_name || "—"}</span>
              <div>
                <span className="font-cinzel" style={{
                  fontSize: 10, padding: "3px 8px", borderRadius: 99,
                  background: u.tier === "pro" ? "rgba(201,168,76,.15)" : "rgba(255,255,255,.05)",
                  border: u.tier === "pro" ? "1px solid rgba(201,168,76,.3)" : "none",
                  color: u.tier === "pro" ? "#E8CD7E" : "#6E6757",
                }}>{u.tier.toUpperCase()}</span>
                {u.tier === "pro" && u.subscription_expires_at && (
                  <div style={{ fontSize: 10, color: "#6E6757", marginTop: 2 }}>до {new Date(u.subscription_expires_at).toLocaleDateString("ru-RU")}</div>
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

        {/* Mobile cards */}
        <div className="admin-cards-mobile" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {users.map(u => <UserCard key={u.id} u={u} />)}
          {users.length === 0 && (
            <div style={{ padding: "40px 20px", textAlign: "center", color: "#6E6757" }}>Нет пользователей</div>
          )}
        </div>

        {/* Pagination */}
        {pages > 1 && (
          <div style={{ display: "flex", justifyContent: "center", gap: 8, marginTop: 24, flexWrap: "wrap" }}>
            {Array.from({ length: pages }, (_, i) => i + 1).map(p => (
              <button key={p} onClick={() => setPage(p)} style={{
                width: 36, height: 36, borderRadius: 10, border: "none", cursor: "pointer",
                background: p === page ? "rgba(201,168,76,.15)" : "rgba(255,255,255,.04)",
                color: p === page ? "#E8CD7E" : "#A89E8B", fontSize: 13,
              }}>{p}</button>
            ))}
          </div>
        )}
        </>}
      </div>

      <style>{`
        @media (min-width: 768px) {
          .admin-stats-grid { grid-template-columns: repeat(4,1fr) !important; }
          .admin-table-desktop { display: block !important; }
          .admin-cards-mobile { display: none !important; }
        }
      `}</style>
    </div>
  );
}

function actionBtn(color = "#E8CD7E", borderColor = "rgba(201,168,76,.3)"): React.CSSProperties {
  return {
    height: 30, padding: "0 12px", borderRadius: 8, fontSize: 12,
    background: "transparent", border: `1px solid ${borderColor}`,
    color, cursor: "pointer", whiteSpace: "nowrap",
  };
}
