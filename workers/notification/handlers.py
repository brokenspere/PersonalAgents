import json
import logging
import os
import boto3
import requests
from botocore.config import Config
from typing import Dict, Any

from shared.models import AnalyzedPayload, ScreenedPayload
from workers.notification.service import (
    filter_for_telegram, # filter_for_discord, 
    format_telegram_message, # format_discord_message
    format_screened_payload_telegram
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm_client = boto3.client('ssm', config=Config(connect_timeout=5, read_timeout=5))

# Cache credentials outside the handler for warm starts
TELEGRAM_CREDS_CACHE = {}
DISCORD_CREDS_CACHE = {}

def get_telegram_credentials() -> tuple[str, str]:
    if 'bot_token' in TELEGRAM_CREDS_CACHE and 'chat_id' in TELEGRAM_CREDS_CACHE:
        return TELEGRAM_CREDS_CACHE['bot_token'], TELEGRAM_CREDS_CACHE['chat_id']
        
    token_param_name = os.environ.get('TELEGRAM_BOT_TOKEN_SSM')
    chat_id_param_name = os.environ.get('TELEGRAM_CHAT_ID_SSM')
    
    if not token_param_name or not chat_id_param_name:
        return None, None
        
    try:
        response = ssm_client.get_parameters(
            Names=[token_param_name, chat_id_param_name],
            WithDecryption=True
        )
        params = {p['Name']: p['Value'] for p in response['Parameters']}
        
        bot_token = params.get(token_param_name)
        chat_id = params.get(chat_id_param_name)
        
        if bot_token and chat_id:
            TELEGRAM_CREDS_CACHE['bot_token'] = bot_token
            TELEGRAM_CREDS_CACHE['chat_id'] = chat_id
            
        return bot_token, chat_id
    except Exception as e:
        logger.exception("Failed to fetch secrets from SSM: %s", e)
        return None, None

def send_telegram_notification_aws(message: str) -> None:
    bot_token, chat_id = get_telegram_credentials()
    
    # If the dummy value from terraform is still present, or no credentials, skip
    if not bot_token or not chat_id or bot_token == "dummy_value_change_me":
        logger.info("Telegram credentials not properly configured (dummy or missing), skipping.")
        return
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(url, json={
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }, timeout=10)
    
    if not response.ok:
        logger.error(f"Telegram API response: {response.text}")
        logger.error(f"Failed message content: {message}")
        
    response.raise_for_status()

def sqs_event_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for SQS events.
    """
    for record in event.get('Records', []):
        try:
            body = json.loads(record['body'])
            
            if 'screened_tickers' in body:
                payload = ScreenedPayload.model_validate(body)
                if not payload.screened_tickers:
                    logger.info("ScreenedPayload contains no tickers to notify.")
                    continue
                
                tg_messages = format_screened_payload_telegram(payload)
                try:
                    for msg in tg_messages:
                        send_telegram_notification_aws(msg)
                    logger.info(f"Successfully sent Telegram notification for ScreenedPayload.")
                except requests.RequestException as exc:
                    logger.warning(f"Telegram notification failed for ScreenedPayload: {exc}")
                    raise
            else:
                payload = AnalyzedPayload.model_validate(body)
                if not payload.items and not payload.trending_tickers:
                    logger.info("Payload contains no items to notify.")
                    continue
                    
                tg_items = filter_for_telegram(payload.items)
                if tg_items or payload.trending_tickers:
                    tg_messages = format_telegram_message(payload, tg_items)
                    try:
                        for msg in tg_messages:
                            send_telegram_notification_aws(msg)
                        logger.info(f"Successfully sent Telegram notification with {len(tg_items)} items.")
                    except requests.RequestException as exc:
                        logger.warning(f"Telegram notification failed: {exc}")
                        raise
                else:
                    logger.info("No items met Telegram filter criteria.")

        except Exception as exc:
            logger.exception("Failed to parse or process payload: %s", exc)
            continue
            
    return {"statusCode": 200, "body": "Processed batch"}
