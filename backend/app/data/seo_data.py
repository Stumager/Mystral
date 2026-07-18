ZODIAC_SIGNS = [
    {"slug": "aries", "name": "Овен", "dates": "21 марта — 19 апреля", "element": "Огонь", "modality": "Кардинальный", "ruler": "Марс", "stone": "Алмаз", "color": "Красный", "number": 1, "best": ["leo", "sagittarius", "gemini"], "worst": ["cancer", "capricorn"], "keywords": ["овен характеристика", "знак зодиака овен", "гороскоп овен"]},
    {"slug": "taurus", "name": "Телец", "dates": "20 апреля — 20 мая", "element": "Земля", "modality": "Фиксированный", "ruler": "Венера", "stone": "Изумруд", "color": "Зелёный", "number": 2, "best": ["virgo", "capricorn", "cancer"], "worst": ["leo", "aquarius"], "keywords": ["телец характеристика", "знак зодиака телец", "гороскоп телец"]},
    {"slug": "gemini", "name": "Близнецы", "dates": "21 мая — 20 июня", "element": "Воздух", "modality": "Мутабельный", "ruler": "Меркурий", "stone": "Агат", "color": "Жёлтый", "number": 3, "best": ["libra", "aquarius", "aries"], "worst": ["virgo", "pisces"], "keywords": ["близнецы характеристика", "знак зодиака близнецы", "гороскоп близнецы"]},
    {"slug": "cancer", "name": "Рак", "dates": "21 июня — 22 июля", "element": "Вода", "modality": "Кардинальный", "ruler": "Луна", "stone": "Жемчуг", "color": "Серебристый", "number": 4, "best": ["scorpio", "pisces", "taurus"], "worst": ["aries", "libra"], "keywords": ["рак характеристика", "знак зодиака рак", "гороскоп рак"]},
    {"slug": "leo", "name": "Лев", "dates": "23 июля — 22 августа", "element": "Огонь", "modality": "Фиксированный", "ruler": "Солнце", "stone": "Рубин", "color": "Золотой", "number": 5, "best": ["aries", "sagittarius", "gemini"], "worst": ["taurus", "scorpio"], "keywords": ["лев характеристика", "знак зодиака лев", "гороскоп лев"]},
    {"slug": "virgo", "name": "Дева", "dates": "23 августа — 22 сентября", "element": "Земля", "modality": "Мутабельный", "ruler": "Меркурий", "stone": "Сапфир", "color": "Синий", "number": 6, "best": ["taurus", "capricorn", "cancer"], "worst": ["gemini", "sagittarius"], "keywords": ["дева характеристика", "знак зодиака дева", "гороскоп дева"]},
    {"slug": "libra", "name": "Весы", "dates": "23 сентября — 22 октября", "element": "Воздух", "modality": "Кардинальный", "ruler": "Венера", "stone": "Опал", "color": "Розовый", "number": 7, "best": ["gemini", "aquarius", "leo"], "worst": ["cancer", "capricorn"], "keywords": ["весы характеристика", "знак зодиака весы", "гороскоп весы"]},
    {"slug": "scorpio", "name": "Скорпион", "dates": "23 октября — 21 ноября", "element": "Вода", "modality": "Фиксированный", "ruler": "Плутон", "stone": "Топаз", "color": "Тёмно-красный", "number": 8, "best": ["cancer", "pisces", "virgo"], "worst": ["leo", "aquarius"], "keywords": ["скорпион характеристика", "знак зодиака скорпион", "гороскоп скорпион"]},
    {"slug": "sagittarius", "name": "Стрелец", "dates": "22 ноября — 21 декабря", "element": "Огонь", "modality": "Мутабельный", "ruler": "Юпитер", "stone": "Бирюза", "color": "Фиолетовый", "number": 9, "best": ["aries", "leo", "libra"], "worst": ["virgo", "pisces"], "keywords": ["стрелец характеристика", "знак зодиака стрелец", "гороскоп стрелец"]},
    {"slug": "capricorn", "name": "Козерог", "dates": "22 декабря — 19 января", "element": "Земля", "modality": "Кардинальный", "ruler": "Сатурн", "stone": "Гранат", "color": "Коричневый", "number": 10, "best": ["taurus", "virgo", "scorpio"], "worst": ["aries", "libra"], "keywords": ["козерог характеристика", "знак зодиака козерог", "гороскоп козерог"]},
    {"slug": "aquarius", "name": "Водолей", "dates": "20 января — 18 февраля", "element": "Воздух", "modality": "Фиксированный", "ruler": "Уран", "stone": "Аметист", "color": "Голубой", "number": 11, "best": ["gemini", "libra", "sagittarius"], "worst": ["taurus", "scorpio"], "keywords": ["водолей характеристика", "знак зодиака водолей", "гороскоп водолей"]},
    {"slug": "pisces", "name": "Рыбы", "dates": "19 февраля — 20 марта", "element": "Вода", "modality": "Мутабельный", "ruler": "Нептун", "stone": "Аквамарин", "color": "Морской", "number": 12, "best": ["cancer", "scorpio", "taurus"], "worst": ["gemini", "sagittarius"], "keywords": ["рыбы характеристика", "знак зодиака рыбы", "гороскоп рыбы"]},
]
ZODIAC_BY_SLUG = {s["slug"]: s for s in ZODIAC_SIGNS}

