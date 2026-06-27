from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.seo_generator import get_seo_content
from app.data.seo_data import (
    NUMEROLOGY_BY_SLUG, NUMEROLOGY_SEO, RUNE_BY_SLUG, RUNE_SEO,
    SUITS, SUITS_RU, TAROT_BY_SLUG, TAROT_CARDS, ZODIAC_BY_SLUG, ZODIAC_SIGNS,
)

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))
TODAY = lambda: date.today().isoformat()


@router.get("/zodiac", response_class=HTMLResponse)
async def zodiac_hub(request: Request):
    return templates.TemplateResponse("seo/zodiac_hub.html", {
        "request": request, "signs": ZODIAC_SIGNS,
        "title": "Знаки зодиака — характеристика и совместимость | Mystral",
        "description": "Все 12 знаков зодиака с подробной характеристикой, совместимостью и персональным гороскопом. Узнайте свой знак на Mystral.",
        "canonical": "https://mystral.space/zodiac",
        "faq": None, "cta_text": None,
    })


@router.get("/zodiac/{slug}", response_class=HTMLResponse)
async def zodiac_sign(slug: str, request: Request, session: AsyncSession = Depends(get_session)):
    sign = ZODIAC_BY_SLUG.get(slug)
    if not sign:
        raise HTTPException(404)
    content = await get_seo_content("zodiac", slug, sign, session)
    return templates.TemplateResponse("seo/zodiac_sign.html", {
        "request": request, "sign": sign, "content": content, "all_signs": ZODIAC_SIGNS,
        "h1": f"{sign['name']} — знак зодиака: характер и гороскоп",
        "title": f"{sign['name']} — характеристика, гороскоп и совместимость | Mystral",
        "description": f"{sign['name']} — знак {sign['element']} ({sign['dates']}). Характер, совместимость, карьера и любовь. Персональный гороскоп, натальная карта и расклады Таро бесплатно на Mystral — эзотерической платформе.",
        "canonical": f"https://mystral.space/zodiac/{slug}",
        "og_image": f"https://mystral.space/zodiac/{slug}/constellation.svg",
        "faq": content.get("faq", []), "cta_text": content.get("cta_text"),
        "today": TODAY(),
    })


@router.get("/tarot", response_class=HTMLResponse)
async def tarot_hub(request: Request):
    major = [c for c in TAROT_CARDS if c["arcana"] == "major"]
    suits_data = []
    for si, suit in enumerate(SUITS):
        cards = [c for c in TAROT_CARDS if c["suit"] == suit]
        suits_data.append((suit, SUITS_RU[si], cards))
    return templates.TemplateResponse("seo/tarot_hub.html", {
        "request": request, "major": major, "suits": suits_data,
        "title": "Карты Таро — значение всех 78 карт | Mystral",
        "description": "Полный справочник карт Таро: 22 Старших Аркана и 56 Младших Арканов с подробным значением.",
        "canonical": "https://mystral.space/tarot",
        "faq": None, "cta_text": None,
    })


@router.get("/tarot/{slug}", response_class=HTMLResponse)
async def tarot_card(slug: str, request: Request, session: AsyncSession = Depends(get_session)):
    card = TAROT_BY_SLUG.get(slug)
    if not card:
        raise HTTPException(404)
    content = await get_seo_content("tarot", slug, card, session)
    idx = TAROT_CARDS.index(card)
    prev_card = TAROT_CARDS[idx - 1] if idx > 0 else None
    next_card = TAROT_CARDS[idx + 1] if idx < len(TAROT_CARDS) - 1 else None
    if card["arcana"] == "major":
        related = [c for c in TAROT_CARDS if c["arcana"] == "major" and c["slug"] != slug]
    else:
        related = [c for c in TAROT_CARDS if c["suit"] == card["suit"] and c["slug"] != slug]
    return templates.TemplateResponse("seo/tarot_card.html", {
        "request": request, "card": card, "content": content,
        "prev": prev_card, "next": next_card, "related": related[:14],
        "h1": f"{card['name_ru']} — значение в Таро",
        "title": f"{card['name_ru']} — значение карты Таро | Mystral",
        "description": f"Значение карты Таро «{card['name_ru']}» в прямом и обратном положении. Толкование в любви, карьере, финансах.",
        "canonical": f"https://mystral.space/tarot/{slug}",
        "faq": content.get("faq", []), "cta_text": content.get("cta_text"),
        "today": TODAY(),
    })


