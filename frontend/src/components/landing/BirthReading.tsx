import { useState } from "react";
import { getZodiacSign } from "../../utils/zodiac";
import { ArrowRightIcon, ZodiacIcon } from "../icons/AstroIcons";

/**
 * Life path number.
 *
 * Mirrors `backend/app/data/numerology.py::reduce` exactly, master numbers
 * included — 11, 22 and 33 are never reduced further. If the two ever drift,
 * a visitor gets one number on the landing and a different one inside the
 * app for the same birth date.
 */
function lifePath(iso: string): number {
  let n = iso.replace(/-/g, "").split("").reduce((sum, d) => sum + Number(d), 0);
  while (n > 9 && n !== 11 && n !== 22 && n !== 33) {
    n = String(n).split("").reduce((sum, d) => sum + Number(d), 0);
  }
  return n;
}

const SIGN_META: Record<string, { element: string; modality: string; dates: string; ru: string; en: string }> = {
  Aries:       { element: "fire",  modality: "cardinal", dates: "21.03 – 19.04", ru: "Первопроходец: начинаете там, где другие ещё раздумывают.", en: "The initiator: you start where others are still deliberating." },
  Taurus:      { element: "earth", modality: "fixed",    dates: "20.04 – 20.05", ru: "Опора: цените надёжность и доводите начатое до конца.", en: "The anchor: you value solidity and finish what you begin." },
  Gemini:      { element: "air",   modality: "mutable",  dates: "21.05 – 20.06", ru: "Связной: быстро схватываете и легко соединяете несоединимое.", en: "The connector: quick to grasp, quick to link the unlinkable." },
  Cancer:      { element: "water", modality: "cardinal", dates: "21.06 – 22.07", ru: "Хранитель: чувствуете настроение раньше, чем его произнесут.", en: "The keeper: you read a mood before anyone names it." },
  Leo:         { element: "fire",  modality: "fixed",    dates: "23.07 – 22.08", ru: "Центр: вам естественно быть тем, вокруг кого собираются.", en: "The centre: being the one others gather around comes naturally." },
  Virgo:       { element: "earth", modality: "mutable",  dates: "23.08 – 22.09", ru: "Мастер деталей: видите то, что остальные пролистывают.", en: "The craftsman: you see what everyone else scrolls past." },
  Libra:       { element: "air",   modality: "cardinal", dates: "23.09 – 22.10", ru: "Равновесие: ищете справедливое решение, а не удобное.", en: "The balance: you look for the fair answer, not the easy one." },
  Scorpio:     { element: "water", modality: "fixed",    dates: "23.10 – 21.11", ru: "Глубина: вас не устраивают поверхностные объяснения.", en: "The depth: surface explanations never satisfy you." },
  Sagittarius: { element: "fire",  modality: "mutable",  dates: "22.11 – 21.12", ru: "Странник: вам нужен горизонт, а не потолок.", en: "The wanderer: you need a horizon, not a ceiling." },
  Capricorn:   { element: "earth", modality: "cardinal", dates: "22.12 – 19.01", ru: "Стратег: играете вдолгую и почти всегда доходите.", en: "The strategist: you play long and almost always arrive." },
  Aquarius:    { element: "air",   modality: "fixed",    dates: "20.01 – 18.02", ru: "Иначе мыслящий: правила для вас — материал, а не закон.", en: "The outlier: rules are material to you, not law." },
  Pisces:      { element: "water", modality: "mutable",  dates: "19.02 – 20.03", ru: "Проводник: чувствуете подтекст там, где другие слышат слова.", en: "The channel: you sense subtext where others hear only words." },
};

const ELEMENT_LABEL: Record<string, { ru: string; en: string; color: string }> = {
  fire:  { ru: "Огонь", en: "Fire",  color: "#C95050" },
  earth: { ru: "Земля", en: "Earth", color: "#6E9A8A" },
  air:   { ru: "Воздух", en: "Air",  color: "#8A7FC0" },
  water: { ru: "Вода",  en: "Water", color: "#4B7CB5" },
};

const MODALITY_LABEL: Record<string, { ru: string; en: string }> = {
  cardinal: { ru: "Кардинальный", en: "Cardinal" },
  fixed:    { ru: "Фиксированный", en: "Fixed" },
  mutable:  { ru: "Мутабельный", en: "Mutable" },
};

