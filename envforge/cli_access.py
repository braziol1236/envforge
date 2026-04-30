"""CLI commands for snapshot access tracking."""
from __future__ import annotations

import click

from envforge.snapshot_access import (
    record_access,
    get_last_access,
    list_access_log,
    clear_access_log,
    AccessError,
)


@click.group("access")
def access_cmd():
    """Track and inspect snapshot access times."""


@access_cmd.command("touch")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".snapshots", show_default=True)
def touch_cmd(name: str, snapshot_dir: str):
    """Record an access event for NAME."""
    try:
        ts = record_access(name, snapshot_dir)
        click.echo(f"Recorded access for '{name}' at {ts.isoformat()}")
    except AccessError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@access_cmd.command("show")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".snapshots", show_default=True)
def show_access_cmd(name: str, snapshot_dir: str):
    """Show the last access time for NAME."""
    ts = get_last_access(name, snapshot_dir)
    if ts is None:
        click.echo(f"No access recorded for '{name}'.")
    else:
        click.echo(f"{name}: {ts.isoformat()}")


@access_cmd.command("log")
@click.option("--dir", "snapshot_dir", default=".snapshots", show_default=True)
def log_cmd(snapshot_dir: str):
    """List all access records, newest first."""
    records = list_access_log(snapshot_dir)
    if not records:
        click.echo("No access records found.")
        return
    for r in records:
        click.echo(f"{r['name']:<30} {r['last_access'].isoformat()}")


@access_cmd.command("clear")
@click.option("--dir", "snapshot_dir", default=".snapshots", show_default=True)
@click.confirmation_option(prompt="Clear all access records?")
def clear_cmd(snapshot_dir: str):
    """Delete the entire access log."""
    clear_access_log(snapshot_dir)
    click.echo("Access log cleared.")
