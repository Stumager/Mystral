from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.seo_generator import get_seo_content
from app.data.seo_data import (
    LUNAR_DAY_BY_SLUG, LUNAR_DAY_SEO, NATAL_PLANETS, NATAL_PLANETS_BY_SLUG,
    NUMEROLOGY_BY_SLUG, NUMEROLOGY_SEO, RUNE_BY_SLUG, RUNE_SEO,
    SUITS, TAROT_BY_SLUG, TAROT_CARDS, ZODIAC_BY_SLUG, ZODIAC_SIGNS,
)
from app.data.seo_i18n import (
    ALL_LANGS, LANG_NATIVE, OG_LOCALE, PREFIX_LANGS, SUITS_HDR, UI,
    abs_url, hreflang_alternates, localize_card, localize_lunar_day,
    localize_natal_planet, localize_num, localize_rune, localize_sign,
    url_prefix,
)

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))
TODAY = lambda: date.today().isoformat()


def _resolve_lang(lang: Optional[str]) -> str:
    """None (root path) -> ru; unknown prefix -> plain 404, not a 422 JSON body."""
    if lang is None:
        return "ru"
    if lang not in PREFIX_LANGS:
        raise HTTPException(404)
    return lang


def _legacy_lang_redirect(request: Request, lang: str, path: str) -> Optional[RedirectResponse]:
    """The old hreflang markup advertised ?lang=xx URLs for months — 301 any
    such indexed URL to its real subdirectory version. Only relevant on the
    root (ru) routes; junk or ?lang=ru just falls through to the ru page."""
    if lang != "ru":
        return None
    q = request.query_params.get("lang")
    if q in PREFIX_LANGS:
        return RedirectResponse(f"/{q}{path}", status_code=301)
    return None


def _ctx(lang: str, path: str, title: str, description: str, content: Optional[dict] = None, **extra) -> dict:
    """Shared template context: chrome translations, canonical, hreflang set,
    language-switcher data, fallback flag for robots noindex."""
    ctx = {
        "lang": lang,
        "t": UI[lang],
        "prefix": url_prefix(lang),
        "canonical": abs_url(lang, path),
        "alternates": hreflang_alternates(path),
        "lang_native": LANG_NATIVE,
        "og_locale": OG_LOCALE[lang],
        "title": title,
        "description": description,
        "content": content,
        "faq": (content or {}).get("faq") or None,
        "cta_text": (content or {}).get("cta_text"),
        "is_fallback": bool((content or {}).get("_fallback")),
    }
    ctx.update(extra)
    return ctx


@router.get("/zodiac", response_class=HTMLResponse)
@router.get("/{lang}/zodiac", response_class=HTMLResponse)
async def zodiac_hub(request: Request):
    lang = _resolve_lang(request.path_params.get("lang"))
    redirect = _legacy_lang_redirect(request, lang, "/zodiac")
    if redirect:
        return redirect
    t = UI[lang]
    return templates.TemplateResponse(request, "seo/zodiac_hub.html", _ctx(
        lang, "/zodiac", t["zodiac_hub_title"], t["zodiac_hub_desc"],
        signs=[localize_sign(s, lang) for s in ZODIAC_SIGNS],
    ))


@router.get("/zodiac/{slug}", response_class=HTMLResponse)
@router.get("/{lang}/zodiac/{slug}", response_class=HTMLResponse)
async def zodiac_sign(slug: str, request: Request, session: AsyncSession = Depends(get_session)):
    lang = _resolve_lang(request.path_params.get("lang"))
    redirect = _legacy_lang_redirect(request, lang, f"/zodiac/{slug}")
    if redirect:
        return redirect
    raw = ZODIAC_BY_SLUG.get(slug)
    if not raw:
        raise HTTPException(404)
    sign = localize_sign(raw, lang)
    content = await get_seo_content("zodiac", slug, sign, session, lang)
    t = UI[lang]
    return templates.TemplateResponse(request, "seo/zodiac_sign.html", _ctx(
        lang, f"/zodiac/{slug}",
        t["zodiac_title"].format(**sign),
        t["zodiac_desc"].format(**sign),
        content=content,
        sign=sign,
        all_signs=[localize_sign(s, lang) for s in ZODIAC_SIGNS],
        h1=t["zodiac_h1"].format(**sign),
        og_image=abs_url(lang, f"/zodiac/{slug}/constellation.svg"),
        today=TODAY(),
        # TZ-085: zodiac is the only section with a relevant landing so far
        # (natal-chart) — everything else keeps the default "/" CTA target
        # until their own landings exist.
        cta_href=f"{url_prefix(lang)}/natal-chart",
    ))


