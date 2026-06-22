from __future__ import annotations

from datetime import date, datetime

# ---------------------------------------------------------------------------
# Pythagorean letter tables (TZ-030 spec)
# ---------------------------------------------------------------------------
LATIN_VALUES = {
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9,
    "J": 1, "K": 2, "L": 3, "M": 4, "N": 5, "O": 6, "P": 7, "Q": 8, "R": 9,
    "S": 1, "T": 2, "U": 3, "V": 4, "W": 5, "X": 6, "Y": 7, "Z": 8,
}

CYR_VALUES = {
    "А": 1, "Б": 2, "В": 6, "Г": 3, "Д": 4, "Е": 5, "Ё": 5, "Ж": 8,
    "З": 7, "И": 1, "Й": 1, "К": 2, "Л": 3, "М": 4, "Н": 5, "О": 7,
    "П": 8, "Р": 9, "С": 1, "Т": 2, "У": 3, "Ф": 4, "Х": 5, "Ц": 6,
    "Ч": 7, "Ш": 8, "Щ": 9, "Ъ": 1, "Ы": 2, "Ь": 3, "Э": 4, "Ю": 5, "Я": 6,
}

LATIN_VOWELS = set("AEIOUY")
CYR_VOWELS = set("АЕЁИОУЫЭЮЯ")

# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def reduce(n: int) -> int:
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(d) for d in str(n))
    return n


def life_path(birth_date: date) -> int:
    digits = [int(c) for c in birth_date.isoformat().replace("-", "")]
    return reduce(sum(digits))


def destiny_number(full_name: str) -> int:
    total = 0
    for c in full_name.upper():
        total += LATIN_VALUES.get(c, 0) + CYR_VALUES.get(c, 0)
    return reduce(total)


def soul_number(full_name: str) -> int:
    total = 0
    for c in full_name.upper():
        if c in LATIN_VOWELS:
            total += LATIN_VALUES[c]
        elif c in CYR_VOWELS:
            total += CYR_VALUES[c]
    return reduce(total)


def personality_number(full_name: str) -> int:
    total = 0
    for c in full_name.upper():
        if c in LATIN_VALUES and c not in LATIN_VOWELS:
            total += LATIN_VALUES[c]
        elif c in CYR_VALUES and c not in CYR_VOWELS:
            total += CYR_VALUES[c]
    return reduce(total)


def birthday_number(birth_date: date) -> int:
    return reduce(birth_date.day)


def personal_year(birth_date: date, year: int) -> int:
    s = birth_date.day + birth_date.month + sum(int(d) for d in str(year))
    return reduce(s)


def personal_month(birth_date: date, year: int, month: int) -> int:
    return reduce(personal_year(birth_date, year) + month)


def personal_day(birth_date: date, target: date) -> int:
    return reduce(personal_month(birth_date, target.year, target.month) + target.day)


KARMIC_DESCRIPTIONS_RU = {
    13: "Кармический долг 13 — лень в прошлых жизнях. Нужно учиться работать усердно и доводить дела до конца.",
    14: "Кармический долг 14 — злоупотребление свободой. Урок умеренности и ответственности за свои действия.",
    16: "Кармический долг 16 — разрушение эго. Урок смирения, духовного роста через потери и перестройку.",
    19: "Кармический долг 19 — злоупотребление властью. Урок самостоятельности без подавления других.",
}
KARMIC_DESCRIPTIONS_EN = {
    13: "Karmic debt 13 — laziness in past lives. Learn to work hard and finish what you start.",
    14: "Karmic debt 14 — abuse of freedom. Lesson of moderation and responsibility for your actions.",
    16: "Karmic debt 16 — ego destruction. Lesson of humility, spiritual growth through loss and rebuilding.",
    19: "Karmic debt 19 — abuse of power. Lesson of independence without suppressing others.",
}


def karmic_numbers(birth_date: date) -> list[dict]:
    digits_str = birth_date.isoformat().replace("-", "")
    total = sum(int(c) for c in digits_str)
    intermediates = {total}
    while total > 9:
        total = sum(int(d) for d in str(total))
        intermediates.add(total)
    day = birth_date.day
    intermediates.add(day)
    result = []
    for kn in (13, 14, 16, 19):
        if kn in intermediates:
            result.append({"number": kn})
    return result


