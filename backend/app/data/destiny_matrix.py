"""TZ-101: Матрица судьбы (Destiny Matrix) — the eight-point octagram plus
its centre, derived from a birth date.

The formula was verified against independent sources *before* implementation
(TZ-101 step 0, results recorded in PROGRESS.md): two articles with worked
examples, two independent open-source implementations, and a live calculator
run over four birth dates covering the tricky cases (day > 22, a point
landing exactly on 22). One correction came out of that check — the
right-hand point is the digit sum of the YEAR alone, not of the whole date.

Geometry: two overlapping squares. The personal square sits on the cardinal
points (left/top/right/bottom) and therefore reads as a diamond; the
ancestral square sits on the diagonals and reads as axis-aligned. Each
ancestral corner is the sum of the two personal points it sits between,
which is what makes the adjacency below geometric rather than arbitrary.
"""
from __future__ import annotations

from datetime import date

from app.core.structural_i18n import pick
from app.data.destiny_matrix_i18n import ARCANA_MATRIX_I18N
from app.data.seo_data import TAROT_MAJOR_RU
from app.data.seo_i18n import TAROT_MAJOR_I18N

ARCANA_COUNT = 22


def reduce22(n: int) -> int:
    """Fold a number into the 1..22 arcana range by repeated digit summing.

    Deliberately not app.data.numerology.reduce(): that folds to 1..9 and
    treats 11/22/33 as Pythagorean master numbers to be preserved. Here the
    target range is 1..22, 22 is an ordinary arcana, and 11 must not be
    special-cased — same digit-summing idea, incompatible stopping rule.
    """
    while n > ARCANA_COUNT:
        n = sum(int(d) for d in str(n))
    return n


def arcana_name(n: int, lang: str) -> str:
    """Arcana 1..21 are the Major Arcana of the same number; 22 is The Fool,
    which Tarot numbers 0 — hence the modulo instead of a direct index."""
    idx = n % ARCANA_COUNT
    if lang == "ru":
        return TAROT_MAJOR_RU[idx]
    names = TAROT_MAJOR_I18N.get(lang) or TAROT_MAJOR_I18N["en"]
    return names[idx]


# Point order is the order they're verified, returned, and rendered in:
# the four personal points, the centre, then the four ancestral corners.
# `pos` is consumed by the frontend octagram to place each point.
POINTS = [
    {"id": "personality",  "pos": "left",         "square": "personal"},
    {"id": "talents",      "pos": "top",          "square": "personal"},
    {"id": "ancestry",     "pos": "right",        "square": "personal"},
    {"id": "realization",  "pos": "bottom",       "square": "personal"},
    {"id": "core",         "pos": "centre",       "square": "personal"},
    {"id": "father_gift",  "pos": "top-left",     "square": "ancestral"},
    {"id": "mother_gift",  "pos": "top-right",    "square": "ancestral"},
    {"id": "father_task",  "pos": "bottom-right", "square": "ancestral"},
    {"id": "mother_task",  "pos": "bottom-left",  "square": "ancestral"},
]

POINT_IDS = [p["id"] for p in POINTS]


def calculate(birth: date) -> dict[str, int]:
    """The nine arcana numbers of the base matrix, keyed by POINT_IDS.

    Ancestral corners pair up by diagonal: father's line is top-left +
    bottom-right, mother's line is top-right + bottom-left.
    """
    a = reduce22(birth.day)
    b = reduce22(birth.month)
    c = reduce22(birth.year)
    d = reduce22(a + b + c)
    e = reduce22(a + b + c + d)
    f = reduce22(a + b)
    g = reduce22(b + c)
    h = reduce22(c + d)
    i = reduce22(d + a)
    return {
        "personality": a, "talents": b, "ancestry": c, "realization": d,
        "core": e,
        "father_gift": f, "mother_gift": g, "father_task": h, "mother_task": i,
    }


