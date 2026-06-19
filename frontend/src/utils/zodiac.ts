export interface ZodiacInfo {
  sign: string;
  symbol: string;
  en: string;
}

const SIGNS: Array<{ sign: string; en: string; symbol: string; from: [number, number]; to: [number, number] }> = [
  { sign: "Козерог",   en: "Capricorn",   symbol: "♑", from: [1, 1],   to: [1, 19]  },
  { sign: "Водолей",   en: "Aquarius",    symbol: "♒", from: [1, 20],  to: [2, 18]  },
  { sign: "Рыбы",     en: "Pisces",      symbol: "♓", from: [2, 19],  to: [3, 20]  },
  { sign: "Овен",     en: "Aries",       symbol: "♈", from: [3, 21],  to: [4, 19]  },
  { sign: "Телец",    en: "Taurus",      symbol: "♉", from: [4, 20],  to: [5, 20]  },
  { sign: "Близнецы", en: "Gemini",      symbol: "♊", from: [5, 21],  to: [6, 20]  },
  { sign: "Рак",      en: "Cancer",      symbol: "♋", from: [6, 21],  to: [7, 22]  },
  { sign: "Лев",      en: "Leo",         symbol: "♌", from: [7, 23],  to: [8, 22]  },
  { sign: "Дева",     en: "Virgo",       symbol: "♍", from: [8, 23],  to: [9, 22]  },
  { sign: "Весы",     en: "Libra",       symbol: "♎", from: [9, 23],  to: [10, 22] },
  { sign: "Скорпион", en: "Scorpio",     symbol: "♏", from: [10, 23], to: [11, 21] },
  { sign: "Стрелец",  en: "Sagittarius", symbol: "♐", from: [11, 22], to: [12, 21] },
  { sign: "Козерог",  en: "Capricorn",   symbol: "♑", from: [12, 22], to: [12, 31] },
];

export function getZodiacSign(birthDate: string): ZodiacInfo {
  const [, m, d] = birthDate.split("-").map(Number);
  for (const s of SIGNS) {
    const afterFrom = m > s.from[0] || (m === s.from[0] && d >= s.from[1]);
    const beforeTo = m < s.to[0] || (m === s.to[0] && d <= s.to[1]);
    if (afterFrom && beforeTo) return { sign: s.sign, symbol: s.symbol, en: s.en };
  }
  return { sign: "Козерог", symbol: "♑", en: "Capricorn" };
}
