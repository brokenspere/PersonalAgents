import pytest
from unittest.mock import patch, MagicMock
from scheduler.tasks import emit_event
from shared.models import Event

@patch('scheduler.tasks.app.send_task')
def test_emit_event_market_open(mock_send_task):
    emit_event('market.open', 'NYSE')
    
    mock_send_task.assert_called_once()
    args, kwargs = mock_send_task.call_args
    assert args[0] == 'workers.scraper.tasks.handle_market_event'
    
    # Check that payload contains expected data
    payload = kwargs['args'][0]
    assert payload['event_type'] == 'market.open'
    assert payload['market'] == 'NYSE'

@patch('scheduler.tasks.app.send_task')
def test_emit_event_non_market(mock_send_task):
    emit_event('system.ping', 'ALL')
    
    # Should not send to scraper worker
    mock_send_task.assert_not_called()