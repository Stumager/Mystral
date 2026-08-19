"""TZ-115: Денежная линия (Money Line) — three arcana derived from the base
Matrix of Destiny (TZ-101), the second module built on the same foundation
as the karmic tail (TZ-114). No new user input: it folds three of the nine
already-computed points.

Step 0 (verified before writing this — see PROGRESS.md): matrica-sudby.ru's
own money-line article is textually vague about which base points its
formula letters refer to, and most other competitor sites don't publish the
formula at all (they gate it behind a paid calculator/consultation). What
settled it was two images on that article — one diagram labelled with
letters (Б, В, Г, Д at fixed grid positions), a second with the same
diagram's example filled in with actual numbers (8, 4, 9, 19 at the same
positions) — read directly (not through a text summariser, which on a
different competitor site fabricated an entire formula that doesn't exist
on the page it claimed to summarise). Plugging the numbers into the site's
own stated formula reproduces the stated result exactly:

    entry(А)  = reduce22(Б + В)        = reduce22(8+4)  = 12
    source(Г) = reduce22(Б + Д)        = reduce22(8+19) = 9
    block(Е)  = reduce22(entry+source) = reduce22(12+9) = 21

Б sits at the exact centre of the diagram (only `core` can be — there is
only one centre) and Д sits at the diagram's right cardinal point (only
`ancestry` sits there in this codebase's geometry). В does not: the site's
own text calls the entry point "karmic energy, because it also sits on the
karmic tail" — the only base point that phrase can mean is `realization`,
since it's the only one used anywhere in karmic_tail.py's formula. Checked
this by brute-force simulation rather than trusting the phrase alone: of
every calendar date 1900-2100 whose (core, ancestry) match the example's
(8, 19) — 504 of them — `realization` equals the example's В (4) for 420
of them (83%), with no other of the nine points coming remotely close
(the runner-up manages 7%). That number isn't 100% because `realization`
isn't a deterministic function of (core, ancestry) alone, but it settles
which point the formula means, not what a specific illustrative date was.
With В = realization, entry(А) collapses to reduce22(core + realization) —
exactly karmic_tail.calculate_tail()'s first digit — which is what makes
the site's "also on the karmic tail" phrase literally true, not loosely
poetic.

Copyright: the fold rule above is arithmetic, not protected expression.
Unlike the karmic tail, no source found gives the money line named
combinations (no "Диктатор"-style archetype table exists for it in any
source checked) — every source that publishes anything past the bare
concept interprets it per single arcana (1-22), the same shape as
destiny_matrix.ARCANA_ENERGY. MONEY_ENERGY below is fully original text,
written for this project without reading back or paraphrasing any
competitor's wording, in that same shape.

Content safety (reviewed with the product owner before this shipped):
matrica-sudby.ru's own text around the money line carries a fatalistic
"karmic ban" frame — a past-life debt can flatly prevent this life's
money from arriving, and its "block" position is described as "always
negative" with no way through. None of that made it into MONEY_ENERGY —
each `block` entry names a workable behaviour pattern (e.g. arcana 20 is
"carrying a parent's money story without noticing it isn't yours", not
"unblock money by forgiving your parents or it won't come"), and the
matrix.py prompt frames the block position as something to work on, not
a verdict. test_money_line.py has a keyword guard against this
regressing.

Separately, the competitor's arcana 3/4 route money through "female/male
spheres of activity" — flagged for a decision alongside the above. The
product owner's call was to leave that gendering as-is, consistent with
keeping TZ-114's "Одинокая женщина" archetype; MONEY_ENERGY[3]/[4] here
were never gendered in the first place (written from the arcana's
general theme, not the competitor's text), so nothing needed changing to
honour that call.
"""
from __future__ import annotations

from datetime import date

from app.core.structural_i18n import pick
from app.data.destiny_matrix import calculate, reduce22
from app.data.money_line_i18n import MONEY_ENERGY_I18N

MONEY_LINE_POSITIONS = ("entry", "source", "block")


def calculate_money_line(points: dict[str, int]) -> dict[str, int]:
    """The three money-line numbers from an already-computed base matrix
    (destiny_matrix.calculate() output) — see module docstring."""
    core = points["core"]
    ancestry = points["ancestry"]
    realization = points["realization"]
    entry = reduce22(core + realization)
    source = reduce22(core + ancestry)
    block = reduce22(entry + source)
    return {"entry": entry, "source": source, "block": block}


