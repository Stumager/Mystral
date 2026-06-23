import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { PaywallSheet } from "../components/PaywallSheet";
import { BottomNav, Button, Card } from "../components/ui";
import { TIMEZONES } from "../constants/timezones";
import { useAuth } from "../context/AuthContext";
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
  const [daysLeft, setDaysLeft] = useState<number | null>(null);
  const [expiresAt, setExpiresAt] = useState<string | null>(null);

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

  const inputCls =
    "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 " +
    "text-text-primary text-sm placeholder:text-text-faint " +
    "focus:outline-none focus:border-violet-600 transition-colors";

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
    <div className="flex flex-col min-h-screen relative" style={{ background: "var(--gradient-page)" }}>
      <header
        className="flex items-center justify-between px-4 shrink-0 backdrop-blur-md"
        style={{ height: 46, background: "var(--bg-header)", borderBottom: "1px solid var(--border-gold)" }}
      >
        <div className="w-8" />
        <span className="font-cinzel text-sm tracking-[.25em]" style={{ color: "#E8CD7E" }}>
          {t("profile.title")}
        </span>
        <div className="w-8" />
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-6 pb-24 flex flex-col gap-5">

        {/* Avatar + name */}
        <div className="flex flex-col items-center gap-2">
          <div
            className="w-16 h-16 rounded-full flex items-center justify-center font-display text-2xl text-white"
            style={{ background: "#6B4EFF" }}
          >
            {firstLetter}
          </div>
          <p className="font-display text-text-primary text-xl">
            {user?.name ?? t("profile.guest")}
          </p>
          {zodiacLabel && (
            <p className="text-text-faint text-xs">{zodiacLabel}</p>
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
          <div
            className="w-full rounded-full overflow-hidden"
            style={{ height: 4, background: "rgba(107,78,255,0.15)" }}
          >
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${completion}%`, background: "#6B4EFF" }}
            />
          </div>
          <p className="text-text-faint text-[10px] mt-2">{hint}</p>
        </Card>

        {/* Birth data form */}
        <Card>
          <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">
            {t("profile.birth_data")}
          </p>
          <div className="flex flex-col gap-3">
            <div>
              <div className="grid grid-cols-3 gap-2">
                <input className={inputCls} placeholder={t("profile.day")}   type="number" min="1"    max="31"   value={form.day}   onChange={setField("day")} />
                <input className={inputCls} placeholder={t("profile.month")} type="number" min="1"    max="12"   value={form.month} onChange={setField("month")} />
                <input className={inputCls} placeholder={t("profile.year")}  type="number" min="1900" max="2025" value={form.year}  onChange={setField("year")} />
              </div>
              {(formErrors.day || formErrors.month || formErrors.year || formErrors.date) && (
                <p className="text-red-400 text-xs mt-1">{formErrors.day || formErrors.month || formErrors.year || formErrors.date}</p>
              )}
            </div>
            <div className="grid grid-cols-2 gap-2">
              <input className={inputCls} placeholder={t("profile.hour")}    type="number" min="0" max="23" value={form.hour}   onChange={setField("hour")} />
              <input className={inputCls} placeholder={t("profile.minutes")} type="number" min="0" max="59" value={form.minute} onChange={setField("minute")} />
            </div>
            <input className={inputCls} placeholder={t("profile.birth_city")} value={form.city} onChange={setField("city")} />
            <input className={inputCls} placeholder={t("profile.birth_name")} value={form.name} onChange={setField("name")} />
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
              <span className="font-display text-sm" style={{ color: "#C9A84C" }}>✦</span>
              <p className="font-display text-sm text-text-primary">{t("profile.pro_active")}</p>
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
          <p className="text-text-faint text-[9px] uppercase tracking-widest mb-4">
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
                <input type="email" placeholder={t("login.email")} value={linkEmailForm.email} onChange={e => setLinkEmailForm(p => ({ ...p, email: e.target.value }))} className={inputCls} />
                <input type="password" placeholder={t("profile.password")} value={linkEmailForm.password} onChange={e => setLinkEmailForm(p => ({ ...p, password: e.target.value }))} className={inputCls} />
                <input type="password" placeholder={t("profile.confirm_password")} value={linkEmailForm.confirm} onChange={e => setLinkEmailForm(p => ({ ...p, confirm: e.target.value }))} className={inputCls} />
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
          <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">
            {t("profile.notifications")}
          </p>
          <div className="flex items-center justify-between mb-3">
            <span className="text-text-muted text-sm">{t("profile.daily_horoscope")}</span>
            <button
              onClick={() => handleToggleNotif(!notifEnabled)}
              className="w-10 h-5 rounded-full transition-colors relative"
              style={{ background: notifEnabled ? "#6B4EFF" : "rgba(107,78,255,0.2)" }}
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
        </Card>

        {/* Settings */}
        <Card>
          <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">
            {t("profile.settings")}
          </p>

          <div className="flex items-center justify-between mb-4">
            <span className="text-text-muted text-sm">{t("profile.language")}</span>
            <div className="flex rounded-xl overflow-hidden border border-border-subtle">
              {(["ru", "en"] as const).map(l => (
                <button
                  key={l}
                  onClick={() => handleLang(l)}
                  className="px-4 py-1.5 text-xs font-sans transition-colors"
                  style={{
                    background: lang === l ? "#6B4EFF" : "transparent",
                    color: lang === l ? "#fff" : "#9B8FBB",
                  }}
                >
                  {l.toUpperCase()}
                </button>
              ))}
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
              <span className="text-xs text-violet-400">✓ Telegram</span>
            </div>
          ) : (
            <Button variant="ghost" size="sm" className="w-full" onClick={logout}>
              {t("profile.logout")}
            </Button>
          )}
        </Card>

      </main>

      {/* Toast overlay */}
      {toast && (
        <div className="fixed top-14 left-0 right-0 flex justify-center pointer-events-none" style={{ zIndex: 50 }}>
          <span className="text-xs px-4 py-2 rounded-full" style={{ background: "rgba(107,78,255,0.2)", border: "0.5px solid rgba(107,78,255,0.4)", color: "#C9A84C" }}>
            {toast}
          </span>
        </div>
      )}

      <BottomNav active="profile" onNavigate={onNavigate} />

      <PaywallSheet open={showPaywall} onClose={() => setShowPaywall(false)} />
    </div>
  );
}