def missing_numbers(birth_date: date) -> list[int]:
    digits = set(int(c) for c in birth_date.isoformat().replace("-", "") if c.isdigit())
    return sorted([n for n in range(1, 10) if n not in digits])


# ---------------------------------------------------------------------------
# Pythagoras square
# ---------------------------------------------------------------------------
CELL_NAMES_RU = {
    1: "Характер и сила воли",
    2: "Энергетика и биополе",
    3: "Познание и интерес к наукам",
    4: "Здоровье и физическое состояние",
    5: "Логика и интуиция",
    6: "Трудолюбие и ответственность",
    7: "Везение и удача",
    8: "Чувство долга и обязательность",
    9: "Память и интеллект",
}
CELL_NAMES_EN = {
    1: "Character & willpower",
    2: "Energy & biofield",
    3: "Cognition & interest in science",
    4: "Health & physical state",
    5: "Logic & intuition",
    6: "Diligence & responsibility",
    7: "Luck & fortune",
    8: "Sense of duty & reliability",
    9: "Memory & intellect",
}

CELL_LEVELS_RU = {
    0: "Отсутствует — качество не развито, требует работы",
    1: "Слабое — есть задатки, нужно развивать",
    2: "Среднее — нормальный уровень, стабильно",
    3: "Сильное — ярко выражено, ваша опора",
    4: "Очень сильное — доминирует, может быть избыточно",
}
CELL_LEVELS_EN = {
    0: "Absent — quality undeveloped, needs work",
    1: "Weak — basic potential, needs development",
    2: "Average — normal level, stable",
    3: "Strong — clearly expressed, your strength",
    4: "Very strong — dominant, may be excessive",
}

LINE_DEFS = [
    {"cells": [1, 2, 3], "title_ru": "Самооценка и целеустремлённость", "title_en": "Self-esteem & determination",
     "desc_ru": "Чем больше цифр — тем выше самооценка и сильнее целеустремлённость.",
     "desc_en": "More digits mean higher self-esteem and stronger determination."},
    {"cells": [4, 5, 6], "title_ru": "Стабильность семьи", "title_en": "Family stability",
     "desc_ru": "Показывает стремление к семье, стабильности и комфорту.",
     "desc_en": "Shows desire for family, stability, and comfort."},
    {"cells": [7, 8, 9], "title_ru": "Духовное развитие", "title_en": "Spiritual development",
     "desc_ru": "Связь с высшим, талант, интуиция, духовные практики.",
     "desc_en": "Connection to higher self, talent, intuition, spiritual practices."},
    {"cells": [1, 4, 7], "title_ru": "Личностный потенциал", "title_en": "Personal potential",
     "desc_ru": "Способность реализовать себя и достичь целей.",
     "desc_en": "Ability to realize yourself and achieve goals."},
    {"cells": [2, 5, 8], "title_ru": "Социальная активность", "title_en": "Social activity",
     "desc_ru": "Общительность, умение взаимодействовать с людьми.",
     "desc_en": "Sociability, ability to interact with people."},
    {"cells": [3, 6, 9], "title_ru": "Финансовый потенциал", "title_en": "Financial potential",
     "desc_ru": "Способность зарабатывать и приумножать материальные блага.",
     "desc_en": "Ability to earn and multiply material wealth."},
    {"cells": [1, 5, 9], "title_ru": "Духовная диагональ (самооценка)", "title_en": "Spiritual diagonal (self-esteem)",
     "desc_ru": "Внутренний стержень, самопознание, глубинная уверенность.",
     "desc_en": "Inner core, self-knowledge, deep confidence."},
    {"cells": [3, 5, 7], "title_ru": "Диагональ интуиции и удачи", "title_en": "Intuition & luck diagonal",
     "desc_ru": "Природная интуиция, везение, умение оказаться в нужном месте.",
     "desc_en": "Natural intuition, luck, being in the right place at the right time."},
]


