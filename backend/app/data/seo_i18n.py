"""Static translations for multilingual SEO pages (TZ-037c).

Russian content stays in seo_data.py and is served from root paths;
this module covers the 5 prefixed languages (en/es/pt/tr/uk) plus the
per-language UI chrome (nav, breadcrumbs, CTA, format strings) for all 6.
Language codes match the rest of the platform: uk, not ua.
"""

from app.core.structural_i18n import localized_field, pick, pick_list
from app.data.lunar_days import LUNAR_DAYS
from app.data.lunar_i18n import LUNAR_DAYS_I18N
from app.data.natal_i18n import PLANET_NAMES_I18N
from app.data.seo_data import ZODIAC_BY_SLUG

BASE_URL = "https://mystral.space"

PREFIX_LANGS = ("en", "es", "pt", "tr", "uk")
ALL_LANGS = ("ru",) + PREFIX_LANGS

LANG_NATIVE = {
    "ru": "Русский", "en": "English", "es": "Español",
    "pt": "Português", "tr": "Türkçe", "uk": "Українська",
}

# hreflang region-neutral codes are the same as our own codes
OG_LOCALE = {"ru": "ru_RU", "en": "en_US", "es": "es_ES", "pt": "pt_BR", "tr": "tr_TR", "uk": "uk_UA"}


def url_prefix(lang: str) -> str:
    return "" if lang == "ru" else f"/{lang}"


def abs_url(lang: str, path: str) -> str:
    return f"{BASE_URL}{url_prefix(lang)}{path}"


def hreflang_alternates(path: str) -> list[tuple[str, str]]:
    """7 pairs: 6 languages + x-default pointing at the Russian original."""
    alts = [(lang, abs_url(lang, path)) for lang in ALL_LANGS]
    alts.append(("x-default", abs_url("ru", path)))
    return alts


# ---------------------------------------------------------------------------
# UI chrome + title/description/h1 format strings.
# The ru entries mirror the previously hardcoded template/handler strings
# byte-for-byte so Russian pages do not change.
# ---------------------------------------------------------------------------

