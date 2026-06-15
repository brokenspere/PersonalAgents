import logging
import os
from typing import List, Optional
import yfinance as yf
from google import genai
from google.genai import types

from shared.models import EnrichedPayload, AnalyzedPayload, AnalyzedHeadlineItem, EnrichedHeadlineItem

logger = logging.getLogger(__name__)

# Pre-load agent instructions outside the function to avoid IO on every invocation
AGENT_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '.gemini', 'agents', 'finance-analysis.agent.md')
try:
    with open(AGENT_FILE_PATH, 'r', encoding='utf-8') as f:
        AGENT_INSTRUCTIONS = f.read()
except Exception as e:
    logger.warning(f"Could not load agent file from {AGENT_FILE_PATH}: {e}")
    AGENT_INSTRUCTIONS = "You are a financial analysis agent. Provide your analysis entirely in Thai language."

def fetch_market_data(ticker_symbol: str) -> str:
    """
    Fetches basic fundamental/technical data for a given ticker.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        if not info or 'regularMarketPrice' not in info and 'currentPrice' not in info:
            # Fallback to fast history
            hist = ticker.history(period="5d")
            if hist.empty:
                return f"No data found for {ticker_symbol}"
            last_close = hist['Close'].iloc[-1]
            return f"{ticker_symbol} Last Close: {last_close:.2f}"
            
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 'N/A')
        prev_close = info.get('previousClose', 'N/A')
        sector = info.get('sector', 'N/A')
        return f"{ticker_symbol} ({sector}): Price {current_price}, Prev Close {prev_close}"
    except Exception as e:
        logger.warning(f"Failed to fetch data for {ticker_symbol}: {e}")
        return f"Error fetching {ticker_symbol} data."

def analyze_with_gemini(text: str, market_data: str, sentiment: float, api_key: str) -> Optional[str]:
    """
    Calls Gemini API to analyze the headline with market data and sentiment,
    using the instructions from the finance-analysis agent file.
    Outputs exclusively in Thai language.
    """
    if not api_key:
        return None

    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        Headline: {text}
        VADER Sentiment Score: {sentiment}
        Market Data Context: {market_data}
        """
        
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=AGENT_INSTRUCTIONS
            )
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini API analysis failed: {e}")
        return None

def analyze_payload(payload: EnrichedPayload, api_key: Optional[str]) -> AnalyzedPayload:
    """
    Augments the enriched payload with financial data and LLM analysis.
    """
    analyzed_items: List[AnalyzedHeadlineItem] = []
    
    for item in payload.items:
        market_context_parts = []
        for ticker in item.extracted_tickers:
            data = fetch_market_data(ticker)
            market_context_parts.append(data)
            
        market_data_str = " | ".join(market_context_parts) if market_context_parts else "No specific ticker data."
        
        analysis = None
        if api_key:
            analysis = analyze_with_gemini(
                text=item.title,
                market_data=market_data_str,
                sentiment=item.sentiment_score,
                api_key=api_key
            )
        else:
            analysis = "[Simulated Analysis - API Key Missing] ข่าวนี้อาจส่งผลกระทบต่อตลาด (This news might impact the market)."

        analyzed_item = AnalyzedHeadlineItem(
            title=item.title,
            url=item.url,
            sentiment_score=item.sentiment_score,
            extracted_tickers=item.extracted_tickers,
            analysis=analysis
        )
        analyzed_items.append(analyzed_item)
        
    return AnalyzedPayload(
        source=payload.source,
        market=payload.market,
        timestamp=payload.timestamp,
        items=analyzed_items,
        trending_tickers=payload.trending_tickers
    )
