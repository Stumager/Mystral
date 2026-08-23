"""TZ-116: Детская матрица (Children's Matrix) — the third module built on
the base Matrix of Destiny (TZ-101). Unlike the karmic tail (TZ-114) and
money line (TZ-115), this one needs no new formula at all: it reinterprets
the same nine already-computed points (destiny_matrix.calculate()) through
a different lens — a parent reading about their child, not an adult reading
about themselves. No new user input beyond the child's birth date.

Step 0 (verified before writing this — see PROGRESS.md): checked 5+
competitor sources for a separate "children's matrix" naming system, the
way the karmic tail has one. Found none — every source (matrica-sudby.ru,
gadalkindom.ru, acronum.ru, magya-online.ru) says explicitly that there is
no separate calculation or naming for children, only a different
interpretive emphasis. The one thing that looked like a children's-matrix
archetype table (acronum.ru's "Аркан 1 — Маг", "Аркан 2 — Жрица", ...) is
just the standard Major Arcana names already used throughout this whole
system (destiny_matrix.arcana_name()) — public-domain Tarot terminology,
not a competitor's proprietary system. So there is no naming question here
the way there was for TZ-114.

Content safety (reviewed with the product owner before this shipped, per
the same discipline as TZ-114/115 — full findings in PROGRESS.md): several
competitor sources frame a child's matrix through inherited ancestral debt
("karma is felt for seven generations of the line", "this is what the
mother's line expects of the child") — the same fatalistic/blame-shaped
framing flagged and deliberately excluded from TZ-115's MONEY_ENERGY, now
doubly important because the subject being read about cannot consent or
push back the way an adult reading about themselves can. CHILD_ARCANA_ENERGY
below has no "shadow"/"block"/"weakness" field at all (unlike
destiny_matrix.ARCANA_ENERGY and money_line.MONEY_ENERGY, which both do) —
every entry is exactly two fields, `strength` (a natural inclination) and
`support` (something a parent can actually do), because a reading a parent
holds about a child that isn't theirs to interpret for themselves is a
different risk profile from a reading an adult holds about their own life:
there is no "shadow" field here for a parent to read as a verdict on their
kid. Nothing here says what a child "can't" do or "isn't cut out for".
"""
from __future__ import annotations

from datetime import date

from app.core.structural_i18n import pick
from app.data.childrens_matrix_i18n import CHILD_ARCANA_I18N
from app.data.destiny_matrix import POINTS, arcana_name, calculate

# The single point exposed to free users (task 7, confirmed with the product
# owner): "talents" is literally the child's innate-ability point — the
# "what's my kid's main talent" hook. The other eight points and the AI
# reading are Pro, same rule for both.
FREE_POINT_ID = "talents"