# Original energy keywords for the money line, written for this project —
# competitor interpretation texts are deliberately not reproduced in any
# form. `flow` is what draws money in through this arcana, `block` is what
# shuts it off — same light/shadow shape as destiny_matrix.ARCANA_ENERGY,
# just reframed for money specifically rather than the arcana in general.
MONEY_ENERGY = {
    1: {
        "flow_ru": "деньги идут через инициативу — предложить, начать первым, возглавить",
        "block_ru": "распыление на десять начинаний вместо одного доведённого до денег",
        "flow_en": "money follows initiative — pitching first, starting, taking the lead",
        "block_en": "spreading across ten beginnings instead of finishing the one that pays",
    },
    2: {
        "flow_ru": "доход растёт, когда есть согласие между тем, что чувствуешь, и тем, чем занимаешься",
        "block_ru": "работа наперекор внутреннему несогласию тихо перекрывает поток",
        "flow_en": "income grows when what you feel and what you do for money actually agree",
        "block_en": "working against an inner objection quietly shuts the flow off",
    },
    3: {
        "flow_ru": "деньги приходят через щедрость, заботу, создание чего-то, что кормит других",
        "block_ru": "раздавать бесплатно то, за что давно пора называть цену",
        "flow_en": "money comes through generosity, care, making something that nourishes others",
        "block_en": "giving away for free what's long overdue a price tag",
    },
    4: {
        "flow_ru": "доход держится на структуре — системе, регламенте, надёжном каркасе дела",
        "block_ru": "жёсткий контроль до отказа делегировать хоть что-то",
        "flow_en": "income holds up on structure — a system, a process, a reliable backbone",
        "block_en": "control so tight that delegating even one task feels out of reach",
    },
    5: {
        "flow_ru": "деньги приходят через передачу знаний — обучение, наставничество, экспертизу",
        "block_ru": "держаться чужой методики вместо того, чтобы взять ответственность за свою",
        "flow_en": "money comes through passing on knowledge — teaching, mentoring, expertise",
        "block_en": "clinging to someone else's method instead of owning your own",
    },
    6: {
        "flow_ru": "доход растёт через отношения и честный выбор — с кем работать, а с кем нет",
        "block_ru": "браться за проект из вежливости, хотя внутри уже прозвучало «нет»",
        "flow_en": "income grows through relationships and an honest choice of who to work with",
        "block_en": "taking on work out of politeness when the answer inside was already no",
    },
    7: {
        "flow_ru": "деньги идут за целеустремлённым движением к результату, без оглядки назад",
        "block_ru": "распылять энергию рывками вместо ровного, доведённого до конца курса",
        "flow_en": "money follows focused movement toward a result, without looking back",
        "block_en": "burning energy in bursts instead of a steady course carried through",
    },
    8: {
        "flow_ru": "доход стабилен там, где есть порядок, точность и выполненные обязательства",
        "block_ru": "хаос в документах и договорённостях, который однажды дорого аукнется",
        "flow_en": "income is steady where there's order, precision, and kept commitments",
        "block_en": "chaos in paperwork and agreements that eventually costs money",
    },
    9: {
        "flow_ru": "деньги приходят через глубокую, самостоятельную работу над сложной темой",
        "block_ru": "прятать экспертизу из страха, что она окажется никому не нужна",
        "flow_en": "money comes through deep, independent work on a difficult subject",
        "block_en": "hiding your expertise for fear no one will want it",
    },
    10: {
        "flow_ru": "доход приходит через удачный момент — важно заметить его и не упустить",
        "block_ru": "ждать идеальных условий и пропускать возможность, которая уже здесь",
        "flow_en": "income comes through good timing — the trick is noticing and not missing it",
        "block_en": "waiting for perfect conditions and missing the opportunity already here",
    },
    11: {
        "flow_ru": "деньги идут через активность — своё дело, движение, реальную ответственность",
        "block_ru": "оставаться в найме там, где давно тесно, из страха самостоятельности",
        "flow_en": "money follows activity — your own venture, motion, real accountability",
        "block_en": "staying employed somewhere too small out of fear of going it alone",
    },
    12: {
        "flow_ru": "доход приходит через служение — то, что отдаёшь людям, а не то, что берёшь",
        "block_ru": "стесняться называть цену за то, что помогает людям",
        "flow_en": "income comes through service — what you give people, not what you extract",
        "block_en": "feeling embarrassed to charge for something that genuinely helps people",
    },
    13: {
        "flow_ru": "деньги приходят через смену курса — новую сферу, новый формат работы",
        "block_ru": "держаться за угасающее дело только потому, что жаль вложенного времени",
        "flow_en": "money comes through changing course — a new field, a new way of working",
        "block_en": "clinging to a fading venture only because of the time already sunk into it",
    },
    14: {
        "flow_ru": "доход растёт там, где дело выбрано по душе, а не по расчёту",
        "block_ru": "заниматься прибыльным, но абсолютно чужим делом ради самой прибыли",
        "flow_en": "income grows where the work is chosen for love of it, not just calculation",
        "block_en": "doing something profitable but completely alien just for the profit",
    },
    15: {
        "flow_ru": "деньги приходят через долгосрочные вложения и терпение",
        "block_ru": "гнаться за быстрой наживой и рискованными схемами вместо системной работы",
        "flow_en": "money comes through long-term investment and patience",
        "block_en": "chasing quick money and risky schemes instead of steady, systemic work",
    },
    16: {
        "flow_ru": "доход приходит через готовность резко сменить сферу, когда старая исчерпана",
        "block_ru": "цепляться за рухнувшую модель заработка, отказываясь строить новую",
        "flow_en": "income comes through willingness to pivot hard once the old field is spent",
        "block_en": "clinging to a collapsed income model instead of building a new one",
    },
    17: {
        "flow_ru": "деньги приходят через известность — быть на виду, делиться своим голосом",
        "block_ru": "прятаться от внимания, хотя именно оно приносит клиентов",
        "flow_en": "money comes through visibility — being seen, sharing your own voice",
        "block_en": "hiding from attention when attention is exactly what brings clients",
    },
    18: {
        "flow_ru": "доход приходит через работу с тонкими темами — тревогой, страхом, подсознанием",
        "block_ru": "использовать чужую тревогу для продажи вместо того, чтобы её снимать",
        "flow_en": "income comes through working with delicate subjects — anxiety, fear, the unconscious",
        "block_en": "selling to someone else's anxiety instead of actually easing it",
    },
    19: {
        "flow_ru": "деньги приходят через открытость и естественное тепло к людям",
        "block_ru": "гнаться за показным успехом вместо настоящего контакта с аудиторией",
        "flow_en": "money comes through openness and natural warmth toward people",
        "block_en": "chasing the appearance of success instead of real contact with an audience",
    },
    20: {
        "flow_ru": "доход раскрывается через честный пересмотр родовых установок о деньгах",
        "block_ru": "нести родительский сценарий о деньгах, даже не заметив, что он не твой",
        "flow_en": "income opens up through an honest look at inherited beliefs about money",
        "block_en": "carrying a parent's money story without ever noticing it isn't yours",
    },
    21: {
        "flow_ru": "деньги приходят через масштаб — международную работу, широкий охват, завершённые проекты",
        "block_ru": "искусственно сужать себя до локального, привычного, безопасного",
        "flow_en": "money comes through scale — international work, wide reach, finished projects",
        "block_en": "artificially shrinking to the local, familiar, and safe",
    },
    22: {
        "flow_ru": "доход приходит через независимость — работу на себя, пассивные источники",
        "block_ru": "оставаться в чужой структуре из страха перед ответственностью за своё дело",
        "flow_en": "income comes through independence — working for yourself, passive sources",
        "block_en": "staying inside someone else's structure for fear of owning your own venture",
    },
}


def money_energy(n: int, lang: str) -> dict[str, str]:
    base = MONEY_ENERGY[n]
    return {
        "flow": pick(base, "flow", lang, MONEY_ENERGY_I18N, str(n)),
        "block": pick(base, "block", lang, MONEY_ENERGY_I18N, str(n)),
    }


def build_money_line(birth: date, lang: str) -> dict:
    """Full API payload: the three positions with their arcana number and
    money-specific energy keywords. Deterministic, same pattern as
    build_karmic_tail() — nothing here is persisted."""
    points = calculate(birth)
    values = calculate_money_line(points)
    return {
        "positions": [
            {"id": pos, "arcana": values[pos], **money_energy(values[pos], lang)}
            for pos in MONEY_LINE_POSITIONS
        ],
    }
