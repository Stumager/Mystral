import { useEffect, useRef, useState } from "react";
import { Button } from "./ui";
import { apiRequest } from "../utils/api";
import { validateDay, validateMonth, validateYear, validateDateExists } from "../utils/validate";

export interface Partner {
  id: string; name: string; birth_date: string;
  zodiac_sign: string; zodiac_sign_ru: string; zodiac_symbol: string;
  has_time: boolean; has_city: boolean;
}

interface PartnerPickerProps {
  token: string | null;
  lang: string;
  onSelect: (partner: Partner) => void;
  // Hitting the free 3-partner cap surfaces the host page's own
  // PaywallSheet rather than a plain-text fallback here — this component
  // doesn't mount one itself, so both host pages keep the real upgrade CTA
  // exactly as before the extraction, not a degraded copy of it.
  onPaywall: () => void;
}

// TZ-119: extracted out of Compatibility.tsx's inline "step === partners"
// block, unchanged in behavior, so the Matrix Compatibility module (TZ-118)
// reuses the exact same partner list/add/delete UI instead of building a
// second selector — the ticket's explicit ask, not a stylistic preference.
export function PartnerPicker({ token, lang, onSelect, onPaywall }: PartnerPickerProps) {
  const [partners, setPartners] = useState<Partner[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [addForm, setAddForm] = useState({ name: "", day: "", month: "", year: "", hour: "", minute: "", city: "" });
  const [addErrors, setAddErrors] = useState<Record<string, string>>({});

  const loaded = useRef(false);
  useEffect(() => {
    if (loaded.current || !token) return;
    loaded.current = true;
    loadPartners();
  }, [token]);

  async function loadPartners() {
    try {
      const res = await fetch("/api/v1/partners", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setPartners(Array.isArray(data) ? data : []);
      }
    } catch { setPartners([]); }
  }

  async function handleAddPartner() {
    const errs: Record<string, string> = {};
    if (!addForm.name.trim()) errs.name = lang === "ru" ? "Укажи имя" : "Enter name";
    const de = validateDay(addForm.day); if (de) errs.day = de;
    const me = validateMonth(addForm.month); if (me) errs.month = me;
    const ye = validateYear(addForm.year); if (ye) errs.year = ye;
    if (!de && !me && !ye) { const dx = validateDateExists(addForm.day, addForm.month, addForm.year); if (dx) errs.date = dx; }
    if (Object.values(errs).some(Boolean)) { setAddErrors(errs); return; }

    setLoading(true);
    try {
      const bd = `${addForm.year}-${addForm.month.padStart(2, "0")}-${addForm.day.padStart(2, "0")}`;
      const body: Record<string, unknown> = { name: addForm.name, birth_date: bd };
      if (addForm.hour) body.birth_hour = parseInt(addForm.hour);
      if (addForm.minute) body.birth_minute = parseInt(addForm.minute);
      if (addForm.city.trim()) body.birth_city = addForm.city;
      await apiRequest("/partners", body, token ?? undefined);
      await loadPartners();
      setShowAddForm(false);
      setAddForm({ name: "", day: "", month: "", year: "", hour: "", minute: "", city: "" });
    } catch (e: unknown) {
      const err = e as { code?: string; message?: string };
      if (err.code === "FREE_LIMIT_REACHED") onPaywall();
      else setError(err.message || (lang === "ru" ? "Ошибка" : "Error"));
    } finally { setLoading(false); }
  }

  async function handleDeletePartner(id: string) {
    try {
      await fetch(`/api/v1/partners/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      setPartners(prev => prev.filter(p => p.id !== id));
    } catch {}
  }

  const inputCls = "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 text-text-primary text-sm placeholder:text-text-faint focus:outline-none focus:border-violet-600 transition-colors";

  return (
    <div className="flex flex-col gap-3">
      <p className="font-cinzel uppercase mb-1" style={{ fontSize: 10, letterSpacing: ".22em", color: "#C9A84C" }}>
        {lang === "ru" ? "Твои партнёры" : "Your partners"}
      </p>

      {partners.map(p => (
        <div key={p.id} className="cursor-pointer active:scale-[0.98] transition-all"
          style={{ display: "flex", gap: 14, padding: "14px 16px", borderRadius: 14, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", alignItems: "center", justifyContent: "space-between" }}
          onClick={() => onSelect(p)}>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div className="font-cormorant" style={{ width: 40, height: 40, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, color: "#F0E9DA", background: "linear-gradient(135deg,#4B3C86,#C9A84C)" }}>
              {p.name[0]?.toUpperCase()}
            </div>
            <div>
              <p className="text-text-primary text-sm">{p.name}</p>
              <p className="text-text-faint text-[10px]">{p.zodiac_symbol} {lang === "ru" ? p.zodiac_sign_ru : p.zodiac_sign}</p>
            </div>
          </div>
          <button className="text-text-faint text-xs px-2" onClick={e => { e.stopPropagation(); handleDeletePartner(p.id); }}>x</button>
        </div>
      ))}

      {showAddForm ? (
        <div style={{ borderRadius: 18, background: "linear-gradient(155deg,rgba(255,255,255,.045),rgba(255,255,255,.01))", border: "1px solid rgba(201,168,76,.13)", padding: "16px" }}>
          <div className="flex flex-col gap-2">
            <input className={inputCls} placeholder={lang === "ru" ? "Имя" : "Name"} value={addForm.name}
              onChange={e => { setAddForm(p => ({ ...p, name: e.target.value })); setAddErrors(p => ({ ...p, name: "" })); }} />
            {addErrors.name && <p className="text-red-400 text-[10px]">{addErrors.name}</p>}
            <div className="grid grid-cols-3 gap-2">
              <input className={inputCls} placeholder={lang === "ru" ? "День" : "Day"} type="number" value={addForm.day}
                onChange={e => { setAddForm(p => ({ ...p, day: e.target.value })); setAddErrors(p => ({ ...p, day: "", date: "" })); }} />
              <input className={inputCls} placeholder={lang === "ru" ? "Месяц" : "Month"} type="number" value={addForm.month}
                onChange={e => { setAddForm(p => ({ ...p, month: e.target.value })); setAddErrors(p => ({ ...p, month: "", date: "" })); }} />
              <input className={inputCls} placeholder={lang === "ru" ? "Год" : "Year"} type="number" value={addForm.year}
                onChange={e => { setAddForm(p => ({ ...p, year: e.target.value })); setAddErrors(p => ({ ...p, year: "", date: "" })); }} />
            </div>
            {(addErrors.day || addErrors.month || addErrors.year || addErrors.date) && (
              <p className="text-red-400 text-[10px]">{addErrors.day || addErrors.month || addErrors.year || addErrors.date}</p>
            )}
            <p className="text-text-faint text-[9px] mt-1">{lang === "ru" ? "Время рождения (для лунной совместимости)" : "Birth time (for moon compatibility)"}</p>
            <div className="grid grid-cols-2 gap-2">
              <input className={inputCls} placeholder={lang === "ru" ? "Час (0–23)" : "Hour (0–23)"} type="number" min="0" max="23" value={addForm.hour}
                onChange={e => setAddForm(p => ({ ...p, hour: e.target.value }))} />
              <input className={inputCls} placeholder={lang === "ru" ? "Минуты" : "Minutes"} type="number" min="0" max="59" value={addForm.minute}
                onChange={e => setAddForm(p => ({ ...p, minute: e.target.value }))} />
            </div>
            <input className={inputCls} placeholder={lang === "ru" ? "Город рождения (для синастрии)" : "Birth city (for synastry)"} value={addForm.city}
              onChange={e => setAddForm(p => ({ ...p, city: e.target.value }))} />
            <div className="flex gap-2">
              <Button variant="primary" size="sm" className="flex-1" onClick={handleAddPartner} disabled={loading}>
                {loading ? "..." : (lang === "ru" ? "Добавить" : "Add")}
              </Button>
              <Button variant="ghost" size="sm" className="flex-1" onClick={() => setShowAddForm(false)}>
                {lang === "ru" ? "Отмена" : "Cancel"}
              </Button>
            </div>
          </div>
        </div>
      ) : (
        <button className="w-full py-3 text-sm transition-colors" onClick={() => setShowAddForm(true)}
          style={{ borderRadius: 14, border: "1px solid rgba(201,168,76,.4)", color: "#E8CD7E", background: "transparent" }}>
          {lang === "ru" ? "Добавить партнёра" : "Add partner"} +
        </button>
      )}

      {error && <p className="text-red-400 text-xs text-center">{error}</p>}
    </div>
  );
}