# Original developmental keywords, written for this project — competitor
# interpretation texts are deliberately not reproduced in any form. See the
# module docstring for why there is no second, shadow-style field here.
CHILD_ARCANA_ENERGY = {
    1: {
        "strength_ru": "инициативность, тянется начинать первым, лидерский инстинкт в игре",
        "support_ru": "давай реальные небольшие проекты «от и до», хвали за старт, а не только за результат",
        "strength_en": "initiative, tends to start things first, a leader's instinct in play",
        "support_en": "give real small projects start-to-finish, praise the starting, not only the result",
    },
    2: {
        "strength_ru": "богатый внутренний мир, интуиция, умеет наблюдать тихо и подмечать детали",
        "support_ru": "оставляй время побыть одному, не заставляй быть «на людях» без пауз",
        "strength_en": "a rich inner world, intuition, quietly observant and detail-noticing",
        "support_en": "leave room for time alone, don't push constant socialising without a break",
    },
    3: {
        "strength_ru": "забота о других, творческая щедрость, естественная тяга к уюту и красоте",
        "support_ru": "давай пространство для творческой игры, не торопи с ранней ответственностью",
        "strength_en": "care for others, creative generosity, a natural pull toward comfort and beauty",
        "support_en": "make room for creative play, don't rush early responsibility onto them",
    },
    4: {
        "strength_ru": "любит порядок и правила, природный организатор, держит слово",
        "support_ru": "давай предсказуемый распорядок, позволяй самому что-то выстраивать и планировать",
        "strength_en": "likes order and rules, a natural organiser, keeps their word",
        "support_en": "keep routines predictable, let them plan and build things themselves",
    },
    5: {
        "strength_ru": "хорошо учится через наставника, уважает традиции, любит объяснять другим",
        "support_ru": "найди фигуру наставника рядом, давай возможность самому кого-то научить",
        "strength_en": "learns well through a mentor, respects tradition, enjoys explaining to others",
        "support_en": "find a mentor figure nearby, let them teach someone else something",
    },
    6: {
        "strength_ru": "ценит отношения, выбирает от сердца, чувствует, что для него по-настоящему важно",
        "support_ru": "уважай его собственный выбор, даже маленький — не решай за него всё подряд",
        "strength_en": "values relationships, chooses from the heart, senses what truly matters to them",
        "support_en": "honour their own choices, even small ones — don't decide everything for them",
    },
    7: {
        "strength_ru": "азартный, целеустремлённый, любит движение и понятную цель впереди",
        "support_ru": "давай ясную цель и физическую активность, оставляй время без плотного расписания",
        "strength_en": "driven, goal-oriented, likes momentum and a clear target ahead",
        "support_en": "give a clear goal and physical activity, leave room outside a packed schedule",
    },
    8: {
        "strength_ru": "эмоциональная устойчивость, спокойствие под давлением, терпение",
        "support_ru": "показывай своим примером спокойное обращение с раздражением, не торопи его темп",
        "strength_en": "emotional steadiness, calm under pressure, patience",
        "support_en": "model calm handling of frustration yourself, don't rush their pace",
    },
    9: {
        "strength_ru": "глубокая сосредоточенность, комфортно наедине с собой, думает своей головой",
        "support_ru": "уважай потребность побыть одному, не заставляй общаться, если не хочется",
        "strength_en": "deep focus, comfortable alone, thinks things through independently",
        "support_en": "respect the need for solitude, don't force socialising when they don't want it",
    },
    10: {
        "strength_ru": "гибкость, легко подстраивается под перемены, устойчив к неожиданностям",
        "support_ru": "не расписывай каждую минуту заранее, давай пространство для импровизации",
        "strength_en": "adaptability, adjusts to change easily, resilient to surprises",
        "support_en": "don't plan every minute in advance, leave room to improvise",
    },
    11: {
        "strength_ru": "острое чувство справедливости, честность, видит причину и следствие",
        "support_ru": "объясняй «почему» за правилами, а не только «потому что я так сказал»",
        "strength_en": "a sharp sense of fairness, honesty, sees cause and effect",
        "support_en": "explain the 'why' behind a rule, not just 'because I said so'",
    },
    12: {
        "strength_ru": "терпелив, смотрит на вещи под новым углом, спокойно выдерживает паузу",
        "support_ru": "не торопи с решением, давай время просто понаблюдать, прежде чем включиться",
        "strength_en": "patient, sees things from a fresh angle, comfortable sitting with a pause",
        "support_en": "don't rush a decision, give time to just watch before joining in",
    },
    13: {
        "strength_ru": "легко переживает перемены, не держится за отжившее, быстро отпускает старое",
        "support_ru": "предупреждай о переменах заранее, не заставляй цепляться за то, что он перерос",
        "strength_en": "handles change easily, doesn't cling to what's outgrown, lets go quickly",
        "support_en": "give advance notice of change, don't make them cling to what they've outgrown",
    },
    14: {
        "strength_ru": "естественно уравновешивает крайности, умеет сочетать разные интересы",
        "support_ru": "не дави выбором «или-или», давай совмещать несколько увлечений сразу",
        "strength_en": "naturally balances extremes, blends different interests well",
        "support_en": "don't force an either-or choice, let them combine a few interests at once",
    },
    15: {
        "strength_ru": "сильная воля, страстность, честен в своих желаниях",
        "support_ru": "давай слова для желаний вместо стыда за них, мягко подсвечивай нездоровые привязанности",
        "strength_en": "strong will, passion, honest about what they want",
        "support_en": "give words for wants instead of shame around them, gently flag unhealthy attachments",
    },
    16: {
        "strength_ru": "честность без прикрас, не боится ломки старого и резких перемен",
        "support_ru": "не наказывай за прямоту, давай безопасный выход внезапным вспышкам энергии",
        "strength_en": "unvarnished honesty, unafraid of breaking old patterns or sudden change",
        "support_en": "don't punish bluntness, give a safe outlet for sudden bursts of energy",
    },
    17: {
        "strength_ru": "надежда, вдохновляет других, спокойно чувствует себя на виду",
        "support_ru": "давай иногда «сцену» и внимание, береги его оптимизм от насмешек",
        "strength_en": "hope, inspires others, comfortable being seen",
        "support_en": "give them a stage and attention sometimes, protect their optimism from mockery",
    },
    18: {
        "strength_ru": "богатое воображение, чуткость к настроению и атмосфере, интуитивность",
        "support_ru": "не обесценивай страхи как «глупости», давай место фантазии и игре",
        "strength_en": "a rich imagination, sensitive to mood and atmosphere, intuitive",
        "support_en": "don't dismiss fears as silly, make room for imagination and play",
    },
    19: {
        "strength_ru": "теплота, радость, легко находит общий язык с людьми",
        "support_ru": "давай радости быть громкой иногда, не требуй постоянной сдержанности",
        "strength_en": "warmth, joy, connects easily with people",
        "support_en": "let their joy be loud sometimes, don't demand constant restraint",
    },
    20: {
        "strength_ru": "склонен осмыслять произошедшее, учится на своих ошибках, ищет смысл",
        "support_ru": "проговаривай, что случилось, после конфликтов, не стыди за повторную попытку",
        "strength_en": "reflects on what happened, learns from mistakes, looks for meaning",
        "support_en": "talk through what happened after a conflict, don't shame a second try",
    },
    21: {
        "strength_ru": "доводит дела до конца, видит картину целиком, легко переключается между сферами",
        "support_ru": "давай завершать начатое в своём темпе, отмечай именно завершения, а не только рывки",
        "strength_en": "sees things through to completion, grasps the big picture, moves easily between areas",
        "support_en": "let them finish what they start at their own pace, celebrate completions specifically",
    },
    22: {
        "strength_ru": "бесстрашное начало нового, любопытство, спокойно относится к неизвестности",
        "support_ru": "давай пробовать без подстраховки каждый раз, не переусердствуй с предупреждениями",
        "strength_en": "fearless about starting something new, curiosity, comfortable with the unknown",
        "support_en": "let them try without a safety net every time, don't over-warn them",
    },
}


def child_arcana_energy(n: int, lang: str) -> dict[str, str]:
    base = CHILD_ARCANA_ENERGY[n]
    return {
        "strength": pick(base, "strength", lang, CHILD_ARCANA_I18N, str(n)),
        "support": pick(base, "support", lang, CHILD_ARCANA_I18N, str(n)),
    }


def build_children_matrix(birth: date, lang: str) -> dict:
    """Full API payload: every point with its arcana number, name and
    developmental keywords. Deterministic, same pattern as build_matrix()
    in destiny_matrix.py — nothing here is persisted. Free/Pro point-level
    gating is applied by the API layer, not here (this always returns the
    full nine points, same as build_karmic_tail()/build_money_line() stay
    tier-agnostic)."""
    values = calculate(birth)
    return {
        "points": [
            {
                "id": p["id"],
                "pos": p["pos"],
                "square": p["square"],
                "arcana": values[p["id"]],
                "arcana_name": arcana_name(values[p["id"]], lang),
                **child_arcana_energy(values[p["id"]], lang),
            }
            for p in POINTS
        ],
    }
