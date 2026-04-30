"""CLI commands for snapshot labels."""
from __future__ import annotations

import click

from envforge.snapshot_labels import (
    LabelError,
    find_by_label,
    get_labels,
    remove_label,
    set_label,
)


@click.group("labels")
def labels_cmd() -> None:
    """Manage key-value labels on snapshots."""


@labels_cmd.command("set")
@click.argument("name")
@click.argument("key")
@click.argument("value")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def set_label_cmd(name: str, key: str, value: str, snapshot_dir: str) -> None:
    """Attach KEY=VALUE label to snapshot NAME."""
    try:
        set_label(snapshot_dir, name, key, value)
        click.echo(f"Label '{key}={value}' set on '{name}'.")
    except LabelError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@labels_cmd.command("remove")
@click.argument("name")
@click.argument("key")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def remove_label_cmd(name: str, key: str, snapshot_dir: str) -> None:
    """Remove a label KEY from snapshot NAME."""
    removed = remove_label(snapshot_dir, name, key)
    if removed:
        click.echo(f"Label '{key}' removed from '{name}'.")
    else:
        click.echo(f"Label '{key}' not found on '{name}'.")


@labels_cmd.command("show")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def show_labels_cmd(name: str, snapshot_dir: str) -> None:
    """Show all labels for snapshot NAME."""
    labels = get_labels(snapshot_dir, name)
    if not labels:
        click.echo(f"No labels on '{name}'.")
        return
    for k, v in sorted(labels.items()):
        click.echo(f"  {k}={v}")


@labels_cmd.command("find")
@click.argument("key")
@click.option("--value", default=None, help="Filter by label value.")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def find_by_label_cmd(key: str, value: str | None, snapshot_dir: str) -> None:
    """Find snapshots that have a given label KEY."""
    results = find_by_label(snapshot_dir, key, value)
    if not results:
        click.echo("No snapshots found.")
        return
    for snap in results:
        click.echo(snap)
