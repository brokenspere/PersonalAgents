import html
import logging
import os
import requests
from typing import List

from shared.models import EnrichedPayload, EnrichedHeadlineItem

logger = logging.getLogger(__name__)

# Config (used by Celery worker path)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def filter_for_telegram(items: List[EnrichedHeadlineItem]) -> List[EnrichedHeadlineItem]:
    """
    Telegram only receives highly impactful news (sentiment > 0.5 or < -0.5).
    """
    return [item for item in items if abs(item.sentiment_score) > 0.5]

def filter_for_discord(items: List[EnrichedHeadlineItem]) -> List[EnrichedHeadlineItem]:
    """
    Discord receives all news that have identified tickers.
    """
    return [item for item in items if item.extracted_tickers]

def format_telegram_message(payload: EnrichedPayload, items: List[EnrichedHeadlineItem]) -> str:
    source = html.escape(payload.source)
    market = html.escape(payload.market) if payload.market else "Unknown"
    message = f"📢 <b>Impactful updates from {source} for {market}</b>:\n\n"
    if payload.trending_tickers:
        message += f"🔥 <b>Trending Tickers:</b> {', '.join(payload.trending_tickers)}\n\n"
        
    for item in items:
        title = html.escape(item.title)
        url = html.escape(str(item.url))
        tickers = f" [Tags: {', '.join(item.extracted_tickers)}]" if item.extracted_tickers else ""
        message += f"🔹 <a href=\"{url}\">{title}</a>{tickers} (Sentiment: {item.sentiment_score:.2f})\n\n"
    return message

# def format_discord_message(payload: EnrichedPayload, items: List[EnrichedHeadlineItem]) -> str:
#     source = payload.source
#     market = payload.market if payload.market else "Unknown"
#     message = f"📢 **Ticker updates from {source} for {market}**:\n\n"
#     if payload.trending_tickers:
#         message += f"🔥 **Trending Tickers:** {', '.join(payload.trending_tickers)}\n\n"
#         
#     for item in items:
#         title = item.title
#         url = str(item.url)
#         tickers = f" [Tags: {', '.join(item.extracted_tickers)}]" if item.extracted_tickers else ""
#         message += f"🔹 [{title}]({url}){tickers} (Sentiment: {item.sentiment_score:.2f})\n"
#     return message

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
