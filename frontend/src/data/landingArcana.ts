/**
 * Short upright readings for the 22 Major Arcana, used by the landing's
 * "card of the day" draw.
 *
 * Kept separate from `data/tarot.ts` (which only carries names and numbers)
 * and deliberately client-side: the draw has to answer instantly for a
 * visitor who has not signed up yet, so it must not depend on the AI
 * endpoints that the real in-app spreads use. These are a teaser — the full
 * per-position interpretation lives behind the app.
 */

export interface ArcanaReading {
  /** Matches MAJOR_ARCANA[].id in data/tarot.ts. */
  id: number;
  ru: { name: string; keyword: string; text: string };
  en: { name: string; keyword: string; text: string };
}

export const ARCANA_READINGS: ArcanaReading[] = [
  { id: 0,
    ru: { name: "Шут", keyword: "Начало", text: "Чистый лист и свобода выбора. День для шага, который вы давно откладывали — опыт придёт по дороге." },
    en: { name: "The Fool", keyword: "Beginning", text: "A clean slate and freedom to choose. A day for the step you keep postponing — experience arrives on the way." } },
  { id: 1,
    ru: { name: "Маг", keyword: "Воля", text: "Все инструменты уже в ваших руках. Намерение сегодня превращается в результат быстрее обычного." },
    en: { name: "The Magician", keyword: "Will", text: "Every tool is already in your hands. Intention turns into result faster than usual today." } },
  { id: 2,
    ru: { name: "Жрица", keyword: "Интуиция", text: "Ответ приходит в тишине, а не в споре. Доверьтесь первому внутреннему отклику — он точнее расчёта." },
    en: { name: "High Priestess", keyword: "Intuition", text: "The answer comes in silence, not argument. Trust the first inner response — it beats calculation." } },
  { id: 3,
    ru: { name: "Императрица", keyword: "Изобилие", text: "Время растить, а не торопить. Забота о себе и близких вернётся сторицей уже на этой неделе." },
    en: { name: "The Empress", keyword: "Abundance", text: "A time to grow things, not rush them. Care for yourself and others returns multiplied this week." } },
  { id: 4,
    ru: { name: "Император", keyword: "Опора", text: "Структура даёт свободу. Наведите порядок в одном деле — остальные подтянутся следом." },
    en: { name: "The Emperor", keyword: "Structure", text: "Structure creates freedom. Put one area in order and the rest will follow." } },
  { id: 5,
    ru: { name: "Иерофант", keyword: "Опыт", text: "Хороший день спросить совета у того, кто прошёл этот путь раньше. Традиция сейчас надёжнее эксперимента." },
    en: { name: "The Hierophant", keyword: "Guidance", text: "A good day to ask someone who walked this path first. Tradition beats experiment right now." } },
  { id: 6,
    ru: { name: "Влюблённые", keyword: "Выбор", text: "Развилка, где важны не выгода, а ценности. Выбирайте то, с чем сможете жить долго." },
    en: { name: "The Lovers", keyword: "Choice", text: "A fork where values matter more than gain. Choose what you can live with for a long time." } },
  { id: 7,
    ru: { name: "Колесница", keyword: "Движение", text: "Победа достаётся тому, кто держит направление. Сфокусируйтесь на одной цели — и не сворачивайте." },
    en: { name: "The Chariot", keyword: "Momentum", text: "Victory goes to whoever holds the line. Pick one goal and do not swerve." } },
  { id: 8,
    ru: { name: "Сила", keyword: "Мягкость", text: "Не давить, а приручать. Спокойствие сегодня решает больше задач, чем напор." },
    en: { name: "Strength", keyword: "Gentleness", text: "Tame rather than force. Calm solves more today than pressure does." } },
  { id: 9,
    ru: { name: "Отшельник", keyword: "Тишина", text: "Шаг назад от суеты даёт ясность. Побудьте наедине с вопросом — ответ уже почти сформулирован." },
    en: { name: "The Hermit", keyword: "Solitude", text: "A step back from the noise brings clarity. Sit alone with the question — the answer is nearly formed." } },
  { id: 10,
    ru: { name: "Колесо Фортуны", keyword: "Поворот", text: "Полоса меняется. То, что казалось затянувшимся, сдвинется без ваших усилий — будьте готовы поймать момент." },
    en: { name: "Wheel of Fortune", keyword: "Turning", text: "The tide changes. What felt stuck moves without your effort — be ready to catch it." } },
  { id: 11,
    ru: { name: "Справедливость", keyword: "Баланс", text: "День расчётов и честных итогов. Решение, принятое по совести, окажется и самым выгодным." },
    en: { name: "Justice", keyword: "Balance", text: "A day of reckoning and honest totals. The decision made in good conscience proves the profitable one." } },
  { id: 12,
    ru: { name: "Повешенный", keyword: "Пауза", text: "Пробуйте посмотреть на ситуацию с другой стороны. Пауза сейчас — не потеря, а разворот перспективы." },
    en: { name: "The Hanged Man", keyword: "Pause", text: "Try the situation from another angle. A pause now is not loss but a shift of perspective." } },
  { id: 13,
    ru: { name: "Смерть", keyword: "Обновление", text: "Что-то завершается — и это к лучшему. Отпустите отжившее, чтобы освободить место новому." },
    en: { name: "Death", keyword: "Renewal", text: "Something ends, and for the better. Let the outworn go to make room for what is next." } },
  { id: 14,
    ru: { name: "Умеренность", keyword: "Мера", text: "Золотая середина во всём. Смешайте противоположности вместо того, чтобы выбирать между ними." },
    en: { name: "Temperance", keyword: "Measure", text: "The middle path in everything. Blend the opposites instead of choosing between them." } },
  { id: 15,
    ru: { name: "Дьявол", keyword: "Привязка", text: "Проверьте, где вы держитесь за то, что давно держит вас. Цепь чаще всего не заперта." },
    en: { name: "The Devil", keyword: "Attachment", text: "Check where you hold on to what has been holding you. The chain is usually unlocked." } },
  { id: 16,
    ru: { name: "Башня", keyword: "Слом", text: "Внезапная ясность рушит удобную иллюзию. Больно, но после этого станет честнее и проще." },
    en: { name: "The Tower", keyword: "Rupture", text: "Sudden clarity breaks a comfortable illusion. It stings, then everything gets honest and simple." } },
  { id: 17,
    ru: { name: "Звезда", keyword: "Надежда", text: "После трудного — вдох. Возвращается вера в замысел, и он действительно сбывается." },
    en: { name: "The Star", keyword: "Hope", text: "After the hard part, a breath. Faith in the plan returns — and the plan does come true." } },
  { id: 18,
    ru: { name: "Луна", keyword: "Туман", text: "Не всё видно ясно, и это нормально. Не принимайте окончательных решений до утра." },
    en: { name: "The Moon", keyword: "Fog", text: "Not everything is visible, and that is fine. Make no final decisions before morning." } },
  { id: 19,
    ru: { name: "Солнце", keyword: "Ясность", text: "Самая светлая карта колоды. Успех, признание и простая радость — берите и не сомневайтесь." },
    en: { name: "The Sun", keyword: "Clarity", text: "The brightest card in the deck. Success, recognition and plain joy — take it without second-guessing." } },
  { id: 20,
    ru: { name: "Суд", keyword: "Итог", text: "Прошлое просит честной оценки. Признайте сделанное — и получите право начать заново." },
    en: { name: "Judgement", keyword: "Reckoning", text: "The past asks for an honest verdict. Own what you did and earn the right to begin again." } },
  { id: 21,
    ru: { name: "Мир", keyword: "Завершение", text: "Круг замкнулся, цель достигнута. Отметьте это — следующий виток начнётся уже с новой высоты." },
    en: { name: "The World", keyword: "Completion", text: "The circle closes, the goal is met. Mark it — the next turn starts from higher ground." } },
];