@router.get("/tarot", response_class=HTMLResponse)
@router.get("/{lang}/tarot", response_class=HTMLResponse)
async def tarot_hub(request: Request):
    lang = _resolve_lang(request.path_params.get("lang"))
    redirect = _legacy_lang_redirect(request, lang, "/tarot")
    if redirect:
        return redirect
    t = UI[lang]
    major = [localize_card(c, lang) for c in TAROT_CARDS if c["arcana"] == "major"]
    suits_data = []
    for si, suit in enumerate(SUITS):
        cards = [localize_card(c, lang) for c in TAROT_CARDS if c["suit"] == suit]
        suits_data.append((suit, SUITS_HDR[lang][si], cards))
    return templates.TemplateResponse(request, "seo/tarot_hub.html", _ctx(
        lang, "/tarot", t["tarot_hub_title"], t["tarot_hub_desc"],
        major=major, suits=suits_data,
    ))


@router.get("/tarot/{slug}", response_class=HTMLResponse)
@router.get("/{lang}/tarot/{slug}", response_class=HTMLResponse)
async def tarot_card(slug: str, request: Request, session: AsyncSession = Depends(get_session)):
    lang = _resolve_lang(request.path_params.get("lang"))
    redirect = _legacy_lang_redirect(request, lang, f"/tarot/{slug}")
    if redirect:
        return redirect
    card = TAROT_BY_SLUG.get(slug)
    if not card:
        raise HTTPException(404)
    lcard = localize_card(card, lang)
    name = lcard["display_name"]
    gen_data = card if lang == "ru" else {**card, "name": name}
    content = await get_seo_content("tarot", slug, gen_data, session, lang)
    idx = TAROT_CARDS.index(card)
    prev_card = localize_card(TAROT_CARDS[idx - 1], lang) if idx > 0 else None
    next_card = localize_card(TAROT_CARDS[idx + 1], lang) if idx < len(TAROT_CARDS) - 1 else None
    if card["arcana"] == "major":
        related = [c for c in TAROT_CARDS if c["arcana"] == "major" and c["slug"] != slug]
    else:
        related = [c for c in TAROT_CARDS if c["suit"] == card["suit"] and c["slug"] != slug]
    t = UI[lang]
    suit_label = t["major_arcana"] if card["arcana"] == "major" else SUITS_HDR[lang][SUITS.index(card["suit"])]
    return templates.TemplateResponse(request, "seo/tarot_card.html", _ctx(
        lang, f"/tarot/{slug}",
        t["tarot_title"].format(name=name),
        t["tarot_desc"].format(name=name),
        content=content,
        card=lcard, suit_label=suit_label,
        prev=prev_card, next=next_card,
        related=[localize_card(c, lang) for c in related[:14]],
        h1=t["tarot_h1"].format(name=name),
        today=TODAY(),
    ))


@router.get("/runes", response_class=HTMLResponse)
@router.get("/{lang}/runes", response_class=HTMLResponse)
async def runes_hub(request: Request):
    lang = _resolve_lang(request.path_params.get("lang"))
    redirect = _legacy_lang_redirect(request, lang, "/runes")
    if redirect:
        return redirect
    t = UI[lang]
    return templates.TemplateResponse(request, "seo/runes_hub.html", _ctx(
        lang, "/runes", t["runes_hub_title"], t["runes_hub_desc"],
        runes=[localize_rune(r, lang) for r in RUNE_SEO],
    ))