const LIFE_PATH: Record<number, { ru: { k: string; t: string }; en: { k: string; t: string } }> = {
  1:  { ru: { k: "Лидер",     t: "Ваш путь — идти первым и брать ответственность за направление." },  en: { k: "Leader",    t: "Your path is to go first and own the direction." } },
  2:  { ru: { k: "Дипломат",  t: "Ваша сила — в союзе: вы соединяете людей, которые без вас не сошлись бы." }, en: { k: "Diplomat",  t: "Your strength is partnership: you join people who would not meet otherwise." } },
  3:  { ru: { k: "Творец",    t: "Вам дано выражать — словом, образом, идеей. Молчание вам дорого стоит." }, en: { k: "Creator",   t: "You are meant to express — in word, image, idea. Silence costs you." } },
  4:  { ru: { k: "Строитель", t: "Вы создаёте то, что стоит долго. Основательность — не скучность, а ваш метод." }, en: { k: "Builder",   t: "You make things that last. Thoroughness is your method, not your limit." } },
  5:  { ru: { k: "Свобода",   t: "Перемены для вас — топливо. Любая клетка, даже золотая, гасит вас." },  en: { k: "Freedom",   t: "Change is your fuel. Any cage, even a gilded one, dims you." } },
  6:  { ru: { k: "Забота",    t: "Ваш путь связан с домом, гармонией и ответственностью за близких." }, en: { k: "Care",      t: "Your path runs through home, harmony and responsibility for others." } },
  7:  { ru: { k: "Искатель",  t: "Вам нужно понять, а не поверить. Одиночество для вас — рабочий инструмент." }, en: { k: "Seeker",    t: "You need to understand, not believe. Solitude is a working tool for you." } },
  8:  { ru: { k: "Власть",    t: "Ваша тема — масштаб и ресурс. Вы умеете превращать замысел в структуру." }, en: { k: "Power",     t: "Your theme is scale and resource. You turn intent into structure." } },
  9:  { ru: { k: "Служение",  t: "Вы мыслите шире личной выгоды — и именно там находите себя." },     en: { k: "Service",   t: "You think past personal gain — and that is exactly where you find yourself." } },
  11: { ru: { k: "Провидец",  t: "Мастер-число. Обострённая интуиция и способность вести за собой примером." }, en: { k: "Visionary", t: "A master number. Heightened intuition and the pull of leading by example." } },
  22: { ru: { k: "Мастер",    t: "Мастер-число. Вы способны воплощать в материи то, что другие только представляют." }, en: { k: "Master builder", t: "A master number. You can build in matter what others only picture." } },
  33: { ru: { k: "Учитель",   t: "Мастер-число. Редкий путь наставничества и безусловной отдачи." },   en: { k: "Teacher",   t: "A master number. The rare path of mentorship and unconditional giving." } },
};

interface Props { ru: boolean; onOpenApp: () => void; }