UI = {
    "ru": {
        "nav_home": "Главная", "nav_zodiac": "Зодиак", "nav_tarot": "Таро", "nav_runes": "Руны",
        "nav_numerology": "Нумерология",
        "bc_home": "Главная", "bc_zodiac": "Знаки зодиака", "bc_tarot": "Карты Таро",
        "bc_runes": "Руны", "bc_numerology": "Нумерология", "bc_number": "Число {number}",
        "faq_title": "Часто задаваемые вопросы",
        "cta_title": "Откройте Mystral",
        "cta_default": "Персональный гороскоп, натальная карта, Таро и руны — бесплатно.",
        "cta_button": "Попробовать бесплатно",
        "footer": "© 2026 Mystral. Эзотерическая платформа.",
        "label_stone": "Камень", "label_color": "Цвет", "label_type": "Тип",
        "other_signs": "Другие знаки зодиака", "other_cards": "Другие карты",
        "major_arcana": "Старший Аркан", "major_arcana_plural": "Старшие Арканы",
        "all_runes": "Все руны Футарка", "other_numbers": "Другие числа жизненного пути",
        "number_link": "Число {number} — {name}",
        "aett_fmt": "{aett}-й атт",
        "constellation_alt": "Созвездие {name} — знак зодиака",
        "card_alt": "{name} — карта Таро",
        "zodiac_h1": "{name} — знак зодиака: характер и гороскоп",
        "zodiac_title": "{name} — характеристика, гороскоп и совместимость | Mystral",
        "zodiac_desc": "{name} — знак {element} ({dates}). Характер, совместимость, карьера и любовь. Персональный гороскоп, натальная карта и расклады Таро бесплатно на Mystral — эзотерической платформе.",
        "tarot_h1": "{name} — значение в Таро",
        "tarot_title": "{name} — значение карты Таро | Mystral",
        "tarot_desc": "Значение карты Таро «{name}» в прямом и обратном положении. Толкование в любви, карьере, финансах.",
        "rune_h1": "Руна {name} — значение и толкование",
        "rune_title": "Руна {name} — значение и толкование | Mystral",
        "rune_desc": "Руна {name} ({symbol}) — подробное значение в гадании, магическое применение и использование в ставах.",
        "num_h1": "Число жизненного пути {number} — {name}",
        "num_title": "Число жизненного пути {number} — значение | Mystral",
        "num_desc": "Число жизненного пути {number} «{name}» — характер, предназначение, карьера и отношения в нумерологии.",
        "zodiac_hub_h1": "Знаки зодиака — характеристика и совместимость",
        "zodiac_hub_intro": "Все 12 знаков зодиака с подробной характеристикой, совместимостью и персональным гороскопом на каждый день.",
        "zodiac_hub_title": "Знаки зодиака — характеристика и совместимость | Mystral",
        "zodiac_hub_desc": "Все 12 знаков зодиака с подробной характеристикой, совместимостью и персональным гороскопом. Узнайте свой знак на Mystral.",
        "tarot_hub_h1": "Карты Таро — значение всех 78 карт",
        "tarot_hub_intro": "Полный справочник карт Таро: 22 Старших Аркана и 56 Младших Арканов с подробным значением в прямом и обратном положении.",
        "tarot_hub_title": "Карты Таро — значение всех 78 карт | Mystral",
        "tarot_hub_desc": "Полный справочник карт Таро: 22 Старших Аркана и 56 Младших Арканов с подробным значением.",
        "runes_hub_h1": "Руны Старшего Футарка — значение и толкование",
        "runes_hub_intro": "24 руны Старшего Футарка с подробным значением, толкованием в гадании и применением в магических ставах.",
        "runes_hub_title": "Руны Старшего Футарка — значение и толкование | Mystral",
        "runes_hub_desc": "24 руны Старшего Футарка с подробным значением, толкованием и применением в магических ставах.",
        "numerology_hub_h1": "Числа жизненного пути — нумерология по дате рождения",
        "numerology_hub_intro": "Девять чисел жизненного пути от 1 до 9 с подробным значением: характер, предназначение, карьера, любовь и отношения по классической нумерологии.",
        "numerology_hub_title": "Числа жизненного пути — нумерология | Mystral",
        "numerology_hub_desc": "Все девять чисел жизненного пути в нумерологии: характер, предназначение и совместимость. Бесплатный нумерологический разбор по дате рождения и имени на Mystral.",
        "nav_natal": "Натальная карта", "nav_lunar": "Лунный календарь",
        "bc_natal": "Натальная карта", "bc_lunar": "Лунный календарь", "bc_lunar_day": "{number}-й лунный день",
        "natal_hub_h1": "Натальная карта — значение планет в гороскопе",
        "natal_hub_intro": "Десять планет натальной карты и их значение в гороскопе рождения — от Солнца и Луны до Плутона. Узнайте, как расположение планет влияет на характер и судьбу.",
        "natal_hub_title": "Натальная карта — значение планет в гороскопе | Mystral",
        "natal_hub_desc": "Значение планет в натальной карте: Солнце, Луна, Меркурий, Венера, Марс, Юпитер, Сатурн, Уран, Нептун, Плутон. Бесплатный расчёт натальной карты на Mystral.",
        "natal_planet_h1": "{name} в натальной карте — значение и влияние",
        "natal_planet_title": "{name} в натальной карте — значение | Mystral",
        "natal_planet_desc": "Значение планеты {name} в натальной карте: характер, знаки зодиака, дома гороскопа, любовь и карьера.",
        "other_planets": "Другие планеты натальной карты",
        "lunar_hub_h1": "Лунный календарь — 30 лунных дней",
        "lunar_hub_intro": "Все 30 лунных дней с подробным значением: здоровье, красота, деньги, любовь, работа и духовные практики на каждый день лунного цикла.",
        "lunar_hub_title": "Лунный календарь — значение 30 лунных дней | Mystral",
        "lunar_hub_desc": "Полный лунный календарь: значение всех 30 лунных дней, благоприятные и неблагоприятные дела, талисманы. Персональный лунный гороскоп на Mystral.",
        "lunar_day_h1": "{number}-й лунный день — значение",
        "lunar_day_title": "{number}-й лунный день — значение | Mystral",
        "lunar_day_desc": "{number}-й лунный день «{title}» — подробное значение, благоприятные и неблагоприятные дела, талисманы и советы.",
        "other_lunar_days": "Другие лунные дни",
        "label_favorable": "Благоприятно", "label_unfavorable": "Неблагоприятно", "label_stones": "Камни-талисманы",
        "nav_compat": "Совместимость", "bc_compat": "Совместимость",
        "compat_hub_h1": "Совместимость знаков зодиака",
        "compat_hub_title": "Совместимость знаков зодиака — полное руководство | Mystral",
        "compat_hub_desc": "Совместимость всех знаков зодиака в любви, браке и дружбе. Как стихии, полярность и планеты влияют на отношения. Бесплатный расчёт совместимости на Mystral.",
        "compat_by_sign": "Совместимость по знаку",
        "compat_sign_h1": "Совместимость {name} с другими знаками зодиака",
        "compat_sign_title": "Совместимость {name} — с кем подходит по гороскопу | Mystral",
        "compat_sign_desc": "Совместимость знака {name} в любви, браке и дружбе с другими знаками зодиака. Лучшие и сложные пары.",
        "label_best": "Лучшая совместимость", "label_worst": "Сложная совместимость",
        "other_compat_signs": "Совместимость других знаков",
        "natal_house_h1": "{number}-й дом гороскопа — {name}",
        "natal_house_title": "{number}-й дом гороскопа — {name} | Mystral",
        "natal_house_desc": "Значение {number}-го дома натальной карты «{name}»: за что отвечает, какие планеты усиливают, как трактовать в гороскопе.",
        "other_houses": "Другие дома гороскопа", "natal_houses_title": "Дома гороскопа",
        "natal_planets_title": "Планеты гороскопа",
        "ascendant_h1": "Асцендент в натальной карте — значение",
        "ascendant_title": "Асцендент — значение восходящего знака | Mystral",
        "ascendant_desc": "Что такое асцендент в натальной карте, как он влияет на внешность и первое впечатление, как рассчитать восходящий знак.",
        # TZ-110: pillar-landing chrome (/natal-chart, /lunar-calendar, /compatibility).
        # The three CTA names come from the TZ-095 glossary — never "AI"/"рассчитать".
        "home_icon_title": "На главную",
        "pillar_cta_natal": "Послание светил",
        "pillar_cta_lunar": "Зов Луны",
        "pillar_cta_compat": "Голос звёзд",
        "pillar_cta_hint": "Бесплатно, в приложении Mystral",
        "preview_title": "Так выглядит разбор",
        "preview_badge": "Пример",
        "preview_love": "Любовь", "preview_friendship": "Дружба", "preview_work": "Работа",
        "preview_score_label": "Общая совместимость",
        "preview_natal_quote": "Солнце в десятом доме даёт тягу к признанию: вам важно, чтобы дело было видно. Луна в четвёртом уравновешивает это потребностью в тихом доме.",
        "preview_lunar_quote": "Одиннадцатый лунный день — пик силы месяца. Хорошо начинать то, что откладывали, и плохо — спорить и переедать.",
        "preview_compat_quote": "Огонь и Воздух раздувают друг друга: Льву нужен зритель, Весам — собеседник. Слабое место пары — быт, а не чувства.",
        "hero_natal_alt": "Колесо натальной карты с планетами и аспектами",
        "hero_lunar_alt": "Лунный круг из 30 дней с фазами Луны",
        "hero_compat_alt": "Два круга знаков зодиака, соединённые линиями связи",
        # TZ-111: E-E-A-T — footer trust links + /about page + pillar method notes.
        "nav_about": "О проекте",
        "footer_privacy": "Конфиденциальность",
        "footer_terms": "Условия использования",
        "footer_legal": "Самозанятый Нечунаев Александр Вячеславович · ИНН 230307450300",
        "bc_about": "О проекте",
        "about_title": "О проекте Mystral — кто мы и как считаем | Mystral",
        "about_desc": "Кто делает Mystral, на каких расчётах основаны натальная карта, лунный календарь, совместимость и Матрица судьбы, и как с нами связаться.",
        "about_h1": "О проекте Mystral",
        "about_lede": "Mystral — эзотерическая платформа: натальные карты, лунный календарь, совместимость, Таро, руны, нумерология и Матрица судьбы. Здесь — кто её делает и на чём основаны расчёты.",
        "about_who_h2": "Кто стоит за Mystral",
        "about_who_body": "Mystral разрабатывает и поддерживает Александр Нечунаев, зарегистрированный как самозанятый (ИНН 230307450300). Это независимый проект без внешнего инвестора и анонимной команды — с автором можно связаться напрямую по email.",
        "about_method_h2": "На чём основаны расчёты",
        "about_method_natal": "Натальная карта — астрономический расчёт положений планет на эфемеридах Swiss Ephemeris, с точностью, сопоставимой с профессиональным астрологическим ПО.",
        "about_method_lunar": "Лунный календарь — фаза и лунные сутки вычисляются по астрономическому синодическому циклу Луны, трактовки даны по традиционной системе 30 лунных дней.",
        "about_method_compat": "Совместимость сочетает несколько классических техник: сравнение знаков и стихий, нумерологию, китайский зодиак и синастрию — сопоставление аспектов между двумя реальными натальными картами.",
        "about_method_matrix": "Формула Матрицы судьбы перед запуском была сверена с независимыми источниками и калькуляторами — цифры на схеме совпадают с ними до последней точки.",
        "about_method_numerology": "Нумерология строится на классическом методе таблицы Пифагора.",
        "about_method_tarot": "Значения карт Таро и рун опираются на традиционные, общепринятые толкования этих систем.",
        "about_ai_disclosure": "Пояснительный текст — советы, описания, ответы на частые вопросы — формулируется языковыми моделями на основе уже рассчитанных данных: сначала расчёт, потом текст, а не наоборот.",
        "about_trust_h2": "Почему можно доверять",
        "about_trust_body": "Мы не скрываем, кто мы и как считаем. Формулы проверяются по независимым источникам до релиза, юридические реквизиты и контакты открыты, а обработка персональных данных описана в Политике конфиденциальности.",
        "about_legal_lede": "Подробнее:",
        "method_note_natal": "Расчёт — по реальным астрономическим эфемеридам Swiss Ephemeris.",
        "method_note_lunar": "Фаза Луны и лунные сутки рассчитываются астрономически, трактовка — по традиционному календарю.",
        "method_note_compat": "Разбор сочетает классическую синастрию с проверенными техниками по знакам и стихиям.",
        "method_note_more": "Подробнее о методологии",
        "about_matrix_label": "Матрица судьбы",
        # TZ-113: /destiny-matrix pillar + 22 arcana leaf pages. CTA and
        # light/shadow labels reuse the exact in-app matrix.* glossary terms
        # (frontend/src/i18n/locales/*.json) rather than inventing new ones.
        "nav_matrix": "Матрица судьбы", "bc_matrix": "Матрица судьбы",
        "pillar_cta_matrix": "Послание арканов",
        "hero_matrix_alt": "Восьмиконечная звезда Матрицы судьбы — личный и родовой квадраты",
        "method_note_matrix": "Формула Матрицы судьбы сверена с независимыми источниками и калькуляторами перед запуском.",
        "destiny_hub_h1": "Матрица судьбы — расчёт по дате рождения",
        "destiny_hub_intro": "Матрица судьбы — восьмиконечная звезда из личного и родового квадратов: каждая точка получает число одного из 22 арканов. Расчёт по дню, месяцу и году рождения, толкование раскрывает светлую и теневую сторону энергии каждой точки.",
        "destiny_hub_title": "Матрица судьбы — расчёт онлайн по дате рождения | Mystral",
        "destiny_hub_desc": "Матрица судьбы по дате рождения: личный и родовой квадраты, 22 аркана, светлая и теневая сторона каждой точки. Как рассчитывается октаграмма и что она показывает.",
        "arcana_list_title": "Все 22 аркана Матрицы",
        "destiny_arcana_h1": "{name} — {number}-й аркан в Матрице судьбы",
        "destiny_arcana_title": "{name} — {number}-й аркан Матрицы судьбы | Mystral",
        "destiny_arcana_desc": "{name} — значение {number}-го аркана в Матрице судьбы: светлая и теневая сторона, проявление в личном и родовом квадрате.",
        "other_arcana": "Другие арканы Матрицы",
        "label_light": "В плюсе", "label_shadow": "В тени",
        "preview_matrix_quote": "Точка опоры показывает главную задачу воплощения, личный квадрат — характер и путь, родовой — то, что досталось по наследству и что предстоит трансформировать.",
        "point_core": "Точка опоры", "point_personality": "Личность", "point_talents": "Таланты",
    },
    "en": {
        "nav_home": "Home", "nav_zodiac": "Zodiac", "nav_tarot": "Tarot", "nav_runes": "Runes",
        "nav_numerology": "Numerology",
        "bc_home": "Home", "bc_zodiac": "Zodiac Signs", "bc_tarot": "Tarot Cards",
        "bc_runes": "Runes", "bc_numerology": "Numerology", "bc_number": "Number {number}",
        "faq_title": "Frequently Asked Questions",
        "cta_title": "Discover Mystral",
        "cta_default": "Personal horoscope, natal chart, Tarot and runes — free.",
        "cta_button": "Try for free",
        "footer": "© 2026 Mystral. Esoteric platform.",
        "label_stone": "Stone", "label_color": "Color", "label_type": "Type",
        "other_signs": "Other zodiac signs", "other_cards": "Other cards",
        "major_arcana": "Major Arcana", "major_arcana_plural": "Major Arcana",
        "all_runes": "All Futhark runes", "other_numbers": "Other life path numbers",
        "number_link": "Number {number} — {name}",
        "aett_fmt": "Aett {aett}",
        "constellation_alt": "The {name} constellation — zodiac sign",
        "card_alt": "{name} — Tarot card",
        "zodiac_h1": "{name} — Zodiac Sign: Character and Horoscope",
        "zodiac_title": "{name} — Traits, Horoscope and Compatibility | Mystral",
        "zodiac_desc": "{name} — {element} sign ({dates}). Character, compatibility, career and love. Free personal horoscope, natal chart and Tarot readings on Mystral, the esoteric platform.",
        "tarot_h1": "{name} — Tarot Card Meaning",
        "tarot_title": "{name} — Tarot Card Meaning | Mystral",
        "tarot_desc": "The meaning of the {name} Tarot card, upright and reversed. Interpretation in love, career and finances.",
        "rune_h1": "The {name} Rune — Meaning and Interpretation",
        "rune_title": "The {name} Rune — Meaning and Interpretation | Mystral",
        "rune_desc": "The {name} rune ({symbol}) — detailed meaning in divination, magical uses and bind runes.",
        "num_h1": "Life Path Number {number} — {name}",
        "num_title": "Life Path Number {number} — Meaning | Mystral",
        "num_desc": "Life path number {number}, “{name}” — character, purpose, career and relationships in numerology.",
        "zodiac_hub_h1": "Zodiac Signs — Traits and Compatibility",
        "zodiac_hub_intro": "All 12 zodiac signs with detailed traits, compatibility and a personal daily horoscope.",
        "zodiac_hub_title": "Zodiac Signs — Traits and Compatibility | Mystral",
        "zodiac_hub_desc": "All 12 zodiac signs with detailed traits, compatibility and a personal horoscope. Find your sign on Mystral.",
        "tarot_hub_h1": "Tarot Cards — the Meaning of All 78 Cards",
        "tarot_hub_intro": "A complete Tarot reference: 22 Major Arcana and 56 Minor Arcana with detailed upright and reversed meanings.",
        "tarot_hub_title": "Tarot Cards — the Meaning of All 78 Cards | Mystral",
        "tarot_hub_desc": "A complete Tarot reference: 22 Major Arcana and 56 Minor Arcana with detailed meanings.",
        "runes_hub_h1": "Elder Futhark Runes — Meaning and Interpretation",
        "runes_hub_intro": "The 24 Elder Futhark runes with detailed meanings, divination interpretation and use in bind runes.",
        "runes_hub_title": "Elder Futhark Runes — Meaning and Interpretation | Mystral",
        "runes_hub_desc": "The 24 Elder Futhark runes with detailed meanings, interpretation and magical uses.",
        "numerology_hub_h1": "Life Path Numbers — Numerology by Birth Date",
        "numerology_hub_intro": "The nine life path numbers, 1 through 9, with detailed meanings: character, purpose, career and relationships in classical numerology.",
        "numerology_hub_title": "Life Path Numbers — Numerology | Mystral",
        "numerology_hub_desc": "All nine life path numbers in numerology: character, purpose and compatibility. Free numerology reading by birth date and name on Mystral.",
        "nav_natal": "Natal Chart", "nav_lunar": "Lunar Calendar",
        "bc_natal": "Natal Chart", "bc_lunar": "Lunar Calendar", "bc_lunar_day": "Lunar Day {number}",
        "natal_hub_h1": "Natal Chart — Meaning of the Planets in Astrology",
        "natal_hub_intro": "The ten planets of the natal chart and their meaning in a birth horoscope — from the Sun and Moon to Pluto. Discover how planetary placements shape character and destiny.",
        "natal_hub_title": "Natal Chart — Meaning of the Planets | Mystral",
        "natal_hub_desc": "The meaning of the planets in a natal chart: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto. Free natal chart calculation on Mystral.",
        "natal_planet_h1": "{name} in the Natal Chart — Meaning and Influence",
        "natal_planet_title": "{name} in the Natal Chart — Meaning | Mystral",
        "natal_planet_desc": "The meaning of {name} in the natal chart: personality, zodiac signs, houses, love and career.",
        "other_planets": "Other Natal Chart Planets",
        "lunar_hub_h1": "Lunar Calendar — All 30 Lunar Days",
        "lunar_hub_intro": "All 30 lunar days with detailed meanings: health, beauty, money, love, work and spiritual practice for every day of the lunar cycle.",
        "lunar_hub_title": "Lunar Calendar — Meaning of the 30 Lunar Days | Mystral",
        "lunar_hub_desc": "The complete lunar calendar: the meaning of all 30 lunar days, favorable and unfavorable activities, talismans. Personal lunar horoscope on Mystral.",
        "lunar_day_h1": "Lunar Day {number} — Meaning",
        "lunar_day_title": "Lunar Day {number} — Meaning | Mystral",
        "lunar_day_desc": "Lunar day {number}, \"{title}\" — detailed meaning, favorable and unfavorable activities, talismans and advice.",
        "other_lunar_days": "Other Lunar Days",
        "label_favorable": "Favorable", "label_unfavorable": "Unfavorable", "label_stones": "Talisman Stones",
        "nav_compat": "Compatibility", "bc_compat": "Compatibility",
        "compat_hub_h1": "Zodiac Sign Compatibility",
        "compat_hub_title": "Zodiac Sign Compatibility — the Complete Guide | Mystral",
        "compat_hub_desc": "The compatibility of every zodiac sign in love, marriage and friendship. How elements, polarity and ruling planets shape a relationship. Free compatibility calculation on Mystral.",
        "compat_by_sign": "Compatibility by Sign",
        "compat_sign_h1": "{name} Compatibility with Other Zodiac Signs",
        "compat_sign_title": "{name} Compatibility — Who {name} Matches With | Mystral",
        "compat_sign_desc": "The compatibility of {name} in love, marriage and friendship with other zodiac signs. Best and challenging matches.",
        "label_best": "Best Compatibility", "label_worst": "Challenging Compatibility",
        "other_compat_signs": "Compatibility of Other Signs",
        "natal_house_h1": "House {number} of the Horoscope — {name}",
        "natal_house_title": "House {number} of the Horoscope — {name} | Mystral",
        "natal_house_desc": "The meaning of house {number} of the natal chart, \"{name}\": what it governs, which planets strengthen it, how to interpret it in a horoscope.",
        "other_houses": "Other Horoscope Houses", "natal_houses_title": "Horoscope Houses",
        "natal_planets_title": "Horoscope Planets",
        "ascendant_h1": "The Ascendant in the Natal Chart — Meaning",
        "ascendant_title": "Ascendant — the Meaning of the Rising Sign | Mystral",
        "ascendant_desc": "What the ascendant is in a natal chart, how it shapes appearance and first impressions, and how to calculate your rising sign.",
        "home_icon_title": "Home",
        "pillar_cta_natal": "Message of the Luminaries",
        "pillar_cta_lunar": "Call of the Moon",
        "pillar_cta_compat": "Voice of the Stars",
        "pillar_cta_hint": "Free, inside the Mystral app",
        "preview_title": "This is what a reading looks like",
        "preview_badge": "Example",
        "preview_love": "Love", "preview_friendship": "Friendship", "preview_work": "Work",
        "preview_score_label": "Overall match",
        "preview_natal_quote": "The Sun in the tenth house gives a pull toward recognition — you need your work to be seen. The Moon in the fourth balances that with a need for a quiet home.",
        "preview_lunar_quote": "The eleventh lunar day is the month's peak of strength. A good day to begin what you kept postponing, a poor one for arguments and heavy meals.",
        "preview_compat_quote": "Fire and Air feed each other: Leo needs an audience, Libra needs a conversation. This pair's weak spot is daily routine, not feeling.",
        "hero_natal_alt": "A natal chart wheel with planets and aspects",
        "hero_lunar_alt": "A lunar circle of 30 days with the phases of the Moon",
        "hero_compat_alt": "Two zodiac circles joined by lines of connection",
        # TZ-111: E-E-A-T — footer trust links + /about page + pillar method notes.
        "nav_about": "About",
        "footer_privacy": "Privacy",
        "footer_terms": "Terms of Use",
        "footer_legal": "Alexander Nechunaev, sole proprietor · Tax ID 230307450300",
        "bc_about": "About",
        "about_title": "About Mystral — who we are and how we calculate | Mystral",
        "about_desc": "Who builds Mystral, what the natal chart, lunar calendar, compatibility and Destiny Matrix calculations are based on, and how to reach us.",
        "about_h1": "About Mystral",
        "about_lede": "Mystral is an esoteric platform: natal charts, lunar calendar, compatibility, Tarot, runes, numerology and the Destiny Matrix. Here's who builds it and what the calculations are based on.",
        "about_who_h2": "Who's behind Mystral",
        "about_who_body": "Mystral is built and maintained by Alexander Nechunaev, registered as a sole proprietor (Tax ID 230307450300). It's an independent project with no outside investor and no anonymous team — you can reach the author directly by email.",
        "about_method_h2": "What the calculations are based on",
        "about_method_natal": "The natal chart is a real astronomical calculation of planetary positions using Swiss Ephemeris data, with accuracy comparable to professional astrology software.",
        "about_method_lunar": "The lunar calendar computes the Moon's phase and lunar day from the real astronomical synodic cycle; interpretations follow the traditional 30-day lunar calendar system.",
        "about_method_compat": "Compatibility combines several classical techniques: sign and element comparison, numerology, Chinese zodiac, and synastry — comparing the aspects between two real natal charts.",
        "about_method_matrix": "The Destiny Matrix formula was checked against independent sources and calculators before launch — the numbers on the chart match them down to the last point.",
        "about_method_numerology": "Numerology is built on the classical Pythagorean square method.",
        "about_method_tarot": "Tarot card and rune meanings follow the traditional, widely accepted interpretations of these systems.",
        "about_ai_disclosure": "The explanatory text — advice, descriptions, FAQ answers — is written by language models grounded in the data that's already been calculated: calculation first, text second, never the other way around.",
        "about_trust_h2": "Why you can trust this",
        "about_trust_body": "We don't hide who we are or how we calculate. Formulas are checked against independent sources before release, legal details and contact information are public, and personal data handling is described in the Privacy Policy.",
        "about_legal_lede": "Read more:",
        "method_note_natal": "Calculated from real astronomical Swiss Ephemeris data.",
        "method_note_lunar": "Moon phase and lunar day are calculated astronomically; interpretation follows the traditional calendar.",
        "method_note_compat": "The reading combines classical synastry with proven sign- and element-based techniques.",
        "method_note_more": "More about our methodology",
        "about_matrix_label": "Destiny Matrix",
        # TZ-113
        "nav_matrix": "Destiny Matrix", "bc_matrix": "Destiny Matrix",
        "pillar_cta_matrix": "Message of the Arcana",
        "hero_matrix_alt": "An eight-pointed star of the Destiny Matrix — the personal and ancestral squares",
        "method_note_matrix": "The Destiny Matrix formula was checked against independent sources and calculators before launch.",
        "destiny_hub_h1": "Destiny Matrix — Calculated from Your Birth Date",
        "destiny_hub_intro": "The Destiny Matrix is an eight-pointed star built from a personal and an ancestral square, where every point resolves to one of 22 arcana. The calculation uses the day, month and year of birth; the reading covers each point's light and shadow energy.",
        "destiny_hub_title": "Destiny Matrix — Free Online Calculation by Birth Date | Mystral",
        "destiny_hub_desc": "The Destiny Matrix by birth date: the personal and ancestral squares, 22 arcana, the light and shadow side of every point. How the octagram is calculated and what it shows.",
        "arcana_list_title": "All 22 Arcana of the Matrix",
        "destiny_arcana_h1": "{name} — Arcanum {number} in the Destiny Matrix",
        "destiny_arcana_title": "{name} — Arcanum {number} of the Destiny Matrix | Mystral",
        "destiny_arcana_desc": "{name} — the meaning of arcanum {number} in the Destiny Matrix: its light and shadow side, and how it shows up in the personal and ancestral square.",
        "other_arcana": "Other Arcana of the Matrix",
        "label_light": "At its best", "label_shadow": "In shadow",
        "preview_matrix_quote": "The core point shows the central task of this lifetime; the personal square shapes character and path, while the ancestral square carries what was inherited and what still needs transforming.",
        "point_core": "Inner core", "point_personality": "Personality", "point_talents": "Talents",
    },
    "es": {
        "nav_home": "Inicio", "nav_zodiac": "Zodiaco", "nav_tarot": "Tarot", "nav_runes": "Runas",
        "nav_numerology": "Numerología",
        "bc_home": "Inicio", "bc_zodiac": "Signos del zodiaco", "bc_tarot": "Cartas del Tarot",
        "bc_runes": "Runas", "bc_numerology": "Numerología", "bc_number": "Número {number}",
        "faq_title": "Preguntas frecuentes",
        "cta_title": "Descubre Mystral",
        "cta_default": "Horóscopo personal, carta natal, Tarot y runas — gratis.",
        "cta_button": "Probar gratis",
        "footer": "© 2026 Mystral. Plataforma esotérica.",
        "label_stone": "Piedra", "label_color": "Color", "label_type": "Tipo",
        "other_signs": "Otros signos del zodiaco", "other_cards": "Otras cartas",
        "major_arcana": "Arcano Mayor", "major_arcana_plural": "Arcanos Mayores",
        "all_runes": "Todas las runas del Futhark", "other_numbers": "Otros números del camino de vida",
        "number_link": "Número {number} — {name}",
        "aett_fmt": "Aett {aett}",
        "constellation_alt": "La constelación de {name} — signo del zodiaco",
        "card_alt": "{name} — carta del Tarot",
        "zodiac_h1": "{name} — signo del zodiaco: carácter y horóscopo",
        "zodiac_title": "{name} — características, horóscopo y compatibilidad | Mystral",
        "zodiac_desc": "{name} — signo de {element} ({dates}). Carácter, compatibilidad, carrera y amor. Horóscopo personal, carta natal y tiradas de Tarot gratis en Mystral, la plataforma esotérica.",
        "tarot_h1": "{name} — significado en el Tarot",
        "tarot_title": "{name} — significado de la carta del Tarot | Mystral",
        "tarot_desc": "Significado de la carta del Tarot «{name}» al derecho y al revés. Interpretación en el amor, la carrera y las finanzas.",
        "rune_h1": "Runa {name} — significado e interpretación",
        "rune_title": "Runa {name} — significado e interpretación | Mystral",
        "rune_desc": "La runa {name} ({symbol}) — significado detallado en la adivinación, uso mágico y talismanes rúnicos.",
        "num_h1": "Camino de vida {number} — {name}",
        "num_title": "Camino de vida {number} — significado | Mystral",
        "num_desc": "El camino de vida {number}, «{name}»: carácter, propósito, carrera y relaciones en la numerología.",
        "zodiac_hub_h1": "Signos del zodiaco — características y compatibilidad",
        "zodiac_hub_intro": "Los 12 signos del zodiaco con características detalladas, compatibilidad y horóscopo personal para cada día.",
        "zodiac_hub_title": "Signos del zodiaco — características y compatibilidad | Mystral",
        "zodiac_hub_desc": "Los 12 signos del zodiaco con características detalladas, compatibilidad y horóscopo personal. Descubre tu signo en Mystral.",
        "tarot_hub_h1": "Cartas del Tarot — significado de las 78 cartas",
        "tarot_hub_intro": "Guía completa del Tarot: 22 Arcanos Mayores y 56 Arcanos Menores con significado detallado al derecho y al revés.",
        "tarot_hub_title": "Cartas del Tarot — significado de las 78 cartas | Mystral",
        "tarot_hub_desc": "Guía completa del Tarot: 22 Arcanos Mayores y 56 Arcanos Menores con significado detallado.",
        "runes_hub_h1": "Runas del Futhark Antiguo — significado e interpretación",
        "runes_hub_intro": "Las 24 runas del Futhark Antiguo con significado detallado, interpretación en la adivinación y uso en talismanes.",
        "runes_hub_title": "Runas del Futhark Antiguo — significado e interpretación | Mystral",
        "runes_hub_desc": "Las 24 runas del Futhark Antiguo con significado detallado, interpretación y usos mágicos.",
        "numerology_hub_h1": "Números del camino de vida — numerología por fecha de nacimiento",
        "numerology_hub_intro": "Los nueve números del camino de vida, del 1 al 9, con significado detallado: carácter, propósito, carrera y relaciones según la numerología clásica.",
        "numerology_hub_title": "Números del camino de vida — numerología | Mystral",
        "numerology_hub_desc": "Los nueve números del camino de vida en la numerología: carácter, propósito y compatibilidad. Cálculo numerológico gratis por fecha de nacimiento y nombre en Mystral.",
        "nav_natal": "Carta Natal", "nav_lunar": "Calendario Lunar",
        "bc_natal": "Carta Natal", "bc_lunar": "Calendario Lunar", "bc_lunar_day": "Día Lunar {number}",
        "natal_hub_h1": "Carta Natal — Significado de los Planetas en Astrología",
        "natal_hub_intro": "Los diez planetas de la carta natal y su significado en el horóscopo de nacimiento — del Sol y la Luna a Plutón. Descubre cómo la posición de los planetas moldea el carácter y el destino.",
        "natal_hub_title": "Carta Natal — Significado de los Planetas | Mystral",
        "natal_hub_desc": "El significado de los planetas en la carta natal: Sol, Luna, Mercurio, Venus, Marte, Júpiter, Saturno, Urano, Neptuno, Plutón. Cálculo gratuito de la carta natal en Mystral.",
        "natal_planet_h1": "{name} en la Carta Natal — Significado e Influencia",
        "natal_planet_title": "{name} en la Carta Natal — Significado | Mystral",
        "natal_planet_desc": "El significado de {name} en la carta natal: personalidad, signos del zodiaco, casas astrológicas, amor y carrera.",
        "other_planets": "Otros Planetas de la Carta Natal",
        "lunar_hub_h1": "Calendario Lunar — Los 30 Días Lunares",
        "lunar_hub_intro": "Los 30 días lunares con significado detallado: salud, belleza, dinero, amor, trabajo y práctica espiritual para cada día del ciclo lunar.",
        "lunar_hub_title": "Calendario Lunar — Significado de los 30 Días Lunares | Mystral",
        "lunar_hub_desc": "El calendario lunar completo: el significado de los 30 días lunares, actividades favorables y desfavorables, talismanes. Horóscopo lunar personal en Mystral.",
        "lunar_day_h1": "Día Lunar {number} — Significado",
        "lunar_day_title": "Día Lunar {number} — Significado | Mystral",
        "lunar_day_desc": "El día lunar {number}, «{title}» — significado detallado, actividades favorables y desfavorables, talismanes y consejos.",
        "other_lunar_days": "Otros Días Lunares",
        "label_favorable": "Favorable", "label_unfavorable": "Desfavorable", "label_stones": "Piedras Talismán",
        "nav_compat": "Compatibilidad", "bc_compat": "Compatibilidad",
        "compat_hub_h1": "Compatibilidad de los signos del zodiaco",
        "compat_hub_title": "Compatibilidad de los signos del zodiaco — la guía completa | Mystral",
        "compat_hub_desc": "La compatibilidad de todos los signos del zodiaco en el amor, el matrimonio y la amistad. Cómo los elementos, la polaridad y los planetas regentes moldean una relación. Cálculo de compatibilidad gratis en Mystral.",
        "compat_by_sign": "Compatibilidad por signo",
        "compat_sign_h1": "Compatibilidad de {name} con otros signos del zodiaco",
        "compat_sign_title": "Compatibilidad de {name} — con quién combina | Mystral",
        "compat_sign_desc": "La compatibilidad de {name} en el amor, el matrimonio y la amistad con otros signos del zodiaco. Las mejores parejas y las más difíciles.",
        "label_best": "Mejor compatibilidad", "label_worst": "Compatibilidad difícil",
        "other_compat_signs": "Compatibilidad de otros signos",
        "natal_house_h1": "Casa {number} del horóscopo — {name}",
        "natal_house_title": "Casa {number} del horóscopo — {name} | Mystral",
        "natal_house_desc": "El significado de la casa {number} de la carta natal, «{name}»: qué rige, qué planetas la fortalecen, cómo interpretarla en un horóscopo.",
        "other_houses": "Otras casas del horóscopo", "natal_houses_title": "Casas del horóscopo",
        "natal_planets_title": "Planetas del horóscopo",
        "ascendant_h1": "El Ascendente en la Carta Natal — Significado",
        "ascendant_title": "Ascendente — el significado del signo ascendente | Mystral",
        "ascendant_desc": "Qué es el ascendente en una carta natal, cómo moldea la apariencia y la primera impresión, y cómo calcular tu signo ascendente.",
        "home_icon_title": "Inicio",
        "pillar_cta_natal": "Mensaje de los Astros",
        "pillar_cta_lunar": "Llamada de la Luna",
        "pillar_cta_compat": "Voz de las Estrellas",
        "pillar_cta_hint": "Gratis, en la app de Mystral",
        "preview_title": "Así se ve una lectura",
        "preview_badge": "Ejemplo",
        "preview_love": "Amor", "preview_friendship": "Amistad", "preview_work": "Trabajo",
        "preview_score_label": "Compatibilidad general",
        "preview_natal_quote": "El Sol en la casa diez impulsa hacia el reconocimiento: necesitas que tu trabajo se vea. La Luna en la cuatro lo equilibra con la necesidad de un hogar tranquilo.",
        "preview_lunar_quote": "El undécimo día lunar es el pico de fuerza del mes. Buen día para empezar lo aplazado, malo para discutir y comer de más.",
        "preview_compat_quote": "Fuego y Aire se avivan mutuamente: Leo necesita público, Libra necesita conversación. El punto débil de la pareja es la rutina, no el sentimiento.",
        "hero_natal_alt": "Rueda de la carta natal con planetas y aspectos",
        "hero_lunar_alt": "Un círculo lunar de 30 días con las fases de la Luna",
        "hero_compat_alt": "Dos círculos zodiacales unidos por líneas de conexión",
        # TZ-111: E-E-A-T — footer trust links + /about page + pillar method notes.
        "nav_about": "Sobre nosotros",
        "footer_privacy": "Privacidad",
        "footer_terms": "Términos de uso",
        "footer_legal": "Alexander Nechunaev, autónomo · ID fiscal 230307450300",
        "bc_about": "Sobre nosotros",
        "about_title": "Sobre Mystral — quiénes somos y cómo calculamos | Mystral",
        "about_desc": "Quién crea Mystral, en qué se basan los cálculos de la carta natal, el calendario lunar, la compatibilidad y la Matriz del Destino, y cómo contactarnos.",
        "about_h1": "Sobre Mystral",
        "about_lede": "Mystral es una plataforma esotérica: cartas natales, calendario lunar, compatibilidad, Tarot, runas, numerología y la Matriz del Destino. Aquí explicamos quién la crea y en qué se basan los cálculos.",
        "about_who_h2": "Quién está detrás de Mystral",
        "about_who_body": "Mystral es desarrollado y mantenido por Alexander Nechunaev, registrado como autónomo (ID fiscal 230307450300). Es un proyecto independiente, sin inversores externos ni equipo anónimo — puedes contactar directamente al autor por email.",
        "about_method_h2": "En qué se basan los cálculos",
        "about_method_natal": "La carta natal es un cálculo astronómico real de las posiciones planetarias usando datos de Swiss Ephemeris, con una precisión comparable a la del software astrológico profesional.",
        "about_method_lunar": "El calendario lunar calcula la fase y el día lunar a partir del ciclo sinódico astronómico real de la Luna; las interpretaciones siguen el sistema tradicional de 30 días lunares.",
        "about_method_compat": "La compatibilidad combina varias técnicas clásicas: comparación de signos y elementos, numerología, zodiaco chino y sinastría — comparando los aspectos entre dos cartas natales reales.",
        "about_method_matrix": "La fórmula de la Matriz del Destino se verificó con fuentes y calculadoras independientes antes del lanzamiento — las cifras del esquema coinciden con ellas hasta el último punto.",
        "about_method_numerology": "La numerología se basa en el método clásico del cuadrado de Pitágoras.",
        "about_method_tarot": "Los significados de las cartas del Tarot y las runas siguen las interpretaciones tradicionales y comúnmente aceptadas de estos sistemas.",
        "about_ai_disclosure": "El texto explicativo — consejos, descripciones, respuestas a preguntas frecuentes — se redacta con modelos de lenguaje a partir de datos ya calculados: primero el cálculo, después el texto, nunca al revés.",
        "about_trust_h2": "Por qué puedes confiar en esto",
        "about_trust_body": "No ocultamos quiénes somos ni cómo calculamos. Las fórmulas se verifican con fuentes independientes antes de publicarse, los datos legales y de contacto son públicos, y el tratamiento de datos personales se describe en la Política de Privacidad.",
        "about_legal_lede": "Más información:",
        "method_note_natal": "Calculado con datos astronómicos reales de Swiss Ephemeris.",
        "method_note_lunar": "La fase lunar y el día lunar se calculan astronómicamente; la interpretación sigue el calendario tradicional.",
        "method_note_compat": "El análisis combina la sinastría clásica con técnicas probadas por signo y elemento.",
        "method_note_more": "Más sobre nuestra metodología",
        "about_matrix_label": "Matriz del Destino",
        # TZ-113
        "nav_matrix": "Matriz del Destino", "bc_matrix": "Matriz del Destino",
        "pillar_cta_matrix": "Mensaje de los Arcanos",
        "hero_matrix_alt": "Una estrella de ocho puntas de la Matriz del Destino — los cuadrados personal y ancestral",
        "method_note_matrix": "La fórmula de la Matriz del Destino se verificó con fuentes y calculadoras independientes antes del lanzamiento.",
        "destiny_hub_h1": "Matriz del Destino — cálculo por fecha de nacimiento",
        "destiny_hub_intro": "La Matriz del Destino es una estrella de ocho puntas formada por un cuadrado personal y uno ancestral, donde cada punto se resuelve en uno de los 22 arcanos. El cálculo usa el día, el mes y el año de nacimiento; la lectura recorre el lado luminoso y la sombra de cada punto.",
        "destiny_hub_title": "Matriz del Destino — cálculo online gratis por fecha de nacimiento | Mystral",
        "destiny_hub_desc": "La Matriz del Destino por fecha de nacimiento: los cuadrados personal y ancestral, 22 arcanos, el lado luminoso y la sombra de cada punto. Cómo se calcula el octagrama y qué muestra.",
        "arcana_list_title": "Los 22 arcanos de la Matriz",
        "destiny_arcana_h1": "{name} — arcano {number} en la Matriz del Destino",
        "destiny_arcana_title": "{name} — arcano {number} de la Matriz del Destino | Mystral",
        "destiny_arcana_desc": "{name} — el significado del arcano {number} en la Matriz del Destino: su lado luminoso y su sombra, y cómo se manifiesta en el cuadrado personal y ancestral.",
        "other_arcana": "Otros arcanos de la Matriz",
        "label_light": "En su mejor versión", "label_shadow": "En sombra",
        "preview_matrix_quote": "El punto de apoyo muestra la tarea central de esta vida; el cuadrado personal moldea el carácter y el camino, mientras que el cuadrado ancestral guarda lo heredado y lo que aún falta transformar.",
        "point_core": "Punto de apoyo", "point_personality": "Personalidad", "point_talents": "Talentos",
    },
    "pt": {
        "nav_home": "Início", "nav_zodiac": "Zodíaco", "nav_tarot": "Tarô", "nav_runes": "Runas",
        "nav_numerology": "Numerologia",
        "bc_home": "Início", "bc_zodiac": "Signos do zodíaco", "bc_tarot": "Cartas de Tarô",
        "bc_runes": "Runas", "bc_numerology": "Numerologia", "bc_number": "Número {number}",
        "faq_title": "Perguntas frequentes",
        "cta_title": "Descubra o Mystral",
        "cta_default": "Horóscopo pessoal, mapa astral, Tarô e runas — grátis.",
        "cta_button": "Experimente grátis",
        "footer": "© 2026 Mystral. Plataforma esotérica.",
        "label_stone": "Pedra", "label_color": "Cor", "label_type": "Tipo",
        "other_signs": "Outros signos do zodíaco", "other_cards": "Outras cartas",
        "major_arcana": "Arcano Maior", "major_arcana_plural": "Arcanos Maiores",
        "all_runes": "Todas as runas do Futhark", "other_numbers": "Outros números do caminho de vida",
        "number_link": "Número {number} — {name}",
        "aett_fmt": "Aett {aett}",
        "constellation_alt": "A constelação de {name} — signo do zodíaco",
        "card_alt": "{name} — carta de Tarô",
        "zodiac_h1": "{name} — signo do zodíaco: caráter e horóscopo",
        "zodiac_title": "{name} — características, horóscopo e compatibilidade | Mystral",
        "zodiac_desc": "{name} — signo de {element} ({dates}). Caráter, compatibilidade, carreira e amor. Horóscopo pessoal, mapa astral e tiragens de Tarô grátis no Mystral, a plataforma esotérica.",
        "tarot_h1": "{name} — significado no Tarô",
        "tarot_title": "{name} — significado da carta de Tarô | Mystral",
        "tarot_desc": "Significado da carta de Tarô «{name}» na posição normal e invertida. Interpretação no amor, na carreira e nas finanças.",
        "rune_h1": "Runa {name} — significado e interpretação",
        "rune_title": "Runa {name} — significado e interpretação | Mystral",
        "rune_desc": "A runa {name} ({symbol}) — significado detalhado na adivinhação, uso mágico e talismãs rúnicos.",
        "num_h1": "Caminho de vida {number} — {name}",
        "num_title": "Caminho de vida {number} — significado | Mystral",
        "num_desc": "O caminho de vida {number}, «{name}»: caráter, propósito, carreira e relacionamentos na numerologia.",
        "zodiac_hub_h1": "Signos do zodíaco — características e compatibilidade",
        "zodiac_hub_intro": "Os 12 signos do zodíaco com características detalhadas, compatibilidade e horóscopo pessoal para cada dia.",
        "zodiac_hub_title": "Signos do zodíaco — características e compatibilidade | Mystral",
        "zodiac_hub_desc": "Os 12 signos do zodíaco com características detalhadas, compatibilidade e horóscopo pessoal. Descubra o seu signo no Mystral.",
        "tarot_hub_h1": "Cartas de Tarô — significado das 78 cartas",
        "tarot_hub_intro": "Guia completo do Tarô: 22 Arcanos Maiores e 56 Arcanos Menores com significado detalhado na posição normal e invertida.",
        "tarot_hub_title": "Cartas de Tarô — significado das 78 cartas | Mystral",
        "tarot_hub_desc": "Guia completo do Tarô: 22 Arcanos Maiores e 56 Arcanos Menores com significado detalhado.",
        "runes_hub_h1": "Runas do Futhark Antigo — significado e interpretação",
        "runes_hub_intro": "As 24 runas do Futhark Antigo com significado detalhado, interpretação na adivinhação e uso em talismãs.",
        "runes_hub_title": "Runas do Futhark Antigo — significado e interpretação | Mystral",
        "runes_hub_desc": "As 24 runas do Futhark Antigo com significado detalhado, interpretação e usos mágicos.",
        "numerology_hub_h1": "Números do caminho de vida — numerologia pela data de nascimento",
        "numerology_hub_intro": "Os nove números do caminho de vida, de 1 a 9, com significado detalhado: caráter, propósito, carreira e relacionamentos segundo a numerologia clássica.",
        "numerology_hub_title": "Números do caminho de vida — numerologia | Mystral",
        "numerology_hub_desc": "Os nove números do caminho de vida na numerologia: caráter, propósito e compatibilidade. Cálculo numerológico grátis pela data de nascimento e nome no Mystral.",
        "nav_natal": "Mapa Astral", "nav_lunar": "Calendário Lunar",
        "bc_natal": "Mapa Astral", "bc_lunar": "Calendário Lunar", "bc_lunar_day": "Dia Lunar {number}",
        "natal_hub_h1": "Mapa Astral — Significado dos Planetas na Astrologia",
        "natal_hub_intro": "Os dez planetas do mapa astral e seu significado no horóscopo de nascimento — do Sol e da Lua a Plutão. Descubra como a posição dos planetas molda o caráter e o destino.",
        "natal_hub_title": "Mapa Astral — Significado dos Planetas | Mystral",
        "natal_hub_desc": "O significado dos planetas no mapa astral: Sol, Lua, Mercúrio, Vênus, Marte, Júpiter, Saturno, Urano, Netuno, Plutão. Cálculo gratuito do mapa astral no Mystral.",
        "natal_planet_h1": "{name} no Mapa Astral — Significado e Influência",
        "natal_planet_title": "{name} no Mapa Astral — Significado | Mystral",
        "natal_planet_desc": "O significado de {name} no mapa astral: personalidade, signos do zodíaco, casas astrológicas, amor e carreira.",
        "other_planets": "Outros Planetas do Mapa Astral",
        "lunar_hub_h1": "Calendário Lunar — Os 30 Dias Lunares",
        "lunar_hub_intro": "Os 30 dias lunares com significado detalhado: saúde, beleza, dinheiro, amor, trabalho e prática espiritual para cada dia do ciclo lunar.",
        "lunar_hub_title": "Calendário Lunar — Significado dos 30 Dias Lunares | Mystral",
        "lunar_hub_desc": "O calendário lunar completo: o significado dos 30 dias lunares, atividades favoráveis e desfavoráveis, talismãs. Horóscopo lunar pessoal no Mystral.",
        "lunar_day_h1": "Dia Lunar {number} — Significado",
        "lunar_day_title": "Dia Lunar {number} — Significado | Mystral",
        "lunar_day_desc": "O dia lunar {number}, «{title}» — significado detalhado, atividades favoráveis e desfavoráveis, talismãs e conselhos.",
        "other_lunar_days": "Outros Dias Lunares",
        "label_favorable": "Favorável", "label_unfavorable": "Desfavorável", "label_stones": "Pedras Talismã",
        "nav_compat": "Compatibilidade", "bc_compat": "Compatibilidade",
        "compat_hub_h1": "Compatibilidade dos signos do zodíaco",
        "compat_hub_title": "Compatibilidade dos signos do zodíaco — o guia completo | Mystral",
        "compat_hub_desc": "A compatibilidade de todos os signos do zodíaco no amor, no casamento e na amizade. Como os elementos, a polaridade e os planetas regentes moldam um relacionamento. Cálculo de compatibilidade grátis no Mystral.",
        "compat_by_sign": "Compatibilidade por signo",
        "compat_sign_h1": "Compatibilidade de {name} com outros signos do zodíaco",
        "compat_sign_title": "Compatibilidade de {name} — com quem combina | Mystral",
        "compat_sign_desc": "A compatibilidade de {name} no amor, no casamento e na amizade com outros signos do zodíaco. As melhores combinações e as mais difíceis.",
        "label_best": "Melhor compatibilidade", "label_worst": "Compatibilidade difícil",
        "other_compat_signs": "Compatibilidade de outros signos",
        "natal_house_h1": "Casa {number} do horóscopo — {name}",
        "natal_house_title": "Casa {number} do horóscopo — {name} | Mystral",
        "natal_house_desc": "O significado da casa {number} do mapa astral, «{name}»: o que rege, quais planetas a fortalecem, como interpretá-la num horóscopo.",
        "other_houses": "Outras casas do horóscopo", "natal_houses_title": "Casas do horóscopo",
        "natal_planets_title": "Planetas do horóscopo",
        "ascendant_h1": "O Ascendente no Mapa Astral — Significado",
        "ascendant_title": "Ascendente — o significado do signo ascendente | Mystral",
        "ascendant_desc": "O que é o ascendente num mapa astral, como molda a aparência e a primeira impressão, e como calcular o seu signo ascendente.",
        "home_icon_title": "Início",
        "pillar_cta_natal": "Mensagem dos Astros",
        "pillar_cta_lunar": "Chamado da Lua",
        "pillar_cta_compat": "Voz das Estrelas",
        "pillar_cta_hint": "Grátis, no app Mystral",
        "preview_title": "É assim que fica a leitura",
        "preview_badge": "Exemplo",
        "preview_love": "Amor", "preview_friendship": "Amizade", "preview_work": "Trabalho",
        "preview_score_label": "Compatibilidade geral",
        "preview_natal_quote": "O Sol na décima casa puxa para o reconhecimento: você precisa que seu trabalho seja visto. A Lua na quarta equilibra isso com a necessidade de um lar tranquilo.",
        "preview_lunar_quote": "O décimo primeiro dia lunar é o pico de força do mês. Bom para começar o que foi adiado, ruim para discutir e comer demais.",
        "preview_compat_quote": "Fogo e Ar se alimentam: Leão precisa de plateia, Libra precisa de conversa. O ponto fraco do par é a rotina, não o sentimento.",
        "hero_natal_alt": "Roda do mapa astral com planetas e aspectos",
        "hero_lunar_alt": "Um círculo lunar de 30 dias com as fases da Lua",
        "hero_compat_alt": "Dois círculos zodiacais unidos por linhas de conexão",
        # TZ-111: E-E-A-T — footer trust links + /about page + pillar method notes.
        "nav_about": "Sobre nós",
        "footer_privacy": "Privacidade",
        "footer_terms": "Termos de uso",
        "footer_legal": "Alexander Nechunaev, autônomo · ID fiscal 230307450300",
        "bc_about": "Sobre nós",
        "about_title": "Sobre a Mystral — quem somos e como calculamos | Mystral",
        "about_desc": "Quem cria a Mystral, em que se baseiam os cálculos do mapa astral, calendário lunar, compatibilidade e Matriz do Destino, e como entrar em contato.",
        "about_h1": "Sobre a Mystral",
        "about_lede": "Mystral é uma plataforma esotérica: mapas astrais, calendário lunar, compatibilidade, Tarô, runas, numerologia e a Matriz do Destino. Aqui está quem a desenvolve e em que se baseiam os cálculos.",
        "about_who_h2": "Quem está por trás da Mystral",
        "about_who_body": "A Mystral é desenvolvida e mantida por Alexander Nechunaev, registrado como autônomo (ID fiscal 230307450300). É um projeto independente, sem investidor externo nem equipe anônima — você pode contatar o autor diretamente por email.",
        "about_method_h2": "Em que se baseiam os cálculos",
        "about_method_natal": "O mapa astral é um cálculo astronômico real das posições planetárias usando dados do Swiss Ephemeris, com precisão comparável à de softwares astrológicos profissionais.",
        "about_method_lunar": "O calendário lunar calcula a fase e o dia lunar a partir do ciclo sinódico astronômico real da Lua; as interpretações seguem o sistema tradicional de 30 dias lunares.",
        "about_method_compat": "A compatibilidade combina várias técnicas clássicas: comparação de signos e elementos, numerologia, zodíaco chinês e sinastria — comparando os aspectos entre dois mapas astrais reais.",
        "about_method_matrix": "A fórmula da Matriz do Destino foi verificada com fontes e calculadoras independentes antes do lançamento — os números no esquema coincidem com elas até o último ponto.",
        "about_method_numerology": "A numerologia se baseia no método clássico do quadrado de Pitágoras.",
        "about_method_tarot": "Os significados das cartas de Tarô e runas seguem as interpretações tradicionais e amplamente aceitas desses sistemas.",
        "about_ai_disclosure": "O texto explicativo — conselhos, descrições, respostas a perguntas frequentes — é redigido por modelos de linguagem a partir de dados já calculados: primeiro o cálculo, depois o texto, nunca o contrário.",
        "about_trust_h2": "Por que você pode confiar",
        "about_trust_body": "Não escondemos quem somos nem como calculamos. As fórmulas são verificadas com fontes independentes antes do lançamento, os dados legais e de contato são públicos, e o tratamento de dados pessoais está descrito na Política de Privacidade.",
        "about_legal_lede": "Saiba mais:",
        "method_note_natal": "Calculado com dados astronômicos reais do Swiss Ephemeris.",
        "method_note_lunar": "A fase lunar e o dia lunar são calculados astronomicamente; a interpretação segue o calendário tradicional.",
        "method_note_compat": "A análise combina sinastria clássica com técnicas comprovadas por signo e elemento.",
        "method_note_more": "Mais sobre nossa metodologia",
        "about_matrix_label": "Matriz do Destino",
        # TZ-113
        "nav_matrix": "Matriz do Destino", "bc_matrix": "Matriz do Destino",
        "pillar_cta_matrix": "Mensagem dos Arcanos",
        "hero_matrix_alt": "Uma estrela de oito pontas da Matriz do Destino — os quadrados pessoal e ancestral",
        "method_note_matrix": "A fórmula da Matriz do Destino foi verificada com fontes e calculadoras independentes antes do lançamento.",
        "destiny_hub_h1": "Matriz do Destino — cálculo pela data de nascimento",
        "destiny_hub_intro": "A Matriz do Destino é uma estrela de oito pontas formada por um quadrado pessoal e um ancestral, em que cada ponto resulta em um dos 22 arcanos. O cálculo usa o dia, o mês e o ano de nascimento; a leitura percorre o lado luminoso e a sombra de cada ponto.",
        "destiny_hub_title": "Matriz do Destino — cálculo online grátis pela data de nascimento | Mystral",
        "destiny_hub_desc": "A Matriz do Destino pela data de nascimento: os quadrados pessoal e ancestral, 22 arcanos, o lado luminoso e a sombra de cada ponto. Como o octagrama é calculado e o que ele mostra.",
        "arcana_list_title": "Os 22 arcanos da Matriz",
        "destiny_arcana_h1": "{name} — arcano {number} na Matriz do Destino",
        "destiny_arcana_title": "{name} — arcano {number} da Matriz do Destino | Mystral",
        "destiny_arcana_desc": "{name} — o significado do arcano {number} na Matriz do Destino: seu lado luminoso e sua sombra, e como se manifesta no quadrado pessoal e ancestral.",
        "other_arcana": "Outros arcanos da Matriz",
        "label_light": "No seu melhor", "label_shadow": "Na sombra",
        "preview_matrix_quote": "O ponto de apoio mostra a tarefa central desta vida; o quadrado pessoal molda o caráter e o caminho, enquanto o quadrado ancestral guarda o que foi herdado e o que ainda precisa ser transformado.",
        "point_core": "Ponto de apoio", "point_personality": "Personalidade", "point_talents": "Talentos",
    },
    "tr": {
        "nav_home": "Ana Sayfa", "nav_zodiac": "Burçlar", "nav_tarot": "Tarot", "nav_runes": "Rünler",
        "nav_numerology": "Numeroloji",
        "bc_home": "Ana Sayfa", "bc_zodiac": "Burçlar", "bc_tarot": "Tarot Kartları",
        "bc_runes": "Rünler", "bc_numerology": "Numeroloji", "bc_number": "Sayı {number}",
        "faq_title": "Sıkça Sorulan Sorular",
        "cta_title": "Mystral'ı Keşfedin",
        "cta_default": "Kişisel burç yorumu, doğum haritası, Tarot ve rünler — ücretsiz.",
        "cta_button": "Ücretsiz deneyin",
        "footer": "© 2026 Mystral. Ezoterik platform.",
        "label_stone": "Taş", "label_color": "Renk", "label_type": "Tip",
        "other_signs": "Diğer burçlar", "other_cards": "Diğer kartlar",
        "major_arcana": "Büyük Arkana", "major_arcana_plural": "Büyük Arkana",
        "all_runes": "Tüm Futhark rünleri", "other_numbers": "Diğer yaşam yolu sayıları",
        "number_link": "Sayı {number} — {name}",
        "aett_fmt": "{aett}. aett",
        "constellation_alt": "{name} takımyıldızı — burç",
        "card_alt": "{name} — Tarot kartı",
        "zodiac_h1": "{name} burcu: karakter ve burç yorumu",
        "zodiac_title": "{name} burcu — özellikleri, yorumu ve uyumu | Mystral",
        "zodiac_desc": "{name} — {element} burcu ({dates}). Karakter, uyum, kariyer ve aşk. Mystral ezoterik platformunda ücretsiz kişisel burç yorumu, doğum haritası ve Tarot açılımları.",
        "tarot_h1": "{name} — Tarot'ta anlamı",
        "tarot_title": "{name} — Tarot kartının anlamı | Mystral",
        "tarot_desc": "{name} Tarot kartının düz ve ters anlamı. Aşk, kariyer ve finans yorumu.",
        "rune_h1": "{name} rünü — anlamı ve yorumu",
        "rune_title": "{name} rünü — anlamı ve yorumu | Mystral",
        "rune_desc": "{name} rünü ({symbol}) — falda ayrıntılı anlamı, büyüsel kullanımı ve rün tılsımları.",
        "num_h1": "Yaşam yolu sayısı {number} — {name}",
        "num_title": "Yaşam yolu sayısı {number} — anlamı | Mystral",
        "num_desc": "Numerolojide yaşam yolu sayısı {number} «{name}» — karakter, yaşam amacı, kariyer ve ilişkiler.",
        "zodiac_hub_h1": "Burçlar — özellikleri ve uyumu",
        "zodiac_hub_intro": "12 burcun tamamı: ayrıntılı özellikler, burç uyumu ve her gün için kişisel burç yorumu.",
        "zodiac_hub_title": "Burçlar — özellikleri ve uyumu | Mystral",
        "zodiac_hub_desc": "12 burcun tamamı: ayrıntılı özellikler, uyum ve kişisel burç yorumu. Burcunuzu Mystral'da keşfedin.",
        "tarot_hub_h1": "Tarot kartları — 78 kartın anlamı",
        "tarot_hub_intro": "Eksiksiz Tarot rehberi: 22 Büyük Arkana ve 56 Küçük Arkana, düz ve ters ayrıntılı anlamlarıyla.",
        "tarot_hub_title": "Tarot kartları — 78 kartın anlamı | Mystral",
        "tarot_hub_desc": "Eksiksiz Tarot rehberi: 22 Büyük Arkana ve 56 Küçük Arkana, ayrıntılı anlamlarıyla.",
        "runes_hub_h1": "Eski Futhark rünleri — anlamı ve yorumu",
        "runes_hub_intro": "Eski Futhark'ın 24 rünü: ayrıntılı anlamları, fal yorumu ve rün tılsımlarında kullanımı.",
        "runes_hub_title": "Eski Futhark rünleri — anlamı ve yorumu | Mystral",
        "runes_hub_desc": "Eski Futhark'ın 24 rünü: ayrıntılı anlamları, yorumu ve büyüsel kullanımı.",
        "numerology_hub_h1": "Yaşam Yolu Sayıları — Doğum Tarihine Göre Numeroloji",
        "numerology_hub_intro": "1'den 9'a kadar dokuz yaşam yolu sayısının ayrıntılı anlamı: karakter, yaşam amacı, kariyer ve ilişkiler klasik numerolojiye göre.",
        "numerology_hub_title": "Yaşam Yolu Sayıları — Numeroloji | Mystral",
        "numerology_hub_desc": "Numerolojideki dokuz yaşam yolu sayısının tümü: karakter, yaşam amacı ve uyum. Mystral'da doğum tarihi ve isme göre ücretsiz numeroloji analizi.",
        "nav_natal": "Doğum Haritası", "nav_lunar": "Ay Takvimi",
        "bc_natal": "Doğum Haritası", "bc_lunar": "Ay Takvimi", "bc_lunar_day": "{number}. Ay Günü",
        "natal_hub_h1": "Doğum Haritası — Astrolojide Gezegenlerin Anlamı",
        "natal_hub_intro": "Doğum haritasının on gezegeni ve doğum burcundaki anlamları — Güneş ve Ay'dan Plüton'a kadar. Gezegen konumlarının karakteri ve kaderi nasıl şekillendirdiğini keşfedin.",
        "natal_hub_title": "Doğum Haritası — Gezegenlerin Anlamı | Mystral",
        "natal_hub_desc": "Doğum haritasında gezegenlerin anlamı: Güneş, Ay, Merkür, Venüs, Mars, Jüpiter, Satürn, Uranüs, Neptün, Plüton. Mystral'da ücretsiz doğum haritası hesaplama.",
        "natal_planet_h1": "Doğum Haritasında {name} — Anlamı ve Etkisi",
        "natal_planet_title": "Doğum Haritasında {name} — Anlamı | Mystral",
        "natal_planet_desc": "Doğum haritasında {name} gezegeninin anlamı: karakter, burçlar, evler, aşk ve kariyer.",
        "other_planets": "Diğer Doğum Haritası Gezegenleri",
        "lunar_hub_h1": "Ay Takvimi — 30 Ay Gününün Tamamı",
        "lunar_hub_intro": "Ay döngüsünün her günü için ayrıntılı anlamlarıyla 30 ay günü: sağlık, güzellik, para, aşk, iş ve manevi uygulamalar.",
        "lunar_hub_title": "Ay Takvimi — 30 Ay Gününün Anlamı | Mystral",
        "lunar_hub_desc": "Eksiksiz ay takvimi: 30 ay gününün tamamının anlamı, uğurlu ve uğursuz faaliyetler, tılsımlar. Mystral'da kişisel ay burcu yorumu.",
        "lunar_day_h1": "{number}. Ay Günü — Anlamı",
        "lunar_day_title": "{number}. Ay Günü — Anlamı | Mystral",
        "lunar_day_desc": "{number}. ay günü, «{title}» — ayrıntılı anlamı, uğurlu ve uğursuz faaliyetler, tılsımlar ve öneriler.",
        "other_lunar_days": "Diğer Ay Günleri",
        "label_favorable": "Uğurlu", "label_unfavorable": "Uğursuz", "label_stones": "Tılsım Taşları",
        "nav_compat": "Uyum", "bc_compat": "Uyum",
        "compat_hub_h1": "Burç uyumu",
        "compat_hub_title": "Burç uyumu — eksiksiz rehber | Mystral",
        "compat_hub_desc": "Tüm burçların aşkta, evlilikte ve arkadaşlıkta uyumu. Elementler, kutupluluk ve yönetici gezegenler bir ilişkiyi nasıl şekillendirir. Mystral'da ücretsiz uyum hesaplama.",
        "compat_by_sign": "Burca göre uyum",
        "compat_sign_h1": "{name} burcunun diğer burçlarla uyumu",
        "compat_sign_title": "{name} uyumu — kimle uyumlu | Mystral",
        "compat_sign_desc": "{name} burcunun aşkta, evlilikte ve arkadaşlıkta diğer burçlarla uyumu. En iyi ve en zor eşleşmeler.",
        "label_best": "En iyi uyum", "label_worst": "Zor uyum",
        "other_compat_signs": "Diğer burçların uyumu",
        "natal_house_h1": "Burç haritasının {number}. evi — {name}",
        "natal_house_title": "Burç haritasının {number}. evi — {name} | Mystral",
        "natal_house_desc": "Doğum haritasının {number}. evinin, «{name}», anlamı: neyi yönettiği, hangi gezegenlerin güçlendirdiği, burç haritasında nasıl yorumlanacağı.",
        "other_houses": "Diğer burç evleri", "natal_houses_title": "Burç evleri",
        "natal_planets_title": "Burç gezegenleri",
        "ascendant_h1": "Doğum Haritasında Yükselen Burç — Anlamı",
        "ascendant_title": "Yükselen Burç — anlamı | Mystral",
        "ascendant_desc": "Doğum haritasında yükselen burç nedir, görünüşü ve ilk izlenimi nasıl şekillendirir, yükselen burcunuzu nasıl hesaplarsınız.",
        "home_icon_title": "Ana Sayfa",
        "pillar_cta_natal": "Gök Cisimlerinin Mesajı",
        "pillar_cta_lunar": "Ay'ın Çağrısı",
        "pillar_cta_compat": "Yıldızların Sesi",
        "pillar_cta_hint": "Ücretsiz, Mystral uygulamasında",
        "preview_title": "Bir yorum böyle görünür",
        "preview_badge": "Örnek",
        "preview_love": "Aşk", "preview_friendship": "Dostluk", "preview_work": "İş",
        "preview_score_label": "Genel uyum",
        "preview_natal_quote": "Onuncu evdeki Güneş tanınma isteği verir: emeğinizin görülmesi gerekir. Dördüncü evdeki Ay bunu sessiz bir yuva ihtiyacıyla dengeler.",
        "preview_lunar_quote": "On birinci ay günü ayın güç doruğudur. Ertelediklerinize başlamak için iyi, tartışmak ve fazla yemek için kötü bir gün.",
        "preview_compat_quote": "Ateş ve Hava birbirini körükler: Aslan seyirci ister, Terazi sohbet. Bu çiftin zayıf noktası duygular değil, gündelik düzendir.",
        "hero_natal_alt": "Gezegenler ve açılarla doğum haritası çarkı",
        "hero_lunar_alt": "Ay'ın evreleriyle 30 günlük ay çemberi",
        "hero_compat_alt": "Bağlantı çizgileriyle birleşen iki burç çemberi",
        # TZ-111: E-E-A-T — footer trust links + /about page + pillar method notes.
        "nav_about": "Hakkımızda",
        "footer_privacy": "Gizlilik",
        "footer_terms": "Kullanım Koşulları",
        "footer_legal": "Alexander Nechunaev, bireysel girişimci · Vergi No 230307450300",
        "bc_about": "Hakkımızda",
        "about_title": "Mystral Hakkında — kimiz ve nasıl hesaplıyoruz | Mystral",
        "about_desc": "Mystral'ı kim yapıyor, doğum haritası, ay takvimi, uyum ve Kader Matrisi hesaplamaları neye dayanıyor ve bize nasıl ulaşabilirsiniz.",
        "about_h1": "Mystral Hakkında",
        "about_lede": "Mystral bir ezoterik platformdur: doğum haritaları, ay takvimi, uyum, Tarot, rünler, numeroloji ve Kader Matrisi. Burada kimin yaptığını ve hesaplamaların neye dayandığını anlatıyoruz.",
        "about_who_h2": "Mystral'ın arkasında kim var",
        "about_who_body": "Mystral, bireysel girişimci olarak kayıtlı Alexander Nechunaev (Vergi No 230307450300) tarafından geliştirilip sürdürülüyor. Dışarıdan yatırımcısı ve anonim ekibi olmayan bağımsız bir proje — yazara doğrudan e-posta ile ulaşabilirsiniz.",
        "about_method_h2": "Hesaplamalar neye dayanıyor",
        "about_method_natal": "Doğum haritası, Swiss Ephemeris verileriyle gezegen konumlarının gerçek astronomik hesabıdır; hassasiyeti profesyonel astroloji yazılımlarıyla kıyaslanabilir.",
        "about_method_lunar": "Ay takvimi, Ay'ın gerçek astronomik sinodik döngüsünden faz ve ay gününü hesaplar; yorumlar geleneksel 30 günlük ay takvimi sistemini izler.",
        "about_method_compat": "Uyum analizi birkaç klasik tekniği birleştirir: burç ve element karşılaştırması, numeroloji, Çin burçları ve sinastri — iki gerçek doğum haritası arasındaki açıların karşılaştırılması.",
        "about_method_matrix": "Kader Matrisi formülü, yayından önce bağımsız kaynaklar ve hesap makineleriyle karşılaştırıldı — şemadaki rakamlar son noktasına kadar eşleşiyor.",
        "about_method_numerology": "Numeroloji, klasik Pisagor karesi yöntemine dayanır.",
        "about_method_tarot": "Tarot kartı ve rün anlamları, bu sistemlerin geleneksel ve yaygın kabul gören yorumlarını izler.",
        "about_ai_disclosure": "Açıklayıcı metin — tavsiyeler, açıklamalar, sık sorulan soru yanıtları — zaten hesaplanmış verilere dayanarak dil modelleriyle yazılır: önce hesaplama, sonra metin, asla tersi değil.",
        "about_trust_h2": "Neden güvenebilirsiniz",
        "about_trust_body": "Kim olduğumuzu ve nasıl hesapladığımızı gizlemiyoruz. Formüller yayından önce bağımsız kaynaklarla karşılaştırılır, yasal bilgiler ve iletişim bilgileri açıktır, kişisel veri işleme Gizlilik Politikası'nda açıklanmıştır.",
        "about_legal_lede": "Daha fazla bilgi:",
        "method_note_natal": "Gerçek astronomik Swiss Ephemeris verileriyle hesaplanır.",
        "method_note_lunar": "Ay fazı ve ay günü astronomik olarak hesaplanır; yorum geleneksel takvimi izler.",
        "method_note_compat": "Bu analiz klasik sinastriyi burç ve element temelli kanıtlanmış tekniklerle birleştirir.",
        "method_note_more": "Yöntemimiz hakkında daha fazla bilgi",
        "about_matrix_label": "Kader Matrisi",
        # TZ-113
        "nav_matrix": "Kader Matrisi", "bc_matrix": "Kader Matrisi",
        "pillar_cta_matrix": "Arkanaların Mesajı",
        "hero_matrix_alt": "Kader Matrisi'nin sekiz köşeli yıldızı — kişisel kare ve soy karesi",
        "method_note_matrix": "Kader Matrisi formülü, yayından önce bağımsız kaynaklar ve hesap makineleriyle karşılaştırıldı.",
        "destiny_hub_h1": "Kader Matrisi — doğum tarihinden hesaplama",
        "destiny_hub_intro": "Kader Matrisi, kişisel kare ve soy karesinden oluşan sekiz köşeli bir yıldızdır; her nokta 22 arkanadan birine karşılık gelir. Hesaplama doğum günü, ayı ve yılını kullanır; yorum her noktanın en iyi hâlini ve gölgesini ele alır.",
        "destiny_hub_title": "Kader Matrisi — doğum tarihinden ücretsiz online hesaplama | Mystral",
        "destiny_hub_desc": "Doğum tarihine göre Kader Matrisi: kişisel kare ve soy karesi, 22 arkana, her noktanın en iyi hâli ve gölgesi. Sekiz köşeli yıldız nasıl hesaplanır ve neyi gösterir.",
        "arcana_list_title": "Matrisin 22 arkanasının tamamı",
        "destiny_arcana_h1": "{name} — Kader Matrisi'nde {number}. arkana",
        "destiny_arcana_title": "{name} — Kader Matrisi'nin {number}. arkanası | Mystral",
        "destiny_arcana_desc": "{name} — Kader Matrisi'nde {number}. arkananın anlamı: en iyi hâli ve gölgesi, kişisel kare ve soy karesinde nasıl ortaya çıktığı.",
        "other_arcana": "Matrisin diğer arkanaları",
        "label_light": "En iyi hâlinde", "label_shadow": "Gölgede",
        "preview_matrix_quote": "Dayanak noktası bu yaşamın temel görevini gösterir; kişisel kare karakteri ve yolu şekillendirirken, soy karesi mirası ve hâlâ dönüştürülmesi gerekeni taşır.",
        "point_core": "Dayanak noktası", "point_personality": "Kişilik", "point_talents": "Yetenekler",
    },
    "uk": {
        "nav_home": "Головна", "nav_zodiac": "Зодіак", "nav_tarot": "Таро", "nav_runes": "Руни",
        "nav_numerology": "Нумерологія",
        "bc_home": "Головна", "bc_zodiac": "Знаки зодіаку", "bc_tarot": "Карти Таро",
        "bc_runes": "Руни", "bc_numerology": "Нумерологія", "bc_number": "Число {number}",
        "faq_title": "Часті запитання",
        "cta_title": "Відкрийте Mystral",
        "cta_default": "Персональний гороскоп, натальна карта, Таро та руни — безкоштовно.",
        "cta_button": "Спробувати безкоштовно",
        "footer": "© 2026 Mystral. Езотерична платформа.",
        "label_stone": "Камінь", "label_color": "Колір", "label_type": "Тип",
        "other_signs": "Інші знаки зодіаку", "other_cards": "Інші карти",
        "major_arcana": "Старший Аркан", "major_arcana_plural": "Старші Аркани",
        "all_runes": "Усі руни Футарка", "other_numbers": "Інші числа життєвого шляху",
        "number_link": "Число {number} — {name}",
        "aett_fmt": "{aett}-й атт",
        "constellation_alt": "Сузір'я {name} — знак зодіаку",
        "card_alt": "{name} — карта Таро",
        "zodiac_h1": "{name} — знак зодіаку: характер і гороскоп",
        "zodiac_title": "{name} — характеристика, гороскоп і сумісність | Mystral",
        "zodiac_desc": "{name} ({dates}), стихія — {element}. Характер, сумісність, кар'єра та любов. Персональний гороскоп, натальна карта та розклади Таро безкоштовно на Mystral — езотеричній платформі.",
        "tarot_h1": "{name} — значення в Таро",
        "tarot_title": "{name} — значення карти Таро | Mystral",
        "tarot_desc": "Значення карти Таро «{name}» у прямому та перевернутому положенні. Тлумачення в коханні, кар'єрі, фінансах.",
        "rune_h1": "Руна {name} — значення та тлумачення",
        "rune_title": "Руна {name} — значення та тлумачення | Mystral",
        "rune_desc": "Руна {name} ({symbol}) — детальне значення в гаданні, магічне застосування та використання у ставах.",
        "num_h1": "Число життєвого шляху {number} — {name}",
        "num_title": "Число життєвого шляху {number} — значення | Mystral",
        "num_desc": "Число життєвого шляху {number} «{name}» — характер, призначення, кар'єра та стосунки в нумерології.",
        "zodiac_hub_h1": "Знаки зодіаку — характеристика та сумісність",
        "zodiac_hub_intro": "Усі 12 знаків зодіаку з детальною характеристикою, сумісністю та персональним гороскопом на кожен день.",
        "zodiac_hub_title": "Знаки зодіаку — характеристика та сумісність | Mystral",
        "zodiac_hub_desc": "Усі 12 знаків зодіаку з детальною характеристикою, сумісністю та персональним гороскопом. Дізнайтеся свій знак на Mystral.",
        "tarot_hub_h1": "Карти Таро — значення всіх 78 карт",
        "tarot_hub_intro": "Повний довідник карт Таро: 22 Старших Аркани та 56 Молодших Арканів із детальним значенням у прямому та перевернутому положенні.",
        "tarot_hub_title": "Карти Таро — значення всіх 78 карт | Mystral",
        "tarot_hub_desc": "Повний довідник карт Таро: 22 Старших Аркани та 56 Молодших Арканів із детальним значенням.",
        "runes_hub_h1": "Руни Старшого Футарка — значення та тлумачення",
        "runes_hub_intro": "24 руни Старшого Футарка з детальним значенням, тлумаченням у гаданні та застосуванням у магічних ставах.",
        "runes_hub_title": "Руни Старшого Футарка — значення та тлумачення | Mystral",
        "runes_hub_desc": "24 руни Старшого Футарка з детальним значенням, тлумаченням і застосуванням у магічних ставах.",
        "numerology_hub_h1": "Числа життєвого шляху — нумерологія за датою народження",
        "numerology_hub_intro": "Дев'ять чисел життєвого шляху від 1 до 9 з детальним значенням: характер, призначення, кар'єра, любов і стосунки за класичною нумерологією.",
        "numerology_hub_title": "Числа життєвого шляху — нумерологія | Mystral",
        "numerology_hub_desc": "Усі дев'ять чисел життєвого шляху в нумерології: характер, призначення і сумісність. Безкоштовний нумерологічний розбір за датою народження та іменем на Mystral.",
        "nav_natal": "Натальна карта", "nav_lunar": "Місячний календар",
        "bc_natal": "Натальна карта", "bc_lunar": "Місячний календар", "bc_lunar_day": "{number}-й місячний день",
        "natal_hub_h1": "Натальна карта — значення планет в астрології",
        "natal_hub_intro": "Десять планет натальної карти та їхнє значення в гороскопі народження — від Сонця і Місяця до Плутона. Дізнайтеся, як розташування планет впливає на характер і долю.",
        "natal_hub_title": "Натальна карта — значення планет | Mystral",
        "natal_hub_desc": "Значення планет у натальній карті: Сонце, Місяць, Меркурій, Венера, Марс, Юпітер, Сатурн, Уран, Нептун, Плутон. Безкоштовний розрахунок натальної карти на Mystral.",
        "natal_planet_h1": "{name} у натальній карті — значення і вплив",
        "natal_planet_title": "{name} у натальній карті — значення | Mystral",
        "natal_planet_desc": "Значення планети {name} у натальній карті: характер, знаки зодіаку, доми гороскопу, кохання та кар'єра.",
        "other_planets": "Інші планети натальної карти",
        "lunar_hub_h1": "Місячний календар — усі 30 місячних днів",
        "lunar_hub_intro": "Усі 30 місячних днів з детальним значенням: здоров'я, краса, гроші, кохання, робота та духовні практики на кожен день місячного циклу.",
        "lunar_hub_title": "Місячний календар — значення 30 місячних днів | Mystral",
        "lunar_hub_desc": "Повний місячний календар: значення всіх 30 місячних днів, сприятливі та несприятливі справи, талісмани. Персональний місячний гороскоп на Mystral.",
        "lunar_day_h1": "{number}-й місячний день — значення",
        "lunar_day_title": "{number}-й місячний день — значення | Mystral",
        "lunar_day_desc": "{number}-й місячний день «{title}» — детальне значення, сприятливі та несприятливі справи, талісмани і поради.",
        "other_lunar_days": "Інші місячні дні",
        "label_favorable": "Сприятливо", "label_unfavorable": "Несприятливо", "label_stones": "Камені-талісмани",
        "nav_compat": "Сумісність", "bc_compat": "Сумісність",
        "compat_hub_h1": "Сумісність знаків зодіаку",
        "compat_hub_title": "Сумісність знаків зодіаку — повний гід | Mystral",
        "compat_hub_desc": "Сумісність усіх знаків зодіаку в коханні, шлюбі та дружбі. Як стихії, полярність і керуючі планети впливають на стосунки. Безкоштовний розрахунок сумісності на Mystral.",
        "compat_by_sign": "Сумісність за знаком",
        "compat_sign_h1": "Сумісність {name} з іншими знаками зодіаку",
        "compat_sign_title": "Сумісність {name} — з ким підходить | Mystral",
        "compat_sign_desc": "Сумісність знака {name} в коханні, шлюбі та дружбі з іншими знаками зодіаку. Найкращі та складні пари.",
        "label_best": "Найкраща сумісність", "label_worst": "Складна сумісність",
        "other_compat_signs": "Сумісність інших знаків",
        "natal_house_h1": "{number}-й дім гороскопу — {name}",
        "natal_house_title": "{number}-й дім гороскопу — {name} | Mystral",
        "natal_house_desc": "Значення {number}-го дому натальної карти «{name}»: за що відповідає, які планети підсилюють, як тлумачити в гороскопі.",
        "other_houses": "Інші доми гороскопу", "natal_houses_title": "Доми гороскопу",
        "natal_planets_title": "Планети гороскопу",
        "ascendant_h1": "Асцендент у натальній карті — значення",
        "ascendant_title": "Асцендент — значення висхідного знака | Mystral",
        "ascendant_desc": "Що таке асцендент у натальній карті, як він впливає на зовнішність і перше враження, як розрахувати висхідний знак.",
        "home_icon_title": "На головну",
        "pillar_cta_natal": "Послання світил",
        "pillar_cta_lunar": "Поклик Місяця",
        "pillar_cta_compat": "Голос зірок",
        "pillar_cta_hint": "Безкоштовно, у застосунку Mystral",
        "preview_title": "Так виглядає розбір",
        "preview_badge": "Приклад",
        "preview_love": "Кохання", "preview_friendship": "Дружба", "preview_work": "Робота",
        "preview_score_label": "Загальна сумісність",
        "preview_natal_quote": "Сонце в десятому домі дає тягу до визнання: вам важливо, щоб справу було видно. Місяць у четвертому врівноважує це потребою в тихому домі.",
        "preview_lunar_quote": "Одинадцятий місячний день — пік сили місяця. Добре починати те, що відкладали, і погано — сперечатися та переїдати.",
        "preview_compat_quote": "Вогонь і Повітря роздмухують одне одного: Леву потрібен глядач, Терезам — співрозмовник. Слабке місце пари — побут, а не почуття.",
        "hero_natal_alt": "Колесо натальної карти з планетами та аспектами",
        "hero_lunar_alt": "Місячне коло з 30 днів із фазами Місяця",
        "hero_compat_alt": "Два кола знаків зодіаку, з'єднані лініями зв'язку",
        # TZ-111: E-E-A-T — footer trust links + /about page + pillar method notes.
        "nav_about": "Про нас",
        "footer_privacy": "Конфіденційність",
        "footer_terms": "Умови використання",
        "footer_legal": "Олександр Нечунаєв, самозайнята особа · Податковий номер 230307450300",
        "bc_about": "Про нас",
        "about_title": "Про Mystral — хто ми і як рахуємо | Mystral",
        "about_desc": "Хто створює Mystral, на чому базуються розрахунки натальної карти, місячного календаря, сумісності та Матриці долі, і як з нами зв'язатися.",
        "about_h1": "Про Mystral",
        "about_lede": "Mystral — езотерична платформа: натальні карти, місячний календар, сумісність, Таро, руни, нумерологія та Матриця долі. Тут — хто її створює і на чому базуються розрахунки.",
        "about_who_h2": "Хто стоїть за Mystral",
        "about_who_body": "Mystral розробляє й підтримує Олександр Нечунаєв, зареєстрований як самозайнята особа (податковий номер 230307450300). Це незалежний проєкт без зовнішнього інвестора й анонімної команди — з автором можна зв'язатися напряму електронною поштою.",
        "about_method_h2": "На чому базуються розрахунки",
        "about_method_natal": "Натальна карта — астрономічний розрахунок положень планет за даними Swiss Ephemeris, з точністю, порівнянною з професійним астрологічним ПЗ.",
        "about_method_lunar": "Місячний календар обчислює фазу та місячну добу за реальним астрономічним синодичним циклом Місяця; тлумачення дані за традиційною системою 30 місячних діб.",
        "about_method_compat": "Сумісність поєднує кілька класичних технік: порівняння знаків і стихій, нумерологію, китайський зодіак і синастрію — зіставлення аспектів між двома реальними натальними картами.",
        "about_method_matrix": "Формулу Матриці долі перед запуском звірили з незалежними джерелами й калькуляторами — цифри на схемі збігаються з ними до останньої точки.",
        "about_method_numerology": "Нумерологія базується на класичному методі квадрата Піфагора.",
        "about_method_tarot": "Значення карт Таро й рун спираються на традиційні, загальноприйняті тлумачення цих систем.",
        "about_ai_disclosure": "Пояснювальний текст — поради, описи, відповіді на часті запитання — формулюється мовними моделями на основі вже розрахованих даних: спочатку розрахунок, потім текст, а не навпаки.",
        "about_trust_h2": "Чому можна довіряти",
        "about_trust_body": "Ми не приховуємо, хто ми і як рахуємо. Формули перевіряються за незалежними джерелами до релізу, юридичні реквізити й контакти відкриті, а обробка персональних даних описана в Політиці конфіденційності.",
        "about_legal_lede": "Докладніше:",
        "method_note_natal": "Розрахунок — за реальними астрономічними даними Swiss Ephemeris.",
        "method_note_lunar": "Фаза Місяця та місячна доба розраховуються астрономічно, тлумачення — за традиційним календарем.",
        "method_note_compat": "Розбір поєднує класичну синастрію з перевіреними техніками за знаками й стихіями.",
        "method_note_more": "Докладніше про методологію",
        "about_matrix_label": "Матриця долі",
        # TZ-113
        "nav_matrix": "Матриця долі", "bc_matrix": "Матриця долі",
        "pillar_cta_matrix": "Послання арканів",
        "hero_matrix_alt": "Восьмипроменева зірка Матриці долі — особистий і родовий квадрати",
        "method_note_matrix": "Формулу Матриці долі перед запуском звірили з незалежними джерелами й калькуляторами.",
        "destiny_hub_h1": "Матриця долі — розрахунок за датою народження",
        "destiny_hub_intro": "Матриця долі — восьмипроменева зірка з особистого і родового квадратів: кожна точка отримує число одного з 22 арканів. Розрахунок за днем, місяцем і роком народження, тлумачення розкриває плюс і тінь енергії кожної точки.",
        "destiny_hub_title": "Матриця долі — розрахунок онлайн за датою народження | Mystral",
        "destiny_hub_desc": "Матриця долі за датою народження: особистий і родовий квадрати, 22 аркани, плюс і тінь кожної точки. Як розраховується октаграма і що вона показує.",
        "arcana_list_title": "Усі 22 аркани Матриці",
        "destiny_arcana_h1": "{name} — {number}-й аркан у Матриці долі",
        "destiny_arcana_title": "{name} — {number}-й аркан Матриці долі | Mystral",
        "destiny_arcana_desc": "{name} — значення {number}-го аркана в Матриці долі: плюс і тінь, прояв в особистому і родовому квадраті.",
        "other_arcana": "Інші аркани Матриці",
        "label_light": "У плюсі", "label_shadow": "У тіні",
        "preview_matrix_quote": "Точка опори показує головне завдання втілення, особистий квадрат — характер і шлях, родовий — те, що дісталося у спадок і що належить трансформувати.",
        "point_core": "Точка опори", "point_personality": "Особистість", "point_talents": "Таланти",
    },
}


