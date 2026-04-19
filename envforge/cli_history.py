"""CLI commands for snapshot history."""

import click
from pathlib import Path

from envforge.history import get_history, clear_history
from envforge.snapshot import get_snapshot_path


DEFAULT_DIR = Path.home() / ".envforge"


@click.group("history")
def history_cmd():
    """View or clear snapshot history."""
    pass


@history_cmd.command("show")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=str(DEFAULT_DIR), help="Snapshot directory")
def show_history_cmd(name, snapshot_dir):
    """Show access history for a snapshot."""
    d = Path(snapshot_dir)
    events = get_history(d, name)
    if not events:
        click.echo(f"No history found for '{name}'.")
        return
    click.echo(f"History for '{name}':")
    for entry in events:
        click.echo(f"  [{entry['timestamp']}] {entry['event']}")


@history_cmd.command("clear")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=str(DEFAULT_DIR), help="Snapshot directory")
def clear_history_cmd(name, snapshot_dir):
    """Clear history for a snapshot."""
    d = Path(snapshot_dir)
    clear_history(d, name)
    click.echo(f"History cleared for '{name}'.")