TAROT_MAJOR = [
    "the-fool", "the-magician", "the-high-priestess", "the-empress", "the-emperor",
    "the-hierophant", "the-lovers", "the-chariot", "strength", "the-hermit",
    "wheel-of-fortune", "justice", "the-hanged-man", "death", "temperance",
    "the-devil", "the-tower", "the-star", "the-moon", "the-sun",
    "judgement", "the-world",
]
TAROT_MAJOR_RU = [
    "Шут", "Маг", "Верховная Жрица", "Императрица", "Император",
    "Иерофант", "Влюблённые", "Колесница", "Сила", "Отшельник",
    "Колесо Фортуны", "Справедливость", "Повешенный", "Смерть", "Умеренность",
    "Дьявол", "Башня", "Звезда", "Луна", "Солнце",
    "Суд", "Мир",
]
SUITS = ["wands", "cups", "swords", "pentacles"]
SUITS_RU = ["Жезлов", "Кубков", "Мечей", "Пентаклей"]
RANKS = ["ace", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "page", "knight", "queen", "king"]
RANKS_RU = ["Туз", "Двойка", "Тройка", "Четвёрка", "Пятёрка", "Шестёрка", "Семёрка", "Восьмёрка", "Девятка", "Десятка", "Паж", "Рыцарь", "Королева", "Король"]

TAROT_CARDS: list[dict] = []
for i, slug in enumerate(TAROT_MAJOR):
    TAROT_CARDS.append({"slug": slug, "name_ru": TAROT_MAJOR_RU[i], "number": i, "arcana": "major", "suit": None, "keywords": [f"таро {TAROT_MAJOR_RU[i].lower()}", f"значение {TAROT_MAJOR_RU[i].lower()}"]})
idx = 22
for si, suit in enumerate(SUITS):
    for ri, rank in enumerate(RANKS):
        slug = f"{rank}-of-{suit}"
        name_ru = f"{RANKS_RU[ri]} {SUITS_RU[si]}"
        TAROT_CARDS.append({"slug": slug, "name_ru": name_ru, "number": idx, "arcana": "minor", "suit": suit, "keywords": [f"таро {name_ru.lower()}", f"значение {name_ru.lower()}"]})
        idx += 1
TAROT_BY_SLUG = {c["slug"]: c for c in TAROT_CARDS}

