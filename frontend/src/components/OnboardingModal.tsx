import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";
import { Button } from "./ui";

interface Props {
  onClose: () => void;
}

export function OnboardingModal({ onClose }: Props) {
  const { t } = useTranslation();
  const { token, updateUser } = useAuth();
  const [day, setDay] = useState("");
  const [month, setMonth] = useState("");
  const [year, setYear] = useState("");
  const [loading, setLoading] = useState(false);

  const canSubmit = day && month && year;

  async function handleSubmit() {
    if (!canSubmit) return;
    setLoading(true);
    try {
      const birthDate = `${year}-${month.padStart(2, "0")}-${day.padStart(2, "0")}`;
      const res = await fetch("/api/v1/profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ birth_date: birthDate }),
      });
      if (res.ok) {
        updateUser({ has_birth_date: true });
        onClose();
      }
    } catch {
      // silently fail — user can fill in profile later
    } finally {
      setLoading(false);
    }
  }

  const inputCls =
    "w-full bg-bg-surface border border-border-subtle rounded-xl px-3 py-2.5 " +
    "text-text-primary text-sm text-center placeholder:text-text-faint " +
    "focus:outline-none focus:border-violet-600 transition-colors";

  return (
    <div
      className="fixed inset-0 flex flex-col justify-end"
      style={{ zIndex: 100, background: "rgba(0,0,0,0.75)" }}
      onClick={e => e.target === e.currentTarget && onClose()}
    >
      <div
        className="w-full max-w-[390px] mx-auto rounded-t-2xl px-5 pt-6 pb-10 flex flex-col gap-4"
        style={{ background: "#100d24", border: "0.5px solid rgba(107,78,255,0.2)" }}
      >
        <div className="flex items-center justify-between">
          <p className="font-display text-text-primary text-lg">
            {t("onboarding.title")}
          </p>
          <button
            onClick={onClose}
            className="text-text-faint text-xl leading-none w-8 h-8 flex items-center justify-center"
          >
            ✕
          </button>
        </div>

        <p className="text-text-muted text-sm">
          {t("onboarding.subtitle")}
        </p>

        <div className="grid grid-cols-3 gap-2">
          <input
            className={inputCls}
            placeholder={t("onboarding.day")}
            type="number"
            min="1"
            max="31"
            value={day}
            onChange={e => setDay(e.target.value)}
          />
          <input
            className={inputCls}
            placeholder={t("onboarding.month")}
            type="number"
            min="1"
            max="12"
            value={month}
            onChange={e => setMonth(e.target.value)}
          />
          <input
            className={inputCls}
            placeholder={t("onboarding.year")}
            type="number"
            min="1900"
            max="2025"
            value={year}
            onChange={e => setYear(e.target.value)}
          />
        </div>

        <Button
          variant="primary"
          className="w-full"
          onClick={handleSubmit}
          disabled={loading || !canSubmit}
        >
          {loading ? "..." : t("onboarding.continue")}
        </Button>

        <p className="text-text-faint text-[10px] text-center">
          {t("onboarding.hint")}
        </p>
      </div>
    </div>
  );
}
