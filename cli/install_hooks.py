"""CLI command to install git hooks."""

import click
import os
import shutil
import stat
from pathlib import Path


@click.command()
def install_hooks():
    """Install git hooks for automatic validation."""
    
    # Find git root
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            text=True,
            check=True
        )
        git_dir = Path(result.stdout.strip())
        hooks_dir = git_dir / 'hooks'
    except:
        click.secho("[ERROR] Not in a git repository!", fg='red')
        return 1
    
    # Get the source hooks directory
    package_dir = Path(__file__).parent.parent
    hooks_to_install = ['commit-msg']  # Changed from pre-commit to commit-msg
    
    installed = []
    for hook_name in hooks_to_install:
        source_hook = package_dir / 'hooks' / hook_name
        
        if not source_hook.exists():
            click.secho(f"[WARNING] Hook script not found at {source_hook}", fg='yellow')
            continue
        
        dest_hook = hooks_dir / hook_name
        
        # Backup existing hook
        if dest_hook.exists():
            backup = hooks_dir / f'{hook_name}.backup'
            shutil.copy2(dest_hook, backup)
            click.echo(f"[INFO] Backed up existing hook to {backup}")
        
        # Copy hook
        shutil.copy2(source_hook, dest_hook)
        
        # Make executable
        os.chmod(dest_hook, os.stat(dest_hook).st_mode | stat.S_IEXEC)
        installed.append(hook_name)
    
    if not installed:
        click.secho("[ERROR] No hooks were installed!", fg='red')
        return 1
    
    click.secho("\n[SUCCESS] Git hooks installed!", fg='green')
    for hook in installed:
        click.echo(f"  - {hook}")
    
    click.echo("\nThe hook will:")
    click.echo("  1. Validate commit messages contain Jira ID (e.g., PROJ-123)")
    click.echo("  2. Fetch Jira story details")
    click.echo("  3. Validate code changes against story (with AI)")
    click.echo("  4. Block commits that don't match the story")
    
    click.echo("\n" + "="*60)
    click.echo("CONFIGURATION NEEDED:")
    click.echo("="*60)
    click.echo("\nCreate .env file with:")
    click.echo("  JIRA_URL=https://skbhethi.atlassian.net")
    click.echo("  JIRA_EMAIL=your.email@example.com")
    click.echo("  JIRA_API_TOKEN=your_token_here")
    click.echo("  OPENAI_API_KEY=your_openai_key (optional, for AI validation)")
    
    click.echo("\n" + "="*60)
    click.echo("USAGE:")
    click.echo("="*60)
    click.echo("\n  git commit -m 'PROJ-123: Add OAuth authentication'")
    click.echo("\nTo skip validation:")
    click.echo("  SKIP_INTENT_VALIDATION=1 git commit -m 'message'")
    click.echo("\nTo disable AI validation:")
    click.echo("  ENABLE_AI_VALIDATION=false git commit -m 'PROJ-123: message'")
    
    return 0
