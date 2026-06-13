import pytest
import os
from unittest.mock import patch, MagicMock
from shared.deduplicator import is_duplicate

@patch.dict(os.environ, {"DEDUPLICATION_TABLE": "TestCache"}, clear=True)
@patch('shared.deduplicator.dynamodb')
def test_is_duplicate_false(mock_dynamodb):
    # Setup mock
    mock_table = MagicMock()
    mock_dynamodb.Table.return_value = mock_table
    mock_table.get_item.return_value = {} # No 'Item' means not duplicate
    
    # Run
    result = is_duplicate("http://example.com")
    
    # Assert
    assert result is False
    mock_table.get_item.assert_called_once_with(Key={'url': 'http://example.com'})
    mock_table.put_item.assert_called_once()
    assert mock_table.put_item.call_args[1]['Item']['url'] == 'http://example.com'

@patch.dict(os.environ, {"DEDUPLICATION_TABLE": "TestCache"}, clear=True)
@patch('shared.deduplicator.dynamodb')
def test_is_duplicate_true(mock_dynamodb):
    # Setup mock
    mock_table = MagicMock()
    mock_dynamodb.Table.return_value = mock_table
    mock_table.get_item.return_value = {'Item': {'url': 'http://example.com'}} # Has 'Item'
    
    # Run
    result = is_duplicate("http://example.com")
    
    # Assert
    assert result is True
    mock_table.get_item.assert_called_once_with(Key={'url': 'http://example.com'})
    mock_table.put_item.assert_not_called()

@patch.dict(os.environ, {"DEDUPLICATION_TABLE": ""}, clear=True)
@patch('shared.deduplicator.dynamodb')
def test_is_duplicate_disabled(mock_dynamodb):
    # DEDUPLICATION_TABLE is empty
    result = is_duplicate("http://example.com")
    
    # Assert
    assert result is False
    mock_dynamodb.Table.assert_not_called()

@patch.dict(os.environ, {"DEDUPLICATION_TABLE": "TestCache"}, clear=True)
@patch('shared.deduplicator.dynamodb')
def test_is_duplicate_exception(mock_dynamodb):
    # Setup mock to raise exception
    mock_table = MagicMock()
    mock_dynamodb.Table.return_value = mock_table
    mock_table.get_item.side_effect = Exception("DynamoDB down")
    
    # Run
    result = is_duplicate("http://example.com")
    
    # Assert fails open (False)
    assert result is False
