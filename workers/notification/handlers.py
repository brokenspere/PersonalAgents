import json
import logging
import os
import boto3
import requests
from botocore.config import Config
from typing import Dict, Any

from shared.models import AnalyzedPayload
from workers.notification.service import (
    filter_for_telegram, # filter_for_discord, 
    format_telegram_message, # format_discord_message
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

# def get_discord_webhook_url() -> str:
#     if 'webhook_url' in DISCORD_CREDS_CACHE:
#         return DISCORD_CREDS_CACHE['webhook_url']
#         
#     webhook_param_name = os.environ.get('DISCORD_WEBHOOK_URL_SSM')
#     if not webhook_param_name:
#         return None
#         
#     try:
#         response = ssm_client.get_parameter(
#             Name=webhook_param_name,
#             WithDecryption=True
#         )
#         webhook_url = response['Parameter']['Value']
#         if webhook_url:
#             DISCORD_CREDS_CACHE['webhook_url'] = webhook_url
#         return webhook_url
#     except Exception as e:
#         logger.exception("Failed to fetch Discord secret from SSM: %s", e)
#         return None

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
    response.raise_for_status()

# def send_discord_notification_aws(message: str) -> None:
#     webhook_url = get_discord_webhook_url()
#     
#     if not webhook_url or webhook_url == "dummy_value_change_me":
#         logger.info("Discord webhook not properly configured (dummy or missing), skipping.")
#         return
#         
#     response = requests.post(webhook_url, json={'content': message}, timeout=10)
#     response.raise_for_status()

def sqs_event_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for SQS events.
    """
    for record in event.get('Records', []):
        try:
            body = json.loads(record['body'])
            payload = AnalyzedPayload.model_validate(body)
        except Exception as exc:
            logger.exception("Failed to parse analyzed payload: %s", exc)
            continue # Skip this record, avoid poison pill loop
            
        if not payload.items and not payload.trending_tickers:
            logger.info("Payload contains no items to notify.")
            continue
            
        # Telegram filtering and sending
        tg_items = filter_for_telegram(payload.items)
        if tg_items or payload.trending_tickers:
            tg_message = format_telegram_message(payload, tg_items)
            try:
                send_telegram_notification_aws(tg_message)
                logger.info(f"Successfully sent Telegram notification with {len(tg_items)} items.")
            except requests.RequestException as exc:
                logger.warning(f"Telegram notification failed: {exc}")
                raise # Fail the function to trigger SQS visibility timeout/retry
        else:
            logger.info("No items met Telegram filter criteria.")

        # Discord filtering and sending
#         dc_items = filter_for_discord(payload.items)
#         if dc_items or payload.trending_tickers:
#             dc_message = format_discord_message(payload, dc_items)
#             try:
#                 send_discord_notification_aws(dc_message)
#                 logger.info(f"Successfully sent Discord notification with {len(dc_items)} items.")
#             except requests.RequestException as exc:
#                 logger.warning(f"Discord notification failed: {exc}")
#                 raise
#         else:
#             logger.info("No items met Discord filter criteria.")
            
    return {"statusCode": 200, "body": "Processed batch"}
