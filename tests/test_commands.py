"""Tests for CLI commands."""

import pytest
import json
from pathlib import Path
from click.testing import CliRunner
from cli.commands import cli


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def temp_intent_dir(tmp_path, monkeypatch):
    """Create a temporary intent directory."""
    intent_dir = tmp_path / '.intent'
    intent_dir.mkdir()
    monkeypatch.setattr('cli.utils.get_intent_dir', lambda: intent_dir)
    return intent_dir


def test_start_intent(runner, temp_intent_dir):
    """Test starting a new intent."""
    result = runner.invoke(cli, ['start', 'Add authentication feature'])
    assert result.exit_code == 0
    assert 'Intent started' in result.output
    
    # Verify intent file was created
    intent_file = temp_intent_dir / 'current_intent.json'
    assert intent_file.exists()
    
    with open(intent_file) as f:
        data = json.load(f)
    assert data['message'] == 'Add authentication feature'
    assert data['status'] == 'active'


def test_start_intent_when_active(runner, temp_intent_dir):
    """Test starting a new intent when one is already active."""
    # Start first intent
    runner.invoke(cli, ['start', 'First intent'])
    
    # Try to start second intent
    result = runner.invoke(cli, ['start', 'Second intent'])
    assert result.exit_code == 0
    assert 'Active intent already exists' in result.output


def test_commit_without_intent(runner, temp_intent_dir):
    """Test committing without an active intent."""
    result = runner.invoke(cli, ['commit', '-m', 'Some commit'])
    assert result.exit_code == 0
    assert 'No active intent found' in result.output


def test_commit_with_intent(runner, temp_intent_dir):
    """Test committing with an active intent."""
    # Start intent
    runner.invoke(cli, ['start', 'Add feature'])
    
    # Make commit
    result = runner.invoke(cli, ['commit', '-m', 'Implement feature'])
    assert result.exit_code == 0
    assert 'Commit recorded' in result.output
    
    # Verify commit was recorded
    intent_file = temp_intent_dir / 'current_intent.json'
    with open(intent_file) as f:
        data = json.load(f)
    assert len(data['commits']) == 1
    assert data['commits'][0]['message'] == 'Implement feature'


def test_close_intent(runner, temp_intent_dir):
    """Test closing an intent."""
    # Start intent and make commits
    runner.invoke(cli, ['start', 'Add feature'])
    runner.invoke(cli, ['commit', '-m', 'First commit'])
    runner.invoke(cli, ['commit', '-m', 'Second commit'])
    
    # Close intent
    result = runner.invoke(cli, ['close'])
    assert result.exit_code == 0
    assert 'Intent Session Summary' in result.output
    assert 'Commits made: 2' in result.output


def test_close_without_intent(runner, temp_intent_dir):
    """Test closing when no intent is active."""
    result = runner.invoke(cli, ['close'])
    assert result.exit_code == 0
    assert 'No active intent found' in result.output
