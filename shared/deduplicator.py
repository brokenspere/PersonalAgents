import os
import boto3
import time
import logging

logger = logging.getLogger(__name__)

dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
CACHE_TABLE_NAME = os.environ.get('DEDUPLICATION_TABLE', 'ScraperCache')

def is_duplicate(url: str, ttl_seconds: int = 86400) -> bool:
    """
    Checks if a URL has been seen recently. 
    Returns True if duplicate, False if new.
    Saves the URL if it is new.
    """
    if not os.environ.get('DEDUPLICATION_TABLE'):
        logger.warning("DEDUPLICATION_TABLE not set, skipping deduplication.")
        return False

    try:
        table = dynamodb.Table(CACHE_TABLE_NAME)
        response = table.get_item(Key={'url': url})
        
        if 'Item' in response:
            return True
            
        # Not a duplicate, insert it
        expires_at = int(time.time()) + ttl_seconds
        table.put_item(
            Item={
                'url': url,
                'expires_at': expires_at
            }
        )
        return False
    except Exception as e:
        logger.warning(f"Failed to check/update DynamoDB deduplication cache: {e}")
        return False
