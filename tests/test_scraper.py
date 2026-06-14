import pytest
from unittest.mock import patch, MagicMock
from workers.scraper.tasks import handle_market_event
from workers.scraper.service import extract_headlines_from_html, fetch_yahoo_finance_html, YAHOO_FINANCE_URL
from shared.models import Event

SAMPLE_HTML = """
<html>
  <body>
    <a href="/news/test-news-article-123.html">This is a valid news headline that is long enough</a>
    <a href="/video/test-video.html">Watch this video about market trends right now</a>
    <a href="/short">Short</a>
    <a href="https://example.com/not-article">Not a news link with long enough text to pass length</a>
  </body>
</html>
"""

def test_extract_headlines_from_html():
    items = extract_headlines_from_html(SAMPLE_HTML)
    
    # Expecting 2 items due to filtering logic
    assert len(items) == 2
    assert items[0].title == "This is a valid news headline that is long enough"
    # Ensure it uses the correct base domain for relative links
    assert items[0].url == "https://finance.yahoo.com/news/test-news-article-123.html"
    assert items[1].title == "Watch this video about market trends right now"
    assert items[1].url == "https://finance.yahoo.com/video/test-video.html"

@patch('requests.get')
def test_fetch_yahoo_finance_html(mock_get):
    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    html = fetch_yahoo_finance_html()
    
    assert html == "<html></html>"
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == YAHOO_FINANCE_URL
    assert 'User-Agent' in kwargs['headers']

@patch('workers.scraper.tasks.fetch_yahoo_finance_html')
@patch('workers.scraper.tasks.app.send_task')
def test_handle_market_event_success(mock_send_task, mock_fetch):
    mock_fetch.return_value = SAMPLE_HTML
    
    event_dict = Event(event_type='market.open', market='NYSE').model_dump(mode='json')
    
    handle_market_event(event_dict)
    
    mock_send_task.assert_called_once()
    args, kwargs = mock_send_task.call_args
    assert args[0] == 'workers.notification.tasks.handle_news_ready'
    
    payload = kwargs['args'][0]
    assert payload['source'] == 'yahoo_finance'
    assert payload['market'] == 'NYSE'
    assert len(payload['items']) == 2

@patch('workers.scraper.tasks.fetch_yahoo_finance_html')
@patch('workers.scraper.tasks.app.send_task')
def test_handle_market_event_wrong_market(mock_send_task, mock_fetch):
    event_dict = Event(event_type='market.open', market='NASDAQ').model_dump(mode='json')
    handle_market_event(event_dict)
    
    # Should not process non-NYSE events
    mock_fetch.assert_not_called()
    mock_send_task.assert_not_called()