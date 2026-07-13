const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validateEmail(email: string): string | null {
  if (!email.trim()) return "Email обязателен";
  if (!EMAIL_RE.test(email)) return "Введи корректный email";
  return null;
}

export function validatePassword(pass: string): string | null {
  if (!pass) return "Пароль обязателен";
  if (pass.length < 6) return "Минимум 6 символов";
  return null;
}

export function validateDay(day: string): string | null {
  const n = Number(day);
  if (!day || isNaN(n) || n < 1 || n > 31) return "День: от 1 до 31";
  return null;
}

export function validateMonth(month: string): string | null {
  const n = Number(month);
  if (!month || isNaN(n) || n < 1 || n > 12) return "Месяц: от 1 до 12";
  return null;
}

export function validateYear(year: string): string | null {
  const n = Number(year);
  const cur = new Date().getFullYear();
  if (!year || isNaN(n) || n < 1900 || n > cur) return "Укажи корректный год";
  return null;
}

export function validateDateExists(day: string, month: string, year: string): string | null {
  const d = Number(day), m = Number(month), y = Number(year);
  if (isNaN(d) || isNaN(m) || isNaN(y)) return null;
  const date = new Date(y, m - 1, d);
  if (date.getDate() !== d) return "Такой даты нет";
  return null;
}

export function validateName(name: string): string | null {
  const trimmed = name.trim();
  if (!trimmed) return "Укажи имя";
  if (trimmed.length < 2) return "Минимум 2 символа";
  if (trimmed.length > 50) return "Максимум 50 символов";
  if (/[<>]/.test(name)) return "Имя не должно содержать < или >";
  if (!/\p{L}/u.test(name)) return "Имя должно содержать хотя бы одну букву";
  return null;
}

export function validateCity(city: string): string | null {
  if (city.trim().length < 2) return "Укажи город";
  return null;
}