def ancestral_centre(points: dict[str, int]) -> int:
    """Centre of the ancestral square — the sum of its four corners. Shown as
    a secondary figure; it has no interpretation endpoint of its own."""
    return reduce22(
        points["father_gift"] + points["mother_gift"]
        + points["father_task"] + points["mother_task"]
    )


# Short original energy keywords, written for this project — competitor
# interpretation texts are deliberately not reproduced in any form. These
# only seed the prompt and give the octagram a caption; the actual reading is
# generated per-user through the AI pipeline.
ARCANA_ENERGY = {
    1: {
        "light_ru": "воля, инициатива, дар убеждения, умение начинать",
        "shadow_ru": "манипуляция, суета без результата, обещания вместо дел",
        "light_en": "will, initiative, persuasion, the power to begin",
        "shadow_en": "manipulation, busywork without result, promises instead of action",
    },
    2: {
        "light_ru": "интуиция, глубина, умение слушать тишину",
        "shadow_ru": "холодность, тайны ради тайн, уход от близости",
        "light_en": "intuition, depth, listening to silence",
        "shadow_en": "coldness, secrecy for its own sake, withdrawal from closeness",
    },
    3: {
        "light_ru": "изобилие, забота, чувственность, творческая плодовитость",
        "shadow_ru": "гиперопека, лень, жизнь чужими руками",
        "light_en": "abundance, care, sensuality, creative fertility",
        "shadow_en": "smothering care, indolence, living through others",
    },
    4: {
        "light_ru": "структура, ответственность, умение держать опору",
        "shadow_ru": "жёсткость, контроль, страх потерять власть",
        "light_en": "structure, responsibility, holding steady ground",
        "shadow_en": "rigidity, control, fear of losing authority",
    },
    5: {
        "light_ru": "наставничество, традиция, поиск смысла",
        "shadow_ru": "догматизм, чужие правила вместо своих",
        "light_en": "mentorship, tradition, the search for meaning",
        "shadow_en": "dogma, borrowed rules in place of your own",
    },
    6: {
        "light_ru": "выбор от сердца, притяжение, честность в отношениях",
        "shadow_ru": "нерешительность, метания, выбор из страха",
        "light_en": "choice from the heart, attraction, honesty in relationships",
        "shadow_en": "indecision, drifting, choosing out of fear",
    },
    7: {
        "light_ru": "движение, победа через собранность, свой курс",
        "shadow_ru": "гонка ради гонки, агрессия, потеря управления",
        "light_en": "momentum, victory through focus, holding your own course",
        "shadow_en": "racing for its own sake, aggression, losing the reins",
    },
    8: {
        "light_ru": "спокойная мощь, выдержка, укрощение импульсов",
        "shadow_ru": "подавленный гнев, насилие над собой, надрыв",
        "light_en": "quiet power, endurance, taming impulse",
        "shadow_en": "suppressed anger, self-coercion, burnout",
    },
    9: {
        "light_ru": "мудрость, самостоятельность, честность с собой",
        "shadow_ru": "изоляция, отказ просить помощи, гордая тоска",
        "light_en": "wisdom, self-reliance, honesty with yourself",
        "shadow_en": "isolation, refusing help, proud loneliness",
    },
    10: {
        "light_ru": "удачный поворот, чувство момента, гибкость",
        "shadow_ru": "ставка на случай, качели, отказ от ответственности",
        "light_en": "the lucky turn, a sense of timing, flexibility",
        "shadow_en": "betting on chance, swings, dodging responsibility",
    },
    11: {
        "light_ru": "ясность, честность, умение видеть причину и следствие",
        "shadow_ru": "осуждение, торг с совестью, двойные стандарты",
        "light_en": "clarity, fairness, seeing cause and effect",
        "shadow_en": "judgement of others, bargaining with conscience, double standards",
    },
    12: {
        "light_ru": "смена угла зрения, зрелая пауза, принятие",
        "shadow_ru": "жертвенность, застревание, ожидание вместо шага",
        "light_en": "a shift in perspective, a chosen pause, acceptance",
        "shadow_en": "martyrdom, stuckness, waiting instead of moving",
    },
    13: {
        "light_ru": "завершение, обновление, смелость отпустить",
        "shadow_ru": "цепляние за отжившее, страх перемен, затянутый финал",
        "light_en": "completion, renewal, the courage to let go",
        "shadow_en": "clinging to what is over, fear of change, a drawn-out ending",
    },
    14: {
        "light_ru": "баланс, мера, соединение несоединимого",
        "shadow_ru": "полумеры, вечное смешивание без выбора",
        "light_en": "balance, measure, blending opposites",
        "shadow_en": "half-measures, endless mixing without ever choosing",
    },
    15: {
        "light_ru": "страсть, витальность, честность о своих желаниях",
        "shadow_ru": "зависимости, сделки с собой, власть материи",
        "light_en": "passion, vitality, honesty about desire",
        "shadow_en": "addiction, bargains with yourself, matter in charge",
    },
    16: {
        "light_ru": "освобождающий слом, правда вместо иллюзии",
        "shadow_ru": "разрушение как привычка, кризис на ровном месте",
        "light_en": "a freeing collapse, truth instead of illusion",
        "shadow_en": "destruction as a habit, crisis out of nowhere",
    },
    17: {
        "light_ru": "надежда, вдохновение, дар быть заметным",
        "shadow_ru": "мечты вместо шагов, зависимость от восхищения",
        "light_en": "hope, inspiration, the gift of being seen",
        "shadow_en": "dreaming instead of doing, needing to be admired",
    },
    18: {
        "light_ru": "воображение, чуткость, работа с бессознательным",
        "shadow_ru": "тревога, самообман, туман вместо ясности",
        "light_en": "imagination, sensitivity, working with the unconscious",
        "shadow_en": "anxiety, self-deception, fog instead of clarity",
    },
    19: {
        "light_ru": "радость, ясность, естественное тепло к людям",
        "shadow_ru": "показное сияние, выгорание, тщеславие",
        "light_en": "joy, clarity, natural warmth toward people",
        "shadow_en": "performative shine, burnout, vanity",
    },
    20: {
        "light_ru": "пробуждение, честный пересмотр, зов призвания",
        "shadow_ru": "вина за прошлое, суд над собой, откладывание",
        "light_en": "awakening, honest reckoning, the call of vocation",
        "shadow_en": "guilt over the past, self-condemnation, postponement",
    },
    21: {
        "light_ru": "целостность, завершённый цикл, широта горизонта",
        "shadow_ru": "остановка на достигнутом, бегство в масштаб",
        "light_en": "wholeness, a completed cycle, a wide horizon",
        "shadow_en": "resting on laurels, escaping into sheer scale",
    },
    22: {
        "light_ru": "свобода, лёгкость, готовность начать с нуля",
        "shadow_ru": "безответственность, побег, жизнь без корней",
        "light_en": "freedom, lightness, readiness to start from zero",
        "shadow_en": "irresponsibility, escape, a life without roots",
    },
}


def arcana_energy(n: int, lang: str) -> dict[str, str]:
    base = ARCANA_ENERGY[n]
    return {
        "light": pick(base, "light", lang, ARCANA_MATRIX_I18N, str(n)),
        "shadow": pick(base, "shadow", lang, ARCANA_MATRIX_I18N, str(n)),
    }


def build_matrix(birth: date, lang: str) -> dict:
    """Full API payload: every point with its arcana number, name and energy
    keywords. Deterministic — the same birth date always yields the same
    matrix, which is why nothing here is persisted as a "reading"."""
    values = calculate(birth)
    return {
        "points": [
            {
                "id": p["id"],
                "pos": p["pos"],
                "square": p["square"],
                "arcana": values[p["id"]],
                "arcana_name": arcana_name(values[p["id"]], lang),
                **arcana_energy(values[p["id"]], lang),
            }
            for p in POINTS
        ],
        "ancestral_centre": ancestral_centre(values),
    }
