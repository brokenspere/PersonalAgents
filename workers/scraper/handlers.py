import json
import logging
import os
import boto3
from typing import Dict, Any

from shared.models import Event, ExtractionPayload
from workers.scraper.service import fetch_yahoo_finance_html, extract_headlines_from_html

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs_client = boto3.client('sqs')
NOTIFICATION_QUEUE_URL = os.environ.get('NOTIFICATION_QUEUE_URL')

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
        headlines = extract_headlines_from_html(html_content)
        
        payload = ExtractionPayload(
            source='yahoo_finance',
            market=event_model.market,
            items=headlines
        )
        
        if NOTIFICATION_QUEUE_URL:
            sqs_client.send_message(
                QueueUrl=NOTIFICATION_QUEUE_URL,
                MessageBody=payload.model_dump_json()
            )
            logger.info("Successfully pushed payload to SQS")
        else:
            logger.warning("NOTIFICATION_QUEUE_URL is not set. Payload not sent.")
            
        return {"statusCode": 200, "body": "Success"}
        
    except Exception as exc:
        logger.exception("Unexpected error during scraping: %s", exc)
        raise # Let Lambda handle retries/DLQ