@router.get("/runes/{slug}", response_class=HTMLResponse)
@router.get("/{lang}/runes/{slug}", response_class=HTMLResponse)
async def rune_page(slug: str, request: Request, session: AsyncSession = Depends(get_session)):
    lang = _resolve_lang(request.path_params.get("lang"))
    redirect = _legacy_lang_redirect(request, lang, f"/runes/{slug}")
    if redirect:
        return redirect
    raw = RUNE_BY_SLUG.get(slug)
    if not raw:
        raise HTTPException(404)
    rune = localize_rune(raw, lang)
    content = await get_seo_content("rune", slug, rune, session, lang)
    t = UI[lang]
    return templates.TemplateResponse(request, "seo/rune.html", _ctx(
        lang, f"/runes/{slug}",
        t["rune_title"].format(**rune),
        t["rune_desc"].format(**rune),
        content=content,
        rune=rune,
        all_runes=[localize_rune(r, lang) for r in RUNE_SEO],
        aett_label=t["aett_fmt"].format(aett=rune["aett"]),
        h1=t["rune_h1"].format(**rune),
        today=TODAY(),
    ))


@router.get("/numerology/{slug}", response_class=HTMLResponse)
@router.get("/{lang}/numerology/{slug}", response_class=HTMLResponse)
async def numerology_page(slug: str, request: Request, session: AsyncSession = Depends(get_session)):
    lang = _resolve_lang(request.path_params.get("lang"))
    redirect = _legacy_lang_redirect(request, lang, f"/numerology/{slug}")
    if redirect:
        return redirect
    raw = NUMEROLOGY_BY_SLUG.get(slug)
    if not raw:
        raise HTTPException(404)
    num = localize_num(raw, lang)
    content = await get_seo_content("numerology", slug, num, session, lang)
    t = UI[lang]
    return templates.TemplateResponse(request, "seo/numerology.html", _ctx(
        lang, f"/numerology/{slug}",
        t["num_title"].format(**num),
        t["num_desc"].format(**num),
        content=content,
        num=num,
        all_nums=[localize_num(n, lang) for n in NUMEROLOGY_SEO],
        h1=t["num_h1"].format(**num),
        today=TODAY(),
    ))


@router.get("/natal-chart", response_class=HTMLResponse)
@router.get("/{lang}/natal-chart", response_class=HTMLResponse)
async def natal_chart_hub(request: Request):
    lang = _resolve_lang(request.path_params.get("lang"))
    redirect = _legacy_lang_redirect(request, lang, "/natal-chart")
    if redirect:
        return redirect
    t = UI[lang]
    return templates.TemplateResponse(request, "seo/natal_hub.html", _ctx(
        lang, "/natal-chart", t["natal_hub_title"], t["natal_hub_desc"],
        planets=[localize_natal_planet(p, lang) for p in NATAL_PLANETS],
    ))


@router.get("/natal-chart/planets/{slug}", response_class=HTMLResponse)
@router.get("/{lang}/natal-chart/planets/{slug}", response_class=HTMLResponse)
async def natal_planet_page(slug: str, request: Request, session: AsyncSession = Depends(get_session)):
    lang = _resolve_lang(request.path_params.get("lang"))
    redirect = _legacy_lang_redirect(request, lang, f"/natal-chart/planets/{slug}")
    if redirect:
        return redirect
    raw = NATAL_PLANETS_BY_SLUG.get(slug)
    if not raw:
        raise HTTPException(404)
    planet = localize_natal_planet(raw, lang)
    content = await get_seo_content("natal_planet", slug, planet, session, lang)
    t = UI[lang]
    return templates.TemplateResponse(request, "seo/natal_planet.html", _ctx(
        lang, f"/natal-chart/planets/{slug}",
        t["natal_planet_title"].format(**planet),
        t["natal_planet_desc"].format(**planet),
        content=content,
        planet=planet,
        all_planets=[localize_natal_planet(p, lang) for p in NATAL_PLANETS],
        h1=t["natal_planet_h1"].format(**planet),
        today=TODAY(),
    ))


@router.get("/lunar-calendar", response_class=HTMLResponse)
@router.get("/{lang}/lunar-calendar", response_class=HTMLResponse)
async def lunar_calendar_hub(request: Request):
    lang = _resolve_lang(request.path_params.get("lang"))
    redirect = _legacy_lang_redirect(request, lang, "/lunar-calendar")
    if redirect:
        return redirect
    t = UI[lang]
    return templates.TemplateResponse(request, "seo/lunar_hub.html", _ctx(
        lang, "/lunar-calendar", t["lunar_hub_title"], t["lunar_hub_desc"],
        days=[localize_lunar_day(d, lang) for d in LUNAR_DAY_SEO],
    ))


