import json
import logging
import os
import re
from typing import AsyncIterator

logger = logging.getLogger(__name__)

_client = None
_async_client = None
_CLEAN_RE = re.compile(
    r'[^\x20-\x7E'      # Basic Latin: letters, digits, standard punctuation/symbols
    r'¡-ɏ'    # Latin-1 Supplement + Extended: ES/PT accents, Turkish ĞğİıŞş, Spanish ¡¿
    r'Ѐ-ӿ'    # Cyrillic: RU/UK incl. ЄєІіЇїҐґ
    r'\n\r\t'
    r'«»„""''–—…°№'
    r'♈-♓☽✦★]'
)


_LATIN_TO_CYR = {
    'C': 'С', 'A': 'А', 'E': 'Е', 'O': 'О', 'P': 'Р', 'T': 'Т',
    'B': 'В', 'M': 'М', 'H': 'Н', 'X': 'Х', 'K': 'К',
}
_CYR_CLASS = 'а-яА-ЯёЁЄєІіЇїҐґ'
_STRAY_LATIN_RE = re.compile(
    rf'(?<=[{_CYR_CLASS}])([{"".join(_LATIN_TO_CYR)}])(?=[{_CYR_CLASS}])'
)


def _fix_stray_latin(text: str) -> str:
    # A stray uppercase Latin letter (visually identical to its Cyrillic
    # counterpart) sandwiched between Cyrillic letters, e.g. "Constructivного".
    return _STRAY_LATIN_RE.sub(lambda m: _LATIN_TO_CYR[m.group(1)], text)


def _clean_chunk(text: str) -> str:
    text = _CLEAN_RE.sub('', text)
    return _fix_stray_latin(text)


_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
_OPENROUTER_HEADERS = {"HTTP-Referer": "https://mystral.space", "X-Title": "Mystral"}


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(
            base_url=_OPENROUTER_BASE_URL,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            timeout=30,
            default_headers=_OPENROUTER_HEADERS,
        )
    return _client


def _get_async_client():
    global _async_client
    if _async_client is None:
        from openai import AsyncOpenAI
        _async_client = AsyncOpenAI(
            base_url=_OPENROUTER_BASE_URL,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            timeout=30,
            default_headers=_OPENROUTER_HEADERS,
        )
    return _async_client