def pythagoras_square(birth_date: date, lang: str = "ru") -> dict:
    digits_str = birth_date.isoformat().replace("-", "")
    all_digits = [int(c) for c in digits_str]

    s1 = sum(all_digits)
    s2 = reduce(s1) if s1 > 9 else s1
    first_digit = all_digits[0] if all_digits[0] != 0 else all_digits[1]
    s3 = abs(s1 - 2 * first_digit)
    s4 = reduce(s3) if s3 > 9 else s3

    extra_digits = [int(c) for c in str(s1)] + [int(c) for c in str(s2)] + \
                   [int(c) for c in str(s3)] + [int(c) for c in str(s4)]
    combined = all_digits + extra_digits

    matrix: dict[int, int] = {i: 0 for i in range(1, 10)}
    for d in combined:
        if 1 <= d <= 9:
            matrix[d] += 1

    ru = lang == "ru"
    names = CELL_NAMES_RU if ru else CELL_NAMES_EN
    levels = CELL_LEVELS_RU if ru else CELL_LEVELS_EN

    cells = []
    for n in range(1, 10):
        cnt = matrix[n]
        strength_key = min(cnt, 4)
        strength_label = ["absent", "weak", "average", "strong", "very_strong"][strength_key]
        cells.append({
            "number": n,
            "count": cnt,
            "strength": strength_label,
            "name": names[n],
            "description": levels[strength_key],
        })

    lines = []
    for ld in LINE_DEFS:
        total = sum(matrix[c] for c in ld["cells"])
        lines.append({
            "cells": ld["cells"],
            "total": total,
            "filled": total >= 3,
            "title": ld["title_ru"] if ru else ld["title_en"],
            "description": ld["desc_ru"] if ru else ld["desc_en"],
        })

    return {
        "matrix": matrix,
        "working_numbers": [s1, s2, s3, s4],
        "cells": cells,
        "lines": lines,
    }


