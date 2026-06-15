import html
import logging
import os
import requests
from typing import List

from shared.models import AnalyzedPayload, AnalyzedHeadlineItem

logger = logging.getLogger(__name__)

# Config (used by Celery worker path)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def filter_for_telegram(items: List[AnalyzedHeadlineItem]) -> List[AnalyzedHeadlineItem]:
    """
    Telegram only receives highly impactful news (sentiment > 0.5 or < -0.5) or news with analysis.
    """
    return [item for item in items if abs(item.sentiment_score) > 0.5 or item.analysis]

def filter_for_discord(items: List[AnalyzedHeadlineItem]) -> List[AnalyzedHeadlineItem]:
    """
    Discord receives all news that have identified tickers.
    """
    return [item for item in items if item.extracted_tickers]

def format_telegram_message(payload: AnalyzedPayload, items: List[AnalyzedHeadlineItem]) -> List[str]:
    source = html.escape(payload.source)
    market = html.escape(payload.market) if payload.market else "Unknown"
    
    messages = []
    header = f"📢 <b>Impactful updates from {source} for {market}</b>:\n\n"
    if payload.trending_tickers:
        escaped_trending = [html.escape(t) for t in payload.trending_tickers]
        header += f"🔥 <b>Trending Tickers:</b> {', '.join(escaped_trending)}\n\n"
        
    current_message = header
    
    for item in items:
        title = html.escape(item.title)
        url = html.escape(str(item.url))
        if item.extracted_tickers:
            escaped_tickers = [html.escape(t) for t in item.extracted_tickers]
            tickers = f" [Tags: {', '.join(escaped_tickers)}]"
        else:
            tickers = ""
        
        item_text = f"🔹 <a href=\"{url}\">{title}</a>{tickers} (Sentiment: {item.sentiment_score:.2f})\n"
        if item.analysis:
            analysis_text = html.escape(item.analysis)
            if len(analysis_text) > 2000:
                analysis_text = analysis_text[:1997] + "..."
            item_text += f"💡 <i>Analysis:</i> {analysis_text}\n"
        item_text += "\n"
        
        # Telegram max length is 4096. 4000 is a safe threshold.
        if len(current_message) + len(item_text) > 4000:
            if current_message.strip():
                messages.append(current_message)
            # Continuation header
            current_message = f"📢 <b>Updates from {source} for {market} (cont.)</b>:\n\n" + item_text
        else:
            current_message += item_text
            
    if current_message.strip():
        messages.append(current_message)
        
    return messages

# def format_discord_message(payload: AnalyzedPayload, items: List[AnalyzedHeadlineItem]) -> str:
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
#         if item.analysis:
#             message += f"💡 *Analysis:* {item.analysis}\n"
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
