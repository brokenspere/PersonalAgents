import pytest
from unittest.mock import patch, MagicMock
from workers.enrichment.service import extract_tickers_from_text, enrich_items
from shared.models import HeadlineItem

def test_extract_tickers_from_text():
    # Test simple uppercase words
    text1 = "Apple AAPL announces new iPhone and MSFT struggles"
    tickers1 = extract_tickers_from_text(text1)
    assert 'AAPL' in tickers1
    assert 'MSFT' in tickers1
    
    # Test $ prefix
    text2 = "Traders are buying $TSLA and $GME today"
    tickers2 = extract_tickers_from_text(text2)
    assert 'TSLA' in tickers2
    assert 'GME' in tickers2
    
    # Test stop words exclusion
    text3 = "THE company IS going TO the MOON"
    tickers3 = extract_tickers_from_text(text3)
    assert 'THE' not in tickers3
    assert 'IS' not in tickers3
    assert 'TO' not in tickers3
    # MOON might be extracted as it's not a stop word and is 4 uppercase chars

def test_enrich_items():
    items = [
        HeadlineItem(title="Great news for AAPL, profits are up!", url="http://example.com/1"),
        HeadlineItem(title="Terrible tragedy strikes the nation", url="http://example.com/2")
    ]
    
    enriched = enrich_items(items)
    
    assert len(enriched) == 2
    
    # First item
    assert "AAPL" in enriched[0].extracted_tickers
    assert enriched[0].sentiment_score > 0  # Should be positive
    
    # Second item
    assert enriched[1].sentiment_score < 0  # Should be negative
    assert len(enriched[1].extracted_tickers) == 0
