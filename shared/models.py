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
