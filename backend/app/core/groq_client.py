import json
import logging
import os
import re
from typing import AsyncIterator

logger = logging.getLogger(__name__)

_client = None
_CLEAN_RE = re.compile(r'[^\x20-\x7EÀ-ɏĞğİıŞşЀ-ӿ\n\r\t«»„“”‘’–—…°%№♈-♓☽✦★]')


def _clean_chunk(text: str) -> str:
    return _CLEAN_RE.sub('', text)


def _get_client():
    global _client
    if _client is None:
        from groq import Groq
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=30)
    return _client


async def safe_groq_stream(
    messages: list[dict],
    max_tokens: int = 400,
    lang: str = "ru",
) -> AsyncIterator[str]:
    ru = lang == "ru"
    try:
        client = _get_client()
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            stream=True,
            max_tokens=max_tokens,
        )
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                text = _clean_chunk(text)
                if text:
                    yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        ename = type(e).__name__.lower()
        if "timeout" in ename:
            msg = "AI service not responding, try later" if lang == "en" else "AI сервис не отвечает, попробуй позже"
            err = "timeout"
        elif "ratelimit" in ename:
            msg = "Too many AI requests, wait a minute" if lang == "en" else "Слишком много запросов к AI, подожди минуту"
            err = "groq_limit"
        elif "connection" in ename:
            msg = "No connection to AI service" if lang == "en" else "Нет связи с AI сервисом"
            err = "connection"
        else:
            logger.error("Groq stream error: %s %s", type(e).__name__, e)
            msg = "Something went wrong" if lang == "en" else "Что-то пошло не так"
            err = "unknown"
        yield f'data: {json.dumps({"error": err, "message": msg})}\n\n'