# ---------------------------------------------------------------------------
# Zodiac: per-language names + metadata. Sign order matches seo_data.ZODIAC_SIGNS.
# ---------------------------------------------------------------------------

_SIGN_SLUGS = ["aries", "taurus", "gemini", "cancer", "leo", "virgo",
               "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
_ELEM_IDX = [0, 1, 2, 3] * 3     # Fire, Earth, Air, Water repeating
_MODE_IDX = [0, 1, 2] * 4        # Cardinal, Fixed, Mutable repeating

_ZODIAC_LANG = {
    "en": {
        "names": ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"],
        "dates": ["March 21 — April 19", "April 20 — May 20", "May 21 — June 20",
                  "June 21 — July 22", "July 23 — August 22", "August 23 — September 22",
                  "September 23 — October 22", "October 23 — November 21", "November 22 — December 21",
                  "December 22 — January 19", "January 20 — February 18", "February 19 — March 20"],
        "elements": ["Fire", "Earth", "Air", "Water"],
        "modalities": ["Cardinal", "Fixed", "Mutable"],
        "rulers": ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
                   "Venus", "Pluto", "Jupiter", "Saturn", "Uranus", "Neptune"],
        "stones": ["Diamond", "Emerald", "Agate", "Pearl", "Ruby", "Sapphire",
                   "Opal", "Topaz", "Turquoise", "Garnet", "Amethyst", "Aquamarine"],
        "colors": ["Red", "Green", "Yellow", "Silver", "Gold", "Blue",
                   "Pink", "Dark red", "Purple", "Brown", "Light blue", "Sea green"],
    },
    "es": {
        "names": ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
                  "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"],
        "dates": ["21 de marzo — 19 de abril", "20 de abril — 20 de mayo", "21 de mayo — 20 de junio",
                  "21 de junio — 22 de julio", "23 de julio — 22 de agosto", "23 de agosto — 22 de septiembre",
                  "23 de septiembre — 22 de octubre", "23 de octubre — 21 de noviembre", "22 de noviembre — 21 de diciembre",
                  "22 de diciembre — 19 de enero", "20 de enero — 18 de febrero", "19 de febrero — 20 de marzo"],
        "elements": ["Fuego", "Tierra", "Aire", "Agua"],
        "modalities": ["Cardinal", "Fijo", "Mutable"],
        "rulers": ["Marte", "Venus", "Mercurio", "Luna", "Sol", "Mercurio",
                   "Venus", "Plutón", "Júpiter", "Saturno", "Urano", "Neptuno"],
        "stones": ["Diamante", "Esmeralda", "Ágata", "Perla", "Rubí", "Zafiro",
                   "Ópalo", "Topacio", "Turquesa", "Granate", "Amatista", "Aguamarina"],
        "colors": ["Rojo", "Verde", "Amarillo", "Plateado", "Dorado", "Azul",
                   "Rosa", "Rojo oscuro", "Violeta", "Marrón", "Celeste", "Verde mar"],
    },
    "pt": {
        "names": ["Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem",
                  "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"],
        "dates": ["21 de março — 19 de abril", "20 de abril — 20 de maio", "21 de maio — 20 de junho",
                  "21 de junho — 22 de julho", "23 de julho — 22 de agosto", "23 de agosto — 22 de setembro",
                  "23 de setembro — 22 de outubro", "23 de outubro — 21 de novembro", "22 de novembro — 21 de dezembro",
                  "22 de dezembro — 19 de janeiro", "20 de janeiro — 18 de fevereiro", "19 de fevereiro — 20 de março"],
        "elements": ["Fogo", "Terra", "Ar", "Água"],
        "modalities": ["Cardinal", "Fixo", "Mutável"],
        "rulers": ["Marte", "Vênus", "Mercúrio", "Lua", "Sol", "Mercúrio",
                   "Vênus", "Plutão", "Júpiter", "Saturno", "Urano", "Netuno"],
        "stones": ["Diamante", "Esmeralda", "Ágata", "Pérola", "Rubi", "Safira",
                   "Opala", "Topázio", "Turquesa", "Granada", "Ametista", "Água-marinha"],
        "colors": ["Vermelho", "Verde", "Amarelo", "Prateado", "Dourado", "Azul",
                   "Rosa", "Vermelho escuro", "Violeta", "Marrom", "Azul-claro", "Verde-mar"],
    },
    "tr": {
        "names": ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak",
                  "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"],
        "dates": ["21 Mart — 19 Nisan", "20 Nisan — 20 Mayıs", "21 Mayıs — 20 Haziran",
                  "21 Haziran — 22 Temmuz", "23 Temmuz — 22 Ağustos", "23 Ağustos — 22 Eylül",
                  "23 Eylül — 22 Ekim", "23 Ekim — 21 Kasım", "22 Kasım — 21 Aralık",
                  "22 Aralık — 19 Ocak", "20 Ocak — 18 Şubat", "19 Şubat — 20 Mart"],
        "elements": ["Ateş", "Toprak", "Hava", "Su"],
        "modalities": ["Öncü", "Sabit", "Değişken"],
        "rulers": ["Mars", "Venüs", "Merkür", "Ay", "Güneş", "Merkür",
                   "Venüs", "Plüton", "Jüpiter", "Satürn", "Uranüs", "Neptün"],
        "stones": ["Elmas", "Zümrüt", "Akik", "İnci", "Yakut", "Safir",
                   "Opal", "Topaz", "Turkuaz", "Lal", "Ametist", "Akuamarin"],
        "colors": ["Kırmızı", "Yeşil", "Sarı", "Gümüş", "Altın", "Mavi",
                   "Pembe", "Koyu kırmızı", "Mor", "Kahverengi", "Açık mavi", "Deniz yeşili"],
    },
    "uk": {
        "names": ["Овен", "Телець", "Близнюки", "Рак", "Лев", "Діва",
                  "Терези", "Скорпіон", "Стрілець", "Козеріг", "Водолій", "Риби"],
        "dates": ["21 березня — 19 квітня", "20 квітня — 20 травня", "21 травня — 20 червня",
                  "21 червня — 22 липня", "23 липня — 22 серпня", "23 серпня — 22 вересня",
                  "23 вересня — 22 жовтня", "23 жовтня — 21 листопада", "22 листопада — 21 грудня",
                  "22 грудня — 19 січня", "20 січня — 18 лютого", "19 лютого — 20 березня"],
        "elements": ["Вогонь", "Земля", "Повітря", "Вода"],
        "modalities": ["Кардинальний", "Фіксований", "Мутабельний"],
        "rulers": ["Марс", "Венера", "Меркурій", "Місяць", "Сонце", "Меркурій",
                   "Венера", "Плутон", "Юпітер", "Сатурн", "Уран", "Нептун"],
        "stones": ["Діамант", "Смарагд", "Агат", "Перлина", "Рубін", "Сапфір",
                   "Опал", "Топаз", "Бірюза", "Гранат", "Аметист", "Аквамарин"],
        "colors": ["Червоний", "Зелений", "Жовтий", "Сріблястий", "Золотий", "Синій",
                   "Рожевий", "Темно-червоний", "Фіолетовий", "Коричневий", "Блакитний", "Морський"],
    },
}

