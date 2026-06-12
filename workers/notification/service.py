import html
import logging
import os
import requests

from shared.models import ExtractionPayload

logger = logging.getLogger(__name__)

# Config (used by Celery worker path)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')


def format_notification_message(payload: ExtractionPayload) -> str:
    """
    Formats the extracted payload into an HTML message for Telegram.
    Dynamic content is escaped to prevent Telegram parse errors.
    """
    source = html.escape(payload.source)
    market = html.escape(payload.market)
    message = f"📢 <b>New market updates from {source} for {market}</b>:\n\n"
    for item in payload.items:
        title = html.escape(item.title)
        url = html.escape(str(item.url))
        message += f"🔹 <a href=\"{url}\">{title}</a>\n\n"
    return message


def send_telegram_notification(message: str) -> None:
    """
    Sends a message via Telegram API using env-var credentials (Celery worker path).
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.debug("Telegram credentials not configured, skipping.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(url, json={
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }, timeout=10)
    response.raise_for_status()


def send_discord_notification(message: str) -> None:
    """
    Sends a message via Discord Webhook.
    """
    if not DISCORD_WEBHOOK_URL:
        logger.debug("Discord webhook not configured, skipping.")
        return

    response = requests.post(DISCORD_WEBHOOK_URL, json={
        'content': message
    }, timeout=10)
    response.raise_for_status()
