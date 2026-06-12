import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

from shared.celery_app import app
from shared.models import Event, ExtractionPayload, HeadlineItem

logger = logging.getLogger(__name__)

# Constants
YAHOO_FINANCE_URL = "https://finance.yahoo.com/"
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def extract_headlines_from_html(html_content: str, max_items: int = 5) -> List[HeadlineItem]:
    """
    Parses HTML content to extract news headlines.
    Separated from network IO for testability and clarity.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    items = []
    
    for a_tag in soup.find_all('a', href=True):
        title = a_tag.get_text(strip=True)
        href = a_tag['href']
        
        # Heuristic filtering for news articles
        if title and len(title) > 20 and ('news' in href or 'video' in href or '/m/' in href):
            if href.startswith('/'):
                href = f"https://finance.yahoo.com{href}"
                
            items.append(HeadlineItem(title=title, url=href))
            if len(items) >= max_items:
                break
                
    return items

def fetch_yahoo_finance_html() -> str:
    """
    Fetches the raw HTML from Yahoo Finance.
    """
    response = requests.get(YAHOO_FINANCE_URL, headers=DEFAULT_HEADERS, timeout=10)
    response.raise_for_status()
    return response.text

@app.task(name='workers.scraper.tasks.handle_market_event', bind=True, max_retries=3)
def handle_market_event(self, event_dict: Dict[str, Any]) -> None:
    """
    Listens for market events and triggers the scraping workflow.
    Emits raw scraped data to the notification worker.
    """
    try:
        event = Event.model_validate(event_dict)
    except Exception as exc:
        logger.error(f"Failed to parse event: {exc}")
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
            args=[payload.model_dump(mode='json')]
        )
        
    except requests.RequestException as exc:
        logger.warning(f"Network error while scraping: {exc}. Retrying...")
        raise self.retry(exc=exc, countdown=60)
    except Exception as exc:
        logger.error(f"Unexpected error during scraping: {exc}")
        raise