ZODIAC_I18N = {
    lang: {
        slug: {
            "name": d["names"][i],
            "dates": d["dates"][i],
            "element": d["elements"][_ELEM_IDX[i]],
            "modality": d["modalities"][_MODE_IDX[i]],
            "ruler": d["rulers"][i],
            "stone": d["stones"][i],
            "color": d["colors"][i],
        }
        for i, slug in enumerate(_SIGN_SLUGS)
    }
    for lang, d in _ZODIAC_LANG.items()
}


# ---------------------------------------------------------------------------
# Tarot: Major Arcana names, ranks, suits, and per-language minor-card format.
# Order matches seo_data.TAROT_MAJOR / RANKS / SUITS.
# ---------------------------------------------------------------------------

TAROT_MAJOR_I18N = {
    "en": ["The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
           "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
           "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
           "The Devil", "The Tower", "The Star", "The Moon", "The Sun",
           "Judgement", "The World"],
    "es": ["El Loco", "El Mago", "La Sacerdotisa", "La Emperatriz", "El Emperador",
           "El Hierofante", "Los Enamorados", "El Carro", "La Fuerza", "El Ermitaño",
           "La Rueda de la Fortuna", "La Justicia", "El Colgado", "La Muerte", "La Templanza",
           "El Diablo", "La Torre", "La Estrella", "La Luna", "El Sol",
           "El Juicio", "El Mundo"],
    "pt": ["O Louco", "O Mago", "A Sacerdotisa", "A Imperatriz", "O Imperador",
           "O Hierofante", "Os Amantes", "O Carro", "A Força", "O Eremita",
           "A Roda da Fortuna", "A Justiça", "O Enforcado", "A Morte", "A Temperança",
           "O Diabo", "A Torre", "A Estrela", "A Lua", "O Sol",
           "O Julgamento", "O Mundo"],
    "tr": ["Deli", "Büyücü", "Baş Rahibe", "İmparatoriçe", "İmparator",
           "Aziz", "Aşıklar", "Savaş Arabası", "Güç", "Ermiş",
           "Kader Çarkı", "Adalet", "Asılan Adam", "Ölüm", "Denge",
           "Şeytan", "Kule", "Yıldız", "Ay", "Güneş",
           "Mahkeme", "Dünya"],
    "uk": ["Блазень", "Маг", "Верховна Жриця", "Імператриця", "Імператор",
           "Ієрофант", "Закохані", "Колісниця", "Сила", "Відлюдник",
           "Колесо Фортуни", "Справедливість", "Повішений", "Смерть", "Поміркованість",
           "Диявол", "Вежа", "Зірка", "Місяць", "Сонце",
           "Суд", "Світ"],
}

