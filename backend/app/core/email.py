import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

RESEND_URL = "https://api.resend.com/emails"


async def send_verification_email(to_email: str, code: str) -> bool:
    if not settings.resend_api_key:
        logger.warning("RESEND_API_KEY not set, skipping email to %s", to_email)
        return False

    html = (
        '<div style="background:#07060F;padding:40px 20px;font-family:Georgia,serif;max-width:480px;margin:0 auto">'
        '<div style="text-align:center;margin-bottom:32px">'
        '<div style="font-family:serif;font-size:13px;letter-spacing:.4em;color:#C9A84C">MYSTRAL</div>'
        '</div>'
        '<div style="text-align:center">'
        '<p style="color:#A89E8B;font-size:15px;margin:0 0 24px">Ваш код подтверждения:</p>'
        '<div style="background:rgba(201,168,76,.1);border:1px solid rgba(201,168,76,.3);'
        'border-radius:16px;padding:28px;display:inline-block">'
        f'<span style="font-size:42px;letter-spacing:.3em;color:#C9A84C;font-weight:600">{code}</span>'
        '</div>'
        '<p style="color:#6E6757;font-size:13px;margin:20px 0 0">Код действителен 15 минут</p>'
        '<p style="color:#6E6757;font-size:12px;margin:8px 0 0">'
        'Если вы не регистрировались — проигнорируйте это письмо</p>'
        '</div></div>'
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                RESEND_URL,
                headers={
                    "Authorization": f"Bearer {settings.resend_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": f"Mystral <{settings.smtp_from}>",
                    "to": [to_email],
                    "subject": "Ваш код подтверждения Mystral",
                    "html": html,
                },
            )
        if resp.status_code in (200, 201):
            logger.info("Verification email sent to %s via Resend", to_email)
            return True
        else:
            logger.error("Resend API error %s: %s", resp.status_code, resp.text[:300])
            return False
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to_email, e)
        return False


async def send_reset_email(to_email: str, token: str) -> bool:
    if not settings.resend_api_key:
        logger.warning("RESEND_API_KEY not set, skipping reset email to %s", to_email)
        return False

    link = f"https://mystral.space/reset-password?token={token}"
    html = (
        '<div style="background:#07060F;padding:40px 20px;font-family:Georgia,serif;max-width:480px;margin:0 auto">'
        '<div style="text-align:center;margin-bottom:32px">'
        '<div style="font-family:serif;font-size:13px;letter-spacing:.4em;color:#C9A84C">MYSTRAL</div>'
        '</div>'
        '<div style="text-align:center">'
        '<p style="color:#A89E8B;font-size:15px;margin:0 0 24px">Сброс пароля</p>'
        '<p style="color:#F0E9DA;font-size:14px;margin:0 0 28px">Нажмите кнопку ниже чтобы установить новый пароль:</p>'
        f'<a href="{link}" style="display:inline-block;background:linear-gradient(100deg,#A9882F,#C9A84C,#E8CD7E);'
        'color:#1A1206;font-weight:600;font-size:15px;padding:14px 32px;border-radius:14px;text-decoration:none">'
        'Сбросить пароль</a>'
        '<p style="color:#6E6757;font-size:13px;margin:24px 0 0">Ссылка действительна 1 час</p>'
        '<p style="color:#6E6757;font-size:12px;margin:8px 0 0">'
        'Если вы не запрашивали сброс — проигнорируйте это письмо</p>'
        '</div></div>'
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                RESEND_URL,
                headers={"Authorization": f"Bearer {settings.resend_api_key}", "Content-Type": "application/json"},
                json={"from": f"Mystral <{settings.smtp_from}>", "to": [to_email], "subject": "Сброс пароля Mystral", "html": html},
            )
        if resp.status_code in (200, 201):
            logger.info("Reset email sent to %s", to_email)
            return True
        else:
            logger.error("Resend reset error %s: %s", resp.status_code, resp.text[:300])
            return False
    except Exception as e:
        logger.error("Failed to send reset email to %s: %s", to_email, e)
        return False
