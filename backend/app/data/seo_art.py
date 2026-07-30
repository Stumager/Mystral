"""TZ-110: hero line-art for the three pillar landings, built once at import.

Geometry lives here rather than in the Jinja templates because Jinja has no
trig — every ring, spoke and tick below is a real polar computation, not a
hand-typed coordinate table that silently rots the moment a radius changes.
The aesthetic is the one already approved for the bot's intro image
(bot/static/welcome.jpg): gold line-work on near-black, octagrams,
constellation joins, a solid gold crescent.

Each constant is a complete <svg> string with aria-hidden="true" — the
accessible name is supplied by the template wrapper (localized via
seo_i18n.UI's hero_*_alt keys), so the art itself carries no text to
translate. Animations are scoped to .mx-* classes defined in the pillar
stylesheet, which disables them under prefers-reduced-motion.
"""

import math

GOLD = "#C9A84C"
GOLD_LIGHT = "#E8CD7E"
GOLD_PALE = "#F0D680"

# U+FE0E (VARIATION SELECTOR-15) forces *text* presentation. Without it every
# browser tested substitutes its colour emoji font for U+2648–U+2653 and the
# glyphs come out as purple emoji tiles that ignore fill= entirely — the
# opposite of the gold line-work this art is supposed to be. Confirmed live,
# not assumed: the first render of the natal wheel showed exactly that.
_VS15 = "︎"
_ZODIAC_GLYPHS = [g + _VS15 for g in
                  ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]]


