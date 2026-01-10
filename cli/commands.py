"""CLI commands for intent tracking."""

import click
import json
from datetime import datetime
from pathlib import Path
from .utils import get_intent_dir, get_current_intent, save_intent, get_git_diff
from .ai_validator import AIValidator
from .install_hooks import install_hooks


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
        click.echo(f"Active intent already exists: {current_intent['message']}")
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
@click.option('--validate/--no-validate', default=True, help='Validate intent with AI')
@click.option('--scan-security/--no-scan-security', default=True, help='Scan for security vulnerabilities')
def commit(message, validate, scan_security):
    """Commit changes with intent verification and security scanning."""
    current_intent = get_current_intent()
    
    if not current_intent:
        click.echo("⚠️  No active intent found. Start an intent first with 'intent start'")
        return
    
    # Get the git diff
    diff = get_git_diff()
    if not diff:
        click.echo("⚠️  No staged changes found. Use 'git add' to stage changes first.")
        return
    
    # AI validation if enabled
    validation_result = None
    vulnerability_result = None
    
    if validate or scan_security:
        try:
            validator = AIValidator()
            click.echo("\n🤖 Analyzing changes with AI...")
            
            # Validate intent alignment
            if validate:
                click.echo("   → Checking intent alignment...")
                validation_result = validator.validate_intent(current_intent['message'], diff)
                
                if 'error' not in validation_result:
                    score = validation_result.get('score', 0)
                    click.echo(f"\n📊 Intent Alignment Score: {score}/10")
                    
                    if score < 5:
                        click.secho("⚠️  LOW ALIGNMENT WARNING", fg='red', bold=True)
                    elif score < 7:
                        click.secho("⚠️  Medium alignment", fg='yellow')
                    else:
                        click.secho("✓ Good alignment", fg='green')
                    
                    if validation_result.get('analysis'):
                        click.echo(f"\n💡 Analysis:\n{validation_result['analysis']}")
                    
                    if validation_result.get('suggestions'):
                        click.echo(f"\n💭 Suggestions:\n{validation_result['suggestions']}")
            
            # Security vulnerability scan
            if scan_security:
                click.echo("\n   → Scanning for vulnerabilities...")
                vulnerability_result = validator.check_vulnerabilities(diff)
                
                if 'error' not in vulnerability_result:
                    severity = vulnerability_result.get('severity', 'NONE')
                    click.echo(f"\n🔒 Security Severity: {severity}")
                    
                    if severity in ['HIGH', 'CRITICAL']:
                        click.secho(f"⚠️  {severity} SEVERITY VULNERABILITIES FOUND!", fg='red', bold=True)
                    elif severity == 'MEDIUM':
                        click.secho("⚠️  Medium severity issues found", fg='yellow')
                    else:
                        click.secho("✓ No major security issues detected", fg='green')
                    
                    if vulnerability_result.get('vulnerabilities'):
                        click.echo(f"\n🔍 Vulnerabilities:\n{vulnerability_result['vulnerabilities']}")
                    
                    if vulnerability_result.get('recommendations'):
                        click.echo(f"\n🛡️  Recommendations:\n{vulnerability_result['recommendations']}")
                    
                    # Block commit on critical issues
                    if severity == 'CRITICAL':
                        click.echo("\n❌ Commit blocked due to CRITICAL security issues!")
                        click.echo("Please fix the security vulnerabilities before committing.")
                        return
        
        except ValueError as e:
            click.secho(f"\n⚠️  AI validation disabled: {e}", fg='yellow')
            click.echo("Continuing without AI validation...")
        except Exception as e:
            click.secho(f"\n⚠️  AI validation error: {e}", fg='yellow')
            click.echo("Continuing without AI validation...")
    
    # Record the commit
    commit_data = {
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'validation': validation_result,
        'security': vulnerability_result
    }
    current_intent['commits'].append(commit_data)
    save_intent(current_intent)
    
    click.echo(f"\n✓ Commit recorded: {message}")
    click.echo(f"Intent: {current_intent['message']}")
    click.echo("\nRemember to run 'git commit' to actually commit the changes.")



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


# Add the install-hooks command to the CLI
cli.add_command(install_hooks, name='install-hooks')


if __name__ == '__main__':
    cli()
