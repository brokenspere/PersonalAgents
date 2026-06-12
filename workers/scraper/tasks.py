import logging
import requests
from typing import Dict, Any

from shared.celery_app import app
from shared.models import Event, ExtractionPayload
from workers.scraper.service import extract_headlines_from_html, fetch_yahoo_finance_html

logger = logging.getLogger(__name__)

@app.task(name='workers.scraper.tasks.handle_market_event', bind=True, max_retries=3)
def handle_market_event(self, event_dict: Dict[str, Any]) -> None:
    """
    Listens for market events and triggers the scraping workflow.
    Emits raw scraped data to the notification worker.
    """
    try:
        event = Event.model_validate(event_dict)
    except Exception as exc:
        logger.exception("Failed to parse event: %s", exc)
        return

    # We only scrape for NYSE market events
    if event.market != 'NYSE':
        logger.info(f"Ignoring event for market: {event.market}")
        return
        
    try:
        html_content = fetch_yahoo_finance_html()
        headlines = extract_headlines_from_html(html_content)
        
        payload = ExtractionPayload(
            source='yahoo_finance',
            market=event.market,
            items=headlines
        )
        
        # Route to NotificationWorker
        app.send_task(
            'workers.notification.tasks.handle_news_ready',
            args=[payload.model_dump(mode='json')],
            queue='notification'
        )
        
    except requests.RequestException as exc:
        logger.warning(f"Network error while scraping: {exc}. Retrying...")
        raise self.retry(exc=exc, countdown=60)
    except Exception as exc:
        logger.exception("Unexpected error during scraping: %s", exc)
        raise
