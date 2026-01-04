"""Utility functions for intent tracking."""

import json
from pathlib import Path
from datetime import datetime


def get_intent_dir():
    """Get the .intent directory path."""
    return Path.cwd() / '.intent'


def get_current_intent_file():
    """Get the path to the current intent file."""
    intent_dir = get_intent_dir()
    return intent_dir / 'current_intent.json'


def get_current_intent():
    """Load the current active intent."""
    intent_file = get_current_intent_file()
    
    if not intent_file.exists():
        return None
    
    with open(intent_file, 'r') as f:
        intent_data = json.load(f)
    
    if intent_data.get('status') == 'closed':
        return None
    
    return intent_data


def save_intent(intent_data):
    """Save intent data to file."""
    intent_dir = get_intent_dir()
    intent_dir.mkdir(exist_ok=True)
    
    # Save as current intent
    current_file = get_current_intent_file()
    with open(current_file, 'w') as f:
        json.dump(intent_data, f, indent=2)
    
    # Also save to history if closed
    if intent_data.get('status') == 'closed':
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        history_file = intent_dir / f'intent_{timestamp}.json'
        with open(history_file, 'w') as f:
            json.dump(intent_data, f, indent=2)


def get_git_diff():
    """Get the current git diff."""
    import subprocess
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None