# ---------------------------------------------------------------------------
# Number meanings (1-9, 11, 22, 33)
# ---------------------------------------------------------------------------
NUMBER_DATA: dict[int, dict] = {
    1: {
        "name_ru": "Единица", "name_en": "One",
        "title_ru": "Лидер", "title_en": "Leader",
        "description_ru": "Независимость, амбиции, первопроходец. Вы рождены вести за собой и прокладывать новые пути. Сильная воля и решительность — ваши главные инструменты.",
        "description_en": "Independence, ambition, pioneer. You are born to lead and blaze new trails. Strong will and determination are your main tools.",
        "strengths_ru": ["Решительность", "Инициативность", "Самостоятельность", "Оригинальность"],
        "strengths_en": ["Determination", "Initiative", "Independence", "Originality"],
        "challenges_ru": ["Эгоизм", "Нетерпение", "Упрямство"],
        "challenges_en": ["Selfishness", "Impatience", "Stubbornness"],
        "career_ru": "Предпринимательство, руководство, инновации, фриланс.",
        "career_en": "Entrepreneurship, leadership, innovation, freelance.",
        "love_ru": "Нужен партнёр, который уважает вашу независимость. Избегайте подавления второй половинки.",
        "love_en": "Need a partner who respects your independence. Avoid dominating your partner.",
        "famous": ["Наполеон Бонапарт", "Стив Джобс", "Мартин Лютер Кинг"],
    },
    2: {
        "name_ru": "Двойка", "name_en": "Two",
        "title_ru": "Дипломат", "title_en": "Diplomat",
        "description_ru": "Гармония, сотрудничество, интуиция. Вы чувствуете людей на тонком уровне и умеете находить баланс в любой ситуации.",
        "description_en": "Harmony, cooperation, intuition. You sense people on a subtle level and find balance in any situation.",
        "strengths_ru": ["Дипломатичность", "Чуткость", "Терпение", "Миротворчество"],
        "strengths_en": ["Diplomacy", "Sensitivity", "Patience", "Peacemaking"],
        "challenges_ru": ["Нерешительность", "Зависимость от мнения других", "Застенчивость"],
        "challenges_en": ["Indecisiveness", "Dependence on others' opinions", "Shyness"],
        "career_ru": "Медиация, психология, искусство, командная работа, HR.",
        "career_en": "Mediation, psychology, art, teamwork, HR.",
        "love_ru": "Романтик, ищет глубокую эмоциональную связь. Избегайте растворения в партнёре.",
        "love_en": "Romantic, seeking deep emotional connection. Avoid losing yourself in a partner.",
        "famous": ["Барак Обама", "Мадонна", "Рональд Рейган"],
    },
    3: {
        "name_ru": "Тройка", "name_en": "Three",
        "title_ru": "Творец", "title_en": "Creator",
        "description_ru": "Самовыражение, вдохновение, общительность. Ваша творческая энергия заразительна и притягивает людей.",
        "description_en": "Self-expression, inspiration, sociability. Your creative energy is contagious and attracts people.",
        "strengths_ru": ["Креативность", "Оптимизм", "Красноречие", "Артистизм"],
        "strengths_en": ["Creativity", "Optimism", "Eloquence", "Artistry"],
        "challenges_ru": ["Рассеянность", "Поверхностность", "Склонность к критике"],
        "challenges_en": ["Scattered focus", "Superficiality", "Tendency to criticize"],
        "career_ru": "Искусство, медиа, маркетинг, преподавание, развлечения.",
        "career_en": "Art, media, marketing, teaching, entertainment.",
        "love_ru": "Лёгкий и весёлый партнёр, но нужно учиться глубине отношений.",
        "love_en": "Fun and easy partner, but needs to learn depth in relationships.",
        "famous": ["Джим Керри", "Кристина Агилера", "Джон Траволта"],
    },
    4: {
        "name_ru": "Четвёрка", "name_en": "Four",
        "title_ru": "Строитель", "title_en": "Builder",
        "description_ru": "Стабильность, дисциплина, трудолюбие. Вы создаёте прочный фундамент для всего, за что берётесь.",
        "description_en": "Stability, discipline, hard work. You create a solid foundation for everything you undertake.",
        "strengths_ru": ["Надёжность", "Практичность", "Организованность", "Выносливость"],
        "strengths_en": ["Reliability", "Practicality", "Organization", "Endurance"],
        "challenges_ru": ["Ригидность", "Трудоголизм", "Консерватизм"],
        "challenges_en": ["Rigidity", "Workaholism", "Conservatism"],
        "career_ru": "Инженерия, строительство, финансы, управление проектами.",
        "career_en": "Engineering, construction, finance, project management.",
        "love_ru": "Верный и надёжный партнёр. Нужно учиться спонтанности и романтике.",
        "love_en": "Loyal and reliable partner. Needs to learn spontaneity and romance.",
        "famous": ["Билл Гейтс", "Опра Уинфри", "Элтон Джон"],
    },
    5: {
        "name_ru": "Пятёрка", "name_en": "Five",
        "title_ru": "Искатель", "title_en": "Seeker",
        "description_ru": "Свобода, приключения, перемены. Вы не можете стоять на месте и всегда в поиске нового опыта.",
        "description_en": "Freedom, adventure, change. You can't stand still and are always seeking new experiences.",
        "strengths_ru": ["Адаптивность", "Любознательность", "Харизма", "Многогранность"],
        "strengths_en": ["Adaptability", "Curiosity", "Charisma", "Versatility"],
        "challenges_ru": ["Непостоянство", "Импульсивность", "Страх обязательств"],
        "challenges_en": ["Inconsistency", "Impulsiveness", "Fear of commitment"],
        "career_ru": "Путешествия, журналистика, продажи, стартапы, консалтинг.",
        "career_en": "Travel, journalism, sales, startups, consulting.",
        "love_ru": "Нужна свобода в отношениях. Партнёр не должен быть клеткой.",
        "love_en": "Needs freedom in relationships. A partner shouldn't be a cage.",
        "famous": ["Авраам Линкольн", "Анджелина Джоли", "Мик Джаггер"],
    },
    6: {
        "name_ru": "Шестёрка", "name_en": "Six",
        "title_ru": "Хранитель", "title_en": "Guardian",
        "description_ru": "Забота, ответственность, семья. Вы несёте свет и тепло в жизнь близких. Гармония — ваша главная ценность.",
        "description_en": "Care, responsibility, family. You bring light and warmth to loved ones' lives. Harmony is your core value.",
        "strengths_ru": ["Заботливость", "Ответственность", "Эстетический вкус", "Верность"],
        "strengths_en": ["Caring nature", "Responsibility", "Aesthetic taste", "Loyalty"],
        "challenges_ru": ["Гиперконтроль", "Жертвенность", "Перфекционизм"],
        "challenges_en": ["Over-controlling", "Self-sacrifice", "Perfectionism"],
        "career_ru": "Медицина, образование, дизайн, социальная работа, кулинария.",
        "career_en": "Medicine, education, design, social work, culinary arts.",
        "love_ru": "Идеальный семьянин, но нужно не забывать о себе.",
        "love_en": "Ideal family person, but don't forget about yourself.",
        "famous": ["Альберт Эйнштейн", "Джон Леннон", "Галилео Галилей"],
    },
    7: {
        "name_ru": "Семёрка", "name_en": "Seven",
        "title_ru": "Мыслитель", "title_en": "Thinker",
        "description_ru": "Мудрость, духовность, аналитический ум. Вы ищете глубинный смысл во всём и стремитесь к знаниям.",
        "description_en": "Wisdom, spirituality, analytical mind. You seek deep meaning in everything and strive for knowledge.",
        "strengths_ru": ["Аналитический ум", "Интуиция", "Глубина", "Перфекционизм"],
        "strengths_en": ["Analytical mind", "Intuition", "Depth", "Perfectionism"],
        "challenges_ru": ["Замкнутость", "Скептицизм", "Эмоциональная холодность"],
        "challenges_en": ["Introversion", "Skepticism", "Emotional coldness"],
        "career_ru": "Наука, исследования, IT, философия, психология.",
        "career_en": "Science, research, IT, philosophy, psychology.",
        "love_ru": "Нужен интеллектуальный партнёр. Учитесь открывать чувства.",
        "love_en": "Need an intellectual partner. Learn to open up emotionally.",
        "famous": ["Никола Тесла", "Принцесса Диана", "Владимир Путин"],
    },
    8: {
        "name_ru": "Восьмёрка", "name_en": "Eight",
        "title_ru": "Магнат", "title_en": "Magnate",
        "description_ru": "Власть, успех, материальное изобилие. Вы умеете притягивать ресурсы и управлять крупными проектами.",
        "description_en": "Power, success, material abundance. You know how to attract resources and manage large projects.",
        "strengths_ru": ["Деловая хватка", "Авторитетность", "Стратегическое мышление", "Выносливость"],
        "strengths_en": ["Business acumen", "Authority", "Strategic thinking", "Endurance"],
        "challenges_ru": ["Материализм", "Властность", "Трудоголизм"],
        "challenges_en": ["Materialism", "Domination", "Workaholism"],
        "career_ru": "Бизнес, финансы, недвижимость, управление, юриспруденция.",
        "career_en": "Business, finance, real estate, management, law.",
        "love_ru": "Статусный партнёр. Но не превращайте отношения в сделку.",
        "love_en": "Status-oriented partner. But don't turn relationships into deals.",
        "famous": ["Нельсон Мандела", "Пабло Пикассо", "Сандра Буллок"],
    },
    9: {
        "name_ru": "Девятка", "name_en": "Nine",
        "title_ru": "Гуманист", "title_en": "Humanitarian",
        "description_ru": "Сострадание, мудрость, завершение. Вы служите высшей цели и видите мир масштабно.",
        "description_en": "Compassion, wisdom, completion. You serve a higher purpose and see the world on a grand scale.",
        "strengths_ru": ["Мудрость", "Щедрость", "Харизма", "Широкий кругозор"],
        "strengths_en": ["Wisdom", "Generosity", "Charisma", "Broad outlook"],
        "challenges_ru": ["Идеализм", "Разочарование в людях", "Сложность с завершениями"],
        "challenges_en": ["Idealism", "Disappointment in people", "Difficulty with endings"],
        "career_ru": "Благотворительность, искусство, медицина, духовные практики.",
        "career_en": "Charity, art, medicine, spiritual practices.",
        "love_ru": "Безусловная любовь — ваш дар. Не бойтесь отпускать.",
        "love_en": "Unconditional love is your gift. Don't be afraid to let go.",
        "famous": ["Махатма Ганди", "Мать Тереза", "Джими Хендрикс"],
    },
    11: {
        "name_ru": "Мастер-число 11", "name_en": "Master Number 11",
        "title_ru": "Провидец", "title_en": "Visionary",
        "description_ru": "Интуиция высшего порядка, вдохновение, духовное лидерство. Вы видите то, что скрыто от других, и несёте свет.",
        "description_en": "Higher intuition, inspiration, spiritual leadership. You see what is hidden from others and carry the light.",
        "strengths_ru": ["Сверхинтуиция", "Вдохновение масс", "Духовная глубина", "Харизма"],
        "strengths_en": ["Super-intuition", "Mass inspiration", "Spiritual depth", "Charisma"],
        "challenges_ru": ["Нервное напряжение", "Гиперчувствительность", "Внутренний конфликт"],
        "challenges_en": ["Nervous tension", "Hypersensitivity", "Inner conflict"],
        "career_ru": "Духовное наставничество, искусство, психология, изобретательство.",
        "career_en": "Spiritual mentorship, art, psychology, invention.",
        "love_ru": "Глубокая духовная связь важнее всего. Ищите родственную душу.",
        "love_en": "Deep spiritual connection matters most. Seek a kindred soul.",
        "famous": ["Вольфганг Моцарт", "Барак Обама", "Эдгар Аллан По"],
    },
    22: {
        "name_ru": "Мастер-число 22", "name_en": "Master Number 22",
        "title_ru": "Зодчий", "title_en": "Architect",
        "description_ru": "Масштабные проекты, материализация мечтаний, практическая мудрость. Вы строите для вечности, превращая видение в реальность.",
        "description_en": "Grand projects, manifesting dreams, practical wisdom. You build for eternity, turning vision into reality.",
        "strengths_ru": ["Масштабное мышление", "Практическая реализация", "Организаторский талант", "Выдержка"],
        "strengths_en": ["Grand thinking", "Practical execution", "Organizational talent", "Endurance"],
        "challenges_ru": ["Перфекционизм", "Давление ответственности", "Контроль"],
        "challenges_en": ["Perfectionism", "Pressure of responsibility", "Control issues"],
        "career_ru": "Архитектура, крупный бизнес, политика, международные проекты.",
        "career_en": "Architecture, large business, politics, international projects.",
        "love_ru": "Нужен равный партнёр, который разделяет ваши амбиции.",
        "love_en": "Need an equal partner who shares your ambitions.",
        "famous": ["Пол Маккартни", "Далай-лама", "Ричард Брэнсон"],
    },
    33: {
        "name_ru": "Мастер-число 33", "name_en": "Master Number 33",
        "title_ru": "Целитель", "title_en": "Healer",
        "description_ru": "Сострадание высшего порядка, учительство, жертвенная любовь. Вы исцеляете мир своим присутствием.",
        "description_en": "Higher compassion, teaching, sacrificial love. You heal the world with your presence.",
        "strengths_ru": ["Безусловная любовь", "Целительство", "Мудрость", "Самоотверженность"],
        "strengths_en": ["Unconditional love", "Healing", "Wisdom", "Selflessness"],
        "challenges_ru": ["Эмоциональное выгорание", "Самопожертвование", "Перфекционизм"],
        "challenges_en": ["Emotional burnout", "Self-sacrifice", "Perfectionism"],
        "career_ru": "Целительство, духовные практики, образование, благотворительность.",
        "career_en": "Healing, spiritual practices, education, charity.",
        "love_ru": "Ваша любовь безгранична, но не забывайте любить себя.",
        "love_en": "Your love is boundless, but don't forget to love yourself.",
        "famous": ["Альберт Эйнштейн", "Фрэнсис Бэкон", "Стивен Кинг"],
    },
}