@router.get("/runes", response_class=HTMLResponse)
async def runes_hub(request: Request):
    return templates.TemplateResponse("seo/runes_hub.html", {
        "request": request, "runes": RUNE_SEO,
        "title": "Руны Старшего Футарка — значение и толкование | Mystral",
        "description": "24 руны Старшего Футарка с подробным значением, толкованием и применением в магических ставах.",
        "canonical": "https://mystral.space/runes",
        "faq": None, "cta_text": None,
    })


@router.get("/runes/{slug}", response_class=HTMLResponse)
async def rune_page(slug: str, request: Request, session: AsyncSession = Depends(get_session)):
    rune = RUNE_BY_SLUG.get(slug)
    if not rune:
        raise HTTPException(404)
    content = await get_seo_content("rune", slug, rune, session)
    return templates.TemplateResponse("seo/rune.html", {
        "request": request, "rune": rune, "content": content, "all_runes": RUNE_SEO,
        "h1": f"Руна {rune['name']} — значение и толкование",
        "title": f"Руна {rune['name']} — значение и толкование | Mystral",
        "description": f"Руна {rune['name']} ({rune['symbol']}) — подробное значение в гадании, магическое применение и использование в ставах.",
        "canonical": f"https://mystral.space/runes/{slug}",
        "faq": content.get("faq", []), "cta_text": content.get("cta_text"),
        "today": TODAY(),
    })


@router.get("/numerology/{slug}", response_class=HTMLResponse)
async def numerology_page(slug: str, request: Request, session: AsyncSession = Depends(get_session)):
    num = NUMEROLOGY_BY_SLUG.get(slug)
    if not num:
        raise HTTPException(404)
    content = await get_seo_content("numerology", slug, num, session)
    return templates.TemplateResponse("seo/numerology.html", {
        "request": request, "num": num, "content": content, "all_nums": NUMEROLOGY_SEO,
        "h1": f"Число жизненного пути {num['number']} — {num['name']}",
        "title": f"Число жизненного пути {num['number']} — значение | Mystral",
        "description": f"Число жизненного пути {num['number']} «{num['name']}» — характер, предназначение, карьера и отношения в нумерологии.",
        "canonical": f"https://mystral.space/numerology/{slug}",
        "faq": content.get("faq", []), "cta_text": content.get("cta_text"),
        "today": TODAY(),
    })


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
async def constellation_svg(slug: str):
    c = CONSTELLATIONS.get(slug)
    if not c:
        raise HTTPException(404)
    sign = ZODIAC_BY_SLUG.get(slug, {})
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
    urls = [("https://mystral.space/", "1.0"), ("https://mystral.space/zodiac", "0.9"), ("https://mystral.space/tarot", "0.9"), ("https://mystral.space/runes", "0.9")]
    for s in ZODIAC_SIGNS:
        urls.append((f"https://mystral.space/zodiac/{s['slug']}", "0.9"))
    for c in TAROT_CARDS:
        urls.append((f"https://mystral.space/tarot/{c['slug']}", "0.8"))
    for r in RUNE_SEO:
        urls.append((f"https://mystral.space/runes/{r['slug']}", "0.8"))
    for n in NUMEROLOGY_SEO:
        urls.append((f"https://mystral.space/numerology/{n['slug']}", "0.7"))

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for loc, prio in urls:
        xml += f"<url><loc>{loc}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>{prio}</priority></url>\n"
    xml += "</urlset>"
    return Response(content=xml, media_type="application/xml")