def _polar(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
    """Screen coords for a polar point, 0° = straight up, clockwise."""
    a = math.radians(deg - 90)
    return round(cx + r * math.cos(a), 1), round(cy + r * math.sin(a), 1)


def _line(x1, y1, x2, y2, stroke, width=1, opacity=1.0, extra="") -> str:
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{width}" opacity="{opacity}"{extra}/>')


def _star_field(seed_points: list[tuple[float, float, float]]) -> str:
    """Fixed (not random) background stars — a stable page must render
    byte-identically on every request so ETag/caching stays meaningful."""
    return "".join(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="{GOLD_PALE}" opacity="{0.15 + r * 0.35:.2f}"/>'
        for x, y, r in seed_points
    )


def _octagram(cx: float, cy: float, r: float, stroke: str, width: float = 1, opacity: float = 1.0) -> str:
    """Two overlaid squares at 45° — the platform's recurring mark (same
    figure as the Destiny Matrix octagram from TZ-099)."""
    out = []
    for offset in (0, 45):
        pts = [_polar(cx, cy, r, offset + i * 90) for i in range(4)]
        d = " ".join(f"{x},{y}" for x, y in pts)
        out.append(f'<polygon points="{d}" fill="none" stroke="{stroke}" '
                   f'stroke-width="{width}" opacity="{opacity}"/>')
    return "".join(out)


def _defs(prefix: str) -> str:
    return (
        f'<defs>'
        f'<radialGradient id="{prefix}bg" cx="50%" cy="45%" r="62%">'
        f'<stop offset="0%" stop-color="#1C1650"/><stop offset="70%" stop-color="#0B0920"/>'
        f'<stop offset="100%" stop-color="#07060F"/></radialGradient>'
        f'<linearGradient id="{prefix}gold" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{GOLD_LIGHT}"/><stop offset="100%" stop-color="#A9882F"/>'
        f'</linearGradient>'
        f'<filter id="{prefix}glow" x="-40%" y="-40%" width="180%" height="180%">'
        f'<feGaussianBlur stdDeviation="4"/></filter>'
        f'</defs>'
    )


# ---------------------------------------------------------------------------
# /natal-chart — the chart wheel: 12 sectors, sign glyphs, planets, aspects.
# ---------------------------------------------------------------------------

def _build_natal_wheel() -> str:
    cx = cy = 150.0
    parts = [
        '<svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="mx-art">',
        _defs("nw"),
        f'<circle cx="{cx}" cy="{cy}" r="150" fill="url(#nwbg)"/>',
        _star_field([(28, 44, 1.1), (262, 62, .9), (46, 246, .8), (248, 232, 1.2),
                     (150, 16, .7), (18, 150, .8), (284, 158, .7), (206, 22, .6)]),
    ]

    # Outer rim + the dashed ring that slowly turns.
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="140" fill="none" stroke="{GOLD}" stroke-width="1" opacity=".55"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="118" fill="none" stroke="{GOLD}" stroke-width="1" opacity=".3"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="146" fill="none" stroke="{GOLD}" stroke-width=".8" '
                 f'opacity=".22" stroke-dasharray="2 9" class="mx-spin-slow"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="96" fill="none" stroke="{GOLD}" stroke-width="1" opacity=".22"/>')

    # 12 sector dividers between the glyph ring's two circles.
    for i in range(12):
        x1, y1 = _polar(cx, cy, 118, i * 30)
        x2, y2 = _polar(cx, cy, 140, i * 30)
        parts.append(_line(x1, y1, x2, y2, GOLD, 1, .4))

    # 12 house spokes, inner ring only — thinner, so the wheel reads as two rings.
    for i in range(12):
        x1, y1 = _polar(cx, cy, 96, i * 30 + 15)
        x2, y2 = _polar(cx, cy, 118, i * 30 + 15)
        parts.append(_line(x1, y1, x2, y2, GOLD, .8, .2))

    # Sign glyphs, centred in each sector.
    for i, glyph in enumerate(_ZODIAC_GLYPHS):
        x, y = _polar(cx, cy, 129, i * 30 + 15)
        parts.append(f'<text x="{x}" y="{y + 4.5}" text-anchor="middle" font-size="13" '
                     f'fill="{GOLD_LIGHT}" opacity=".85" font-family="serif">{glyph}</text>')

    # Planets on an inner orbit + the aspect lines between them.
    planet_deg = [28, 82, 124, 186, 230, 278, 334]
    pts = [_polar(cx, cy, 80, d) for d in planet_deg]
    for a, b in [(0, 3), (1, 4), (2, 5), (0, 2), (3, 5), (4, 6), (1, 6)]:
        parts.append(_line(pts[a][0], pts[a][1], pts[b][0], pts[b][1], GOLD, .9, .38,
                           ' class="mx-pulse"'))
    for i, (x, y) in enumerate(pts):
        r = 3.4 if i % 2 == 0 else 2.6
        parts.append(f'<circle cx="{x}" cy="{y}" r="{r + 5}" fill="none" stroke="{GOLD_PALE}" '
                     f'stroke-width=".8" opacity=".2"/>')
        parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{GOLD_PALE}"/>')

    parts.append(_octagram(cx, cy, 26, GOLD_LIGHT, 1, .5))
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{GOLD_PALE}" filter="url(#nwglow)" opacity=".8"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="2.4" fill="{GOLD_PALE}"/>')
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# /lunar-calendar — 30 day ticks around a solid gold crescent.
# ---------------------------------------------------------------------------

def _build_lunar_circle() -> str:
    cx = cy = 150.0
    parts = [
        '<svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="mx-art">',
        _defs("lc"),
        f'<circle cx="{cx}" cy="{cy}" r="150" fill="url(#lcbg)"/>',
        _star_field([(40, 58, 1.0), (256, 48, .8), (34, 232, .9), (262, 244, 1.1),
                     (150, 22, .8), (24, 146, .7), (278, 150, .9), (196, 276, .6)]),
    ]

    parts.append(f'<circle cx="{cx}" cy="{cy}" r="140" fill="none" stroke="{GOLD}" stroke-width=".8" opacity=".28"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="146" fill="none" stroke="{GOLD}" stroke-width=".8" '
                 f'opacity=".2" stroke-dasharray="1 7" class="mx-spin-slow"/>')

    # 30 lunar-day ticks; the quarter days (1, 8, 15, 22) reach further in.
    for i in range(30):
        deg = i * 12
        quarter = i in (0, 7, 14, 21)
        inner = 118 if quarter else 128
        x1, y1 = _polar(cx, cy, inner, deg)
        x2, y2 = _polar(cx, cy, 138, deg)
        parts.append(_line(x1, y1, x2, y2, GOLD_LIGHT if quarter else GOLD,
                           1.4 if quarter else .9, .8 if quarter else .38))
        if quarter:
            px, py = _polar(cx, cy, 110, deg)
            parts.append(f'<circle cx="{px}" cy="{py}" r="2.4" fill="{GOLD_PALE}" opacity=".7"/>')

    # The crescent: one gold disc with a second disc masked out of it.
    parts.append(
        '<mask id="lccut">'
        '<rect width="300" height="300" fill="#000"/>'
        f'<circle cx="{cx}" cy="{cy}" r="62" fill="#fff"/>'
        f'<circle cx="{cx + 29}" cy="{cy - 11}" r="55" fill="#000"/>'
        '</mask>'
    )
    parts.append(f'<g mask="url(#lccut)" class="mx-breathe">'
                 f'<circle cx="{cx}" cy="{cy}" r="62" fill="url(#lcgold)" filter="url(#lcglow)" opacity=".55"/>'
                 f'<circle cx="{cx}" cy="{cy}" r="62" fill="url(#lcgold)"/></g>')

    # The dark disc's own edge, so the waning half still reads as a sphere.
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="62" fill="none" stroke="{GOLD}" stroke-width=".8" opacity=".3"/>')
    parts.append(_octagram(cx, cy, 88, GOLD, .8, .16))
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# /compatibility — two sign circles bound by an octagram at their overlap.
# ---------------------------------------------------------------------------

def _build_compat_rings() -> str:
    cx = cy = 150.0
    lx, rx = 108.0, 192.0
    parts = [
        '<svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="mx-art">',
        _defs("cr"),
        f'<circle cx="{cx}" cy="{cy}" r="150" fill="url(#crbg)"/>',
        _star_field([(36, 52, 1.0), (258, 60, .9), (44, 240, .8), (252, 238, 1.0),
                     (150, 18, .7), (20, 152, .8), (282, 148, .7), (150, 284, .6)]),
    ]

    parts.append(f'<circle cx="{cx}" cy="{cy}" r="144" fill="none" stroke="{GOLD}" stroke-width=".8" '
                 f'opacity=".2" stroke-dasharray="2 9" class="mx-spin-slow"/>')

    # The two circles of the pair, overlapping into a vesica.
    for x in (lx, rx):
        parts.append(f'<circle cx="{x}" cy="{cy}" r="84" fill="none" stroke="{GOLD}" stroke-width="1.1" opacity=".5"/>')
        parts.append(f'<circle cx="{x}" cy="{cy}" r="74" fill="none" stroke="{GOLD}" stroke-width=".8" opacity=".2"/>')

    # Constellation-style joins across the vesica, the "aspect" reading.
    left_pts = [_polar(lx, cy, 74, d) for d in (312, 348, 24, 60)]
    right_pts = [_polar(rx, cy, 74, d) for d in (192, 228, 264, 300)]
    for i, (a, b) in enumerate([(0, 3), (1, 2), (2, 1), (3, 0)]):
        parts.append(_line(left_pts[a][0], left_pts[a][1], right_pts[b][0], right_pts[b][1],
                           GOLD_LIGHT, .9, .3, ' class="mx-pulse"'))
    for x, y in left_pts + right_pts:
        parts.append(f'<circle cx="{x}" cy="{y}" r="2.6" fill="{GOLD_PALE}" opacity=".85"/>')

    # A sign glyph anchoring each circle.
    parts.append(f'<text x="{lx - 30}" y="{cy + 8}" text-anchor="middle" font-size="24" '
                 f'fill="{GOLD_LIGHT}" opacity=".8" font-family="serif">♌{_VS15}</text>')
    parts.append(f'<text x="{rx + 30}" y="{cy + 8}" text-anchor="middle" font-size="24" '
                 f'fill="{GOLD_LIGHT}" opacity=".8" font-family="serif">♎{_VS15}</text>')

    parts.append(_octagram(cx, cy, 40, GOLD_LIGHT, 1, .55))
    parts.append(_octagram(cx, cy, 26, GOLD, .8, .3))
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="{GOLD_PALE}" filter="url(#crglow)" opacity=".7"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="{GOLD_PALE}"/>')
    parts.append("</svg>")
    return "".join(parts)


NATAL_WHEEL_SVG = _build_natal_wheel()
LUNAR_CIRCLE_SVG = _build_lunar_circle()
COMPAT_RINGS_SVG = _build_compat_rings()

HERO_SVG = {
    "natal": NATAL_WHEEL_SVG,
    "lunar": LUNAR_CIRCLE_SVG,
    "compat": COMPAT_RINGS_SVG,
}
