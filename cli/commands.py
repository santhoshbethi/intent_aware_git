"""CLI commands for intent tracking."""

import click
import json
from datetime import datetime
from pathlib import Path
from .utils import get_intent_dir, get_current_intent, save_intent


@click.group()
def cli():
    """AI Intent Tracker - Record and verify your coding intentions."""
    pass


@cli.command()
@click.argument('intent_message')
def start(intent_message):
    """Start a new intent session."""
    intent_dir = get_intent_dir()
    intent_dir.mkdir(exist_ok=True)
    
    # Check if there's already an active intent
    current_intent = get_current_intent()
    if current_intent:
        click.echo(f"⚠️  Active intent already exists: {current_intent['message']}")
        click.echo("Please close the current intent before starting a new one.")
        return
    
    # Create new intent
    intent_data = {
        'message': intent_message,
        'started_at': datetime.now().isoformat(),
        'status': 'active',
        'commits': []
    }
    
    save_intent(intent_data)
    click.echo(f"✓ Intent started: {intent_message}")


@cli.command()
@click.option('-m', '--message', required=True, help='Commit message')
def commit(message):
    """Commit changes with intent verification."""
    current_intent = get_current_intent()
    
    if not current_intent:
        click.echo("⚠️  No active intent found. Start an intent first with 'intent start'")
        return
    
    # Record the commit
    commit_data = {
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    current_intent['commits'].append(commit_data)
    save_intent(current_intent)
    
    click.echo(f"✓ Commit recorded: {message}")
    click.echo(f"Intent: {current_intent['message']}")


@cli.command()
def close():
    """Close the current intent session."""
    current_intent = get_current_intent()
    
    if not current_intent:
        click.echo("⚠️  No active intent found.")
        return
    
    current_intent['status'] = 'closed'
    current_intent['closed_at'] = datetime.now().isoformat()
    save_intent(current_intent)
    
    # Generate summary
    click.echo("\n" + "="*50)
    click.echo("Intent Session Summary")
    click.echo("="*50)
    click.echo(f"\nIntent: {current_intent['message']}")
    click.echo(f"Started: {current_intent['started_at']}")
    click.echo(f"Closed: {current_intent['closed_at']}")
    click.echo(f"\nCommits made: {len(current_intent['commits'])}")
    for i, commit in enumerate(current_intent['commits'], 1):
        click.echo(f"  {i}. {commit['message']}")
    click.echo("\n✓ Intent session closed")


if __name__ == '__main__':
    cli()
