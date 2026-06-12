import pytest
from unittest.mock import patch
from workers.notification.tasks import handle_news_ready
from workers.notification.service import format_notification_message
from shared.models import ExtractionPayload, HeadlineItem

def get_sample_payload():
    return ExtractionPayload(
        source='yahoo_finance',
        market='NYSE',
        items=[
            HeadlineItem(title='Market is up today significantly', url='https://finance.yahoo.com/news/up'),
            HeadlineItem(title='Tech stocks rally continues', url='https://finance.yahoo.com/news/tech')
        ]
    )

def test_format_notification_message():
    payload = get_sample_payload()
    message = format_notification_message(payload)

    assert "New market updates from yahoo_finance for NYSE" in message
    assert "Market is up today significantly" in message
    assert "https://finance.yahoo.com/news/up" in message
    assert "<b>" in message  # HTML mode
    assert "<a href=" in message  # links are rendered as HTML anchors

@patch('workers.notification.tasks.send_telegram_notification')
def test_handle_news_ready_success(mock_telegram):
    payload_dict = get_sample_payload().model_dump(mode='json')
    
    handle_news_ready(payload_dict)
    
    mock_telegram.assert_called_once()

@patch('workers.notification.tasks.send_telegram_notification')
def test_handle_news_ready_empty(mock_telegram):
    payload = get_sample_payload()
    payload.items = []
    payload_dict = payload.model_dump(mode='json')
    
    handle_news_ready(payload_dict)
    
    # Should not notify if there are no items
    mock_telegram.assert_not_called()