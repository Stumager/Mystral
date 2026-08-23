"""TZ-118: Совместимость по Матрице судьбы (Destiny Matrix compatibility) —
the fourth and final module built on the base matrix from TZ-101, and the
first that needs a second person's birth data rather than reinterpreting the
same nine points through a new lens.

Step 0 (verified before writing this — see PROGRESS.md): matrica-sudby.ru
gives a worked numeric example for the compatibility centre point — "в
центре его Матрицы — 6 энергия, у нее — 8... получаем 14" — which is
exactly reduce22(person1.core + person2.core), nothing more elaborate.

The stronger, structural confirmation is the karmic tail: that same site
publishes a 26-entry named table for "the couple's karmic tail" that matches
this codebase's own KARMIC_TAIL table code-for-code (3-7-22 "Узник", 6-14-8
"Диктатор", 9-12-3 "Одинокая женщина", etc. — checked line by line). That
can't be a coincidental naming overlap: it means the compatibility karmic
tail isn't a separate system at all — it's calculate_tail() run on a
(core, realization) pair built the same way as the centre, and every one of
its 26 possible outcomes was already reachable and already named by TZ-114.
Confirmed end-to-end with two of this codebase's own already-verified
reference dates (see tests): 1990-05-15 (core=6) + 1987-12-03 (core=8) give
centre=14 exactly as the site's example, and their combined karmic tail is
21-10-7 — which the same site's table calls "Воин веры", matching this
project's existing KARMIC_TAIL["21-10-7"]["name_ru"] exactly.

A third, independent source (vc.ru/"Матрица Души" — different author, same
niche) confirms the same overlay structure in prose (build each partner's
matrix, then compute a handful of shared points) and separately names a
money/finance point and an "attraction" point. Neither of those turned up a
worked numeric example anywhere checked, including a live paywalled
calculator, and there is no known target value to run a TZ-115-style
point-B disambiguation simulation against — that technique needs a known
answer to test candidates against, and none exists here. Per product owner
decision: not guessing. v1 ships exactly the two indicators confirmed above;
a money/attraction indicator is a later add-on, only if a real worked
example turns up.

Copyright: no new naming system. The centre reuses plain Tarot Major Arcana
names (arcana_name(), already in destiny_matrix.py); the karmic tail reuses
KARMIC_TAIL verbatim, including its existing TZ-114 content-safety
substitution ("Точка невозврата" for the source's "Суицид") — nothing here
needed a fresh naming or copyright decision.

Content safety: reviewed with the product owner. The karmic-tail essence/
task text is unchanged from TZ-114's individual-context wording — no
separate couple framing, by product owner decision, despite compatibility
being a genre where sources lean toward categorical verdicts ("15-8-11
Физическая агрессия... крики и даже рукоприкладство" in the source text,
already reframed here as unprocessed anger rather than a partner-directed
prediction — TZ-114's existing text carries over as-is). The one new piece
of copy — the interpret prompt's explicit "no predetermined good/bad
combination" framing below — is original wording built around an idea
independently confirmed by vc.ru ("не существует «плохих» сочетаний,
которые заранее обрекают пару"), not a translation or paraphrase of that
sentence.
"""
from __future__ import annotations

from datetime import date

from app.core.structural_i18n import pick
from app.data.destiny_matrix import arcana_energy, arcana_name, calculate, reduce22
from app.data.karmic_tail import KARMIC_TAIL, calculate_tail, tail_code
from app.data.karmic_tail_i18n import KARMIC_TAIL_I18N


def combined_points(birth1: date, birth2: date) -> dict[str, int]:
    """The only two base-matrix points v1 needs, each folded the same way
    matrica-sudby.ru's worked example folds the centre: reduce22 of the sum
    of both partners' values at that position. See module docstring."""
    p1, p2 = calculate(birth1), calculate(birth2)
    return {
        "core": reduce22(p1["core"] + p2["core"]),
        "realization": reduce22(p1["realization"] + p2["realization"]),
    }


def build_compatibility(birth1: date, birth2: date, lang: str) -> dict:
    """Full API payload: the combined centre arcana and the couple's karmic
    tail. Deterministic — the same pair of birth dates always yields the
    same result, nothing persisted, same shape as build_matrix()/
    build_karmic_tail() in the sibling modules."""
    points = combined_points(birth1, birth2)
    centre = points["core"]
    tail = calculate_tail(points)
    code = tail_code(tail)
    entry = KARMIC_TAIL[code]
    return {
        "centre": {
            "arcana": centre,
            "arcana_name": arcana_name(centre, lang),
            **arcana_energy(centre, lang),
        },
        "karmic_tail": {
            "t1": tail[0], "t2": tail[1], "t3": tail[2],
            "code": code,
            "name": pick(entry, "name", lang, KARMIC_TAIL_I18N, code),
            "essence": pick(entry, "essence", lang, KARMIC_TAIL_I18N, code),
            "task": pick(entry, "task", lang, KARMIC_TAIL_I18N, code),
        },
    }
