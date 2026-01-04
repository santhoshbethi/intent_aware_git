"""Tests for utility functions."""

import pytest
import json
from pathlib import Path
from cli.utils import (
    get_intent_dir,
    get_current_intent,
    save_intent,
    get_current_intent_file
)


@pytest.fixture
def temp_intent_dir(tmp_path, monkeypatch):
    """Create a temporary intent directory."""
    intent_dir = tmp_path / '.intent'
    monkeypatch.setattr('cli.utils.get_intent_dir', lambda: intent_dir)
    return intent_dir


def test_get_current_intent_none(temp_intent_dir):
    """Test getting current intent when none exists."""
    assert get_current_intent() is None


def test_save_and_load_intent(temp_intent_dir):
    """Test saving and loading an intent."""
    intent_data = {
        'message': 'Test intent',
        'status': 'active',
        'commits': []
    }
    
    save_intent(intent_data)
    loaded_intent = get_current_intent()
    
    assert loaded_intent is not None
    assert loaded_intent['message'] == 'Test intent'
    assert loaded_intent['status'] == 'active'


def test_closed_intent_not_current(temp_intent_dir):
    """Test that closed intents are not returned as current."""
    intent_data = {
        'message': 'Test intent',
        'status': 'closed',
        'commits': []
    }
    
    save_intent(intent_data)
    assert get_current_intent() is None


def test_save_closed_intent_creates_history(temp_intent_dir):
    """Test that closing an intent saves it to history."""
    intent_data = {
        'message': 'Test intent',
        'status': 'closed',
        'commits': []
    }
    
    save_intent(intent_data)
    
    # Check that history file was created
    history_files = list(temp_intent_dir.glob('intent_*.json'))
    assert len(history_files) == 1
    
    with open(history_files[0]) as f:
        data = json.load(f)
    assert data['message'] == 'Test intent'
