import { useEffect, useRef, useState } from "react";
import { BottomNav, Button, Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { streamRequest } from "../utils/api";

interface NatalChartProps {
  onNavigate: (page: string) => void;
}

interface Planet {
  sign: string;
  degree?: number;
}

interface NatalResult {
  sun: Planet;
  moon: Planet;
  rising: Planet;
  mercury: Planet;
  venus: Planet;
  mars: Planet;
}

export function NatalChart({ onNavigate }: NatalChartProps) {
  const { token } = useAuth();
  const [step, setStep] = useState<"form" | "result">("form");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [saveToProfile, setSaveToProfile] = useState(true);
  const [form, setForm] = useState({
    name: "", day: "", month: "", year: "",
    hour: "", minute: "", city: "",
  });
  const [result, setResult] = useState<NatalResult | null>(null);
  const [interpretation, setInterpretation] = useState("");
  const [interpretLoading, setInterpretLoading] = useState(false);

  const profileLoaded = useRef(false);

  useEffect(() => {
    if (profileLoaded.current || !token) return;
    profileLoaded.current = true;

    fetch("/api/v1/profile", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(r => r.json())
      .then(data => {
        if (data.birth_date || data.birth_city) {
          const [y, m, d] = (data.birth_date ?? "").split("-");
          const [h, min] = (data.birth_time ?? "").split(":");
          setForm(prev => ({
            name:   data.birth_name  || prev.name,
            year:   y    || prev.year,
            month:  m    || prev.month,
            day:    d    || prev.day,
            hour:   h    || prev.hour,
            minute: min  || prev.minute,
            city:   data.birth_city  || prev.city,
          }));
        }
      })
      .catch(() => {});
  }, [token]);

  const setField = (field: string) =>
    (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm(prev => ({ ...prev, [field]: e.target.value }));

  const buildBody = () => ({
    name: form.name,
    year: parseInt(form.year),
    month: parseInt(form.month),
    day: parseInt(form.day),
    hour: parseInt(form.hour || "12"),
    minute: parseInt(form.minute || "0"),
    city: form.city,
    lang: "ru",
  });

  async function handleCalculate() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/v1/natal/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildBody()),
      });
      if (!res.ok) throw new Error();
      setResult(await res.json());
      setStep("result");

      if (saveToProfile && token) {
        const b = buildBody();
        const profileBody: Record<string, unknown> = {
          birth_city: b.city,
          birth_name: b.name,
          birth_date: `${b.year}-${String(b.month).padStart(2, "0")}-${String(b.day).padStart(2, "0")}`,
        };
        if (form.hour) {
          profileBody.birth_time = `${String(b.hour).padStart(2, "0")}:${String(b.minute).padStart(2, "0")}`;
          profileBody.birth_time_known = true;
        }
        fetch("/api/v1/profile", {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(profileBody),
        }).catch(() => {});
      }
    } catch {
      setError("Не удалось рассчитать карту. Проверь данные.");
    } finally {
      setLoading(false);
    }
  }

  async function handleInterpret() {
    if (interpretLoading) return;
    setInterpretLoading(true);
    setInterpretation("");
    await streamRequest(
      "/natal/interpret",
      buildBody(),
      (chunk) => setInterpretation(prev => prev + chunk),
      () => setInterpretLoading(false),
    ).catch(() => {
      setInterpretation("Ошибка соединения. Попробуй ещё раз.");
      setInterpretLoading(false);
    });
  }

  const inputCls =
    "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 " +
    "text-text-primary text-sm placeholder:text-text-faint " +
    "focus:outline-none focus:border-violet-600 transition-colors";

  const canSubmit = form.name && form.day && form.month && form.year && form.city;

  return (
    <div className="flex flex-col min-h-screen bg-bg-deep max-w-[390px] mx-auto relative">
      <header
        className="flex items-center justify-between px-4 shrink-0 backdrop-blur-sm"
        style={{ height: 46, background: "rgba(6,4,20,0.75)" }}
      >
        <button
          className="text-text-muted text-lg w-8"
          onClick={() => step === "result" ? setStep("form") : onNavigate("home")}
        >
          ‹
        </button>
        <span className="font-display text-text-primary text-base tracking-widest">
          ✦ Натальная карта
        </span>
        <div className="w-8" />
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-6 pb-24">
        {step === "form" ? (
          <div className="flex flex-col gap-3">
            <p className="text-text-muted text-xs text-center mb-1">
              Введи данные рождения для расчёта карты
            </p>

            <input
              className={inputCls}
              placeholder="Имя"
              value={form.name}
              onChange={setField("name")}
            />

            <div className="grid grid-cols-3 gap-2">
              <input className={inputCls} placeholder="День"   type="number" min="1"    max="31"   value={form.day}   onChange={setField("day")} />
              <input className={inputCls} placeholder="Месяц"  type="number" min="1"    max="12"   value={form.month} onChange={setField("month")} />
              <input className={inputCls} placeholder="Год"    type="number" min="1900" max="2025" value={form.year}  onChange={setField("year")} />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <input className={inputCls} placeholder="Час (0–23)" type="number" min="0" max="23" value={form.hour}   onChange={setField("hour")} />
              <input className={inputCls} placeholder="Минуты"     type="number" min="0" max="59" value={form.minute} onChange={setField("minute")} />
            </div>

            <input
              className={inputCls}
              placeholder="Город рождения"
              value={form.city}
              onChange={setField("city")}
            />

            <p className="text-text-faint text-[10px] text-center">
              Время влияет на точность Асцендента
            </p>

            <label className="flex items-center gap-2 cursor-pointer self-start">
              <input
                type="checkbox"
                checked={saveToProfile}
                onChange={e => setSaveToProfile(e.target.checked)}
                className="w-3.5 h-3.5 accent-violet-600"
              />
              <span className="text-text-muted text-xs">Сохранить в профиль</span>
            </label>

            {error && (
              <p className="text-red-400 text-xs text-center">{error}</p>
            )}

            <Button
              variant="primary"
              className="w-full mt-1"
              onClick={handleCalculate}
              disabled={loading || !canSubmit}
            >
              {loading ? "Расчёт..." : "Рассчитать карту ✦"}
            </Button>
          </div>
        ) : result ? (
          <div className="flex flex-col gap-4">
            <Card>
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">
                Большая тройка
              </p>
              <div className="flex flex-col gap-2.5">
                {[
                  { icon: "☀️", label: "Солнце",    planet: result.sun },
                  { icon: "🌙", label: "Луна",       planet: result.moon },
                  { icon: "⬆️", label: "Асцендент", planet: result.rising },
                ].map(({ icon, label, planet }) => (
                  <div key={label} className="flex items-center justify-between">
                    <span className="text-text-muted text-sm">{icon} {label}</span>
                    <span className="font-display text-sm" style={{ color: "#C9A84C" }}>
                      {planet.sign}
                      {planet.degree !== undefined && (
                        <span className="text-text-faint text-xs ml-1">{planet.degree}°</span>
                      )}
                    </span>
                  </div>
                ))}
              </div>
            </Card>

            <Card>
              <p className="text-text-faint text-[9px] uppercase tracking-widest mb-3">
                Планеты
              </p>
              <div className="flex flex-col gap-2.5">
                {[
                  { label: "Меркурий ☿", planet: result.mercury },
                  { label: "Венера ♀",   planet: result.venus },
                  { label: "Марс ♂",     planet: result.mars },
                ].map(({ label, planet }) => (
                  <div key={label} className="flex items-center justify-between">
                    <span className="text-text-muted text-sm">{label}</span>
                    <span className="text-text-primary text-sm">{planet.sign}</span>
                  </div>
                ))}
              </div>
            </Card>

            {interpretation ? (
              <Card>
                <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">
                  Интерпретация
                </p>
                <p className="text-text-muted text-xs leading-relaxed">
                  {interpretation}
                  {interpretLoading && <span className="animate-pulse">▍</span>}
                </p>
              </Card>
            ) : (
              <Button
                variant="primary"
                className="w-full"
                onClick={handleInterpret}
                disabled={interpretLoading}
              >
                {interpretLoading ? "Читаю карту..." : "Получить интерпретацию ✦"}
              </Button>
            )}
          </div>
        ) : null}
      </main>

      <BottomNav active="natal" onNavigate={onNavigate} />
    </div>
  );
}