# Rank names in seo_data.RANKS order (ace..king). Turkish uses possessive
# forms because the card name is built suit-first ("Asa İkilisi").
RANKS_I18N = {
    "en": ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven",
           "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"],
    "es": ["As", "Dos", "Tres", "Cuatro", "Cinco", "Seis", "Siete",
           "Ocho", "Nueve", "Diez", "Sota", "Caballero", "Reina", "Rey"],
    "pt": ["Ás", "Dois", "Três", "Quatro", "Cinco", "Seis", "Sete",
           "Oito", "Nove", "Dez", "Valete", "Cavaleiro", "Rainha", "Rei"],
    "tr": ["Ası", "İkilisi", "Üçlüsü", "Dörtlüsü", "Beşlisi", "Altılısı", "Yedilisi",
           "Sekizlisi", "Dokuzlusu", "Onlusu", "Uşağı", "Şövalyesi", "Kraliçesi", "Kralı"],
    "uk": ["Туз", "Двійка", "Трійка", "Четвірка", "П'ятірка", "Шістка", "Сімка",
           "Вісімка", "Дев'ятка", "Десятка", "Паж", "Лицар", "Королева", "Король"],
}

# Suit names used inside minor-card names (seo_data.SUITS order:
# wands, cups, swords, pentacles).
_SUITS_NAME = {
    "en": ["Wands", "Cups", "Swords", "Pentacles"],
    "es": ["Bastos", "Copas", "Espadas", "Pentáculos"],
    "pt": ["Paus", "Copas", "Espadas", "Ouros"],
    "tr": ["Asa", "Kupa", "Kılıç", "Tılsım"],
    "uk": ["Жезлів", "Кубків", "Мечів", "Пентаклів"],
}

