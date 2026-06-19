export interface ZodiacInfo {
  sign: string;
  symbol: string;
  en: string;
}

export function getZodiacSign(birthDate: string): ZodiacInfo {
  const [, m, d] = birthDate.split("-").map(Number);
  if ((m === 3 && d >= 21) || (m === 4 && d <= 19)) return { sign: "Овен", symbol: "♈", en: "Aries" };
  if ((m === 4 && d >= 20) || (m === 5 && d <= 20)) return { sign: "Телец", symbol: "♉", en: "Taurus" };
  if ((m === 5 && d >= 21) || (m === 6 && d <= 20)) return { sign: "Близнецы", symbol: "♊", en: "Gemini" };
  if ((m === 6 && d >= 21) || (m === 7 && d <= 22)) return { sign: "Рак", symbol: "♋", en: "Cancer" };
  if ((m === 7 && d >= 23) || (m === 8 && d <= 22)) return { sign: "Лев", symbol: "♌", en: "Leo" };
  if ((m === 8 && d >= 23) || (m === 9 && d <= 22)) return { sign: "Дева", symbol: "♍", en: "Virgo" };
  if ((m === 9 && d >= 23) || (m === 10 && d <= 22)) return { sign: "Весы", symbol: "♎", en: "Libra" };
  if ((m === 10 && d >= 23) || (m === 11 && d <= 21)) return { sign: "Скорпион", symbol: "♏", en: "Scorpio" };
  if ((m === 11 && d >= 22) || (m === 12 && d <= 21)) return { sign: "Стрелец", symbol: "♐", en: "Sagittarius" };
  if ((m === 12 && d >= 22) || (m === 1 && d <= 19)) return { sign: "Козерог", symbol: "♑", en: "Capricorn" };
  if ((m === 1 && d >= 20) || (m === 2 && d <= 18)) return { sign: "Водолей", symbol: "♒", en: "Aquarius" };
  return { sign: "Рыбы", symbol: "♓", en: "Pisces" };
}
