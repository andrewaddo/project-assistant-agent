import click
import json
import sys
from sentinel.engine import SentinelEngine

@click.group()
def cli():
    """Security Sentinel: Protect your secrets."""
    pass

@cli.command()
@click.option('--path', default=None, help='Path to scan')
@click.option('--staged', is_flag=True, help='Scan only staged files')
def scan(path, staged):
    """Perform an ad-hoc security scan."""
    engine = SentinelEngine()
    findings = engine.scan(path=path, staged=staged)
    
    if "error" in findings:
        click.echo(click.style(findings["error"], fg="red"))
        sys.exit(1)

    new_count = findings["summary"]["new_secrets_count"]
    if new_count == 0:
        click.echo(click.style("✅ No new secrets detected.", fg="green"))
    else:
        click.echo(click.style(f"🚨 Found {new_count} new secret(s)!", fg="red", bold=True))
        for file_path, secrets in findings["results"].items():
            click.echo(f"\nFile: {click.style(file_path, underline=True)}")
            for secret in secrets:
                click.echo(f"  - [{secret['severity']}] {secret['type']} on line {secret['line_number']}")
        sys.exit(1)

@cli.command()
def init():
    """Initialize the secrets baseline."""
    engine = SentinelEngine()
    click.echo("Initializing baseline... this may take a moment.")
    engine.initialize_baseline()
    click.echo(click.style("✅ Baseline initialized in .secrets.baseline", fg="green"))

@cli.command()
def watch():
    """Start the background proactive watcher."""
    from sentinel.watcher import start_watcher
    click.echo(click.style("👁️ Sentinel Watcher starting...", fg="blue", bold=True))
    start_watcher()

if __name__ == "__main__":
    cli()
