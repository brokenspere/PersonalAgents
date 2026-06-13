import json
import logging
import os
import boto3
from typing import Dict, Any

from shared.models import Event, ExtractionPayload
from shared.deduplicator import is_duplicate
from workers.scraper.service import fetch_yahoo_finance_html, extract_headlines_from_html, extract_trending_tickers

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs_client = boto3.client('sqs')
ENRICHMENT_QUEUE_URL = os.environ.get('ENRICHMENT_QUEUE_URL')

def market_event_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for EventBridge scheduled events.
    """
    try:
        # EventBridge passes the input dict directly to the event object
        event_model = Event.model_validate(event)
    except Exception as exc:
        logger.exception("Failed to parse event: %s", exc)
        return {"statusCode": 400, "body": "Invalid event payload"}

    if event_model.market != 'NYSE':
        logger.info(f"Ignoring event for market: {event_model.market}")
        return {"statusCode": 200, "body": "Ignored market"}

    try:
        html_content = fetch_yahoo_finance_html()
        all_headlines = extract_headlines_from_html(html_content)
        trending_tickers = extract_trending_tickers(html_content)
        
        # Deduplicate
        new_headlines = [item for item in all_headlines if not is_duplicate(item.url)]
        
        if not new_headlines and not trending_tickers:
            logger.info("No new headlines or trending tickers to process.")
            return {"statusCode": 200, "body": "No new data"}
        
        payload = ExtractionPayload(
            source='yahoo_finance',
            market=event_model.market,
            items=new_headlines,
            trending_tickers=trending_tickers
        )
        
        if ENRICHMENT_QUEUE_URL:
            sqs_client.send_message(
                QueueUrl=ENRICHMENT_QUEUE_URL,
                MessageBody=payload.model_dump_json()
            )
            logger.info("Successfully pushed payload to SQS")
        else:
            logger.warning("ENRICHMENT_QUEUE_URL is not set. Payload not sent.")
            
        return {"statusCode": 200, "body": "Success"}
        
    except Exception as exc:
        logger.exception("Unexpected error during scraping: %s", exc)
        raise # Let Lambda handle retries/DLQ
