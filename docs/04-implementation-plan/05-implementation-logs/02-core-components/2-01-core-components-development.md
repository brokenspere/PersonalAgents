# Implementation Log: Core Components Development

**Task:** Phase 2 - Core Components Development
**Date:** 2026-06-12

## Summary
Implemented the core microservices using Celery. Developed the Scheduler to emit market events using Celery Beat. Created the ScraperWorker to listen to market events and scrape Yahoo Finance using BeautifulSoup. Developed the NotificationWorker to listen for parsed news payloads and dispatch messages to Telegram and Discord with exponential backoff for fault tolerance. Created unit tests for all components and updated `pydantic` to ensure compatibility with Python 3.14.

## Files Changed
- `requirements.txt`
- `scheduler/tasks.py` (Created)
- `workers/scraper/tasks.py` (Created)
- `workers/notification/tasks.py` (Created)
- `shared/models.py`
- `tests/test_scheduler.py` (Created)
- `tests/test_scraper.py` (Created)
- `tests/test_notification.py` (Created)

## Key Decisions
- **Scheduler Routing:** Instead of pub/sub for all events, the scheduler explicitly routes `market.*` events directly to the ScraperWorker (`handle_market_event`) to maintain clear boundaries.
- **Scraping Separation:** Separated the network fetch logic from HTML parsing in the ScraperWorker to ensure easy testability without mocking network responses internally in complex ways.
- **Notification Resiliency:** Implemented exponential backoff for Telegram and Discord API calls in the NotificationWorker.
- **Timezone Awareness:** Updated Pydantic data models to use timezone-aware UTC datetime instances to resolve deprecation warnings.

## Blockers & Resolutions
- **Issue:** Pydantic core module failed to install on Python 3.14 due to native build errors.
  **Resolution:** Upgraded `pydantic` to `>=2.8.0` (installed `2.13.4`) to resolve the compatibility issue.