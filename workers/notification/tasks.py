import os
import logging
import requests
from typing import Dict, Any, Optional

from shared.celery_app import app
from shared.models import ExtractionPayload

logger = logging.getLogger(__name__)

# Config
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def format_notification_message(payload: ExtractionPayload) -> str:
    """
    Formats the extracted payload into a human-readable message.
    """
    message = f"📢 **New market updates from {payload.source} for {payload.market}**:\n\n"
    for item in payload.items:
        message += f"🔹 {item.title}\n   {item.url}\n\n"
    return message

def send_telegram_notification(message: str) -> None:
    """
    Sends a message via Telegram API.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.debug("Telegram credentials not configured, skipping.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(url, json={
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown',
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

@app.task(
    name='workers.notification.tasks.handle_news_ready',
    bind=True,
    max_retries=5,
    default_retry_delay=60 # 1 minute base delay
)
def handle_news_ready(self, payload_dict: Dict[str, Any]) -> None:
    """
    Listens for 'news.ready' payloads and dispatches notifications.
    Implements exponential backoff for network-related failures.
    """
    try:
        payload = ExtractionPayload.model_validate(payload_dict)
    except Exception as exc:
        logger.error(f"Failed to parse extraction payload: {exc}")
        return
        
    if not payload.items:
        logger.info("Payload contains no items to notify.")
        return
        
    message = format_notification_message(payload)
    
    try:
        send_telegram_notification(message)
        # send_discord_notification(message) # Temporarily disabled to focus on Telegram
        logger.info("Successfully sent notifications.")
    except requests.RequestException as exc:
        logger.warning(f"Notification failed, applying exponential backoff: {exc}")
        # Exponential backoff: 60s, 120s, 240s, 480s, etc.
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
