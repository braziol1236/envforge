"""CLI commands for snapshot pinning."""
import os
import click

from envforge.pin import pin_snapshot, unpin, list_pins, resolve_pin


DEFAULT_DIR = os.path.expanduser("~/.envforge/snapshots")


@click.group("pin")
def pin_cmd():
    """Manage snapshot pin aliases."""


@pin_cmd.command("set")
@click.argument("alias")
@click.argument("snapshot")
@click.option("--dir", "snapshot_dir", default=DEFAULT_DIR, hidden=True)
def set_pin_cmd(alias, snapshot, snapshot_dir):
    """Pin ALIAS to SNAPSHOT."""
    try:
        pin_snapshot(alias, snapshot, snapshot_dir)
        click.echo(f"Pinned '{alias}' -> '{snapshot}'")
    except FileNotFoundError:
        click.echo(f"Error: snapshot '{snapshot}' not found.", err=True)
        raise SystemExit(1)


@pin_cmd.command("remove")
@click.argument("alias")
@click.option("--dir", "snapshot_dir", default=DEFAULT_DIR, hidden=True)
def remove_pin_cmd(alias, snapshot_dir):
    """Remove pin ALIAS."""
    try:
        unpin(alias, snapshot_dir)
        click.echo(f"Removed pin '{alias}'")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@pin_cmd.command("list")
@click.option("--dir", "snapshot_dir", default=DEFAULT_DIR, hidden=True)
def list_pins_cmd(snapshot_dir):
    """List all pin aliases."""
    pins = list_pins(snapshot_dir)
    if not pins:
        click.echo("No pins defined.")
        return
    for alias, name in sorted(pins.items()):
        click.echo(f"  {alias} -> {name}")


@pin_cmd.command("show")
@click.argument("alias")
@click.option("--dir", "snapshot_dir", default=DEFAULT_DIR, hidden=True)
def show_pin_cmd(alias, snapshot_dir):
    """Show which snapshot ALIAS points to."""
    try:
        name = resolve_pin(alias, snapshot_dir)
        click.echo(name)
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
