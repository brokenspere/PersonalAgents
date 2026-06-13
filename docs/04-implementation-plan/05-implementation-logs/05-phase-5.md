# Implementation Log: Scraper Feature Enhancements

**Task:** Phase 5 - Scraper Feature Enhancements
**Date:** 2026-06-13

## Summary
Successfully implemented advanced scraper features, aligning with the AWS serverless architecture established in Phase 4. Added data models for enriched payloads. Introduced a circuit breaker for resilience and a DynamoDB-backed deduplication cache to prevent duplicate processing. Developed a new EnrichmentWorker Lambda for NLP ticker extraction and sentiment scoring. Finally, updated the NotificationWorker to consume enriched payloads, filter messages per-channel (Telegram only receives impactful sentiment, Discord receives all ticker updates), and integrated Discord webhooks via SSM.

## Files Changed
- `shared/models.py` (Extended with `EnrichedPayload` and `EnrichedHeadlineItem`)
- `shared/circuit_breaker.py` (Created)
- `shared/deduplicator.py` (Created, backed by DynamoDB)
- `workers/scraper/service.py` (Added header rotation and trending tickers)
- `workers/scraper/handlers.py` (Updated to route to EnrichmentWorker)
- `workers/enrichment/` (Created full module)
- `workers/notification/service.py` (Added channel filtering)
- `workers/notification/handlers.py` (Added Discord handler and SSM integration)
- `terraform/sqs.tf` (Added `enrichment_queue`)
- `terraform/dynamodb.tf` (Created `scraper_cache` table)
- `terraform/lambda.tf` (Added Enrichment Lambda and Discord env var)
- `terraform/iam.tf` (Configured Enrichment IAM role and SQS/Dynamo policies)
- `terraform/ssm.tf` (Added Discord webhook parameter)
- `requirements.txt` (Added `vaderSentiment`)
- `tests/` (Added tests for enrichment, deduplicator, updated notification and scraper tests)

## Key Decisions
- **DynamoDB Deduplication:** Adhered to ADR-0004's serverless strategy by replacing the proposed Redis cache with DynamoDB TTL caching, avoiding the need to spin up ElastiCache/MemoryDB.
- **Enrichment Queue:** Implemented a new SQS queue (`enrichment_queue`) to decouple the Scraper and Enrichment workers.
- **Discord SSM Integration:** Standardized Discord secret management by adding `DISCORD_WEBHOOK_URL_SSM` parameter in Terraform, mirroring Telegram's security posture.

## Blockers & Resolutions
- **Issue:** Reviewer identified missing IAM roles for EnrichmentWorker and Discord handler logic.
  **Resolution:** Added `enrichment_lambda_role` with appropriate SQS read/write permissions, granted Scraper Lambda DynamoDB access, and implemented `send_discord_notification_aws` fetching credentials from SSM.
- **Issue:** Missing unit tests for the new functionalities.
  **Resolution:** Created `test_enrichment.py` and `test_deduplicator.py`, and completely refactored `test_notification.py` to cover the new Lambda handlers and per-channel filtering. All tests pass successfully.

## Update: Temporarily Disable Discord (2026-06-15)
- **Action**: The user requested to temporarily disable Discord notifications to focus solely on Telegram.
- **Files Modified**: 
  - `workers/notification/handlers.py` and `workers/notification/service.py`: Commented out all Discord imports, cache, secrets fetch logic, and execution blocks.
  - `terraform/ssm.tf`, `terraform/lambda.tf`, `terraform/iam.tf`: Commented out Discord SSM parameter definitions and references.
  - `tests/test_notification.py`: Commented out Discord-related tests and updated existing mock patches to ensure tests still pass.
- **Status**: Completed. All tests pass with 0 errors.