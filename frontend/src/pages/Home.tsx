import { useEffect, useRef, useState } from "react";
import { ZodiacOrb } from "../components/three/ZodiacOrb";
import { BottomNav, Card } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { streamRequest } from "../utils/api";

interface HomeProps {
  onNavigate: (page: string) => void;
}

const tools = [
  { id: "tarot",  icon: "🃏", label: "Карты Таро" },
  { id: "moon",   icon: "🌙", label: "Лунный день" },
  { id: "natal",  icon: "🌟", label: "Натальная" },
  { id: "compat", icon: "💑", label: "Совместимость" },
  { id: "numero", icon: "🔢", label: "Нумерология" },
  { id: "runes",  icon: "ᚱ",  label: "Руны" },
];

export function Home({ onNavigate }: HomeProps) {
  const { user } = useAuth();
  const [horoscope, setHoroscope] = useState("");
  const [horoscopeLoading, setHoroscopeLoading] = useState(true);

  const called = useRef(false);

  useEffect(() => {
    if (called.current) return;
    called.current = true;

    streamRequest(
      "/horoscope/stream",
      { sign: "scorpio", lang: "ru", date: new Date().toISOString().slice(0, 10) },
      (chunk) => setHoroscope(prev => prev + chunk),
      () => setHoroscopeLoading(false)
    ).catch(() => {
      setHoroscope("Звёзды временно недоступны. Попробуй позже.");
      setHoroscopeLoading(false);
    });
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-bg-deep max-w-[390px] mx-auto relative overflow-hidden">

      <header
        className="flex items-center justify-between px-4 shrink-0 backdrop-blur-sm"
        style={{ height: 46, background: "rgba(6,4,20,0.75)" }}
      >
        <button className="text-text-muted text-lg w-8">‹</button>
        <span className="font-display text-text-primary text-base tracking-widest">✦ Mystral</span>
        <div className="w-8 flex justify-end">
          <span className="w-2 h-2 rounded-full bg-violet-600 animate-pulse" />
        </div>
      </header>

      <main className="flex-1 overflow-y-auto px-4 pt-4 pb-20">

        <div className="mb-4">
          <p className="text-text-faint text-xs uppercase tracking-widest mb-1">
            Добрый вечер
          </p>
          <p className="text-text-primary font-display text-2xl font-light">
            {user?.name ?? "Гость"} ✨
          </p>
          <p className="text-text-muted text-xs mt-1">
            Скорпион · 11-й лунный день
          </p>
        </div>

        <div className="flex justify-center mb-5">
          <ZodiacOrb sign="Скорпион" symbol="♏" />
        </div>

        <Card className="mb-4 relative overflow-hidden">
          <p className="text-text-faint text-[9px] uppercase tracking-widest mb-2">
            {new Date().toLocaleDateString("ru-RU", { day: "numeric", month: "long", year: "numeric" })} · Гороскоп дня
          </p>
          {horoscopeLoading && !horoscope
            ? <p className="text-text-muted text-xs animate-pulse">Звёзды говорят...</p>
            : <p className="text-text-muted text-xs leading-relaxed">
                {horoscope}
                {horoscopeLoading && <span className="animate-pulse">▍</span>}
              </p>
          }
          <span className="absolute top-3 right-3 text-[9px] px-2 py-0.5
            rounded-full bg-violet-600/10 text-violet-400 border
            border-violet-600/20">AI</span>
        </Card>

        <div className="grid grid-cols-3 gap-2">
          {tools.map(tool => (
            <Card
              key={tool.id}
              className="flex flex-col items-center py-3 px-1 gap-1
                cursor-pointer hover:border-border-medium transition-all
                active:scale-95"
              onClick={() => onNavigate(tool.id)}
            >
              <span className="text-2xl">{tool.icon}</span>
              <span className="text-text-muted text-[10px] text-center leading-tight">
                {tool.label}
              </span>
            </Card>
          ))}
        </div>

      </main>

      <BottomNav active="home" onNavigate={onNavigate} />
    </div>
  );
}
