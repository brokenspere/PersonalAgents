import logging
from typing import List

import requests
from bs4 import BeautifulSoup

from shared.models import HeadlineItem

logger = logging.getLogger(__name__)

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