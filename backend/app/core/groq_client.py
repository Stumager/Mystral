import json
import logging
import os
import re
from typing import AsyncIterator

logger = logging.getLogger(__name__)

_client = None
_async_client = None
_CLEAN_RE = re.compile(r'[^\x20-\x7EÀ-ɏĞğİıŞşЀ-ӿ\n\r\t«»„“”‘’–—…°%№♈-♓☽✦★]')


def _clean_chunk(text: str) -> str:
    return _CLEAN_RE.sub('', text)


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


async def safe_groq_stream(
    messages: list[dict],
    max_tokens: int = 400,
    lang: str = "ru",
) -> AsyncIterator[str]:
    try:
        client = _get_async_client()
        stream = await client.chat.completions.create(
            model="deepseek/deepseek-v4-flash",
            messages=messages,
            stream=True,
            max_tokens=max_tokens,
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
