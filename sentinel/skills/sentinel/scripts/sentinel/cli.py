import click
import json
import sys
import os
import signal
from .engine import SentinelEngine

PID_FILE = ".sentinel.pid"

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
@click.option('--background', is_flag=True, help='Run watcher in background')
def watch(background):
    """Start the background proactive watcher."""
    if os.path.exists(PID_FILE):
        click.echo(click.style("⚠️  Watcher is already running (or .sentinel.pid exists).", fg="yellow"))
        return

    from sentinel.watcher import start_watcher
    
    if background:
        import subprocess
        # Start the process in a new session to detach it from the current terminal
        cmd = [sys.executable, "-m", "sentinel.cli", "watch"]
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL, 
            start_new_session=True
        )
        with open(PID_FILE, "w") as f:
            f.write(str(process.pid))
        click.echo(click.style(f"👁️ Sentinel Watcher started in background (PID: {process.pid})", fg="green"))
    else:
        # Foreground mode
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
        
        click.echo(click.style("👁️ Sentinel Watcher starting in foreground...", fg="blue", bold=True))
        try:
            start_watcher()
        finally:
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)

@cli.command()
@click.argument('file_path')
@click.argument('line_number', type=int)
def approve(file_path, line_number):
    """Approve a finding to add it to the baseline."""
    engine = SentinelEngine()
    if engine.approve_finding(file_path, line_number):
        click.echo(click.style(f"✅ Approved finding in {file_path} on line {line_number}.", fg="green"))
    else:
        click.echo(click.style(f"❌ Could not find or approve secret in {file_path} on line {line_number}.", fg="red"))

@cli.command()
def stop():
    """Stop the background proactive watcher."""
    if not os.path.exists(PID_FILE):
        click.echo(click.style("ℹ️  No watcher process found.", fg="cyan"))
        return

    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())
        
        os.kill(pid, signal.SIGTERM)
        os.remove(PID_FILE)
        click.echo(click.style(f"🛑 Sentinel Watcher (PID: {pid}) stopped successfully.", fg="green"))
    except ProcessLookupError:
        click.echo(click.style("⚠️  Process not found. Cleaning up stale PID file.", fg="yellow"))
        os.remove(PID_FILE)
    except Exception as e:
        click.echo(click.style(f"❌ Error stopping watcher: {e}", fg="red"))

if __name__ == "__main__":
    cli()
