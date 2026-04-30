"""CLI commands for snapshot versioning."""

from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_version import (
    VersionError,
    commit_version,
    delete_versions,
    get_version,
    list_versions,
    restore_version,
)


@click.group("version")
def version_cmd() -> None:
    """Manage snapshot versions."""


@version_cmd.command("commit")
@click.argument("name")
@click.option("--message", "-m", default="", help="Short description of this version.")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def commit_cmd(name: str, message: str, snapshot_dir: str) -> None:
    """Commit the current state of NAME as a new version."""
    try:
        num = commit_version(name, Path(snapshot_dir), message)
        click.echo(f"Committed version {num} for '{name}'.")
    except FileNotFoundError:
        click.echo(f"Snapshot '{name}' not found.", err=True)
        raise SystemExit(1)


@version_cmd.command("list")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def list_cmd(name: str, snapshot_dir: str) -> None:
    """List all versions of NAME."""
    versions = list_versions(name, Path(snapshot_dir))
    if not versions:
        click.echo(f"No versions found for '{name}'.")
        return
    for v in versions:
        msg = f"  [{v['message']}]" if v["message"] else ""
        click.echo(f"  v{v['version']}  {v['timestamp']}{msg}")


@version_cmd.command("show")
@click.argument("name")
@click.argument("version", type=int)
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def show_cmd(name: str, version: int, snapshot_dir: str) -> None:
    """Show vars stored in a specific version."""
    try:
        v = get_version(name, version, Path(snapshot_dir))
    except VersionError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    for k, val in sorted(v["vars"].items()):
        click.echo(f"{k}={val}")


@version_cmd.command("restore")
@click.argument("name")
@click.argument("version", type=int)
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def restore_cmd(name: str, version: int, snapshot_dir: str) -> None:
    """Restore NAME to a previously committed version."""
    try:
        restore_version(name, version, Path(snapshot_dir))
        click.echo(f"Restored '{name}' to version {version}.")
    except VersionError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@version_cmd.command("drop")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def drop_cmd(name: str, snapshot_dir: str) -> None:
    """Delete all version history for NAME."""
    removed = delete_versions(name, Path(snapshot_dir))
    click.echo(f"Removed {removed} version(s) for '{name}'.")