RUNE_SEO = [
    {"slug": "fehu", "name": "Феху", "symbol": "ᚠ", "aett": 1, "keywords": ["руна феху значение", "феху толкование"]},
    {"slug": "uruz", "name": "Уруз", "symbol": "ᚢ", "aett": 1, "keywords": ["руна уруз значение"]},
    {"slug": "thurisaz", "name": "Турисаз", "symbol": "ᚦ", "aett": 1, "keywords": ["руна турисаз значение"]},
    {"slug": "ansuz", "name": "Ансуз", "symbol": "ᚨ", "aett": 1, "keywords": ["руна ансуз значение"]},
    {"slug": "raido", "name": "Райдо", "symbol": "ᚱ", "aett": 1, "keywords": ["руна райдо значение"]},
    {"slug": "kenaz", "name": "Кеназ", "symbol": "ᚲ", "aett": 1, "keywords": ["руна кеназ значение"]},
    {"slug": "gebo", "name": "Гебо", "symbol": "ᚷ", "aett": 1, "keywords": ["руна гебо значение"]},
    {"slug": "wunjo", "name": "Вуньо", "symbol": "ᚹ", "aett": 1, "keywords": ["руна вуньо значение"]},
    {"slug": "hagalaz", "name": "Хагалаз", "symbol": "ᚺ", "aett": 2, "keywords": ["руна хагалаз значение"]},
    {"slug": "nauthiz", "name": "Наутиз", "symbol": "ᚾ", "aett": 2, "keywords": ["руна наутиз значение"]},
    {"slug": "isa", "name": "Иса", "symbol": "ᛁ", "aett": 2, "keywords": ["руна иса значение"]},
    {"slug": "jera", "name": "Йера", "symbol": "ᛃ", "aett": 2, "keywords": ["руна йера значение"]},
    {"slug": "eihwaz", "name": "Эйваз", "symbol": "ᛇ", "aett": 2, "keywords": ["руна эйваз значение"]},
    {"slug": "perthro", "name": "Перт", "symbol": "ᛈ", "aett": 2, "keywords": ["руна перт значение"]},
    {"slug": "algiz", "name": "Альгиз", "symbol": "ᛉ", "aett": 2, "keywords": ["руна альгиз значение"]},
    {"slug": "sowilo", "name": "Совило", "symbol": "ᛊ", "aett": 2, "keywords": ["руна совило значение"]},
    {"slug": "tiwaz", "name": "Тиваз", "symbol": "ᛏ", "aett": 3, "keywords": ["руна тиваз значение"]},
    {"slug": "berkano", "name": "Беркана", "symbol": "ᛒ", "aett": 3, "keywords": ["руна беркана значение"]},
    {"slug": "ehwaz", "name": "Эваз", "symbol": "ᛖ", "aett": 3, "keywords": ["руна эваз значение"]},
    {"slug": "mannaz", "name": "Манназ", "symbol": "ᛗ", "aett": 3, "keywords": ["руна манназ значение"]},
    {"slug": "laguz", "name": "Лагуз", "symbol": "ᛚ", "aett": 3, "keywords": ["руна лагуз значение"]},
    {"slug": "ingwaz", "name": "Ингуз", "symbol": "ᛜ", "aett": 3, "keywords": ["руна ингуз значение"]},
    {"slug": "dagaz", "name": "Дагаз", "symbol": "ᛞ", "aett": 3, "keywords": ["руна дагаз значение"]},
    {"slug": "othala", "name": "Отала", "symbol": "ᛟ", "aett": 3, "keywords": ["руна отала значение"]},
]
RUNE_BY_SLUG = {r["slug"]: r for r in RUNE_SEO}

