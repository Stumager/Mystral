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
        "ascendant_h1": "Асцендент в натальной карте — значение",
        "ascendant_title": "Асцендент — значение восходящего знака | Mystral",
        "ascendant_desc": "Что такое асцендент в натальной карте, как он влияет на внешность и первое впечатление, как рассчитать восходящий знак.",
    },
    "en": {
        "nav_home": "Home", "nav_zodiac": "Zodiac", "nav_tarot": "Tarot", "nav_runes": "Runes",
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
        "ascendant_h1": "The Ascendant in the Natal Chart — Meaning",
        "ascendant_title": "Ascendant — the Meaning of the Rising Sign | Mystral",
        "ascendant_desc": "What the ascendant is in a natal chart, how it shapes appearance and first impressions, and how to calculate your rising sign.",
    },
    "es": {
        "nav_home": "Inicio", "nav_zodiac": "Zodiaco", "nav_tarot": "Tarot", "nav_runes": "Runas",
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
        "ascendant_h1": "El Ascendente en la Carta Natal — Significado",
        "ascendant_title": "Ascendente — el significado del signo ascendente | Mystral",
        "ascendant_desc": "Qué es el ascendente en una carta natal, cómo moldea la apariencia y la primera impresión, y cómo calcular tu signo ascendente.",
    },
    "pt": {
        "nav_home": "Início", "nav_zodiac": "Zodíaco", "nav_tarot": "Tarô", "nav_runes": "Runas",
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
        "ascendant_h1": "O Ascendente no Mapa Astral — Significado",
        "ascendant_title": "Ascendente — o significado do signo ascendente | Mystral",
        "ascendant_desc": "O que é o ascendente num mapa astral, como molda a aparência e a primeira impressão, e como calcular o seu signo ascendente.",
    },
    "tr": {
        "nav_home": "Ana Sayfa", "nav_zodiac": "Burçlar", "nav_tarot": "Tarot", "nav_runes": "Rünler",
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
        "ascendant_h1": "Doğum Haritasında Yükselen Burç — Anlamı",
        "ascendant_title": "Yükselen Burç — anlamı | Mystral",
        "ascendant_desc": "Doğum haritasında yükselen burç nedir, görünüşü ve ilk izlenimi nasıl şekillendirir, yükselen burcunuzu nasıl hesaplarsınız.",
    },
    "uk": {
        "nav_home": "Головна", "nav_zodiac": "Зодіак", "nav_tarot": "Таро", "nav_runes": "Руни",
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
        "ascendant_h1": "Асцендент у натальній карті — значення",
        "ascendant_title": "Асцендент — значення висхідного знака | Mystral",
        "ascendant_desc": "Що таке асцендент у натальній карті, як він впливає на зовнішність і перше враження, як розрахувати висхідний знак.",
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
