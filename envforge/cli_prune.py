"""CLI commands for pruning snapshots."""
from __future__ import annotations

import click
from datetime import datetime, timezone

from envforge.snapshot_prune import (
    prune_expired,
    prune_oldest,
    prune_before,
    format_prune_report,
)


@click.group("prune")
def prune_cmd():
    """Prune snapshots by age, count, or TTL expiry."""


@prune_cmd.command("expired")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory.")
def prune_expired_cmd(snapshot_dir):
    """Delete all snapshots whose TTL has expired."""
    kwargs = {}
    if snapshot_dir:
        kwargs["snapshot_dir"] = snapshot_dir
    deleted = prune_expired(**kwargs)
    click.echo(format_prune_report(deleted))


@prune_cmd.command("oldest")
@click.argument("keep", type=int)
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory.")
def prune_oldest_cmd(keep, snapshot_dir):
    """Keep only the KEEP most-recent snapshots and delete the rest."""
    kwargs = {}
    if snapshot_dir:
        kwargs["snapshot_dir"] = snapshot_dir
    try:
        deleted = prune_oldest(keep=keep, **kwargs)
    except ValueError as exc:
        raise click.ClickException(str(exc))
    click.echo(format_prune_report(deleted))


@prune_cmd.command("before")
@click.argument("cutoff")  # ISO-8601 string
@click.option("--dry-run", is_flag=True, default=False)
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory.")
def prune_before_cmd(cutoff, dry_run, snapshot_dir):
    """Delete snapshots saved before CUTOFF (ISO-8601 datetime)."""
    try:
        cutoff_dt = datetime.fromisoformat(cutoff)
    except ValueError:
        raise click.ClickException(f"Invalid datetime: {cutoff!r}")
    if cutoff_dt.tzinfo is None:
        cutoff_dt = cutoff_dt.replace(tzinfo=timezone.utc)
    kwargs = {}
    if snapshot_dir:
        kwargs["snapshot_dir"] = snapshot_dir
    affected = prune_before(cutoff=cutoff_dt, dry_run=dry_run, **kwargs)
    click.echo(format_prune_report(affected, dry_run=dry_run))
