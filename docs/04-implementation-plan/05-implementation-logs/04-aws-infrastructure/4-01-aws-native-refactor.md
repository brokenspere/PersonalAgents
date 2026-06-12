# Implementation Log: AWS Infrastructure & Serverless Refactoring

**Task:** Phase 4 - AWS Infrastructure & Serverless Refactoring
**Date:** 2026-06-12

## Summary
Refactored the application to use an AWS Native Serverless architecture as agreed in ADR 0004. Wrote the complete Terraform Infrastructure as Code (IaC) setup and refactored the Python logic into AWS Lambda handlers (`market_event_handler` and `sqs_event_handler`), removing dependencies on Celery and Redis.

## Files Changed
- `terraform/main.tf` (Created: Base provider config)
- `terraform/variables.tf` (Created: Project variables)
- `terraform/sqs.tf` (Created: Notification queue and DLQ)
- `terraform/ssm.tf` (Created: Telegram SecureStrings)
- `terraform/cloudwatch.tf` (Created: Log groups with 1-day retention)
- `terraform/iam.tf` (Created: Lambda execution roles and policies)
- `terraform/lambda.tf` (Created: Scraper and Notification functions)
- `terraform/eventbridge.tf` (Created: Cron triggers for market hours)
- `requirements.txt` (Updated: Removed `celery` and `redis`, added `boto3`)
- `workers/scraper/handlers.py` (Created: Lambda entrypoint for scraper)
- `workers/notification/handlers.py` (Created: Lambda entrypoint for notifications, fetching creds from SSM)

## Key Decisions
- **SSM Caching:** In the Notification Lambda handler, Telegram credentials fetched from SSM Parameter Store are cached globally to optimize execution speed on "warm" starts and reduce AWS API calls.
- **Dummy Terraform Payload:** Since CI/CD handles code deployment, the `lambda.tf` provisions functions using a dummy zip file initially. The actual Python code will overwrite this via deployment pipelines.
- **Log Retention:** Implemented the strict 1-day retention policy across all Lambda CloudWatch Log Groups as discussed during the architecture review.

## Blockers & Resolutions
None. Code is refactored and syntax checked.
