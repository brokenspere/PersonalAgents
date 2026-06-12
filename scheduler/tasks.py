from celery.schedules import crontab
from shared.celery_app import app
from shared.models import Event

# Configure Celery Beat schedules
# Note: Celery app is currently set to UTC timezone.
# NYSE hours are 9:30 AM to 4:00 PM Eastern Time.
# We configure timezone='US/Eastern' directly on the app config for clarity.
app.conf.timezone = 'US/Eastern'

app.conf.beat_schedule = {
    'market-open': {
        'task': 'scheduler.tasks.emit_event',
        'schedule': crontab(hour=9, minute=30, day_of_week='1-5'),
        'kwargs': {'event_type': 'market.open', 'market': 'NYSE'}
    },
    'market-close': {
        'task': 'scheduler.tasks.emit_event',
        'schedule': crontab(hour=16, minute=0, day_of_week='1-5'),
        'kwargs': {'event_type': 'market.close', 'market': 'NYSE'}
    },
}

@app.task(name='scheduler.tasks.emit_event', bind=True)
def emit_event(self, event_type: str, market: str) -> None:
    """
    Emits a standard event to the system.
    Instead of complex pub/sub, we route explicitly to the scraper worker 
    based on event type, maintaining clear boundaries and traceability.
    """
    event = Event(event_type=event_type, market=market)
    
    if event_type.startswith('market.'):
        app.send_task(
            'workers.scraper.tasks.handle_market_event',
            args=[event.model_dump(mode='json')]
        )
