import pytest
from unittest.mock import patch, MagicMock
from workers.screener.service import run_screener
from shared.models import ScreenedPayload

@patch('workers.screener.service.yf.Ticker')
@patch('workers.screener.service.analyze_with_gemini')
@patch('workers.screener.service.get_nasdaq100_tickers')
def test_run_screener_passes_technical_check(mock_get_tickers, mock_gemini, mock_ticker):
    # Mock Ticker data
    mock_history = MagicMock()
    mock_history.empty = False
    mock_history.__len__.return_value = 200
    
    # Create a dummy dataframe for history
    import pandas as pd
    import numpy as np
    
    # We need sma_20 > sma_50 > sma_200 and current_price > sma_200
    # Let's create an uptrending series
    prices = np.linspace(100, 200, 200)
    mock_df = pd.DataFrame({'Close': prices})
    mock_history.__getitem__.return_value = mock_df['Close']
    
    mock_ticker_instance = MagicMock()
    mock_ticker_instance.history.return_value = mock_df
    mock_ticker_instance.calendar = None
    mock_ticker.return_value = mock_ticker_instance
    
    mock_gemini.return_value = "Mocked Trading Plan"
    mock_get_tickers.return_value = ['AAPL']
    
    payload = run_screener(market="NYSE", api_key="dummy")
    
    assert isinstance(payload, ScreenedPayload)
    assert len(payload.screened_tickers) == 1
    assert payload.screened_tickers[0].ticker == 'AAPL'
    assert payload.trading_plan == "Mocked Trading Plan"