# Suit names as standalone headers (tarot hub sections, card-page label).
# ru mirrors seo_data.SUITS_RU to keep the Russian hub unchanged.
SUITS_HDR = {
    "ru": ["Жезлов", "Кубков", "Мечей", "Пентаклей"],
    "en": ["Wands", "Cups", "Swords", "Pentacles"],
    "es": ["Bastos", "Copas", "Espadas", "Pentáculos"],
    "pt": ["Paus", "Copas", "Espadas", "Ouros"],
    "tr": ["Asalar", "Kupalar", "Kılıçlar", "Tılsımlar"],
    "uk": ["Жезли", "Кубки", "Мечі", "Пентаклі"],
}

# Word order per language: "Two of Wands" vs "Dos de Bastos" vs "Asa İkilisi".
TAROT_MINOR_FMT = {
    "en": "{rank} of {suit}",
    "es": "{rank} de {suit}",
    "pt": "{rank} de {suit}",
    "tr": "{suit} {rank}",
    "uk": "{rank} {suit}",
}


# ---------------------------------------------------------------------------
# Runes: Latin names are the international standard for en/es/pt/tr;
# Ukrainian uses Cyrillic transliteration. Keys match seo_data.RUNE_SEO slugs.
# ---------------------------------------------------------------------------

_RUNE_LATIN = {
    "fehu": "Fehu", "uruz": "Uruz", "thurisaz": "Thurisaz", "ansuz": "Ansuz",
    "raido": "Raido", "kenaz": "Kenaz", "gebo": "Gebo", "wunjo": "Wunjo",
    "hagalaz": "Hagalaz", "nauthiz": "Nauthiz", "isa": "Isa", "jera": "Jera",
    "eihwaz": "Eihwaz", "perthro": "Perthro", "algiz": "Algiz", "sowilo": "Sowilo",
    "tiwaz": "Tiwaz", "berkano": "Berkano", "ehwaz": "Ehwaz", "mannaz": "Mannaz",
    "laguz": "Laguz", "ingwaz": "Ingwaz", "dagaz": "Dagaz", "othala": "Othala",
}

