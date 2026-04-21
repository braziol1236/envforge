"""CLI commands for snapshot aliasing."""
from __future__ import annotations

import click

from envforge.alias import set_alias, remove_alias, resolve_alias, list_aliases


@click.group("alias")
def alias_cmd() -> None:
    """Manage snapshot aliases."""


@alias_cmd.command("set")
@click.argument("alias")
@click.argument("snapshot")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def set_alias_cmd(alias: str, snapshot: str, snapshot_dir: str) -> None:
    """Create or update ALIAS pointing to SNAPSHOT."""
    try:
        set_alias(alias, snapshot, snapshot_dir)
        click.echo(f"Alias '{alias}' -> '{snapshot}' saved.")
    except FileNotFoundError:
        click.echo(f"Error: snapshot '{snapshot}' not found.", err=True)
        raise SystemExit(1)


@alias_cmd.command("remove")
@click.argument("alias")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def remove_alias_cmd(alias: str, snapshot_dir: str) -> None:
    """Remove ALIAS."""
    removed = remove_alias(alias, snapshot_dir)
    if removed:
        click.echo(f"Alias '{alias}' removed.")
    else:
        click.echo(f"Alias '{alias}' not found.", err=True)
        raise SystemExit(1)


@alias_cmd.command("show")
@click.argument("alias")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def show_alias_cmd(alias: str, snapshot_dir: str) -> None:
    """Show what snapshot ALIAS points to."""
    target = resolve_alias(alias, snapshot_dir)
    if target is None:
        click.echo(f"Alias '{alias}' not found.", err=True)
        raise SystemExit(1)
    click.echo(target)


@alias_cmd.command("list")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def list_aliases_cmd(snapshot_dir: str) -> None:
    """List all aliases."""
    aliases = list_aliases(snapshot_dir)
    if not aliases:
        click.echo("No aliases defined.")
        return
    for alias, target in sorted(aliases.items()):
        click.echo(f"{alias:20s} -> {target}")
