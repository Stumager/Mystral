import json
import logging
import os
from typing import AsyncIterator

from groq import Groq

logger = logging.getLogger(__name__)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=30)


async def safe_groq_stream(
    messages: list[dict],
    max_tokens: int = 400,
    lang: str = "ru",
) -> AsyncIterator[str]:
    ru = lang == "ru"
    try:
        stream = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            stream=True,
            max_tokens=max_tokens,
        )
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        ename = type(e).__name__.lower()
        if "timeout" in ename:
            msg = "AI сервис не отвечает, попробуй позже" if ru else "AI service not responding, try later"
            err = "timeout"
        elif "ratelimit" in ename:
            msg = "Слишком много запросов к AI, подожди минуту" if ru else "Too many AI requests, wait a minute"
            err = "groq_limit"
        elif "connection" in ename:
            msg = "Нет связи с AI сервисом" if ru else "No connection to AI service"
            err = "connection"
        else:
            logger.error("Groq stream error: %s %s", type(e).__name__, e)
            msg = "Что-то пошло не так" if ru else "Something went wrong"
            err = "unknown"
        yield f'data: {json.dumps({"error": err, "message": msg})}\n\n'
