import pytest
from unittest.mock import patch, MagicMock
from shared.models import EnrichedPayload, EnrichedHeadlineItem
from workers.analyst.service import analyze_payload, fetch_market_data

@patch('workers.analyst.service.yf.Ticker')
def test_fetch_market_data(mock_ticker):
    mock_instance = mock_ticker.return_value
    mock_instance.info = {'currentPrice': 150.0, 'previousClose': 148.0, 'sector': 'Technology'}
    
    result = fetch_market_data("AAPL")
    assert "AAPL" in result
    assert "150.0" in result
    assert "Technology" in result

@patch('workers.analyst.service.analyze_with_gemini')
@patch('workers.analyst.service.fetch_market_data')
def test_analyze_payload(mock_fetch, mock_analyze):
    mock_fetch.return_value = "Mocked market data"
    mock_analyze.return_value = "ผลการวิเคราะห์จำลอง (Simulated analysis)"
    
    payload = EnrichedPayload(
        source="test",
        market="test_market",
        items=[
            EnrichedHeadlineItem(
                title="Apple releases new product",
                url="http://example.com",
                extracted_tickers=["AAPL"]
            )
        ],
        trending_tickers=["TSLA"]
    )
    
    result = analyze_payload(payload, api_key="dummy_key")
    
    assert len(result.items) == 1
    assert result.items[0].analysis == "ผลการวิเคราะห์จำลอง (Simulated analysis)"
    mock_analyze.assert_called_once()
    mock_fetch.assert_called_once_with("AAPL")
