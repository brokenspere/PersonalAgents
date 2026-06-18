from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

class Event(BaseModel):
    """
    Standard event payload routed through the message broker.
    """
    event_type: str = Field(..., description="Type of the event, e.g., 'market.open'")
    timestamp: datetime = Field(default_factory=utc_now, description="ISO-8601 timestamp")
    market: Optional[str] = Field(None, description="Market identifier, e.g., 'NYSE'")

class HeadlineItem(BaseModel):
    title: str
    url: str

class ExtractionPayload(BaseModel):
    """
    Raw, unformatted structured data published by a ScraperWorker.
    """
    source: str = Field(..., description="Source of the data, e.g., 'yahoo_finance'")
    market: Optional[str] = Field(None, description="Market identifier")
    timestamp: datetime = Field(default_factory=utc_now)
    items: List[HeadlineItem] = Field(default_factory=list, description="Array of headline/URL objects")
    trending_tickers: List[str] = Field(default_factory=list, description="Array of trending tickers")

class EnrichedHeadlineItem(HeadlineItem):
    extracted_tickers: List[str] = Field(default_factory=list, description="List of tickers extracted from the headline")

class EnrichedPayload(BaseModel):
    """
    Data published by EnrichmentWorker with NLP insights.
    """
    source: str
    market: Optional[str]
    timestamp: datetime = Field(default_factory=utc_now)
    items: List[EnrichedHeadlineItem] = Field(default_factory=list)
    trending_tickers: List[str] = Field(default_factory=list)

class AnalyzedHeadlineItem(EnrichedHeadlineItem):
    analysis: Optional[str] = Field(None, description="Thai language analysis of the headline and market data")

class AnalyzedPayload(BaseModel):
    """
    Data published by AnalystAgent with LLM insights.
    """
    source: str
    market: Optional[str]
    timestamp: datetime = Field(default_factory=utc_now)
    items: List[AnalyzedHeadlineItem] = Field(default_factory=list)
    trending_tickers: List[str] = Field(default_factory=list)
