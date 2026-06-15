import json
import logging
import os
import boto3
from typing import Dict, Any

from shared.models import ExtractionPayload, EnrichedPayload
from workers.enrichment.service import enrich_items

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs_client = boto3.client('sqs')
ANALYST_QUEUE_URL = os.environ.get('ANALYST_QUEUE_URL')

def sqs_event_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for processing SQS messages containing ExtractionPayloads.
    """
    for record in event.get('Records', []):
        try:
            body = json.loads(record['body'])
            payload = ExtractionPayload.model_validate(body)
            
            # Enrich items
            enriched_items = enrich_items(payload.items)
            
            enriched_payload = EnrichedPayload(
                source=payload.source,
                market=payload.market,
                timestamp=payload.timestamp,
                items=enriched_items,
                trending_tickers=payload.trending_tickers
            )
            
            if ANALYST_QUEUE_URL:
                sqs_client.send_message(
                    QueueUrl=ANALYST_QUEUE_URL,
                    MessageBody=enriched_payload.model_dump_json()
                )
                logger.info(f"Enriched and forwarded payload to Analyst Queue. Items: {len(enriched_items)}")
            else:
                logger.warning("ANALYST_QUEUE_URL is not set. Discarding enriched payload.")
                
        except Exception as exc:
            logger.exception("Error processing record: %s", exc)
            raise  # Raises to trigger DLQ mechanism

    return {"statusCode": 200, "body": "Success"}
