"""CLI commands for locking and unlocking snapshots."""

from __future__ import annotations

import click

from envforge.snapshot_lock import (
    lock_snapshot,
    unlock_snapshot,
    is_locked,
    list_locked,
)

DEFAULT_DIR = click.get_app_dir("envforge")


@click.group("lock")
def lock_cmd() -> None:
    """Manage snapshot locks."""


@lock_cmd.command("set")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=DEFAULT_DIR, show_default=True)
def set_lock_cmd(name: str, snapshot_dir: str) -> None:
    """Lock a snapshot to prevent modification or deletion."""
    try:
        lock_snapshot(name, snapshot_dir)
        click.echo(f"Snapshot '{name}' is now locked.")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))


@lock_cmd.command("remove")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=DEFAULT_DIR, show_default=True)
def remove_lock_cmd(name: str, snapshot_dir: str) -> None:
    """Unlock a snapshot."""
    removed = unlock_snapshot(name, snapshot_dir)
    if removed:
        click.echo(f"Snapshot '{name}' is now unlocked.")
    else:
        click.echo(f"Snapshot '{name}' was not locked.")


@lock_cmd.command("status")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=DEFAULT_DIR, show_default=True)
def status_cmd(name: str, snapshot_dir: str) -> None:
    """Show lock status for a snapshot."""
    locked = is_locked(name, snapshot_dir)
    state = "locked" if locked else "unlocked"
    click.echo(f"'{name}' is {state}.")


@lock_cmd.command("list")
@click.option("--dir", "snapshot_dir", default=DEFAULT_DIR, show_default=True)
def list_locks_cmd(snapshot_dir: str) -> None:
    """List all locked snapshots."""
    locked = list_locked(snapshot_dir)
    if not locked:
        click.echo("No snapshots are locked.")
    else:
        for name in locked:
            click.echo(name)
