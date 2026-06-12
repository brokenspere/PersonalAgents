import logging
import requests
from typing import Dict, Any

from shared.celery_app import app
from shared.models import ExtractionPayload
from workers.notification.service import (
    format_notification_message,
    send_telegram_notification,
    send_discord_notification,
)

logger = logging.getLogger(__name__)

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
        logger.exception("Failed to parse extraction payload: %s", exc)
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