@router.get("/lunar-calendar/day/{slug}", response_class=HTMLResponse)
@router.get("/{lang}/lunar-calendar/day/{slug}", response_class=HTMLResponse)
async def lunar_day_page(slug: str, request: Request, session: AsyncSession = Depends(get_session)):
    lang = _resolve_lang(request.path_params.get("lang"))
    redirect = _legacy_lang_redirect(request, lang, f"/lunar-calendar/day/{slug}")
    if redirect:
        return redirect
    raw = LUNAR_DAY_BY_SLUG.get(slug)
    if not raw:
        raise HTTPException(404)
    day = localize_lunar_day(raw, lang)
    content = await get_seo_content("lunar_day", slug, day, session, lang)
    t = UI[lang]
    n = day["number"]
    prev_day = localize_lunar_day(LUNAR_DAY_BY_SLUG[str(n - 1)], lang) if n > 1 else None
    next_day = localize_lunar_day(LUNAR_DAY_BY_SLUG[str(n + 1)], lang) if n < 30 else None
    return templates.TemplateResponse(request, "seo/lunar_day.html", _ctx(
        lang, f"/lunar-calendar/day/{slug}",
        t["lunar_day_title"].format(**day),
        t["lunar_day_desc"].format(**day),
        content=content,
        day=day,
        prev=prev_day, next=next_day,
        all_days=[localize_lunar_day(d, lang) for d in LUNAR_DAY_SEO],
        h1=t["lunar_day_h1"].format(**day),
        today=TODAY(),
    ))


CONSTELLATIONS = {
    "aries": {"pts": [[28,48],[45,38],[68,30]], "lines": [[0,1],[1,2]], "bright": [2]},
    "taurus": {"pts": [[22,20],[40,45],[28,58],[22,52],[50,58],[52,72],[60,40]], "lines": [[0,1],[1,2],[2,3],[1,4],[4,5],[3,5],[0,6]], "bright": [0,5]},
    "gemini": {"pts": [[42,16],[60,18],[38,30],[34,48],[28,65],[64,30],[70,48],[72,65]], "lines": [[0,1],[0,2],[2,3],[3,4],[1,5],[5,6],[6,7]], "bright": [0,1]},
    "cancer": {"pts": [[48,18],[48,38],[54,52],[72,60],[28,72],[50,72]], "lines": [[0,1],[1,2],[2,3],[2,5],[5,4]], "bright": [4]},
    "leo": {"pts": [[78,18],[72,22],[65,32],[60,44],[55,58],[45,70],[58,52],[42,42],[22,38]], "lines": [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,8]], "bright": [3,5,8]},
    "virgo": {"pts": [[68,18],[62,32],[48,48],[30,42],[22,28],[32,68],[62,62],[75,72]], "lines": [[0,1],[1,2],[2,3],[3,4],[3,5],[2,6],[6,7]], "bright": [2,5]},
    "libra": {"pts": [[35,28],[62,20],[45,62],[68,55],[20,55]], "lines": [[0,1],[1,3],[0,4],[0,2],[2,3]], "bright": [0,2]},
    "scorpio": {"pts": [[28,22],[42,20],[58,22],[45,32],[35,42],[28,52],[22,62],[20,72],[22,80],[30,86],[40,88],[50,84],[58,78],[65,72],[70,68]], "lines": [[0,1],[1,2],[1,3],[3,4],[4,5],[5,6],[6,7],[7,8],[8,9],[9,10],[10,11],[11,12],[12,13],[13,14]], "bright": [4,13]},
    "sagittarius": {"pts": [[22,50],[28,35],[35,28],[45,35],[32,55],[45,58],[60,52],[68,40],[22,58]], "lines": [[8,0],[0,4],[4,5],[5,6],[6,7],[0,1],[1,2],[2,3],[3,7],[1,4]], "bright": [2,4,6]},
    "capricorn": {"pts": [[25,32],[58,22],[22,55],[45,50],[72,42],[42,68]], "lines": [[0,1],[1,4],[4,5],[5,2],[2,0],[0,3],[3,4],[2,3]], "bright": [1,4]},
    "aquarius": {"pts": [[30,28],[48,22],[65,32],[58,42],[72,55],[42,50],[38,65],[28,58]], "lines": [[0,1],[1,2],[2,3],[3,4],[3,5],[5,6],[5,7],[1,5]], "bright": [1,2]},
    "pisces": {"pts": [[22,62],[15,52],[18,42],[26,36],[34,42],[30,55],[44,58],[55,42],[65,28],[75,25],[80,35],[78,45],[68,52],[56,55]], "lines": [[0,1],[1,2],[2,3],[3,4],[4,5],[5,0],[5,6],[6,7],[7,8],[8,9],[9,10],[10,11],[11,12],[12,6]], "bright": [3,6,9]},
}


