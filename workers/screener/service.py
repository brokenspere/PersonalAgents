import json
import logging
import os
import time
import random
import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime, timedelta, timezone

import pandas as pd
import yfinance as yf
from google import genai
from google.genai import types

from shared.models import ScreenedPayload, ScreenedTickerItem

logger = logging.getLogger(__name__)

AGENT_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '.gemini', 'agents', 'swing-trade-assistant.md')
try:
    with open(AGENT_FILE_PATH, 'r', encoding='utf-8') as f:
        # Extract content after yaml frontmatter
        content = f.read()
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                AGENT_INSTRUCTIONS = parts[2].strip()
            else:
                AGENT_INSTRUCTIONS = content
        else:
            AGENT_INSTRUCTIONS = content
except Exception as e:
    logger.warning(f"Could not load agent file from {AGENT_FILE_PATH}: {e}")
    AGENT_INSTRUCTIONS = "You are a financial analysis agent. Provide your analysis entirely in Thai language."

def get_nasdaq100_tickers() -> List[str]:
    """
    Dynamically fetches the current Nasdaq-100 tickers from Wikipedia.
    """
    try:
        url = "https://en.wikipedia.org/wiki/Nasdaq-100"
        headers = {"User-Agent": "Mozilla/5.0"}
        logger.info(f"Fetching Nasdaq-100 tickers from {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'constituents'})
        
        tickers = []
        if table:
            headers_row = table.find('tr')
            headers_th = [th.text.strip() for th in headers_row.find_all('th')]
            ticker_idx = headers_th.index('Ticker') if 'Ticker' in headers_th else 1
            
            for row in table.find_all('tr')[1:]:
                cols = row.find_all('td')
                if len(cols) > ticker_idx:
                    ticker = cols[ticker_idx].text.strip()
                    # yfinance uses '-' for class shares instead of '.'
                    ticker = ticker.replace('.', '-')
                    tickers.append(ticker)
        
        logger.info(f"Successfully fetched {len(tickers)} Nasdaq-100 tickers.")
        return tickers
    except Exception as e:
        logger.error(f"Failed to fetch Nasdaq-100 tickers: {e}")
        # Fallback to a safe hardcoded list if scraping fails
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA']

def check_macro_event_risk() -> bool:
    """
    Check if there is a high impact macroeconomic event within the next 7 days.
    """
    calendar_path = os.path.join(os.path.dirname(__file__), '..', '..', 'shared', 'economic_calendar.json')
    try:
        with open(calendar_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            events = data.get('events', [])
            now = datetime.now(timezone.utc)
            for evt in events:
                event_date = datetime.strptime(evt['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
                delta = event_date - now
                if 0 <= delta.days <= 7 and evt.get('impact', '').lower() == 'high':
                    return True
    except Exception as e:
        logger.warning(f"Failed to read economic calendar: {e}")
    return False

def get_upcoming_earnings(ticker: yf.Ticker) -> Optional[str]:
    """
    Check if there's an upcoming earnings date within the next 7 days.
    """
    try:
        calendar = ticker.calendar
        # Depending on yfinance version, calendar might be a dict or dataframe
        if isinstance(calendar, dict) and 'Earnings Date' in calendar:
            dates = calendar['Earnings Date']
            if dates:
                next_date = dates[0]
                if isinstance(next_date, pd.Timestamp):
                    now = datetime.now(next_date.tz) if next_date.tz else datetime.now()
                    delta = next_date - now
                    if 0 <= delta.days <= 7:
                        return next_date.strftime('%Y-%m-%d')
    except Exception as e:
        logger.debug(f"Failed to fetch earnings for {ticker.ticker}: {e}")
    return None

def analyze_with_gemini(tickers_context: str, api_key: str) -> Optional[str]:
    """
    Calls Gemini API to generate the swing trading plan, with model fallbacks and retries.
    """
    if not api_key:
        logger.warning("API key is missing, skipping Gemini analysis.")
        return None

    client = genai.Client(api_key=api_key)
    prompt = f"Filtered Tickers Context:\n{tickers_context}"
    
    # Using stable 1.5 and experimental 2.0 models
    models_to_try = ['gemini-3.1-flash-lite', 'gemini-2.5-flash', 'gemini-2.5-flash-lite']
    max_retries = 3
    
    for model_name in models_to_try:
        for attempt in range(max_retries):
            try:
                logger.info(f"Calling Gemini API for screener plan using {model_name} (Attempt {attempt+1})...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=AGENT_INSTRUCTIONS
                    )
                )
                logger.info(f"Gemini API call successful with {model_name}.")
                return response.text
            except Exception as e:
                error_str = str(e).lower()
                # Retry on rate limit (429) or service unavailable (503)
                if any(code in error_str for code in ["429", "503", "rate limit", "exhausted"]):
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Gemini API {model_name} hit limit/error: {e}. Retrying in {wait_time:.2f}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.warning(f"Gemini API analysis failed with {model_name} due to non-retryable error: {e}")
                    break # Try next model
            
    logger.error("All Gemini API fallback models and retries failed.")
    return "[Error: LLM Analysis Failed - Models Unavailable]"

def run_screener(market: str, api_key: Optional[str]) -> ScreenedPayload:
    """
    Executes the screening logic and returns a ScreenedPayload.
    """
    logger.info(f"Starting screener for market {market}.")
    screened_items = []
    
    macro_risk = check_macro_event_risk()
    watchlist = get_nasdaq100_tickers()
    
    for symbol in watchlist:
        logger.info(f"Screening {symbol}...")
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            if hist.empty or len(hist) < 200:
                logger.info(f"Not enough data for {symbol}.")
                continue
                
            close_prices = hist['Close']
            current_price = float(close_prices.iloc[-1])
            sma_20 = float(close_prices.rolling(window=20).mean().iloc[-1])
            sma_50 = float(close_prices.rolling(window=50).mean().iloc[-1])
            sma_200 = float(close_prices.rolling(window=200).mean().iloc[-1])
            
            # Technical condition: Perfect uptrend
            if sma_20 > sma_50 > sma_200 and current_price > sma_200:
                earnings_date = get_upcoming_earnings(ticker)
                
                # We flag the risk if there's macro risk or upcoming earnings
                has_event_risk = macro_risk or (earnings_date is not None)
                
                item = ScreenedTickerItem(
                    ticker=symbol,
                    current_price=current_price,
                    sma_20=sma_20,
                    sma_50=sma_50,
                    sma_200=sma_200,
                    upcoming_earnings_date=earnings_date,
                    event_risk=has_event_risk
                )
                screened_items.append(item)
                logger.info(f"{symbol} passed technical screening.")
            else:
                logger.info(f"{symbol} did not pass technical screening.")
                
        except Exception as e:
            logger.warning(f"Error processing {symbol}: {e}")

    logger.info(f"Screening complete. {len(screened_items)} tickers passed.")
    
    trading_plan = None
    if screened_items:
        context_lines = []
        for item in screened_items:
            line = (f"Ticker: {item.ticker}, Price: {item.current_price:.2f}, "
                    f"SMA20: {item.sma_20:.2f}, SMA50: {item.sma_50:.2f}, SMA200: {item.sma_200:.2f}, "
                    f"EventRisk: {item.event_risk}, EarningsDate: {item.upcoming_earnings_date}")
            context_lines.append(line)
        
        tickers_context = "\n".join(context_lines)
        
        if api_key:
            trading_plan = analyze_with_gemini(tickers_context, api_key)
        else:
            trading_plan = "[Simulated Trading Plan - API Key Missing]"

    return ScreenedPayload(
        source='swing_trade_screener',
        market=market,
        screened_tickers=screened_items,
        trading_plan=trading_plan
    )
