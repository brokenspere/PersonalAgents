import json
import logging
import os
from typing import Dict, Any

import boto3
from botocore.config import Config

from workers.screener.service import run_screener

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs_client = boto3.client('sqs')
ssm_client = boto3.client('ssm', config=Config(connect_timeout=5, read_timeout=5))

NOTIFICATION_QUEUE_URL = os.environ.get('NOTIFICATION_QUEUE_URL')
GEMINI_API_KEY_SSM = os.environ.get('GEMINI_API_KEY_SSM')

GEMINI_CREDS_CACHE = {}

def get_gemini_api_key() -> str:
    if 'api_key' in GEMINI_CREDS_CACHE:
        return GEMINI_CREDS_CACHE['api_key']
        
    if not GEMINI_API_KEY_SSM:
        return None
        
    try:
        response = ssm_client.get_parameter(
            Name=GEMINI_API_KEY_SSM,
            WithDecryption=True
        )
        api_key = response['Parameter']['Value']
        if api_key:
            GEMINI_CREDS_CACHE['api_key'] = api_key
        return api_key
    except Exception as e:
        logger.exception("Failed to fetch Gemini API Key from SSM: %s", e)
        return None

def eventbridge_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for processing EventBridge triggers (market.close).
    """
    api_key = get_gemini_api_key()
    
    # Allow testing without API key if it's dummy
    if api_key == "dummy_value_change_me":
        logger.warning("Gemini API key is set to dummy value. Analysis might be skipped or mocked.")
        api_key = None

    event_type = event.get('event_type')
    market = event.get('market', 'NYSE')

    if event_type != 'market.close':
        logger.info(f"Ignoring event type: {event_type}")
        return {"statusCode": 200, "body": "Ignored"}

    try:
        payload = run_screener(market=market, api_key=api_key)
        
        if NOTIFICATION_QUEUE_URL:
            sqs_client.send_message(
                QueueUrl=NOTIFICATION_QUEUE_URL,
                MessageBody=payload.model_dump_json()
            )
            logger.info(f"Screened and forwarded payload to Notification Queue. Tickers: {len(payload.screened_tickers)}")
        else:
            logger.warning("NOTIFICATION_QUEUE_URL is not set. Discarding screened payload.")
            
    except Exception as exc:
        logger.exception("Error running screener: %s", exc)
        raise  # Raises to trigger DLQ mechanism if present

    return {"statusCode": 200, "body": "Success"}
