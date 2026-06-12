# Delayed Retry with Backoff for External Notifications

We decided to use a delayed re-queue mechanism (with exponential backoff) for handling external API failures in our NotificationWorkers, rather than immediately routing to a Dead Letter Queue (DLQ). 

When a NotificationWorker attempts to push an `Extraction Payload` to external services (like Discord or Telegram) and encounters a failure (e.g., rate limits, API downtime), it will NACK the event and re-queue it with a delay. This prevents a single failing API from blocking the queue and ensures data is eventually delivered without immediate manual intervention. We will rely on Celery's built-in retry mechanisms to handle this scheduling.