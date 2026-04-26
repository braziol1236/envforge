"""CLI commands for snapshot bookmarks."""

from __future__ import annotations

import click

from envforge.snapshot_bookmark import (
    list_bookmarks,
    remove_bookmark,
    resolve_bookmark,
    set_bookmark,
)


@click.group("bookmark")
def bookmark_cmd() -> None:
    """Manage quick-access bookmarks for snapshots."""


@bookmark_cmd.command("set")
@click.argument("name")
@click.argument("snapshot")
@click.option("--dir", "snapshot_dir", default=".snapshots", show_default=True)
def set_bookmark_cmd(name: str, snapshot: str, snapshot_dir: str) -> None:
    """Create or update bookmark NAME pointing to SNAPSHOT."""
    try:
        set_bookmark(name, snapshot, snapshot_dir)
        click.echo(f"Bookmark '{name}' -> '{snapshot}' saved.")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))


@bookmark_cmd.command("remove")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".snapshots", show_default=True)
def remove_bookmark_cmd(name: str, snapshot_dir: str) -> None:
    """Remove bookmark NAME."""
    removed = remove_bookmark(name, snapshot_dir)
    if removed:
        click.echo(f"Bookmark '{name}' removed.")
    else:
        click.echo(f"No bookmark named '{name}'.")


@bookmark_cmd.command("show")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".snapshots", show_default=True)
def show_bookmark_cmd(name: str, snapshot_dir: str) -> None:
    """Show which snapshot bookmark NAME resolves to."""
    target = resolve_bookmark(name, snapshot_dir)
    if target is None:
        raise click.ClickException(f"No bookmark named '{name}'.")
    click.echo(target)


@bookmark_cmd.command("list")
@click.option("--dir", "snapshot_dir", default=".snapshots", show_default=True)
def list_bookmarks_cmd(snapshot_dir: str) -> None:
    """List all bookmarks."""
    entries = list_bookmarks(snapshot_dir)
    if not entries:
        click.echo("No bookmarks defined.")
        return
    for entry in entries:
        click.echo(f"{entry['name']:20s}  ->  {entry['snapshot']}")
