import json
import logging

from pywebpush import WebPushException, webpush

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_push_sync(subscription: dict, title: str, body: str, url: str = "/") -> str | None:
    if not settings.vapid_private_key:
        logger.warning("VAPID keys not configured")
        return None
    try:
        webpush(
            subscription_info=subscription,
            data=json.dumps({"title": title, "body": body, "url": url, "icon": "/icons/icon-192.png"}),
            vapid_private_key=settings.vapid_private_key,
            vapid_claims={"sub": settings.vapid_claims_email},
        )
        return "ok"
    except WebPushException as e:
        if e.response and e.response.status_code == 410:
            return "expired"
        logger.error("Push error: %s", e)
        return "error"
    except Exception as e:
        logger.error("Push send failed: %s", e)
        return "error"
