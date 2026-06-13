import logging
import random
from typing import List

import requests
from bs4 import BeautifulSoup

from shared.models import HeadlineItem
from shared.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

YAHOO_FINANCE_URL = "https://finance.yahoo.com/"

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
]

def get_random_headers() -> dict:
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
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

        if title and len(title) > 20 and ('news' in href or 'video' in href or '/m/' in href):
            if href.startswith('/'):
                href = f"https://finance.yahoo.com{href}"

            items.append(HeadlineItem(title=title, url=href))
            if len(items) >= max_items:
                break

    return items

def extract_trending_tickers(html_content: str, max_items: int = 5) -> List[str]:
    """
    Extracts trending tickers from Yahoo Finance.
    Looks for elements often used for tickers or symbols.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    tickers = []
    
    # We look for a elements which have href containing 'quote'
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if '/quote/' in href:
            symbol = href.split('/quote/')[1].split('?')[0].split('/')[0]
            if symbol and symbol.isalnum() and symbol not in tickers:
                tickers.append(symbol)
            if len(tickers) >= max_items:
                break
                
    return tickers

@CircuitBreaker(failure_threshold=3, recovery_timeout=60)
def fetch_yahoo_finance_html() -> str:
    """
    Fetches the raw HTML from Yahoo Finance.
    """
    response = requests.get(YAHOO_FINANCE_URL, headers=get_random_headers(), timeout=10)
    response.raise_for_status()
    return response.text