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
from shared.models import EnrichedPayload, EnrichedHeadlineItem

def get_sample_payload():
    return EnrichedPayload(
        source='yahoo_finance',
        market='NYSE',
        trending_tickers=['AAPL', 'MSFT'],
        items=[
            EnrichedHeadlineItem(
                title='Market is up today significantly', 
                url='https://finance.yahoo.com/news/up',
                extracted_tickers=['SPY'],
                sentiment_score=0.8
            ),
            EnrichedHeadlineItem(
                title='Tech stocks rally continues', 
                url='https://finance.yahoo.com/news/tech',
                extracted_tickers=['AAPL', 'MSFT'],
                sentiment_score=0.1 # Not impactful
            ),
            EnrichedHeadlineItem(
                title='Company goes bankrupt', 
                url='https://finance.yahoo.com/news/bad',
                extracted_tickers=[],
                sentiment_score=-0.9 # Impactful
            )
        ]
    )

def test_filter_for_telegram():
    payload = get_sample_payload()
    filtered = filter_for_telegram(payload.items)
    assert len(filtered) == 2
    assert filtered[0].title == 'Market is up today significantly'
    assert filtered[1].title == 'Company goes bankrupt'

# def test_filter_for_discord():
#     payload = get_sample_payload()
#     filtered = filter_for_discord(payload.items)
#     assert len(filtered) == 2
#     assert filtered[0].title == 'Market is up today significantly'
#     assert filtered[1].title == 'Tech stocks rally continues'

def test_format_telegram_message():
    payload = get_sample_payload()
    filtered = filter_for_telegram(payload.items)
    message = format_telegram_message(payload, filtered)

    assert "Impactful updates from yahoo_finance for NYSE" in message
    assert "Trending Tickers:</b> AAPL, MSFT" in message
    assert "Market is up today significantly" in message
    assert "Company goes bankrupt" in message
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
    
    mock_telegram.assert_called_once()
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