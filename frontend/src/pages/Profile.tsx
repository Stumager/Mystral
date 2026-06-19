import { useEffect, useRef, useState } from "react";
import { PaywallSheet } from "../components/PaywallSheet";
import { BottomNav, Button, Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";

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
}

function getZodiacSign(dateStr: string): string {
  const [, m, d] = dateStr.split("-").map(Number);
  if ((m === 3 && d >= 21) || (m === 4 && d <= 19)) return "Овен";
  if ((m === 4 && d >= 20) || (m === 5 && d <= 20)) return "Телец";
  if ((m === 5 && d >= 21) || (m === 6 && d <= 20)) return "Близнецы";
  if ((m === 6 && d >= 21) || (m === 7 && d <= 22)) return "Рак";
  if ((m === 7 && d >= 23) || (m === 8 && d <= 22)) return "Лев";
  if ((m === 8 && d >= 23) || (m === 9 && d <= 22)) return "Дева";
  if ((m === 9 && d >= 23) || (m === 10 && d <= 22)) return "Весы";
  if ((m === 10 && d >= 23) || (m === 11 && d <= 21)) return "Скорпион";
  if ((m === 11 && d >= 22) || (m === 12 && d <= 21)) return "Стрелец";
  if ((m === 12 && d >= 22) || (m === 1 && d <= 19)) return "Козерог";
  if ((m === 1 && d >= 20) || (m === 2 && d <= 18)) return "Водолей";
  return "Рыбы";
}

const PROGRESS_HINTS = [
  "Добавь дату → получи базовый гороскоп",
  "Добавь время → точный Асцендент",
  "Добавь город → натальная карта",
  "Добавь имя → персональные предсказания",
];

const BOT_ID = "8998390466";