export function BirthReading({ ru, onOpenApp }: Props) {
  const [date, setDate] = useState("");
  const [result, setResult] = useState<{ iso: string } | null>(null);
  const [error, setError] = useState("");

  const today = new Date().toISOString().slice(0, 10);

  function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!date) { setError(ru ? "Укажите дату рождения" : "Enter your birth date"); return; }
    const year = Number(date.slice(0, 4));
    if (date > today) { setError(ru ? "Дата в будущем" : "That date is in the future"); return; }
    if (year < 1900) { setError(ru ? "Проверьте год рождения" : "Check the year"); return; }
    setError("");
    setResult({ iso: date });
  }

  const zodiac = result ? getZodiacSign(result.iso) : null;
  const meta = zodiac ? SIGN_META[zodiac.en] : null;
  const lp = result ? lifePath(result.iso) : null;
  const lpCopy = lp !== null ? LIFE_PATH[lp] : null;

  return (
    <div style={{
      padding: 30, borderRadius: 24,
      background: "linear-gradient(160deg,rgba(255,255,255,.055),rgba(255,255,255,.015))",
      border: "1px solid rgba(201,168,76,.2)", backdropFilter: "blur(12px)",
    }}>
      <form onSubmit={submit} style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "flex-start" }}>
        <div style={{ flex: "1 1 200px", minWidth: 180 }}>
          <label htmlFor="lp-birth" className="font-cinzel uppercase" style={{ display: "block", fontSize: 10.5, letterSpacing: ".24em", color: "#C9A84C", marginBottom: 8 }}>
            {ru ? "Дата рождения" : "Birth date"}
          </label>
          <input
            id="lp-birth" type="date" value={date} max={today} min="1900-01-01"
            onChange={e => { setDate(e.target.value); setError(""); }}
            style={{
              width: "100%", height: 50, padding: "0 14px", borderRadius: 13,
              background: "rgba(255,255,255,.04)", border: "1px solid rgba(201,168,76,.28)",
              color: "#F0E9DA", fontSize: 15, fontFamily: "Inter, sans-serif",
              // Without this the native date picker renders its own light
              // chrome — a white panel dropped onto the dark page.
              colorScheme: "dark",
            }}
          />
        </div>
        <button type="submit" style={{
          height: 50, marginTop: 26, padding: "0 24px", borderRadius: 13, border: "none",
          display: "inline-flex", alignItems: "center", gap: 8,
          background: "linear-gradient(100deg,#A9882F,#C9A84C 50%,#E8CD7E)", color: "#1A1206",
          fontWeight: 600, fontSize: 14.5, cursor: "pointer", whiteSpace: "nowrap",
          boxShadow: "0 14px 34px -12px rgba(201,168,76,.55)",
        }}>
          {ru ? "Узнать" : "Reveal"}
          <ArrowRightIcon size={17} strokeWidth={1.7} />
        </button>
      </form>

      {error && <p style={{ fontSize: 13, color: "#D98A8A", marginTop: 10 }}>{error}</p>}

      {result && zodiac && meta && lpCopy && lp !== null && (
        <div key={result.iso} style={{ marginTop: 26, animation: "mystral-fadeup .5s ease-out" }}>
          <div className="lp-result" style={{ display: "grid", gap: 18 }}>
            <style>{`
              .lp-result { grid-template-columns: 1fr; }
              @media (min-width: 720px) { .lp-result { grid-template-columns: 1fr 1fr; } }
            `}</style>

            {/* Sign */}
            <div style={{ padding: 20, borderRadius: 18, background: "rgba(201,168,76,.06)", border: "1px solid rgba(201,168,76,.2)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                <span style={{ color: "#E8CD7E", filter: "drop-shadow(0 0 14px rgba(201,168,76,.5))", display: "flex" }}>
                  <ZodiacIcon sign={zodiac.en} size={42} strokeWidth={1.3} />
                </span>
                <div>
                  <span className="font-cinzel uppercase" style={{ fontSize: 9.5, letterSpacing: ".26em", color: "#C9A84C" }}>
                    {ru ? "Ваш знак" : "Your sign"}
                  </span>
                  <p className="font-cormorant" style={{ fontSize: 27, color: "#F0E9DA", lineHeight: 1.1 }}>
                    {ru ? zodiac.sign : zodiac.en}
                  </p>
                </div>
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 14 }}>
                <Chip color={ELEMENT_LABEL[meta.element].color}>
                  {ru ? ELEMENT_LABEL[meta.element].ru : ELEMENT_LABEL[meta.element].en}
                </Chip>
                <Chip>{ru ? MODALITY_LABEL[meta.modality].ru : MODALITY_LABEL[meta.modality].en}</Chip>
                <Chip>{meta.dates}</Chip>
              </div>
              <p style={{ fontSize: 14, lineHeight: 1.65, color: "#B6AC98", marginTop: 14 }}>
                {ru ? meta.ru : meta.en}
              </p>
            </div>

            {/* Life path */}
            <div style={{ padding: 20, borderRadius: 18, background: "rgba(75,60,134,.14)", border: "1px solid rgba(138,127,192,.26)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                <span className="font-cormorant" style={{
                  width: 52, height: 52, flexShrink: 0, borderRadius: "50%",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 26, color: "#0C0A18",
                  background: "linear-gradient(135deg,#A99BE0,#C9A84C)",
                }}>{lp}</span>
                <div>
                  <span className="font-cinzel uppercase" style={{ fontSize: 9.5, letterSpacing: ".26em", color: "#A99BE0" }}>
                    {ru ? "Число судьбы" : "Life path"}
                  </span>
                  <p className="font-cormorant" style={{ fontSize: 27, color: "#F0E9DA", lineHeight: 1.1 }}>
                    {ru ? lpCopy.ru.k : lpCopy.en.k}
                  </p>
                </div>
              </div>
              <p style={{ fontSize: 14, lineHeight: 1.65, color: "#B6AC98", marginTop: 14 }}>
                {ru ? lpCopy.ru.t : lpCopy.en.t}
              </p>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap", marginTop: 20 }}>
            <button onClick={onOpenApp} style={{
              height: 48, padding: "0 24px", borderRadius: 14, border: "none",
              display: "inline-flex", alignItems: "center", gap: 8,
              background: "linear-gradient(100deg,#A9882F,#C9A84C 50%,#E8CD7E)", color: "#1A1206",
              fontWeight: 600, fontSize: 14.5, cursor: "pointer",
              boxShadow: "0 14px 34px -12px rgba(201,168,76,.55)",
            }}>
              {ru ? "Полный разбор" : "Full reading"}
              <ArrowRightIcon size={17} strokeWidth={1.7} />
            </button>
            <p style={{ fontSize: 12.5, color: "#8A8170", maxWidth: 340, lineHeight: 1.55 }}>
              {ru
                ? "Это верхушка. С временем и местом рождения приложение строит натальную карту с домами и аспектами."
                : "This is the surface. With birth time and place the app builds a natal chart with houses and aspects."}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function Chip({ children, color }: { children: React.ReactNode; color?: string }) {
  return (
    <span style={{
      fontSize: 11.5, padding: "4px 11px", borderRadius: 99,
      background: color ? `${color}1F` : "rgba(255,255,255,.05)",
      border: `1px solid ${color ? `${color}59` : "rgba(255,255,255,.1)"}`,
      color: color ?? "#A89E8B",
    }}>
      {children}
    </span>
  );
}
