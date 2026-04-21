"""CLI commands for resolving variable references inside snapshots."""

from __future__ import annotations

import os

import click

from envforge.resolve import resolve_snapshot, resolve_and_save
from envforge.snapshot import load_snapshot


@click.group("resolve")
def resolve_cmd() -> None:
    """Resolve $VAR / ${VAR} references within a snapshot."""


@resolve_cmd.command("show")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory")
@click.option("--use-os-env", is_flag=True, default=False, help="Fall back to OS env for missing refs")
def show_resolved_cmd(name: str, snapshot_dir: str | None, use_os_env: bool) -> None:
    """Print the snapshot with all variable references expanded."""
    try:
        data = load_snapshot(name, snapshot_dir=snapshot_dir)
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{name}' not found.")

    extra = dict(os.environ) if use_os_env else None
    try:
        resolved = resolve_snapshot(data["vars"], extra_env=extra)
    except ValueError as exc:
        raise click.ClickException(str(exc))

    for k, v in sorted(resolved.items()):
        click.echo(f"{k}={v}")


@resolve_cmd.command("save")
@click.argument("source")
@click.argument("dest")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory")
@click.option("--use-os-env", is_flag=True, default=False, help="Fall back to OS env for missing refs")
def save_resolved_cmd(source: str, dest: str, snapshot_dir: str | None, use_os_env: bool) -> None:
    """Resolve references in SOURCE and save the result as DEST."""
    extra = dict(os.environ) if use_os_env else None
    try:
        resolve_and_save(source, dest, snapshot_dir=snapshot_dir, extra_env=extra)
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{source}' not found.")
    except ValueError as exc:
        raise click.ClickException(str(exc))

    click.echo(f"Resolved snapshot saved as '{dest}'.")
