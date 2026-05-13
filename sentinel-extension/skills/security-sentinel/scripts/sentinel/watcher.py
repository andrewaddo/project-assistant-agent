import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .engine import SentinelEngine
import click

class SentinelHandler(FileSystemEventHandler):
    def __init__(self):
        self.engine = SentinelEngine()

    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Avoid scanning the baseline itself or hidden git files
        if ".secrets.baseline" in event.src_path or ".git" in event.src_path:
            return

        # Trigger a scan on the modified file
        # We use relative path for the engine
        rel_path = os.path.relpath(event.src_path)
        findings = self.engine.scan(path=rel_path)

        if "results" in findings and findings["results"]:
            new_count = findings["summary"]["new_secrets_count"]
            if new_count > 0:
                click.echo(click.style(f"\n⚠️  [PROACTIVE ALERT] {new_count} new secret(s) detected in {rel_path}!", fg="yellow", bold=True))
                for file_path, secrets in findings["results"].items():
                    for secret in secrets:
                        click.echo(f"  -> [{secret['severity']}] {secret['type']} on line {secret['line_number']}")
                click.echo(click.style("Action required: Remove the secret or run 'sentinel approve' if it's a false positive.", dim=True))

def start_watcher(path="."):
    event_handler = SentinelHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