_RUNE_UK = {
    "fehu": "Феху", "uruz": "Уруз", "thurisaz": "Турісаз", "ansuz": "Ансуз",
    "raido": "Райдо", "kenaz": "Кеназ", "gebo": "Гебо", "wunjo": "Вуньо",
    "hagalaz": "Хагалаз", "nauthiz": "Наутіз", "isa": "Іса", "jera": "Йєра",
    "eihwaz": "Ейваз", "perthro": "Перт", "algiz": "Альгіз", "sowilo": "Совіло",
    "tiwaz": "Тіваз", "berkano": "Беркана", "ehwaz": "Еваз", "mannaz": "Манназ",
    "laguz": "Лагуз", "ingwaz": "Інгуз", "dagaz": "Дагаз", "othala": "Отала",
}

RUNE_I18N = {"en": _RUNE_LATIN, "es": _RUNE_LATIN, "pt": _RUNE_LATIN, "tr": _RUNE_LATIN, "uk": _RUNE_UK}


# ---------------------------------------------------------------------------
# Numerology archetypes (life-path-1..9 order matches seo_data.NUMEROLOGY_SEO).
# ---------------------------------------------------------------------------

_NUM_NAMES = {
    "en": ["Leader", "Diplomat", "Creator", "Builder", "Seeker", "Guardian", "Thinker", "Magnate", "Humanitarian"],
    "es": ["Líder", "Diplomático", "Creador", "Constructor", "Buscador", "Guardián", "Pensador", "Magnate", "Humanista"],
    "pt": ["Líder", "Diplomata", "Criador", "Construtor", "Buscador", "Guardião", "Pensador", "Magnata", "Humanista"],
    "tr": ["Lider", "Diplomat", "Yaratıcı", "Kurucu", "Kaşif", "Koruyucu", "Düşünür", "Yönetici", "Hümanist"],
    "uk": ["Лідер", "Дипломат", "Творець", "Будівельник", "Шукач", "Хранитель", "Мислитель", "Магнат", "Гуманіст"],
}

