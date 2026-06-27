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
        "h1": f"Знак зодиака {sign['name']}",
        "title": f"{sign['name']} — характеристика, гороскоп и совместимость | Mystral",
        "description": f"{sign['name']} — знак {sign['element']} ({sign['dates']}). Характер, совместимость, карьера и любовь. Персональный гороскоп на Mystral.",
        "canonical": f"https://mystral.space/zodiac/{slug}",
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
