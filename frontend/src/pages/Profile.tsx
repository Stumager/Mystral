import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { PaywallSheet } from "../components/PaywallSheet";
import { BottomNav, Button, Card } from "../components/ui";
import { TIMEZONES } from "../constants/timezones";
import { useAuth } from "../context/AuthContext";
import { usePushNotifications } from "../hooks/usePushNotifications";
import { StarRating } from "../components/StarRating";
import { isTMA } from "../utils/telegram";
import { validateDay, validateMonth, validateYear, validateDateExists } from "../utils/validate";
import { getZodiacSign } from "../utils/zodiac";

interface ProfilePageProps {
  onNavigate: (page: string) => void;
}

interface ProfileData {
  birth_date: string | null;
  birth_time: string | null;
  birth_time_known: boolean;
  birth_city: string | null;
  birth_name: string | null;
  completion_percent: number;
  notifications_enabled: boolean;
  timezone: string | null;
  subscription_expires_at: string | null;
  days_left: number | null;
}

const BOT_ID = "8998390466";

export function Profile({ onNavigate }: ProfilePageProps) {
  const { t } = useTranslation();
  const { user, token, logout, updateUser } = useAuth();
  const loaded = useRef(false);

  const [form, setForm] = useState({
    day: "", month: "", year: "",
    hour: "", minute: "", city: "", name: "",
  });
  const [completion, setCompletion] = useState(0);
  const [toast, setToast] = useState("");
  const [saving, setSaving] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);
  const [lang, setLang] = useState(user?.lang ?? "ru");

  const [providers, setProviders] = useState<string[]>([]);
  const [showLinkEmail, setShowLinkEmail] = useState(false);
  const [linkEmailForm, setLinkEmailForm] = useState({ email: "", password: "", confirm: "" });
  const [linkEmailError, setLinkEmailError] = useState("");
  const [linkingEmail, setLinkingEmail] = useState(false);

  const [notifEnabled, setNotifEnabled] = useState(false);
  const [notifTz, setNotifTz] = useState("Europe/Moscow");

  const [refData, setRefData] = useState<{ ref_code: string; ref_url: string; total_referrals: number; total_bonus_days: number; referrals: { name: string; bonus_days: number }[] } | null>(null);

  const [reviewRating, setReviewRating] = useState(0);
  const [reviewText, setReviewText] = useState("");
  const [reviewExists, setReviewExists] = useState(false);
  const [reviewSaving, setReviewSaving] = useState(false);

  const [showChangePw, setShowChangePw] = useState(false);
  const [curPw, setCurPw] = useState("");
  const [newPw, setNewPw] = useState("");
  const [confirmNewPw, setConfirmNewPw] = useState("");
  const [pwError, setPwError] = useState("");
  const [pwSaving, setPwSaving] = useState(false);
  const [daysLeft, setDaysLeft] = useState<number | null>(null);
  const [expiresAt, setExpiresAt] = useState<string | null>(null);

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletePassword, setDeletePassword] = useState("");
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState("");
  const [refundLoading, setRefundLoading] = useState(false);
  const [refundReason, setRefundReason] = useState("");
  const [refundStatus, setRefundStatus] = useState<{ status: string | null; admin_comment: string | null } | null>(null);

  function loadRefundStatus() {
    if (!token) return;
    fetch("/api/v1/payments/refund-request/status", { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json()).then(setRefundStatus).catch(() => {});
  }

  const setField = (field: string) =>
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setForm(prev => ({ ...prev, [field]: e.target.value }));
      setFormErrors(prev => ({ ...prev, [field]: "", date: "" }));
    };

  function authHeaders() {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    };
  }

  function showToast(msg: string) {
    setToast(msg);
    setTimeout(() => setToast(""), 2500);
  }

  const progressHints = [
    t("profile.hint_date"),
    t("profile.hint_time"),
    t("profile.hint_city"),
    t("profile.hint_name"),
  ];

  useEffect(() => {
    if (loaded.current || !token) return;
    loaded.current = true;

    Promise.all([
      fetch("/api/v1/profile", { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
      fetch("/api/v1/auth/me", { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
    ])
      .then(([profileData, meData]: [ProfileData, { providers: string[] }]) => {
        setCompletion(profileData.completion_percent ?? 0);
        const [y, m, d] = (profileData.birth_date ?? "").split("-");
        const [h, min] = (profileData.birth_time ?? "").split(":");
        setForm({
          year:   y   ?? "",
          month:  m   ?? "",
          day:    d   ?? "",
          hour:   h   ?? "",
          minute: min ?? "",
          city:   profileData.birth_city ?? "",
          name:   profileData.birth_name ?? "",
        });
        setProviders(meData.providers ?? []);
        setNotifEnabled(profileData.notifications_enabled ?? false);
        if (profileData.timezone) setNotifTz(profileData.timezone);
        setDaysLeft(profileData.days_left);
        setExpiresAt(profileData.subscription_expires_at);
      })
      .catch(() => {});

    if (token) {
      fetch("/api/v1/referrals/my", { headers: { Authorization: `Bearer ${token}` } })
        .then(r => r.json()).then(setRefData).catch(() => {});
      fetch("/api/v1/reviews/my", { headers: { Authorization: `Bearer ${token}` } })
        .then(r => r.json())
        .then(d => { if (d && d.rating) { setReviewRating(d.rating); setReviewText(d.text || ""); setReviewExists(true); } })
        .catch(() => {});
      loadRefundStatus();
    }
  }, [token]);

  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  async function handleSave() {
    if (form.day || form.month || form.year) {
      const errs: Record<string, string> = {};
      if (form.day) { const e = validateDay(form.day); if (e) errs.day = e; }
      if (form.month) { const e = validateMonth(form.month); if (e) errs.month = e; }
      if (form.year) { const e = validateYear(form.year); if (e) errs.year = e; }
      if (form.day && form.month && form.year && !errs.day && !errs.month && !errs.year) {
        const de = validateDateExists(form.day, form.month, form.year);
        if (de) errs.date = de;
      }
      if (Object.values(errs).some(Boolean)) { setFormErrors(errs); return; }
    }
    setSaving(true);
    const body: Record<string, unknown> = {
      birth_city: form.city || null,
      birth_name: form.name || null,
      lang,
    };
    if (form.year && form.month && form.day) {
      body.birth_date = `${form.year}-${form.month.padStart(2, "0")}-${form.day.padStart(2, "0")}`;
    }
    if (form.hour) {
      body.birth_time = `${form.hour.padStart(2, "0")}:${(form.minute || "0").padStart(2, "0")}`;
      body.birth_time_known = true;
    }
    try {
      const res = await fetch("/api/v1/profile", {
        method: "PUT",
        headers: authHeaders(),
        body: JSON.stringify(body),
      });
      const data = await res.json();
      setCompletion(data.completion_percent);
      showToast(t("profile.saved"));
    } catch {
      showToast(t("profile.save_error"));
    } finally {
      setSaving(false);
    }
  }

  async function handleLang(newLang: string) {
    setLang(newLang);
    updateUser({ lang: newLang });
    await fetch("/api/v1/profile", {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify({ lang: newLang }),
    }).catch(() => {});
  }

  async function handleLinkEmail() {
    if (linkEmailForm.password !== linkEmailForm.confirm) {
      setLinkEmailError(t("profile.passwords_mismatch"));
      return;
    }
    setLinkEmailError("");
    setLinkingEmail(true);
    try {
      const res = await fetch("/api/v1/auth/link-email", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ email: linkEmailForm.email, password: linkEmailForm.password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Error");
      setProviders(p => [...p, "email"]);
      setShowLinkEmail(false);
      setLinkEmailForm({ email: "", password: "", confirm: "" });
      showToast(t("profile.email_linked"));
    } catch (e: unknown) {
      setLinkEmailError(e instanceof Error ? e.message : "Error");
    } finally {
      setLinkingEmail(false);
    }
  }

  function handleTelegramWebLogin() {
    const origin = encodeURIComponent(window.location.origin);
    const url = `https://oauth.telegram.org/auth?bot_id=${BOT_ID}&origin=${origin}&request_access=write&embed=1`;
    const popup = window.open(url, "_blank", "width=550,height=450,popup");
    if (!popup) { showToast(t("profile.popup_blocked")); return; }

    const handleMessage = async (event: MessageEvent) => {
      if (event.origin !== "https://oauth.telegram.org") return;
      const data = event.data;
      if (!data || typeof data !== "object" || !data.id) return;
      window.removeEventListener("message", handleMessage);
      clearInterval(checkClosed);
      popup.close();
      try {
        const res = await fetch("/api/v1/auth/link-telegram", {
          method: "POST",
          headers: authHeaders(),
          body: JSON.stringify({ widget_data: data }),
        });
        const json = await res.json();
        if (!res.ok) throw new Error(json.detail || "Error");
        setProviders(p => [...p, "telegram"]);
        showToast(t("profile.tg_linked"));
      } catch (e: unknown) {
        showToast(e instanceof Error ? e.message : t("profile.link_error"));
      }
    };

    window.addEventListener("message", handleMessage);
    const checkClosed = setInterval(() => {
      if (popup.closed) {
        clearInterval(checkClosed);
        window.removeEventListener("message", handleMessage);
      }
    }, 1000);
  }

  async function handleToggleNotif(enabled: boolean) {
    setNotifEnabled(enabled);
    await fetch("/api/v1/profile", {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify({ notifications_enabled: enabled }),
    }).catch(() => {});
  }

  async function handleChangeTz(newTz: string) {
    setNotifTz(newTz);
    await fetch("/api/v1/profile", {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify({ timezone: newTz }),
    }).catch(() => {});
  }

  const inputStyle: React.CSSProperties = {
    width: "100%", padding: "14px 16px", borderRadius: 14,
    background: "rgba(255,255,255,.04)", border: "1px solid rgba(201,168,76,.22)",
    color: "#F0E9DA", fontSize: 15, outline: "none", boxSizing: "border-box",
  };
  void 0; // inputCls removed — using inputStyle instead

  const push = usePushNotifications();

  function PushToggle() {
    if (!push.supported) return null;
    const statusText = push.permission === "denied"
      ? t("profile.push_blocked")
      : push.subscribed
        ? t("profile.push_connected")
        : t("profile.push_off");
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingTop: 14, borderTop: "1px solid rgba(255,255,255,.06)", marginTop: 14 }}>
        <div>
          <p style={{ fontSize: 14, color: "#F0E9DA" }}>{t("profile.push_browser")}</p>
          <p style={{ fontSize: 12, color: "#8A8170" }}>{statusText}</p>
        </div>
        {push.subscribed ? (
          <button onClick={push.unsubscribe} className="w-10 h-5 rounded-full relative" style={{ background: "linear-gradient(90deg,#8A6E2E,#C9A84C)" }}>
            <span className="block w-4 h-4 rounded-full bg-white absolute top-0.5" style={{ left: 22 }} />
          </button>
        ) : push.permission !== "denied" ? (
          <button onClick={push.subscribe} style={{ height: 34, padding: "0 14px", borderRadius: 8, border: "1px solid rgba(201,168,76,.4)", background: "rgba(201,168,76,.06)", color: "#E8CD7E", fontSize: 13, cursor: "pointer" }}>
            {t("profile.push_enable")}
          </button>
        ) : (
          <span style={{ fontSize: 11, color: "#6E6757" }}>{t("profile.push_allow_settings")}</span>
        )}
      </div>
    );
  }

  const firstLetter = (user?.name ?? "?")[0]?.toUpperCase() ?? "?";
  const zodiac = form.year && form.month && form.day
    ? getZodiacSign(`${form.year}-${form.month.padStart(2, "0")}-${form.day.padStart(2, "0")}`)
    : null;
  const zodiacLabel = zodiac
    ? (user?.lang === "en" ? zodiac.en : zodiac.sign)
    : null;

  const hintIndex = Math.floor(completion / 25);
  const hint = completion < 100 ? progressHints[hintIndex] ?? progressHints[3] : t("profile.hint_done");

  return (
    <div className="flex flex-col min-h-screen relative" style={{ background: "var(--gradient-page)", animation: "mystral-fadeup .3s ease-out" }}>
      <header className="lg:hidden" style={{ position: "sticky", top: 0, zIndex: 10, display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 20px", background: "rgba(7,6,15,.82)", backdropFilter: "blur(18px)", borderBottom: "1px solid rgba(201,168,76,.14)" }}>
        <button onClick={() => onNavigate("home")} style={{ color: "#A89E8B", fontSize: 20, background: "none", border: "none", cursor: "pointer" }}>‹</button>
        <span className="font-cinzel" style={{ fontSize: 13, letterSpacing: ".26em", color: "#E8CD7E", textTransform: "uppercase" }}>{t("profile.title")}</span>
        <div style={{ width: 20 }} />
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-6 pb-24 flex flex-col gap-5">

        {/* Avatar + name */}
        <div className="flex flex-col items-center gap-2">
          <div style={{ width: 64, height: 64, borderRadius: "50%", background: "linear-gradient(135deg,#4B3C86,#C9A84C)", border: "2px solid rgba(201,168,76,.3)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <span className="font-cormorant" style={{ fontSize: 28, color: "#0C0A18", fontWeight: 600 }}>{firstLetter}</span>
          </div>
          <p className="font-cormorant" style={{ fontSize: 22, color: "#F0E9DA" }}>
            {user?.name ?? t("profile.guest")}
          </p>
          {zodiacLabel && (
            <p style={{ fontSize: 13, color: "#C9A84C" }}>{zodiacLabel}</p>
          )}
        </div>

        {/* Progress */}
        <Card>
          <div className="flex items-center justify-between mb-2">
            <p className="text-text-muted text-xs">{t("profile.completed")}</p>
            <p className="font-display text-sm" style={{ color: "#C9A84C" }}>
              {completion}%
            </p>
          </div>
          <div style={{ width: "100%", height: 7, borderRadius: 99, background: "rgba(255,255,255,.07)", overflow: "hidden" }}>
            <div style={{ width: `${completion}%`, height: "100%", borderRadius: 99, background: "linear-gradient(90deg,#8A6E2E,#E8CD7E)", boxShadow: "0 0 12px rgba(201,168,76,.5)", transition: "width .5s ease" }} />
          </div>
          <p className="text-text-faint text-[10px] mt-2">{hint}</p>
        </Card>

        {/* Birth data form */}
        <Card>
          <p className="font-cinzel" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C", textTransform: "uppercase" }}>
            {t("profile.birth_data")}
          </p>
          <div className="flex flex-col gap-3">
            <div>
              <div className="grid grid-cols-3 gap-2">
                <input style={inputStyle} placeholder={t("profile.day")}   type="number" min="1"    max="31"   value={form.day}   onChange={setField("day")} />
                <input style={inputStyle} placeholder={t("profile.month")} type="number" min="1"    max="12"   value={form.month} onChange={setField("month")} />
                <input style={inputStyle} placeholder={t("profile.year")}  type="number" min="1900" max="2025" value={form.year}  onChange={setField("year")} />
              </div>
              {(formErrors.day || formErrors.month || formErrors.year || formErrors.date) && (
                <p className="text-red-400 text-xs mt-1">{formErrors.day || formErrors.month || formErrors.year || formErrors.date}</p>
              )}
            </div>
            <div className="grid grid-cols-2 gap-2">
              <input style={inputStyle} placeholder={t("profile.hour")}    type="number" min="0" max="23" value={form.hour}   onChange={setField("hour")} />
              <input style={inputStyle} placeholder={t("profile.minutes")} type="number" min="0" max="59" value={form.minute} onChange={setField("minute")} />
            </div>
            <input style={inputStyle} placeholder={t("profile.birth_city")} value={form.city} onChange={setField("city")} />
            <input style={inputStyle} placeholder={t("profile.birth_name")} value={form.name} onChange={setField("name")} />
          </div>

          <Button
            variant="primary"
            className="w-full mt-4"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? t("profile.saving") : t("profile.save")}
          </Button>

          {toast && (
            <p className="text-center text-xs mt-2" style={{ color: "#C9A84C" }}>
              {toast}
            </p>
          )}
        </Card>

        {/* Subscription tier */}
        {user?.tier === "pro" ? (
          <Card>
            <div className="flex items-center gap-2 mb-1">
              <span className="font-cinzel" style={{ fontSize: 10, color: "#C9A84C", letterSpacing: ".2em" }}>PRO</span>
              <p className="font-cormorant" style={{ fontSize: 16, color: "#F0E9DA" }}>{t("profile.pro_active")}</p>
            </div>
            {expiresAt && daysLeft !== null && (
              <p
                className="text-[10px] mt-1"
                style={{ color: daysLeft <= 3 ? "#f87171" : "#9B8FBB" }}
              >
                {t("profile.pro_until", {
                  date: new Date(expiresAt).toLocaleDateString(user?.lang === "en" ? "en-US" : "ru-RU", { day: "numeric", month: "long" }),
                })} · {t("profile.days_left", { count: daysLeft })}
              </p>
            )}
            {daysLeft !== null && daysLeft <= 3 && (
              <p className="text-[10px] mt-1" style={{ color: "#C9A84C" }}>
                {t("profile.pro_expiring_soon")}
              </p>
            )}
            <Button variant="gold" size="sm" className="w-full mt-2" onClick={() => setShowPaywall(true)}>
              {t("profile.renew")}
            </Button>
            {refundStatus?.status === "pending" ? (
              <p style={{ fontSize: 12, color: "#C9A84C", marginTop: 8, textAlign: "center" }}>
                {t("profile.refund_status_pending")}
              </p>
            ) : (
              <>
                {refundStatus?.status === "rejected" && (
                  <p style={{ fontSize: 11, color: "#D98A8A", marginTop: 8 }}>
                    {t("profile.refund_status_rejected")}
                    {refundStatus.admin_comment && ` — ${t("profile.refund_status_rejected_comment")}: ${refundStatus.admin_comment}`}
                  </p>
                )}
                {refundStatus?.status === "completed" && (
                  <p style={{ fontSize: 11, color: "#6E9A8A", marginTop: 8 }}>{t("profile.refund_status_completed")}</p>
                )}
                {refundStatus?.status === "failed" && (
                  <p style={{ fontSize: 11, color: "#D98A8A", marginTop: 8 }}>{t("profile.refund_status_failed")}</p>
                )}
                <input
                  value={refundReason}
                  onChange={e => setRefundReason(e.target.value)}
                  placeholder={t("profile.refund_reason_placeholder")}
                  style={{ width: "100%", height: 38, marginTop: 8, borderRadius: 12, border: "1px solid rgba(255,255,255,.1)", background: "rgba(255,255,255,.04)", color: "#F0E9DA", fontSize: 13, padding: "0 12px", boxSizing: "border-box", outline: "none" }}
                />
                <button
                  onClick={async () => {
                    setRefundLoading(true);
                    try {
                      const res = await fetch("/api/v1/payments/refund-request", { method: "POST", headers: authHeaders(), body: JSON.stringify({ reason: refundReason || null }) });
                      const d = await res.json();
                      if (d.status === "sent") { showToast(t("profile.refund_sent")); setRefundReason(""); loadRefundStatus(); }
                      else if (d.status === "expired") showToast(t("profile.refund_expired"));
                      else showToast(d.message || d.detail || t("profile.refund_no_payment"));
                    } catch { showToast("Error"); }
                    finally { setRefundLoading(false); }
                  }}
                  disabled={refundLoading}
                  style={{ width: "100%", height: 38, marginTop: 8, borderRadius: 12, border: "1px solid rgba(196,84,84,.3)", background: "transparent", color: "#D98A8A", fontSize: 13, cursor: "pointer" }}
                >
                  {refundLoading ? "..." : t("profile.request_refund")}
                </button>
              </>
            )}
          </Card>
        ) : (
          <Card>
            <p className="text-text-muted text-xs mb-3">{t("profile.free_plan")}</p>
            <Button variant="gold" size="sm" className="w-full" onClick={() => setShowPaywall(true)}>
              {t("profile.upgrade")}
            </Button>
          </Card>
        )}

        {/* Linked accounts */}
        <Card>
          <p className="font-cinzel" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C", textTransform: "uppercase" }}>
            {t("profile.linked_accounts")}
          </p>

          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-text-muted text-sm">Email</span>
                {providers.includes("email") && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full" style={{ background: "rgba(107,78,255,0.15)", color: "#9B8AFF" }}>
                    {t("profile.linked")}
                  </span>
                )}
              </div>
              {!providers.includes("email") && !showLinkEmail && (
                <button onClick={() => setShowLinkEmail(true)} className="text-xs" style={{ color: "#9B8AFF" }}>
                  {t("profile.add")}
                </button>
              )}
            </div>

            {showLinkEmail && (
              <div className="flex flex-col gap-2">
                <input type="email" placeholder={t("login.email")} value={linkEmailForm.email} onChange={e => setLinkEmailForm(p => ({ ...p, email: e.target.value }))} style={inputStyle} />
                <input type="password" placeholder={t("profile.password")} value={linkEmailForm.password} onChange={e => setLinkEmailForm(p => ({ ...p, password: e.target.value }))} style={inputStyle} />
                <input type="password" placeholder={t("profile.confirm_password")} value={linkEmailForm.confirm} onChange={e => setLinkEmailForm(p => ({ ...p, confirm: e.target.value }))} style={inputStyle} />
                {linkEmailError && <p className="text-red-400 text-xs">{linkEmailError}</p>}
                <div className="flex gap-2">
                  <Button variant="primary" size="sm" className="flex-1" onClick={handleLinkEmail} disabled={linkingEmail}>
                    {linkingEmail ? "..." : t("profile.save")}
                  </Button>
                  <Button variant="ghost" size="sm" className="flex-1" onClick={() => { setShowLinkEmail(false); setLinkEmailForm({ email: "", password: "", confirm: "" }); setLinkEmailError(""); }}>
                    {t("profile.cancel")}
                  </Button>
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-text-muted text-sm">Telegram</span>
              {providers.includes("telegram") && (
                <span className="text-[10px] px-2 py-0.5 rounded-full" style={{ background: "rgba(41,182,246,0.12)", color: "#29B6F6" }}>
                  {t("profile.linked")}
                </span>
              )}
            </div>
            {!providers.includes("telegram") && (
              <button onClick={handleTelegramWebLogin} className="text-xs" style={{ color: "#29B6F6" }}>
                {t("profile.link")}
              </button>
            )}
          </div>
        </Card>

        {/* Notifications */}
        <Card>
          <p className="font-cinzel" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C", textTransform: "uppercase" }}>
            {t("profile.notifications")}
          </p>
          <div className="flex items-center justify-between mb-3">
            <span className="text-text-muted text-sm">{t("profile.daily_horoscope")}</span>
            <button
              onClick={() => handleToggleNotif(!notifEnabled)}
              className="w-10 h-5 rounded-full transition-colors relative"
              style={{ background: notifEnabled ? "linear-gradient(90deg,#8A6E2E,#C9A84C)" : "rgba(255,255,255,.1)" }}
            >
              <span
                className="block w-4 h-4 rounded-full bg-white absolute top-0.5 transition-all"
                style={{ left: notifEnabled ? 22 : 2 }}
              />
            </button>
          </div>
          {notifEnabled && (
            <div className="flex items-center justify-between">
              <span className="text-text-faint text-xs">{t("profile.notif_timezone")}</span>
              <select
                value={notifTz}
                onChange={e => handleChangeTz(e.target.value)}
                className="bg-bg-surface border border-border-subtle rounded-lg px-2 py-1 text-text-primary text-xs focus:outline-none max-w-[160px]"
              >
                {TIMEZONES.map(tz => (
                  <option key={tz.value} value={tz.value}>{tz.label}</option>
                ))}
              </select>
            </div>
          )}
          <PushToggle />
        </Card>

        {/* Referral */}
        {refData && (
          <div style={{ padding: 20, borderRadius: 18, background: "linear-gradient(120deg,#1B1546,#0C0A22)", border: "1px solid rgba(201,168,76,.24)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <p className="font-cormorant" style={{ fontSize: 22, color: "#F0E9DA" }}>{t("profile.invite_friends")}</p>
                <p style={{ fontSize: 13, color: "#A89E8B", marginTop: 4 }}>{t("profile.ref_bonus_you")}</p>
                <p style={{ fontSize: 13, color: "#A89E8B" }}>{t("profile.ref_bonus_friend")}</p>
                <p style={{ fontSize: 13, color: "#C9A84C", fontWeight: 600, marginTop: 6 }}>
                  {t("profile.ref_bonus_earned")}: +{refData.total_bonus_days}
                </p>
              </div>
              <span className="font-cinzel" style={{ fontSize: 11, color: "#E8CD7E", background: "rgba(201,168,76,.15)", border: "1px solid rgba(201,168,76,.3)", borderRadius: 99, padding: "4px 12px" }}>
                {refData.total_referrals}
              </span>
            </div>
            <p className="font-cinzel" style={{ fontSize: 9, letterSpacing: ".2em", color: "#C9A84C", textTransform: "uppercase", marginTop: 16, marginBottom: 8 }}>
              {t("profile.your_link")}
            </p>
            <div style={{ display: "flex", gap: 8 }}>
              <input readOnly value={refData.ref_url} style={{ flex: 1, padding: "12px 14px", borderRadius: 12, background: "rgba(255,255,255,.04)", border: "1px solid rgba(201,168,76,.2)", color: "#E8CD7E", fontSize: 13, fontFamily: "monospace", outline: "none", minWidth: 0 }} />
              <button onClick={() => { navigator.clipboard.writeText(refData.ref_url); showToast(t("profile.link_copied")); }}
                style={{ height: 44, padding: "0 16px", borderRadius: 12, border: "1px solid rgba(201,168,76,.4)", background: "rgba(201,168,76,.06)", color: "#E8CD7E", fontSize: 13, cursor: "pointer", flexShrink: 0 }}>
                {t("profile.copy")}
              </button>
            </div>
            <button onClick={() => window.open(`https://t.me/share/url?url=${encodeURIComponent(refData.ref_url)}&text=${encodeURIComponent(t("profile.share_text"))}`, "_blank")}
              style={{ width: "100%", height: 44, marginTop: 10, borderRadius: 12, border: "1px solid rgba(255,255,255,.1)", background: "transparent", color: "#B6AC98", fontSize: 13, cursor: "pointer" }}>
              {t("profile.share_telegram")}
            </button>
            {refData.referrals.length > 0 && (
              <div style={{ marginTop: 16, borderTop: "1px solid rgba(255,255,255,.06)", paddingTop: 14 }}>
                <p className="font-cinzel" style={{ fontSize: 9, letterSpacing: ".15em", color: "#6E6757", textTransform: "uppercase", marginBottom: 8 }}>
                  {t("profile.invited")}
                </p>
                {refData.referrals.map((r, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 0" }}>
                    <div style={{ width: 28, height: 28, borderRadius: "50%", background: "linear-gradient(135deg,#4B3C86,#8A7FC0)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, color: "#F0E9DA" }}>{r.name[0]}</div>
                    <span style={{ fontSize: 13, color: "#B6AC98" }}>{r.name}</span>
                    <span style={{ fontSize: 12, color: "#C9A84C", marginLeft: "auto" }}>+{r.bonus_days}д</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Review */}
        <Card>
          <p className="font-cinzel" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C", textTransform: "uppercase" }}>
            {t("profile.my_review")}
          </p>
          <p className="font-cormorant" style={{ fontSize: 20, color: "#F0E9DA", marginTop: 12, marginBottom: 16 }}>
            {t("profile.rate_mystral")}
          </p>
          <StarRating value={reviewRating} onChange={setReviewRating} size={32} />
          <textarea
            value={reviewText} onChange={e => setReviewText(e.target.value.slice(0, 500))}
            placeholder={t("profile.review_placeholder")}
            style={{ width: "100%", minHeight: 100, padding: "14px 16px", borderRadius: 14, resize: "none", background: "rgba(255,255,255,.04)", border: "1px solid rgba(201,168,76,.22)", color: "#F0E9DA", fontSize: 14, lineHeight: 1.6, marginTop: 16, outline: "none", boxSizing: "border-box" }}
          />
          <p style={{ textAlign: "right", fontSize: 11, color: "#6E6757", marginTop: 4 }}>{reviewText.length}/500</p>
          <Button variant="primary" className="w-full" style={{ marginTop: 12 }}
            disabled={reviewRating === 0 || reviewSaving}
            onClick={async () => {
              setReviewSaving(true);
              try {
                await fetch("/api/v1/reviews", { method: "POST", headers: authHeaders(), body: JSON.stringify({ rating: reviewRating, text: reviewText || null }) });
                showToast(t("profile.review_sent"));
                setReviewExists(true);
              } catch {}
              finally { setReviewSaving(false); }
            }}>
            {reviewSaving ? "..." : reviewExists ? t("profile.update_review") : t("profile.submit_review")}
          </Button>
          <p style={{ fontSize: 12, color: "#6E6757", textAlign: "center", marginTop: 8 }}>
            {t("profile.review_moderation")}
          </p>
        </Card>

        {/* Security */}
        <Card>
          <p className="font-cinzel" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C", textTransform: "uppercase" }}>
            {t("profile.security")}
          </p>
          {providers.includes("email") && (
            <>
              {!showChangePw ? (
                <Button variant="ghost" size="sm" className="w-full mt-3" onClick={() => setShowChangePw(true)}>
                  {t("profile.change_password")}
                </Button>
              ) : (
                <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 10, animation: "mystral-fadeup .25s ease-out" }}>
                  <input type="password" placeholder={t("profile.current_password")}
                    value={curPw} onChange={e => { setCurPw(e.target.value); setPwError(""); }} style={inputStyle} />
                  <input type="password" placeholder={t("profile.new_password")}
                    value={newPw} onChange={e => { setNewPw(e.target.value); setPwError(""); }} style={inputStyle} />
                  <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                    {[
                      { ok: newPw.length >= 8, label: t("profile.min_8_chars") },
                      { ok: /[A-Z]/.test(newPw), label: t("profile.uppercase_letter") },
                      { ok: /[0-9]/.test(newPw), label: t("profile.digit") },
                    ].map(c => (
                      <span key={c.label} style={{ fontSize: 11, color: c.ok ? "#6E9A8A" : "#6E6757" }}>{c.ok ? "✓" : "✗"} {c.label}</span>
                    ))}
                  </div>
                  <input type="password" placeholder={t("profile.confirm_new")}
                    value={confirmNewPw} onChange={e => { setConfirmNewPw(e.target.value); setPwError(""); }}
                    style={{ ...inputStyle, borderColor: confirmNewPw && confirmNewPw !== newPw ? "rgba(196,84,84,.4)" : undefined }} />
                  {pwError && <p style={{ color: "#D98A8A", fontSize: 12 }}>{pwError}</p>}
                  <div className="flex gap-2">
                    <Button variant="primary" size="sm" className="flex-1" disabled={pwSaving || newPw.length < 8 || !/[A-Z]/.test(newPw) || !/[0-9]/.test(newPw) || confirmNewPw !== newPw}
                      onClick={async () => {
                        setPwSaving(true); setPwError("");
                        try {
                          const res = await fetch("/api/v1/auth/change-password", { method: "POST", headers: authHeaders(), body: JSON.stringify({ current_password: curPw, new_password: newPw }) });
                          const d = await res.json();
                          if (!res.ok) { setPwError(d.detail || "Error"); return; }
                          showToast(t("profile.password_changed"));
                          setShowChangePw(false); setCurPw(""); setNewPw(""); setConfirmNewPw("");
                        } catch { setPwError("Error"); }
                        finally { setPwSaving(false); }
                      }}>
                      {pwSaving ? "..." : t("profile.save_pw")}
                    </Button>
                    <Button variant="ghost" size="sm" className="flex-1" onClick={() => { setShowChangePw(false); setCurPw(""); setNewPw(""); setConfirmNewPw(""); setPwError(""); }}>
                      {t("profile.cancel")}
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
          <Button variant="ghost" size="sm" className="w-full mt-3"
            style={{ color: "#D98A8A", borderColor: "rgba(196,84,84,.3)" }}
            onClick={() => setShowDeleteModal(true)}>
            {t("profile.delete_account")}
          </Button>
        </Card>

        {/* Settings */}
        <Card>
          <p className="font-cinzel" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C", textTransform: "uppercase" }}>
            {t("profile.settings")}
          </p>

          <div className="flex items-center justify-between mb-4">
            <span className="text-text-muted text-sm">{t("profile.language")}</span>
            <div>
              <select value={lang} onChange={e => handleLang(e.target.value)}
                style={{ padding: "10px 14px", borderRadius: 14, background: "rgba(255,255,255,.04)", border: "1px solid rgba(201,168,76,.22)", color: "#F0E9DA", fontSize: 14, outline: "none" }}>
                {[
                  { code: "ru", label: "Русский" },
                  { code: "en", label: "English" },
                  { code: "es", label: "Español" },
                  { code: "pt", label: "Português" },
                  { code: "tr", label: "Türkçe" },
                  { code: "uk", label: "Українська" },
                ].map(l => (
                  <option key={l.code} value={l.code} style={{ background: "#0D0B1F" }}>{l.label}</option>
                ))}
              </select>
            </div>
          </div>

          <Button
            variant="ghost"
            size="sm"
            className="w-full mb-3"
            onClick={() => window.open("https://t.me/Mystrallbot?start=support", "_blank")}
          >
            {t("profile.support")}
          </Button>

          {isTMA() ? (
            <div className="flex items-center justify-between py-3">
              <span className="text-text-muted text-sm">{t("profile.tg_account")}</span>
              <span style={{ fontSize: 12, color: "#C9A84C" }}>Telegram</span>
            </div>
          ) : (
            <Button variant="ghost" size="sm" className="w-full" onClick={logout}>
              {t("profile.logout")}
            </Button>
          )}
        </Card>

      </main>

      {/* Delete account modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 flex items-center justify-center" style={{ zIndex: 100, background: "rgba(0,0,0,.7)", backdropFilter: "blur(8px)" }} onClick={e => e.target === e.currentTarget && setShowDeleteModal(false)}>
          <div style={{ padding: 28, borderRadius: 22, maxWidth: 400, width: "90%", background: "linear-gradient(155deg,rgba(20,8,8,.95),rgba(10,4,4,.98))", border: "1px solid rgba(196,84,84,.3)" }}>
            <h3 className="font-cormorant" style={{ fontSize: 28, color: "#D98A8A" }}>{t("profile.delete_account")}</h3>
            <p style={{ fontSize: 14, color: "#A89E8B", lineHeight: 1.7, margin: "12px 0 20px" }}>
              {t("profile.delete_warning")}
            </p>

            {providers.includes("email") ? (
              <input type="password" placeholder={t("profile.delete_password_placeholder")} value={deletePassword} onChange={e => { setDeletePassword(e.target.value); setDeleteError(""); }}
                style={{ width: "100%", padding: "12px 14px", borderRadius: 12, background: "rgba(255,255,255,.04)", border: "1px solid rgba(196,84,84,.2)", color: "#F0E9DA", fontSize: 14, outline: "none", boxSizing: "border-box", marginBottom: 12 }} />
            ) : (
              <label style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16, cursor: "pointer" }}>
                <input type="checkbox" checked={deleteConfirm} onChange={e => setDeleteConfirm(e.target.checked)} style={{ accentColor: "#D98A8A" }} />
                <span style={{ fontSize: 13, color: "#A89E8B" }}>{t("profile.delete_confirm_check")}</span>
              </label>
            )}

            {deleteError && <p style={{ color: "#D98A8A", fontSize: 12, marginBottom: 10 }}>{deleteError}</p>}

            <div style={{ display: "flex", gap: 12 }}>
              <Button variant="ghost" size="sm" className="flex-1" onClick={() => { setShowDeleteModal(false); setDeletePassword(""); setDeleteConfirm(false); setDeleteError(""); }}>
                {t("profile.cancel")}
              </Button>
              <button
                disabled={deleteLoading || (providers.includes("email") ? !deletePassword : !deleteConfirm)}
                onClick={async () => {
                  setDeleteLoading(true); setDeleteError("");
                  try {
                    const body: Record<string, unknown> = providers.includes("email") ? { password: deletePassword } : { confirm: true };
                    const res = await fetch("/api/v1/auth/account", { method: "DELETE", headers: authHeaders(), body: JSON.stringify(body) });
                    const d = await res.json();
                    if (!res.ok) { setDeleteError(d.detail || "Error"); return; }
                    logout();
                  } catch { setDeleteError("Error"); }
                  finally { setDeleteLoading(false); }
                }}
                style={{ flex: 1, height: 38, borderRadius: 12, border: "1px solid rgba(196,84,84,.4)", background: "rgba(196,84,84,.15)", color: "#D98A8A", fontSize: 13, fontWeight: 600, cursor: "pointer" }}
              >
                {deleteLoading ? "..." : t("profile.delete_forever")}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toast overlay */}
      {toast && (
        <div className="fixed top-14 left-0 right-0 flex justify-center pointer-events-none" style={{ zIndex: 50 }}>
          <span className="text-xs px-4 py-2 rounded-full" style={{ background: "rgba(201,168,76,.1)", border: "1px solid rgba(201,168,76,.3)", color: "#E8CD7E" }}>
            {toast}
          </span>
        </div>
      )}

      <BottomNav active="profile" onNavigate={onNavigate} />

      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
    </div>
  );
}
