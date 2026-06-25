export interface SpreadType {
  id: string;
  name_ru: string;
  name_en: string;
  desc_ru: string;
  desc_en: string;
  count: number;
  tier: "free" | "pro";
  positions_ru: string[];
  positions_en: string[];
  icon: string;
  schemes?: { ru: string[]; en: string[] }[];
}

export const SPREADS: SpreadType[] = [
  {
    id: "card_of_day", name_ru: "Карта дня", name_en: "Card of the Day",
    desc_ru: "Одна карта на весь день", desc_en: "One card for the whole day",
    count: 1, tier: "free", icon: "☀",
    positions_ru: ["Карта дня"], positions_en: ["Card of the Day"],
  },
  {
    id: "three_cards", name_ru: "Три карты", name_en: "Three Cards",
    desc_ru: "Классический расклад на 3 карты", desc_en: "Classic 3-card spread",
    count: 3, tier: "free", icon: "☰",
    positions_ru: ["Прошлое", "Настоящее", "Будущее"],
    positions_en: ["Past", "Present", "Future"],
    schemes: [
      { ru: ["Прошлое", "Настоящее", "Будущее"], en: ["Past", "Present", "Future"] },
      { ru: ["Ситуация", "Действие", "Результат"], en: ["Situation", "Action", "Outcome"] },
      { ru: ["Тело", "Разум", "Дух"], en: ["Body", "Mind", "Spirit"] },
      { ru: ["Да", "Нет", "Совет"], en: ["Yes", "No", "Advice"] },
    ],
  },
  {
    id: "celtic_cross", name_ru: "Кельтский крест", name_en: "Celtic Cross",
    desc_ru: "Глубокий анализ ситуации — 10 карт", desc_en: "Deep situation analysis — 10 cards",
    count: 10, tier: "pro", icon: "⊞",
    positions_ru: ["Суть", "Препятствие", "Основа", "Прошлое", "Возможное будущее",
                   "Ближайшее будущее", "Ты сейчас", "Окружение", "Надежды/Страхи", "Итог"],
    positions_en: ["Core", "Challenge", "Foundation", "Past", "Possible Future",
                   "Near Future", "You Now", "Environment", "Hopes/Fears", "Outcome"],
  },
  {
    id: "horseshoe", name_ru: "Подкова", name_en: "Horseshoe",
    desc_ru: "7 карт — обзор ситуации и совет", desc_en: "7 cards — overview and advice",
    count: 7, tier: "pro", icon: "⌓",
    positions_ru: ["Прошлое", "Настоящее", "Скрытые влияния", "Препятствия",
                   "Окружение", "Совет", "Итог"],
    positions_en: ["Past", "Present", "Hidden Influences", "Obstacles",
                   "Environment", "Advice", "Outcome"],
  },
  {
    id: "relationship", name_ru: "На отношения", name_en: "Relationship",
    desc_ru: "7 карт — анализ пары", desc_en: "7 cards — couple analysis",
    count: 7, tier: "pro", icon: "♡",
    positions_ru: ["Ты", "Партнёр", "Связь", "Основа", "Внешнее влияние",
                   "Совет", "Будущее пары"],
    positions_en: ["You", "Partner", "Connection", "Foundation", "External Influence",
                   "Advice", "Future of the Couple"],
  },
  {
    id: "yes_no", name_ru: "Да / Нет", name_en: "Yes / No",
    desc_ru: "5 карт — чёткий ответ на вопрос", desc_en: "5 cards — clear answer to a question",
    count: 5, tier: "pro", icon: "?",
    positions_ru: ["Карта 1", "Карта 2", "Карта 3", "Карта 4", "Карта 5"],
    positions_en: ["Card 1", "Card 2", "Card 3", "Card 4", "Card 5"],
  },
  {
    id: "two_choices", name_ru: "Два пути", name_en: "Two Paths",
    desc_ru: "6 карт — сравнение двух вариантов", desc_en: "6 cards — compare two options",
    count: 6, tier: "pro", icon: "⑂",
    positions_ru: ["Путь А: сейчас", "Путь А: процесс", "Путь А: итог",
                   "Путь Б: сейчас", "Путь Б: процесс", "Путь Б: итог"],
    positions_en: ["Path A: now", "Path A: process", "Path A: outcome",
                   "Path B: now", "Path B: process", "Path B: outcome"],
  },
  {
    id: "person", name_ru: "На человека", name_en: "About a Person",
    desc_ru: "5 карт — характер и намерения", desc_en: "5 cards — character and intentions",
    count: 5, tier: "pro", icon: "○",
    positions_ru: ["Личность", "Мысли", "Чувства", "Намерения", "Итог"],
    positions_en: ["Personality", "Thoughts", "Feelings", "Intentions", "Outcome"],
  },
  {
    id: "year", name_ru: "На год", name_en: "Year Ahead",
    desc_ru: "13 карт — каждый месяц + тема года", desc_en: "13 cards — each month + yearly theme",
    count: 13, tier: "pro", icon: "▦",
    positions_ru: ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                   "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь", "Тема года"],
    positions_en: ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December", "Yearly Theme"],
  },
];