NUMEROLOGY_SEO = [
    {"slug": "life-path-1", "number": 1, "name": "Лидер", "keywords": ["число жизненного пути 1", "нумерология 1"]},
    {"slug": "life-path-2", "number": 2, "name": "Дипломат", "keywords": ["число жизненного пути 2", "нумерология 2"]},
    {"slug": "life-path-3", "number": 3, "name": "Творец", "keywords": ["число жизненного пути 3", "нумерология 3"]},
    {"slug": "life-path-4", "number": 4, "name": "Строитель", "keywords": ["число жизненного пути 4", "нумерология 4"]},
    {"slug": "life-path-5", "number": 5, "name": "Искатель", "keywords": ["число жизненного пути 5", "нумерология 5"]},
    {"slug": "life-path-6", "number": 6, "name": "Хранитель", "keywords": ["число жизненного пути 6", "нумерология 6"]},
    {"slug": "life-path-7", "number": 7, "name": "Мыслитель", "keywords": ["число жизненного пути 7", "нумерология 7"]},
    {"slug": "life-path-8", "number": 8, "name": "Магнат", "keywords": ["число жизненного пути 8", "нумерология 8"]},
    {"slug": "life-path-9", "number": 9, "name": "Гуманист", "keywords": ["число жизненного пути 9", "нумерология 9"]},
]
NUMEROLOGY_BY_SLUG = {n["slug"]: n for n in NUMEROLOGY_SEO}

# name/symbol mirror app/api/v1/natal.py's PLANET_NAMES_RU/PLANET_NAMES_EN/PLANET_SYMBOLS
# for the 10 classical planets only (excludes true_node/south_node/chiron) — kept as a
# separate hardcoded copy rather than importing natal.py, matching this file's existing
# convention of zero cross-module imports; keep in sync by hand if those ever change.
NATAL_PLANETS = [
    {"slug": "sun", "name": "Солнце", "name_en": "Sun", "symbol": "☀️", "keywords": ["солнце в натальной карте", "значение солнца в гороскопе"]},
    {"slug": "moon", "name": "Луна", "name_en": "Moon", "symbol": "🌙", "keywords": ["луна в натальной карте", "значение луны в гороскопе"]},
    {"slug": "mercury", "name": "Меркурий", "name_en": "Mercury", "symbol": "☿", "keywords": ["меркурий в натальной карте", "значение меркурия в гороскопе"]},
    {"slug": "venus", "name": "Венера", "name_en": "Venus", "symbol": "♀", "keywords": ["венера в натальной карте", "значение венеры в гороскопе"]},
    {"slug": "mars", "name": "Марс", "name_en": "Mars", "symbol": "♂", "keywords": ["марс в натальной карте", "значение марса в гороскопе"]},
    {"slug": "jupiter", "name": "Юпитер", "name_en": "Jupiter", "symbol": "♃", "keywords": ["юпитер в натальной карте", "значение юпитера в гороскопе"]},
    {"slug": "saturn", "name": "Сатурн", "name_en": "Saturn", "symbol": "♄", "keywords": ["сатурн в натальной карте", "значение сатурна в гороскопе"]},
    {"slug": "uranus", "name": "Уран", "name_en": "Uranus", "symbol": "♅", "keywords": ["уран в натальной карте", "значение урана в гороскопе"]},
    {"slug": "neptune", "name": "Нептун", "name_en": "Neptune", "symbol": "♆", "keywords": ["нептун в натальной карте", "значение нептуна в гороскопе"]},
    {"slug": "pluto", "name": "Плутон", "name_en": "Pluto", "symbol": "♇", "keywords": ["плутон в натальной карте", "значение плутона в гороскопе"]},
]
NATAL_PLANETS_BY_SLUG = {p["slug"]: p for p in NATAL_PLANETS}

# Thin index only — rich per-day content lives in app/data/lunar_days.py /
# app/data/lunar_i18n.py (reused via localize_lunar_day in seo_i18n.py). Slug is the
# plain day number as a string ("1".."30"), matching the URL /lunar-calendar/day/{n}
# and lunar_i18n.LUNAR_DAYS_I18N's own "1".."30" string keys directly.
LUNAR_DAY_SEO = [
    {"slug": str(n), "number": n, "keywords": [f"{n} лунный день значение", f"{n}-й лунный день"]}
    for n in range(1, 31)
]
LUNAR_DAY_BY_SLUG = {d["slug"]: d for d in LUNAR_DAY_SEO}
