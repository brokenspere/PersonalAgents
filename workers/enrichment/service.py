import re
from typing import List
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from shared.models import EnrichedHeadlineItem, HeadlineItem

analyzer = SentimentIntensityAnalyzer()

def extract_tickers_from_text(text: str) -> List[str]:
    """
    Extracts stock tickers from text. Matches uppercase words with 1-5 characters
    that look like tickers, e.g., AAPL, TSLA. Also matches $AAPL.
    """
    # Simple regex for finding tickers: $TICKER or just TICKER in caps (not a foolproof NLP, but works for headlines often)
    # To reduce noise, we'll only extract words that are entirely uppercase and 1-5 characters, 
    # ignoring common words like "A", "I", "THE", "IN", "ON", "AT", "TO", "IS".
    stop_words = {"A", "I", "THE", "IN", "ON", "AT", "TO", "IS", "OF", "AND", "FOR", "WITH", "BY", "IT", "AS"}
    
    # Match $TICKER
    dollar_tickers = re.findall(r'\$[A-Z]{1,5}\b', text)
    # Match standalone UPPERCASE words
    upper_words = re.findall(r'\b[A-Z]{2,5}\b', text)
    
    tickers = set([t.replace('$', '') for t in dollar_tickers])
    for w in upper_words:
        if w not in stop_words:
            tickers.add(w)
            
    return list(tickers)

def enrich_items(items: List[HeadlineItem]) -> List[EnrichedHeadlineItem]:
    enriched = []
    for item in items:
        sentiment = analyzer.polarity_scores(item.title)
        score = sentiment['compound']
        tickers = extract_tickers_from_text(item.title)
        
        enriched.append(EnrichedHeadlineItem(
            title=item.title,
            url=item.url,
            sentiment_score=score,
            extracted_tickers=tickers
        ))
    return enriched
