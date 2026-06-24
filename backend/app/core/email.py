import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_verification_email(to_email: str, code: str) -> bool:
    if not settings.smtp_host or not settings.smtp_user:
        logger.warning("SMTP not configured, skipping email to %s", to_email)
        return False

    html = f"""
    <div style="background:#07060F;padding:40px 20px;text-align:center;font-family:Arial,sans-serif">
      <div style="max-width:400px;margin:0 auto">
        <div style="font-size:22px;letter-spacing:.3em;color:#E8CD7E;margin-bottom:30px">MYSTRAL</div>
        <div style="font-size:16px;color:#F0E9DA;margin-bottom:20px">Ваш код подтверждения:</div>
        <div style="font-size:36px;letter-spacing:.3em;color:#C9A84C;font-weight:700;
                    background:#0D0B1F;border:1px solid rgba(201,168,76,.3);border-radius:14px;
                    padding:20px;margin:0 auto 20px;max-width:280px">{code}</div>
        <div style="font-size:13px;color:#8A8170;margin-bottom:10px">Код действителен 15 минут</div>
        <div style="font-size:12px;color:#6E6757">Если вы не регистрировались — проигнорируйте это письмо</div>
      </div>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Ваш код подтверждения Mystral"
    msg["From"] = settings.smtp_from or settings.smtp_user
    msg["To"] = to_email
    msg.attach(MIMEText(f"Ваш код подтверждения Mystral: {code}", "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, context=ctx) as server:
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(msg["From"], to_email, msg.as_string())
        logger.info("Verification email sent to %s", to_email)
        return True
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to_email, e)
        return False