_QUALITY_DIRECTIVE = {
    "ru": (
        " Ты — профессиональный астролог и эзотерик. Твой стиль общения: строгий, экспертный, "
        "уважительный. Обращайся к пользователю на «вы». Никакого неформального тона, никаких слов "
        "«слушай», «давай», «кстати». Пиши как специалист пишет клиенту — авторитетно и по делу. "
        "Формат ответа: без вводных фраз («Хороший вопрос», «Давайте разберём»); без воды и общих "
        "фраз («это может означать», «возможно», «в целом»); каждое предложение несёт конкретную "
        "информацию; короткие абзацы по 2-4 предложения, каждый — одна мысль; конкретные планеты, "
        "градусы, аспекты, если есть данные; в конце — одна чёткая практическая рекомендация. "
        "Объём: 150-250 слов. Не больше. "
        "Никогда не вставляй символы чужих алфавитов — только целевой язык. "
        "Пиши обычным текстом без markdown-разметки: никаких **, *, #, ` и списков через дефис в начале строки."
    ),
    "en": (
        " You are a professional astrologer and esotericist. Your communication style is strict, "
        "expert, and respectful. Never use casual filler words like 'look', 'so', 'by the way', "
        "'let's see'. Write the way a specialist writes to a client — authoritative and to the point. "
        "Response format: no filler openers ('Great question', 'Let's break this down'); no vague "
        "general phrases ('this might mean', 'perhaps', 'in general'); every sentence carries concrete "
        "information; short paragraphs of 2-4 sentences, each a single idea; name specific planets, "
        "degrees, aspects when data is available; end with one clear, practical recommendation. "
        "Length: 150-250 words. No more. "
        "Never insert characters from other alphabets — only the target language. "
        "Write in plain text, no markdown formatting: no **, *, #, backticks, or hyphen bullet lists."
    ),
    "es": (
        " Eres un astrólogo y esoterista profesional. Tu estilo de comunicación: riguroso, experto, "
        "respetuoso. Dirígete al usuario de 'usted'. Nada de tono informal, nada de palabras como "
        "'oye', 'vamos', 'por cierto'. Escribe como un especialista le escribe a un cliente — con "
        "autoridad y al grano. Formato de respuesta: sin frases introductorias vacías ('Buena "
        "pregunta', 'Vamos a analizar'); sin relleno ni frases genéricas ('esto podría significar', "
        "'quizás', 'en general'); cada frase aporta información concreta; párrafos cortos de 2 a 4 "
        "frases, cada uno una sola idea; menciona planetas, grados y aspectos concretos si hay datos; "
        "al final, una recomendación práctica clara. Extensión: 150-250 palabras. No más. "
        "Nunca insertes caracteres de otros alfabetos — solo el idioma de destino. "
        "Escribe en texto plano, sin formato markdown: nada de **, *, #, comillas invertidas ni listas con guiones."
    ),
    "pt": (
        " Você é um astrólogo e esoterista profissional. Seu estilo de comunicação: rigoroso, "
        "especialista, respeitoso. Dirija-se ao usuário de forma formal. Nada de tom informal, nada "
        "de palavras como 'olha', 'vamos lá', 'aliás'. Escreva como um especialista escreve para um "
        "cliente — com autoridade e direto ao ponto. Formato da resposta: sem frases introdutórias "
        "vazias ('Boa pergunta', 'Vamos analisar'); sem enrolação nem frases genéricas ('isso pode "
        "significar', 'talvez', 'em geral'); cada frase carrega informação concreta; parágrafos curtos "
        "de 2 a 4 frases, cada um uma única ideia; cite planetas, graus e aspectos concretos quando "
        "houver dados; no final, uma recomendação prática clara. Extensão: 150-250 palavras. Não mais. "
        "Nunca insira caracteres de outros alfabetos — apenas o idioma de destino. "
        "Escreva em texto simples, sem formatação markdown: nada de **, *, #, crases ou listas com hífen."
    ),
    "tr": (
        " Sen profesyonel bir astrolog ve ezoterikçisin. İletişim tarzın: sıkı, uzman, saygılı. "
        "Kullanıcıya resmi 'siz' hitabıyla konuş. Samimi ton yok, 'bak', 'hadi', 'bu arada' gibi "
        "kelimeler yok. Bir uzmanın müşterisine yazdığı gibi yaz — otoriter ve konuya odaklı. Yanıt "
        "formatı: boş giriş cümleleri yok ('Güzel soru', 'Hadi inceleyelim'); dolgu ve genel ifadeler "
        "yok ('bu şu anlama gelebilir', 'belki', 'genel olarak'); her cümle somut bilgi taşır; 2-4 "
        "cümlelik kısa paragraflar, her biri tek bir fikir; veriler varsa somut gezegenleri, dereceleri, "
        "açıları belirt; sonunda net, pratik bir tavsiye. Uzunluk: 150-250 kelime. Daha fazla değil. "
        "Asla başka alfabelerin karakterlerini ekleme — yalnızca hedef dil. "
        "Düz metin yaz, markdown biçimlendirmesi kullanma: **, *, #, ters tırnak veya tire ile "
        "başlayan liste yok."
    ),
    "uk": (
        " Ти — професійний астролог та езотерик. Твій стиль спілкування: строгий, експертний, "
        "шанобливий. Звертайся до користувача на «ви». Жодного неформального тону, жодних слів "
        "«слухай», «давай», «до речі». Пиши як фахівець пише клієнту — авторитетно і по суті. Формат "
        "відповіді: без вступних фраз («Гарне запитання», «Давайте розберемо»); без води й загальних "
        "фраз («це може означати», «можливо», «загалом»); кожне речення несе конкретну інформацію; "
        "короткі абзаци по 2-4 речення, кожен — одна думка; конкретні планети, градуси, аспекти, якщо "
        "є дані; наприкінці — одна чітка практична рекомендація. Обсяг: 150-250 слів. Не більше. "
        "Ніколи не вставляй символи чужих алфавітів — лише цільова мова. "
        "Пиши звичайним текстом без markdown-розмітки: жодних **, *, #, ` і списків через дефіс "
        "на початку рядка."
    ),
}