@router.get("/zodiac/{slug}/constellation.svg", response_class=Response)
@router.get("/{lang}/zodiac/{slug}/constellation.svg", response_class=Response)
async def constellation_svg(slug: str, request: Request):
    lang = _resolve_lang(request.path_params.get("lang"))
    c = CONSTELLATIONS.get(slug)
    if not c:
        raise HTTPException(404)
    sign = localize_sign(ZODIAC_BY_SLUG[slug], lang)
    lines_svg = "".join(f'<line x1="{c["pts"][a][0]}" y1="{c["pts"][a][1]}" x2="{c["pts"][b][0]}" y2="{c["pts"][b][1]}" stroke="rgba(201,168,76,.5)" stroke-width="1"/>' for a, b in c["lines"])
    dots_svg = "".join(
        f'<circle cx="{p[0]}" cy="{p[1]}" r="{"2.8" if i in c["bright"] else "1.6"}" fill="#F0D680"/>'
        f'<circle cx="{p[0]}" cy="{p[1]}" r="{"8" if i in c["bright"] else "5"}" fill="none" stroke="rgba(240,214,128,.25)" stroke-width="1" opacity="{"0.28" if i in c["bright"] else "0.15"}"/>'
        for i, p in enumerate(c["pts"])
    )
    svg = f'''<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="300" height="300" style="background:radial-gradient(circle,#1C1650,#07060F)">
<defs><filter id="g"><feGaussianBlur stdDeviation="2"/></filter></defs>
<circle cx="50" cy="50" r="45" fill="none" stroke="rgba(201,168,76,.12)" stroke-width=".5" stroke-dasharray="1 5"/>
<g filter="url(#g)" opacity=".6">{lines_svg}{dots_svg}</g>
<g>{lines_svg}{dots_svg}</g>
<text x="50" y="94" text-anchor="middle" font-family="Cinzel,serif" font-size="5" letter-spacing=".2em" fill="#C9A84C">{sign.get("name","").upper()}</text>
</svg>'''
    return Response(content=svg, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})


@router.get("/sitemap.xml", response_class=Response)
async def sitemap():
    today = date.today().isoformat()
    paths = [("/zodiac", "0.9"), ("/tarot", "0.9"), ("/runes", "0.9"), ("/natal-chart", "0.9"), ("/lunar-calendar", "0.9")]
    for s in ZODIAC_SIGNS:
        paths.append((f"/zodiac/{s['slug']}", "0.9"))
    for c in TAROT_CARDS:
        paths.append((f"/tarot/{c['slug']}", "0.8"))
    for r in RUNE_SEO:
        paths.append((f"/runes/{r['slug']}", "0.8"))
    for n in NUMEROLOGY_SEO:
        paths.append((f"/numerology/{n['slug']}", "0.7"))
    for p in NATAL_PLANETS:
        paths.append((f"/natal-chart/planets/{p['slug']}", "0.8"))
    for d in LUNAR_DAY_SEO:
        paths.append((f"/lunar-calendar/day/{d['slug']}", "0.8"))

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n')
    # The SPA homepage has no per-language URLs — one plain entry, no hreflang.
    xml += f"<url><loc>https://mystral.space/</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>1.0</priority></url>\n"
    for path, prio in paths:
        links = "".join(
            f'<xhtml:link rel="alternate" hreflang="{hl}" href="{url}"/>'
            for hl, url in hreflang_alternates(path)
        )
        for lang in ALL_LANGS:
            xml += (f"<url><loc>{abs_url(lang, path)}</loc><lastmod>{today}</lastmod>"
                    f"<changefreq>weekly</changefreq><priority>{prio}</priority>{links}</url>\n")
    xml += "</urlset>"
    return Response(content=xml, media_type="application/xml")
