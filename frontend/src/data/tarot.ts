export const MAJOR_ARCANA = [
  { id: 0,  name_ru: 'Шут',             name_en: 'The Fool',          symbol: '🃏', number: '0'    },
  { id: 1,  name_ru: 'Маг',             name_en: 'The Magician',      symbol: '⚡', number: 'I'    },
  { id: 2,  name_ru: 'Жрица',           name_en: 'High Priestess',    symbol: '🌙', number: 'II'   },
  { id: 3,  name_ru: 'Императрица',     name_en: 'The Empress',       symbol: '🌿', number: 'III'  },
  { id: 4,  name_ru: 'Император',       name_en: 'The Emperor',       symbol: '♦',  number: 'IV'   },
  { id: 5,  name_ru: 'Иерофант',        name_en: 'The Hierophant',    symbol: '✝',  number: 'V'    },
  { id: 6,  name_ru: 'Влюблённые',      name_en: 'The Lovers',        symbol: '♡',  number: 'VI'   },
  { id: 7,  name_ru: 'Колесница',       name_en: 'The Chariot',       symbol: '⚔',  number: 'VII'  },
  { id: 8,  name_ru: 'Сила',            name_en: 'Strength',          symbol: '∞',  number: 'VIII' },
  { id: 9,  name_ru: 'Отшельник',       name_en: 'The Hermit',        symbol: '🕯', number: 'IX'   },
  { id: 10, name_ru: 'Колесо Фортуны',  name_en: 'Wheel of Fortune',  symbol: '☸',  number: 'X'    },
  { id: 11, name_ru: 'Справедливость',  name_en: 'Justice',           symbol: '⚖',  number: 'XI'   },
  { id: 12, name_ru: 'Повешенный',      name_en: 'The Hanged Man',    symbol: '🔄', number: 'XII'  },
  { id: 13, name_ru: 'Смерть',          name_en: 'Death',             symbol: '🌑', number: 'XIII' },
  { id: 14, name_ru: 'Умеренность',     name_en: 'Temperance',        symbol: '⚗',  number: 'XIV'  },
  { id: 15, name_ru: 'Дьявол',          name_en: 'The Devil',         symbol: '⛓',  number: 'XV'   },
  { id: 16, name_ru: 'Башня',           name_en: 'The Tower',         symbol: '🌩', number: 'XVI'  },
  { id: 17, name_ru: 'Звезда',          name_en: 'The Star',          symbol: '✦',  number: 'XVII' },
  { id: 18, name_ru: 'Луна',            name_en: 'The Moon',          symbol: '🌕', number: 'XVIII'},
  { id: 19, name_ru: 'Солнце',          name_en: 'The Sun',           symbol: '☀',  number: 'XIX'  },
  { id: 20, name_ru: 'Суд',             name_en: 'Judgement',         symbol: '📯', number: 'XX'   },
  { id: 21, name_ru: 'Мир',             name_en: 'The World',         symbol: '🌍', number: 'XXI'  },
]

export type TarotCardData = typeof MAJOR_ARCANA[number]

export function drawCards(count: number): TarotCardData[] {
  const shuffled = [...MAJOR_ARCANA].sort(() => Math.random() - 0.5)
  return shuffled.slice(0, count)
}