export function Profile({ onNavigate }: ProfilePageProps) {
  const { user, token, logout } = useAuth();
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

  const setField = (field: string) =>
    (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm(prev => ({ ...prev, [field]: e.target.value }));

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
      })
      .catch(() => {});
  }, [token]);

  async function handleSave() {
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
      showToast("Сохранено ✦");
    } catch {
      showToast("Ошибка сохранения");
    } finally {
      setSaving(false);
    }
  }

  async function handleLang(newLang: string) {
    setLang(newLang);
    await fetch("/api/v1/profile", {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify({ lang: newLang }),
    }).catch(() => {});
  }

  async function handleLinkEmail() {
    if (linkEmailForm.password !== linkEmailForm.confirm) {
      setLinkEmailError("Пароли не совпадают");
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
      if (!res.ok) throw new Error(data.detail || "Ошибка");
      setProviders(p => [...p, "email"]);
      setShowLinkEmail(false);
      setLinkEmailForm({ email: "", password: "", confirm: "" });
      showToast("Email привязан ✦");
    } catch (e: unknown) {
      setLinkEmailError(e instanceof Error ? e.message : "Ошибка");
    } finally {
      setLinkingEmail(false);
    }
  }

  function handleTelegramWebLogin() {
    const origin = encodeURIComponent(window.location.origin);
    const url = `https://oauth.telegram.org/auth?bot_id=${BOT_ID}&origin=${origin}&request_access=write&embed=1`;
    const popup = window.open(url, "_blank", "width=550,height=450,popup");
    if (!popup) { showToast("Popup заблокирован"); return; }

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
        if (!res.ok) throw new Error(json.detail || "Ошибка");
        setProviders(p => [...p, "telegram"]);
        showToast("Telegram привязан ✦");
      } catch (e: unknown) {
        showToast(e instanceof Error ? e.message : "Ошибка привязки");
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

  const inputCls =
    "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 " +
    "text-text-primary text-sm placeholder:text-text-faint " +
    "focus:outline-none focus:border-violet-600 transition-colors";

  const firstLetter = (user?.name ?? "?")[0]?.toUpperCase() ?? "?";
  const zodiac = form.year && form.month && form.day
    ? getZodiacSign(`${form.year}-${form.month.padStart(2, "0")}-${form.day.padStart(2, "0")}`)
    : null;

  const hintIndex = Math.floor(completion / 25);
  const hint = completion < 100 ? PROGRESS_HINTS[hintIndex] ?? PROGRESS_HINTS[3] : "Профиль заполнен полностью ✦";

  return (
    <div className="flex flex-col min-h-screen bg-bg-deep max-w-[390px] mx-auto relative">
      <header
        className="flex items-center justify-between px-4 shrink-0 backdrop-blur-sm"
        style={{ height: 46, background: "rgba(6,4,20,0.75)" }}
      >
        <div className="w-8" />
        <span className="font-display text-text-primary text-base tracking-widest">
          ✦ Профиль
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
            {user?.name ?? "Гость"}
          </p>
          {zodiac && (
            <p className="text-text-faint text-xs">{zodiac}</p>
          )}
        </div>

        {/* Progress */}
        <Card>
          <div className="flex items-center justify-between mb-2">
            <p className="text-text-muted text-xs">Профиль заполнен на</p>
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
            Данные рождения
          </p>
          <div className="flex flex-col gap-3">
            <div className="grid grid-cols-3 gap-2">
              <input className={inputCls} placeholder="День"   type="number" min="1"    max="31"   value={form.day}   onChange={setField("day")} />
              <input className={inputCls} placeholder="Месяц"  type="number" min="1"    max="12"   value={form.month} onChange={setField("month")} />
              <input className={inputCls} placeholder="Год"    type="number" min="1900" max="2025" value={form.year}  onChange={setField("year")} />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <input className={inputCls} placeholder="Час (0–23)"   type="number" min="0" max="23" value={form.hour}   onChange={setField("hour")} />
              <input className={inputCls} placeholder="Минуты"       type="number" min="0" max="59" value={form.minute} onChange={setField("minute")} />
            </div>
            <input className={inputCls} placeholder="Город рождения" value={form.city} onChange={setField("city")} />
            <input className={inputCls} placeholder="Имя при рождении" value={form.name} onChange={setField("name")} />
          </div>

          <Button
            variant="primary"
            className="w-full mt-4"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? "Сохранение..." : "Сохранить"}
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
            <div className="flex items-center gap-2">
              <span className="font-display text-sm" style={{ color: "#C9A84C" }}>✦</span>
              <p className="font-display text-sm text-text-primary">Mystral Pro активен</p>
            </div>
            <p className="text-text-faint text-[10px] mt-1">Безлимитный доступ ко всем функциям</p>
          </Card>
        ) : (
          <Card>
            <p className="text-text-muted text-xs mb-3">
              Бесплатный план · 1 расклад/день
            </p>
            <Button
              variant="gold"
              size="sm"
              className="w-full"
              onClick={() => setShowPaywall(true)}
            >
              Перейти на Pro ✦
            </Button>
          </Card>
        )}

        {/* Linked accounts */}
        <Card>
          <p className="text-text-faint text-[9px] uppercase tracking-widest mb-4">
            Связанные аккаунты
          </p>

          {/* Email row */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-text-muted text-sm">Email</span>
                {providers.includes("email") && (
                  <span
                    className="text-[10px] px-2 py-0.5 rounded-full"
                    style={{ background: "rgba(107,78,255,0.15)", color: "#9B8AFF" }}
                  >
                    Привязан
                  </span>
                )}
              </div>
              {!providers.includes("email") && !showLinkEmail && (
                <button
                  onClick={() => setShowLinkEmail(true)}
                  className="text-xs"
                  style={{ color: "#9B8AFF" }}
                >
                  Добавить
                </button>
              )}
            </div>

            {showLinkEmail && (
              <div className="flex flex-col gap-2">
                <input
                  type="email"
                  placeholder="Email"
                  value={linkEmailForm.email}
                  onChange={e => setLinkEmailForm(p => ({ ...p, email: e.target.value }))}
                  className={inputCls}
                />
                <input
                  type="password"
                  placeholder="Пароль"
                  value={linkEmailForm.password}
                  onChange={e => setLinkEmailForm(p => ({ ...p, password: e.target.value }))}
                  className={inputCls}
                />
                <input
                  type="password"
                  placeholder="Повторите пароль"
                  value={linkEmailForm.confirm}
                  onChange={e => setLinkEmailForm(p => ({ ...p, confirm: e.target.value }))}
                  className={inputCls}
                />
                {linkEmailError && (
                  <p className="text-red-400 text-xs">{linkEmailError}</p>
                )}
                <div className="flex gap-2">
                  <Button
                    variant="primary"
                    size="sm"
                    className="flex-1"
                    onClick={handleLinkEmail}
                    disabled={linkingEmail}
                  >
                    {linkingEmail ? "..." : "Сохранить"}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="flex-1"
                    onClick={() => {
                      setShowLinkEmail(false);
                      setLinkEmailForm({ email: "", password: "", confirm: "" });
                      setLinkEmailError("");
                    }}
                  >
                    Отмена
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* Telegram row */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-text-muted text-sm">Telegram</span>
              {providers.includes("telegram") && (
                <span
                  className="text-[10px] px-2 py-0.5 rounded-full"
                  style={{ background: "rgba(41,182,246,0.12)", color: "#29B6F6" }}
                >
                  Привязан
                </span>
              )}
            </div>
            {!providers.includes("telegram") && (
              <button
                onClick={handleTelegramWebLogin}
                className="text-xs"
                style={{ color: "#29B6F6" }}
              >
                Привязать
              </button>
            )}
          </div>
        </Card>

        {/* Settings */}
        <Card>
          <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">
            Настройки
          </p>

          <div className="flex items-center justify-between mb-4">
            <span className="text-text-muted text-sm">Язык</span>
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
            className="w-full"
            onClick={logout}
          >
            Выйти
          </Button>
        </Card>

      </main>

      {/* Toast overlay */}
      {toast && (
        <div
          className="fixed top-14 left-0 right-0 flex justify-center pointer-events-none"
          style={{ zIndex: 50 }}
        >
          <span
            className="text-xs px-4 py-2 rounded-full"
            style={{
              background: "rgba(107,78,255,0.2)",
              border: "0.5px solid rgba(107,78,255,0.4)",
              color: "#C9A84C",
            }}
          >
            {toast}
          </span>
        </div>
      )}

      <BottomNav active="profile" onNavigate={onNavigate} />

      <PaywallSheet
        open={showPaywall}
        onClose={() => setShowPaywall(false)}
      />
    </div>
  );
}
