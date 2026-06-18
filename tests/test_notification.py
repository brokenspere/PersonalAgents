import pytest
import json
from unittest.mock import patch, MagicMock
from workers.notification.handlers import sqs_event_handler
from workers.notification.service import (
    format_telegram_message, 
    # format_discord_message, 
    filter_for_telegram, 
    # filter_for_discord
)
from shared.models import AnalyzedPayload, AnalyzedHeadlineItem

def get_sample_payload():
    return AnalyzedPayload(
        source='yahoo_finance',
        market='NYSE',
        trending_tickers=['AAPL', 'MSFT'],
        items=[
            AnalyzedHeadlineItem(
                title='Market is up today significantly', 
                url='https://finance.yahoo.com/news/up',
                extracted_tickers=['SPY'],
                analysis='Market looks good'
            ),
            AnalyzedHeadlineItem(
                title='Tech stocks rally continues', 
                url='https://finance.yahoo.com/news/tech',
                extracted_tickers=['AAPL', 'MSFT'],
                analysis=None
            ),
            AnalyzedHeadlineItem(
                title='Company goes bankrupt', 
                url='https://finance.yahoo.com/news/bad',
                extracted_tickers=[],
                analysis=None
            )
        ]
    )

def test_filter_for_telegram():
    payload = get_sample_payload()
    filtered = filter_for_telegram(payload.items)
    assert len(filtered) == 1
    assert filtered[0].title == 'Market is up today significantly'

# def test_filter_for_discord():
#     payload = get_sample_payload()
#     filtered = filter_for_discord(payload.items)
#     assert len(filtered) == 2
#     assert filtered[0].title == 'Market is up today significantly'
#     assert filtered[1].title == 'Tech stocks rally continues'

def test_format_telegram_message():
    payload = get_sample_payload()
    filtered = filter_for_telegram(payload.items)
    messages = format_telegram_message(payload, filtered)

    assert len(messages) > 0
    message = messages[0]
    
    assert "Impactful updates from yahoo_finance for NYSE" in message
    assert "Trending Tickers:</b> AAPL, MSFT" in message
    assert "Market is up today significantly" in message
    assert "Company goes bankrupt" not in message
    assert "Tech stocks rally continues" not in message
    assert "<b>" in message  # HTML mode

# def test_format_discord_message():
#     payload = get_sample_payload()
#     filtered = filter_for_discord(payload.items)
#     message = format_discord_message(payload, filtered)
# 
#     assert "**Ticker updates from yahoo_finance for NYSE**" in message
#     assert "**Trending Tickers:** AAPL, MSFT" in message
#     assert "Market is up today significantly" in message
#     assert "Tech stocks rally continues" in message
#     assert "Company goes bankrupt" not in message
#     assert "[Market is up today significantly]" in message  # Markdown link

# @patch('workers.notification.handlers.send_discord_notification_aws')
@patch('workers.notification.handlers.send_telegram_notification_aws')
def test_sqs_event_handler_success(mock_telegram):
    payload_dict = get_sample_payload().model_dump(mode='json')
    event = {
        'Records': [
            {'body': json.dumps(payload_dict)}
        ]
    }
    
    sqs_event_handler(event, None)
    
    # We have 1 message chunk because the payload is small
    assert mock_telegram.call_count == 1
    # mock_discord.assert_called_once()

# @patch('workers.notification.handlers.send_discord_notification_aws')
@patch('workers.notification.handlers.send_telegram_notification_aws')
def test_sqs_event_handler_empty(mock_telegram):
    payload = get_sample_payload()
    payload.items = []
    payload.trending_tickers = []
    payload_dict = payload.model_dump(mode='json')
    
    event = {
        'Records': [
            {'body': json.dumps(payload_dict)}
        ]
    }
    
    sqs_event_handler(event, None)
    
    # Should not notify if there are no items and no trending tickers
    mock_telegram.assert_not_called()
    # mock_discord.assert_not_called()