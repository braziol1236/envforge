"""CLI commands for snapshot groups."""

from __future__ import annotations

import click

from envforge.snapshot_group import (
    add_to_group,
    delete_group,
    get_group_members,
    list_groups,
    remove_from_group,
)


@click.group("group")
def group_cmd() -> None:
    """Organise snapshots into named groups."""


@group_cmd.command("add")
@click.argument("group")
@click.argument("snapshot")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def add_cmd(group: str, snapshot: str, snapshot_dir: str) -> None:
    """Add SNAPSHOT to GROUP."""
    try:
        add_to_group(group, snapshot, snapshot_dir)
        click.echo(f"Added '{snapshot}' to group '{group}'.")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))


@group_cmd.command("remove")
@click.argument("group")
@click.argument("snapshot")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def remove_cmd(group: str, snapshot: str, snapshot_dir: str) -> None:
    """Remove SNAPSHOT from GROUP."""
    removed = remove_from_group(group, snapshot, snapshot_dir)
    if removed:
        click.echo(f"Removed '{snapshot}' from group '{group}'.")
    else:
        click.echo(f"'{snapshot}' was not in group '{group}'.")


@group_cmd.command("list")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def list_cmd(snapshot_dir: str) -> None:
    """List all groups and their members."""
    groups = list_groups(snapshot_dir)
    if not groups:
        click.echo("No groups defined.")
        return
    for name, members in groups.items():
        click.echo(f"{name}: {', '.join(members)}")


@group_cmd.command("show")
@click.argument("group")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def show_cmd(group: str, snapshot_dir: str) -> None:
    """Show members of GROUP."""
    members = get_group_members(group, snapshot_dir)
    if not members:
        click.echo(f"Group '{group}' is empty or does not exist.")
        return
    for m in members:
        click.echo(m)


@group_cmd.command("delete")
@click.argument("group")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def delete_cmd(group: str, snapshot_dir: str) -> None:
    """Delete an entire GROUP."""
    deleted = delete_group(group, snapshot_dir)
    if deleted:
        click.echo(f"Deleted group '{group}'.")
    else:
        click.echo(f"Group '{group}' not found.")