def _quality_directive(lang: str) -> str:
    return _QUALITY_DIRECTIVE.get(lang, _QUALITY_DIRECTIVE["en"])


async def safe_groq_stream(
    messages: list[dict],
    max_tokens: int = 2048,
    lang: str = "ru",
) -> AsyncIterator[str]:
    # Append the universal quality directive to the caller's system message so
    # every router benefits without duplicating it in each prompt.
    if messages and messages[0].get("role") == "system":
        messages = [
            {"role": "system", "content": messages[0]["content"] + _quality_directive(lang)},
            *messages[1:],
        ]
    try:
        client = _get_async_client()
        stream = await client.chat.completions.create(
            model="deepseek/deepseek-v4-flash",
            messages=messages,
            stream=True,
            max_tokens=max_tokens,
            temperature=0.75,
            top_p=0.95,
        )
        async for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                text = _clean_chunk(text)
                if text:
                    yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        ename = type(e).__name__.lower()
        if "timeout" in ename:
            msg = _err_msg(lang, "timeout")
            err = "timeout"
        elif "ratelimit" in ename:
            msg = _err_msg(lang, "ratelimit")
            err = "groq_limit"
        elif "connection" in ename:
            msg = _err_msg(lang, "connection")
            err = "connection"
        else:
            logger.error("Groq stream error: %s %s", type(e).__name__, e)
            msg = _err_msg(lang, "unknown")
            err = "unknown"
        yield f'data: {json.dumps({"error": err, "message": msg})}\n\n'


_ERROR_MESSAGES = {
    "timeout": {
        "ru": "AI сервис не отвечает, попробуй позже",
        "en": "AI service not responding, try later",
        "es": "El servicio de IA no responde, inténtalo más tarde",
        "pt": "Serviço de IA não responde, tente mais tarde",
        "tr": "AI servisi yanıt vermiyor, daha sonra dene",
        "uk": "AI сервіс не відповідає, спробуй пізніше",
    },
    "ratelimit": {
        "ru": "Слишком много запросов к AI, подожди минуту",
        "en": "Too many AI requests, wait a minute",
        "es": "Demasiadas solicitudes de IA, espera un momento",
        "pt": "Muitas solicitações de IA, aguarde um momento",
        "tr": "Çok fazla AI isteği, bir dakika bekle",
        "uk": "Забагато запитів до AI, зачекай хвилинку",
    },
    "connection": {
        "ru": "Нет связи с AI сервисом",
        "en": "No connection to AI service",
        "es": "Sin conexión con el servicio de IA",
        "pt": "Sem conexão com o serviço de IA",
        "tr": "AI servisine bağlantı yok",
        "uk": "Немає зв'язку з AI сервісом",
    },
    "unknown": {
        "ru": "Что-то пошло не так",
        "en": "Something went wrong",
        "es": "Algo salió mal",
        "pt": "Algo deu errado",
        "tr": "Bir şeyler ters gitti",
        "uk": "Щось пішло не так",
    },
}


def _err_msg(lang: str, key: str) -> str:
    return _ERROR_MESSAGES.get(key, {}).get(lang, _ERROR_MESSAGES[key]["en"])
