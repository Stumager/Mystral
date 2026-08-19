"""TZ-114: Кармический хвост (Karmic Tail) — a three-arcana coda derived from
the base Matrix of Destiny (TZ-101). No new user input: it folds two of the
nine already-computed points back on themselves.

Step 0 (verified before writing this, same discipline as TZ-101 — see
PROGRESS.md): which points, and the fold rule, were checked against two
independent worked examples with numeric birth dates (horo.mail.ru,
03.10.1974 -> tail 12-19-7; lisa.ru, 15.08.1992 -> tail 15-5-8). Both
reproduce exactly using *this* codebase's own `core`/`realization` points
and `reduce22()` — nothing here is guessed by analogy with the base formula:

    t1 = reduce22(core + realization)
    t2 = reduce22(t1 + realization)
    t3 = realization

A full simulation of every calendar date 1900-01-01..2100-12-31 through this
formula yields exactly 26 distinct (t1, t2, t3) triples — matching the size
of the reference table published by the sources checked above, which is
strong independent confirmation the formula (not just the point count) is
right, not merely mod-9-equivalent to it (see the TZ-101 point-C postmortem
for why "matches mod 9" is not enough).

Copyright: the two-line fold rule above is a mathematical procedure, not
protected expression. The 26 short archetype names below intentionally match
the ones already circulating across multiple independent competitor sites
(matrica-sudby.ru, horo.mail.ru, gems-brokers.ru, lisa.ru) for the same
numeric codes — product decision, confirmed with the product owner despite
at least one prominent practitioner (Наталия Ладини) publicly claiming
personal authorship of the wider method, on the grounds that these are short
generic archetype labels reused across many unaffiliated sites, not the
protectable part. The `essence`/`task` text is fully original, written for
this project without reading back or paraphrasing any competitor's wording —
same discipline as ARCANA_ENERGY in destiny_matrix.py. One exception: the
code that several competitor tables label "Суицид" is deliberately not used
here — a literal self-harm word as a headline archetype label on a personal
reading is a content-safety problem independent of naming convention, so it
carries an original substitute name instead ("Точка невозврата") that keeps
the same thematic register (a past-life dead end) without the explicit term.
"""
from __future__ import annotations

from datetime import date

from app.core.structural_i18n import pick
from app.data.destiny_matrix import calculate, reduce22
from app.data.karmic_tail_i18n import KARMIC_TAIL_I18N


def calculate_tail(points: dict[str, int]) -> tuple[int, int, int]:
    """The three karmic-tail numbers from an already-computed base matrix
    (destiny_matrix.calculate() output) — see module docstring for the
    verification behind this exact fold."""
    core = points["core"]
    realization = points["realization"]
    t1 = reduce22(core + realization)
    t2 = reduce22(t1 + realization)
    t3 = realization
    return t1, t2, t3


def tail_code(tail: tuple[int, int, int]) -> str:
    return f"{tail[0]}-{tail[1]}-{tail[2]}"