NUMEROLOGY_I18N = {
    lang: {f"life-path-{i + 1}": name for i, name in enumerate(names)}
    for lang, names in _NUM_NAMES.items()
}


# ---------------------------------------------------------------------------
# Localization helpers: return merged view-model dicts so templates keep
# using the same keys (sign.name, rune.name, num.name, card.display_name).
# ---------------------------------------------------------------------------

def localize_sign(sign: dict, lang: str) -> dict:
    if lang == "ru":
        return sign
    return {**sign, **ZODIAC_I18N[lang][sign["slug"]]}


def tarot_display_name(card: dict, lang: str) -> str:
    if lang == "ru":
        return card["name_ru"]
    if card["arcana"] == "major":
        return TAROT_MAJOR_I18N[lang][card["number"]]
    # minor numbers start at 22, ordered suit-major then rank (see seo_data)
    minor_idx = card["number"] - 22
    suit_idx, rank_idx = divmod(minor_idx, 14)
    return TAROT_MINOR_FMT[lang].format(
        rank=RANKS_I18N[lang][rank_idx], suit=_SUITS_NAME[lang][suit_idx],
    )


def localize_card(card: dict, lang: str) -> dict:
    return {**card, "display_name": tarot_display_name(card, lang)}


def localize_rune(rune: dict, lang: str) -> dict:
    if lang == "ru":
        return rune
    return {**rune, "name": RUNE_I18N[lang][rune["slug"]]}


def localize_num(num: dict, lang: str) -> dict:
    if lang == "ru":
        return num
    return {**num, "name": NUMEROLOGY_I18N[lang][num["slug"]]}


# ---------------------------------------------------------------------------
# Natal-chart planets (TZ-083): names reuse app.data.natal_i18n's existing
# TZ-080 translations rather than duplicating a second copy here.
# ---------------------------------------------------------------------------

def localize_natal_planet(planet: dict, lang: str) -> dict:
    if lang == "ru":
        return planet
    return {**planet, "name": localized_field(PLANET_NAMES_I18N, lang, planet["slug"], "name", planet["name_en"])}


# ---------------------------------------------------------------------------
# Lunar-calendar days (TZ-083): the thin LUNAR_DAY_SEO entry (slug/number/
# keywords only) is always merged with the rich per-day content in
# app.data.lunar_days.LUNAR_DAYS / app.data.lunar_i18n.LUNAR_DAYS_I18N, via
# the same pick()/pick_list() helpers app/api/v1/lunar.py already uses for
# the live /lunar/today endpoint — no data is duplicated here.
# ---------------------------------------------------------------------------

def localize_lunar_day(day_seo: dict, lang: str) -> dict:
    raw = LUNAR_DAYS[day_seo["number"]]
    key = day_seo["slug"]
    favorable = pick_list(raw, "favorable", lang, LUNAR_DAYS_I18N, key)
    unfavorable = pick_list(raw, "unfavorable", lang, LUNAR_DAYS_I18N, key)
    return {
        **day_seo,
        "symbol": pick(raw, "symbol", lang, LUNAR_DAYS_I18N, key),
        "title": pick(raw, "title", lang, LUNAR_DAYS_I18N, key),
        "desc": pick(raw, "desc", lang, LUNAR_DAYS_I18N, key),
        "health": pick(raw, "health", lang, LUNAR_DAYS_I18N, key),
        "stones": pick(raw, "stones", lang, LUNAR_DAYS_I18N, key),
        "energy": raw["energy"],
        "favorable": favorable,
        "unfavorable": unfavorable,
        # joined strings for prompt building — str.format(**data) can't join a list
        "favorable_text": ", ".join(favorable),
        "unfavorable_text": ", ".join(unfavorable),
    }


# ---------------------------------------------------------------------------
# Natal houses + ascendant (TZ-094): no existing structural dataset to reuse
# (unlike lunar_day/natal_planet), so names are hand-translated here directly,
# the same way ZODIAC_I18N hand-translates sign names further up this file.
# House order matches seo_data.NATAL_HOUSES (house 1..12).
# ---------------------------------------------------------------------------

_HOUSE_NAMES_LANG = {
    "en": ["House of Self", "House of Money", "House of Communication", "House of Home and Family",
           "House of Creativity", "House of Health and Work", "House of Partnership", "House of Transformation",
           "House of Philosophy", "House of Career", "House of Friendship", "House of the Subconscious"],
    "es": ["Casa del Yo", "Casa del Dinero", "Casa de la Comunicación", "Casa del Hogar y la Familia",
           "Casa de la Creatividad", "Casa de la Salud y el Trabajo", "Casa de la Pareja", "Casa de la Transformación",
           "Casa de la Filosofía", "Casa de la Carrera", "Casa de la Amistad", "Casa del Subconsciente"],
    "pt": ["Casa do Eu", "Casa do Dinheiro", "Casa da Comunicação", "Casa do Lar e da Família",
           "Casa da Criatividade", "Casa da Saúde e do Trabalho", "Casa da Parceria", "Casa da Transformação",
           "Casa da Filosofia", "Casa da Carreira", "Casa da Amizade", "Casa do Subconsciente"],
    "tr": ["Benlik Evi", "Para Evi", "İletişim Evi", "Ev ve Aile Evi",
           "Yaratıcılık Evi", "Sağlık ve Çalışma Evi", "Ortaklık Evi", "Dönüşüm Evi",
           "Felsefe Evi", "Kariyer Evi", "Arkadaşlık Evi", "Bilinçaltı Evi"],
    "uk": ["Дім Особистості", "Дім Грошей", "Дім Спілкування", "Дім Родини",
           "Дім Творчості", "Дім Здоров'я і Праці", "Дім Партнерства", "Дім Трансформації",
           "Дім Філософії", "Дім Кар'єри", "Дім Дружби", "Дім Підсвідомості"],
}
HOUSE_I18N = {
    lang: {str(i + 1): name for i, name in enumerate(names)}
    for lang, names in _HOUSE_NAMES_LANG.items()
}

_ASCENDANT_NAME = {
    "en": "Ascendant", "es": "Ascendente", "pt": "Ascendente",
    "tr": "Yükselen Burç", "uk": "Асцендент",
}


def localize_natal_house(house: dict, lang: str) -> dict:
    if lang == "ru":
        return house
    return {**house, "name": HOUSE_I18N[lang][house["slug"]]}


def localize_ascendant(asc: dict, lang: str) -> dict:
    if lang == "ru":
        return asc
    return {**asc, "name": _ASCENDANT_NAME[lang]}


# ---------------------------------------------------------------------------
# Compatibility (TZ-094): /compatibility/{sign} reuses seo_data.ZODIAC_SIGNS
# directly (same 12 signs, same slugs as /zodiac/{slug}) rather than a
# separate dataset — best/worst are the arrays already on each sign entry.
# ---------------------------------------------------------------------------

def localize_compat_sign(sign_raw: dict, lang: str) -> dict:
    sign = localize_sign(sign_raw, lang)
    best = [localize_sign(ZODIAC_BY_SLUG[s], lang)["name"] for s in sign_raw["best"]]
    worst = [localize_sign(ZODIAC_BY_SLUG[s], lang)["name"] for s in sign_raw["worst"]]
    return {
        **sign,
        "best_names": best, "worst_names": worst,
        # joined strings for prompt building — str.format(**data) can't join a list
        "best_text": ", ".join(best), "worst_text": ", ".join(worst),
    }


# ---------------------------------------------------------------------------
# Destiny Matrix (TZ-113): /destiny-matrix/arcana/{1..22} reuses the name and
# light/shadow energy already computed by app.data.destiny_matrix.
# ---------------------------------------------------------------------------

def localize_destiny_arcana(arcana_seo: dict, lang: str) -> dict:
    """Imported locally rather than at module scope: destiny_matrix.py itself
    does `from app.data.seo_i18n import TAROT_MAJOR_I18N` at import time, so a
    top-level import back into it here would be circular."""
    from app.data.destiny_matrix import arcana_energy, arcana_name
    n = arcana_seo["number"]
    energy = arcana_energy(n, lang)
    return {
        **arcana_seo,
        "name": arcana_name(n, lang),
        "light": energy["light"],
        "shadow": energy["shadow"],
    }