def get_number_data(n: int, lang: str = "ru") -> dict | None:
    nd = NUMBER_DATA.get(n)
    if not nd:
        nd = NUMBER_DATA.get(reduce(n))
    if not nd:
        return None
    ru = lang == "ru"
    return {
        "name": nd["name_ru"] if ru else nd["name_en"],
        "title": nd["title_ru"] if ru else nd["title_en"],
        "description": nd["description_ru"] if ru else nd["description_en"],
        "strengths": nd["strengths_ru"] if ru else nd["strengths_en"],
        "challenges": nd["challenges_ru"] if ru else nd["challenges_en"],
        "career": nd["career_ru"] if ru else nd["career_en"],
        "love": nd["love_ru"] if ru else nd["love_en"],
        "famous": nd["famous"],
    }


# ---------------------------------------------------------------------------
# Angel numbers
# ---------------------------------------------------------------------------
ANGEL_NUMBERS: dict[str, dict] = {
    "00:00": {
        "meaning_ru": "Начало нового цикла. Вселенная обнуляет счётчик — загадайте желание и начните с чистого листа.",
        "meaning_en": "Start of a new cycle. The universe resets the counter — make a wish and start fresh.",
    },
    "01:01": {
        "meaning_ru": "Ваши мысли материализуются. Следите за тем, о чём думаете — это станет реальностью.",
        "meaning_en": "Your thoughts are materializing. Watch what you think — it will become reality.",
    },
    "02:02": {
        "meaning_ru": "Доверьтесь процессу. Партнёрство и сотрудничество принесут результат.",
        "meaning_en": "Trust the process. Partnership and cooperation will bring results.",
    },
    "03:03": {
        "meaning_ru": "Вознесённые мастера рядом. Творческая энергия на пике — действуйте.",
        "meaning_en": "Ascended masters are near. Creative energy is at its peak — take action.",
    },
    "04:04": {
        "meaning_ru": "Ангелы защищают вас. Фундамент вашей жизни укрепляется.",
        "meaning_en": "Angels are protecting you. The foundation of your life is being strengthened.",
    },
    "05:05": {
        "meaning_ru": "Грядут важные перемены. Примите их — они к лучшему.",
        "meaning_en": "Important changes are coming. Accept them — they are for the better.",
    },
    "06:06": {
        "meaning_ru": "Уделите внимание семье и дому. Гармония в близких отношениях важнее карьеры.",
        "meaning_en": "Pay attention to family and home. Harmony in close relationships matters more than career.",
    },
    "07:07": {
        "meaning_ru": "Вы на правильном пути духовного развития. Продолжайте медитировать и изучать себя.",
        "meaning_en": "You are on the right path of spiritual development. Keep meditating and studying yourself.",
    },
    "08:08": {
        "meaning_ru": "Финансовое изобилие приближается. Вы заслуживаете процветания.",
        "meaning_en": "Financial abundance is approaching. You deserve prosperity.",
    },
    "09:09": {
        "meaning_ru": "Цикл завершается. Отпустите старое — новое уже на пороге.",
        "meaning_en": "A cycle is ending. Let go of the old — the new is on the threshold.",
    },
    "10:10": {
        "meaning_ru": "Высшие силы подтверждают ваш выбор. Доверьтесь интуиции.",
        "meaning_en": "Higher forces confirm your choice. Trust your intuition.",
    },
    "11:11": {
        "meaning_ru": "Портал возможностей открыт. Ваши мысли мгновенно материализуются — думайте о хорошем.",
        "meaning_en": "Portal of opportunities is open. Your thoughts instantly materialize — think positive.",
    },
    "12:12": {
        "meaning_ru": "Оптимизм принесёт плоды. Верьте в лучшее — вселенная на вашей стороне.",
        "meaning_en": "Optimism will bear fruit. Believe in the best — the universe is on your side.",
    },
    "13:13": {
        "meaning_ru": "Трансформация неизбежна. Не бойтесь перемен — они несут обновление.",
        "meaning_en": "Transformation is inevitable. Don't fear changes — they bring renewal.",
    },
    "14:14": {
        "meaning_ru": "Ангелы помогают сохранить баланс. Умеренность — ключ к успеху.",
        "meaning_en": "Angels help maintain balance. Moderation is the key to success.",
    },
    "15:15": {
        "meaning_ru": "Перемены в личной жизни. Любовь и отношения выходят на новый уровень.",
        "meaning_en": "Changes in personal life. Love and relationships reach a new level.",
    },
    "16:16": {
        "meaning_ru": "Отпустите иллюзии. Истина освободит вас от ложных привязанностей.",
        "meaning_en": "Let go of illusions. Truth will free you from false attachments.",
    },
    "17:17": {
        "meaning_ru": "Вы на пороге удачи. Ваши усилия скоро будут вознаграждены.",
        "meaning_en": "You are on the verge of luck. Your efforts will soon be rewarded.",
    },
    "18:18": {
        "meaning_ru": "Финансовый цикл завершается позитивно. Ожидайте прибыли.",
        "meaning_en": "Financial cycle is ending positively. Expect profit.",
    },
    "19:19": {
        "meaning_ru": "Завершите начатое. Пора собрать урожай своих трудов.",
        "meaning_en": "Finish what you started. Time to harvest your efforts.",
    },
    "20:20": {
        "meaning_ru": "Божественная поддержка усиливается. Вера и терпение приведут к цели.",
        "meaning_en": "Divine support is strengthening. Faith and patience will lead to your goal.",
    },
    "21:21": {
        "meaning_ru": "Оставайтесь позитивными. Ваш оптимизм притягивает нужных людей.",
        "meaning_en": "Stay positive. Your optimism attracts the right people.",
    },
    "22:22": {
        "meaning_ru": "Мастер-вибрация. Ваши мечты обретают форму — не останавливайтесь.",
        "meaning_en": "Master vibration. Your dreams are taking shape — don't stop.",
    },
    "23:23": {
        "meaning_ru": "Вознесённые мастера помогают вам. Доверяйте своим талантам и действуйте.",
        "meaning_en": "Ascended masters are helping you. Trust your talents and take action.",
    },
    "111": {
        "meaning_ru": "Мощный поток энергии. Ваши мысли мгновенно обретают форму — контролируйте их.",
        "meaning_en": "Powerful energy flow. Your thoughts instantly take form — control them.",
    },
    "222": {
        "meaning_ru": "Всё идёт по плану. Не теряйте веру — результат уже близко.",
        "meaning_en": "Everything is going according to plan. Don't lose faith — the result is near.",
    },
    "333": {
        "meaning_ru": "Вознесённые мастера окружают вас любовью. Раскройте свои творческие способности.",
        "meaning_en": "Ascended masters surround you with love. Unleash your creative abilities.",
    },
    "444": {
        "meaning_ru": "Тысячи ангелов рядом. Вы в полной безопасности — продолжайте путь.",
        "meaning_en": "Thousands of angels are near. You are completely safe — continue your path.",
    },
    "555": {
        "meaning_ru": "Масштабные перемены на горизонте. Будьте готовы — жизнь меняет курс.",
        "meaning_en": "Major changes on the horizon. Be ready — life is changing course.",
    },
    "666": {
        "meaning_ru": "Верните баланс в материальный мир. Духовное важнее материального.",
        "meaning_en": "Restore balance in the material world. Spiritual matters more than material.",
    },
    "777": {
        "meaning_ru": "Божественная удача! Вы полностью выровнены с потоком вселенной.",
        "meaning_en": "Divine luck! You are fully aligned with the universal flow.",
    },
    "888": {
        "meaning_ru": "Финансовое изобилие льётся рекой. Цикл процветания начался.",
        "meaning_en": "Financial abundance is flowing. A cycle of prosperity has begun.",
    },
    "999": {
        "meaning_ru": "Великое завершение. Глава закрывается — новая уже пишется.",
        "meaning_en": "Great completion. A chapter is closing — a new one is already being written.",
    },
    "1111": {
        "meaning_ru": "Космический портал открыт. Всё, о чём вы думаете, воплотится. Загадайте самое сокровенное.",
        "meaning_en": "Cosmic portal is open. Everything you think will manifest. Make your deepest wish.",
    },
    "2222": {
        "meaning_ru": "Мастер-строитель. Ваш фундамент прочен — стройте мечту без страха.",
        "meaning_en": "Master builder. Your foundation is solid — build your dream without fear.",
    },
}