# All 26 combinations reachable through calculate_tail() across every real
# calendar date (verified by simulation, see module docstring) — this table
# is exhaustive, not a curated subset, so every user resolves to a real entry.
KARMIC_TAIL: dict[str, dict[str, str]] = {
    "3-7-22": {
        "name_ru": "Узник", "name_en": "The Prisoner",
        "essence_ru": "несвобода как привычка, чужие решения вместо своих, зависимость от чужого одобрения",
        "essence_en": "unfreedom as a habit, living by other people's decisions, needing outside approval",
        "task_ru": "разрешить себе выбирать, даже маленькое, без чужого разрешения",
        "task_en": "give yourself permission to choose — even something small — without asking first",
    },
    "3-13-10": {
        "name_ru": "Точка невозврата", "name_en": "Point of No Return",
        "essence_ru": "прошлое решение всё оборвать, усталость от борьбы, отказ от собственной жизни",
        "essence_en": "a past decision to end it all, exhaustion from fighting, giving up on your own life",
        "task_ru": "учиться просить о помощи до края, а не после него",
        "task_en": "learn to ask for help before the edge, not after it",
    },
    "3-22-19": {
        "name_ru": "Нерождённое дитя", "name_en": "The Unborn Child",
        "essence_ru": "оборванное воплощение, страх заявить о себе, ощущение, что тебя как будто нет",
        "essence_en": "a life cut short before it began, fear of taking up space, a sense of not fully existing",
        "task_ru": "заново присвоить себе право родиться и быть увиденным",
        "task_en": "reclaim your right to exist and be seen, from scratch",
    },
    "6-5-17": {
        "name_ru": "Гордыня", "name_en": "Pride",
        "essence_ru": "власть через превосходство, страх признать ошибку, одиночество на пьедестале",
        "essence_en": "power through superiority, fear of admitting a mistake, loneliness on a pedestal",
        "task_ru": "разрешить себе быть неправым на глазах у других",
        "task_en": "allow yourself to be wrong in front of others",
    },
    "6-8-20": {
        "name_ru": "Разочарование рода", "name_en": "The Line's Disappointment",
        "essence_ru": "невыполненные родовые ожидания, чувство вины перед семьёй, попытка искупить не свою вину",
        "essence_en": "unmet family expectations, guilt toward the family line, atoning for a debt that isn't yours",
        "task_ru": "отделить свои цели от чужих несбывшихся надежд",
        "task_en": "separate your own goals from someone else's unfulfilled hopes",
    },
    "6-14-8": {
        "name_ru": "Диктатор", "name_en": "The Dictator",
        "essence_ru": "власть через страх, недоверие к чужой воле, потребность контролировать всё вокруг",
        "essence_en": "power through fear, distrust of other people's will, needing to control everything around you",
        "task_ru": "тренировать влияние без давления — вести, а не подчинять",
        "task_en": "practise influence without pressure — lead instead of forcing",
    },
    "6-17-11": {
        "name_ru": "Загубленный талант", "name_en": "Wasted Talent",
        "essence_ru": "дар, который однажды не дали раскрыть, страх снова заявить о способностях",
        "essence_en": "a gift that was once silenced, fear of showing your abilities again",
        "task_ru": "делать заметный шаг в своём деле, не дожидаясь разрешения",
        "task_en": "take a visible step in your craft without waiting for permission",
    },
    "6-20-14": {
        "name_ru": "Жертва рода", "name_en": "The Family's Sacrifice",
        "essence_ru": "привычка отдавать себя ради других, обесценивание собственных нужд",
        "essence_en": "a habit of giving yourself away for others, treating your own needs as unimportant",
        "task_ru": "находить баланс между заботой о близких и заботой о себе",
        "task_en": "find the balance between caring for others and caring for yourself",
    },
    "9-3-21": {
        "name_ru": "Надзиратель", "name_en": "The Overseer",
        "essence_ru": "контроль как форма заботы, недоверие к тому, что справятся без тебя",
        "essence_en": "control disguised as care, distrust that others can manage without you",
        "task_ru": "отпускать контроль там, где достаточно доверия",
        "task_en": "release control where trust is already enough",
    },
    "9-9-18": {
        "name_ru": "Маг", "name_en": "The Magician",
        "essence_ru": "сила намерения, использованная не по назначению, соблазн лёгкого пути через манипуляцию",
        "essence_en": "the power of intent used off-course, the pull toward a shortcut through manipulation",
        "task_ru": "применять свой дар открыто, без скрытых мотивов",
        "task_en": "use your gift openly, without a hidden agenda",
    },
    "9-12-3": {
        "name_ru": "Одинокая женщина", "name_en": "The Lone Woman",
        "essence_ru": "самодостаточность вместо близости, страх снова довериться и быть уязвимой",
        "essence_en": "self-sufficiency in place of closeness, fear of trusting and being vulnerable again",
        "task_ru": "впускать помощь и поддержку, не теряя себя",
        "task_en": "let in help and support without losing yourself",
    },
    "9-15-6": {
        "name_ru": "Мир страстей", "name_en": "World of Passions",
        "essence_ru": "жизнь на эмоциональных качелях, влечение к драматичным сценариям вместо стабильности",
        "essence_en": "life on an emotional see-saw, drawn to dramatic scenarios instead of steadiness",
        "task_ru": "выбирать ровное чувство вместо привычного накала",
        "task_en": "choose a steady feeling over the familiar intensity",
    },
    "9-18-9": {
        "name_ru": "Чародей", "name_en": "The Sorcerer",
        "essence_ru": "тонкое влияние на чужие решения, соблазн управлять исподволь, а не открыто",
        "essence_en": "subtle influence over other people's choices, the pull to steer quietly rather than openly",
        "task_ru": "говорить прямо о том, чего хочешь добиться",
        "task_en": "say plainly what you're trying to achieve",
    },
    "12-16-4": {
        "name_ru": "Император", "name_en": "The Emperor",
        "essence_ru": "власть, добытая жёсткостью, страх потерять статус, недоверие к чужой инициативе",
        "essence_en": "authority won through harshness, fear of losing status, distrust of other people's initiative",
        "task_ru": "делиться властью и признавать чужие заслуги",
        "task_en": "share authority and give credit where it's due",
    },
    "12-19-7": {
        "name_ru": "Воин", "name_en": "The Warrior",
        "essence_ru": "борьба как единственный привычный способ жить, трудности с тем, чтобы просто быть в мире",
        "essence_en": "fighting as the only familiar way to live, trouble simply being at peace",
        "task_ru": "различать настоящую угрозу и старую привычку обороняться",
        "task_en": "tell a real threat apart from an old habit of defending yourself",
    },
    "15-5-8": {
        "name_ru": "Предательство в семье", "name_en": "Betrayal in the Family",
        "essence_ru": "подорванное доверие к близким, ожидание удара оттуда, откуда не ждёшь",
        "essence_en": "trust broken by someone close, expecting betrayal from exactly where you least expect it",
        "task_ru": "давать доверию новый шанс, не проверяя его на прочность заранее",
        "task_en": "give trust a new chance instead of testing it in advance",
    },
    "15-8-11": {
        "name_ru": "Физическая агрессия", "name_en": "Physical Aggression",
        "essence_ru": "непроработанный гнев, который рвётся наружу через тело, а не через слова",
        "essence_en": "unprocessed anger that breaks out through the body instead of through words",
        "task_ru": "находить безопасный выход силе, прежде чем она выйдет сама",
        "task_en": "give that force a safe outlet before it finds one on its own",
    },
    "15-20-5": {
        "name_ru": "Бунтарь", "name_en": "The Rebel",
        "essence_ru": "протест против любых правил, даже полезных, борьба ради борьбы",
        "essence_en": "resistance to any rule, even a useful one, fighting for the sake of fighting",
        "task_ru": "выбирать, за что стоит бороться, а с чем можно согласиться",
        "task_en": "choose what's worth fighting for and what's fine to simply accept",
    },
    "18-3-12": {
        "name_ru": "Физические страдания", "name_en": "Physical Suffering",
        "essence_ru": "тело как место, где хранится непрожитая боль, привычка терпеть до последнего",
        "essence_en": "the body as a place where unprocessed pain is stored, a habit of enduring past the limit",
        "task_ru": "слушать тело раньше, чем оно заставит остановиться",
        "task_en": "listen to the body before it forces you to stop",
    },
    "18-6-6": {
        "name_ru": "Любовная магия", "name_en": "Love Magic",
        "essence_ru": "попытка удержать чувства силой воли или ритуалом вместо честности",
        "essence_en": "trying to hold on to feelings through willpower or ritual instead of honesty",
        "task_ru": "выбирать искренность в отношениях вместо контроля над ними",
        "task_en": "choose honesty in a relationship over trying to control it",
    },
    "18-6-15": {
        "name_ru": "Тёмный маг", "name_en": "The Dark Mage",
        "essence_ru": "дар влияния, однажды использованный во вред, недоверие к собственной силе",
        "essence_en": "a gift for influence once used to cause harm, distrust of your own power",
        "task_ru": "возвращать себе силу постепенно, проверяя её на добрых делах",
        "task_en": "reclaim that power gradually, testing it on something good first",
    },
    "18-9-9": {
        "name_ru": "Волшебник", "name_en": "The Wizard",
        "essence_ru": "знание, которое держат в тайне из страха, что им воспользуются во зло",
        "essence_en": "knowledge kept hidden out of fear it will be misused",
        "task_ru": "делиться своим знанием с теми, кому действительно можно доверять",
        "task_en": "share what you know with the people who've actually earned that trust",
    },
    "21-4-10": {
        "name_ru": "Угнетённая душа", "name_en": "The Oppressed Soul",
        "essence_ru": "привычка подчиняться чужой воле, потерянное ощущение собственных границ",
        "essence_en": "a habit of submitting to someone else's will, a lost sense of your own boundaries",
        "task_ru": "замечать момент, когда молчание вредит, и говорить «нет»",
        "task_en": "notice the moment silence starts to cost you, and say no",
    },
    "21-7-13": {
        "name_ru": "Разрушитель", "name_en": "The Destroyer",
        "essence_ru": "сила, которая однажды снесла больше, чем следовало, страх снова причинить вред",
        "essence_en": "a force that once tore down more than it should have, fear of causing harm again",
        "task_ru": "направлять эту силу на то, что действительно пора завершить",
        "task_en": "aim that force at what genuinely needs to end, and nothing more",
    },
    "21-10-7": {
        "name_ru": "Воин веры", "name_en": "Warrior of Faith",
        "essence_ru": "убеждения, которые когда-то стоили дорого, страх снова отстаивать то, во что веришь",
        "essence_en": "convictions that once came at a high price, fear of standing up for them again",
        "task_ru": "отстаивать взгляды спокойно, без готовности воевать за каждый из них",
        "task_en": "stand by your views calmly, without treating every one as a battle",
    },
    "21-10-16": {
        "name_ru": "Духовный жрец", "name_en": "The Spiritual Priest",
        "essence_ru": "духовный авторитет, который использовали, чтобы решать за других",
        "essence_en": "spiritual authority once used to make choices on other people's behalf",
        "task_ru": "делиться своим опытом, не навязывая его как единственно верный",
        "task_en": "share your experience without insisting it's the only right path",
    },
}


def lookup(tail: tuple[int, int, int]) -> dict[str, str]:
    return KARMIC_TAIL[tail_code(tail)]


def build_karmic_tail(birth: date, lang: str) -> dict:
    """Full API payload: the three numbers, the code, and the localized
    archetype name/essence/task. Deterministic — same pattern as
    build_matrix() in destiny_matrix.py, nothing here is persisted."""
    points = calculate(birth)
    tail = calculate_tail(points)
    code = tail_code(tail)
    entry = KARMIC_TAIL[code]
    return {
        "t1": tail[0], "t2": tail[1], "t3": tail[2],
        "code": code,
        "name": pick(entry, "name", lang, KARMIC_TAIL_I18N, code),
        "essence": pick(entry, "essence", lang, KARMIC_TAIL_I18N, code),
        "task": pick(entry, "task", lang, KARMIC_TAIL_I18N, code),
    }
