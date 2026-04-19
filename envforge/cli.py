"""CLI entry point for envforge using Click."""

import time

import click

from envforge.snapshot import (
    capture_env,
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)


@click.group()
def cli():
    """envforge — snapshot and restore local environment variables."""


@cli.command("save")
@click.argument("name")
@click.option("-d", "--description", default="", help="Optional description.")
@click.option("-k", "--keys", multiple=True, help="Specific keys to capture.")
def save_cmd(name, description, keys):
    """Save current environment as a snapshot."""
    env = capture_env(list(keys) if keys else None)
    path = save_snapshot(name, env, description)
    click.echo(f"✓ Saved snapshot '{name}' with {len(env)} variables → {path}")


@cli.command("list")
def list_cmd():
    """List all saved snapshots."""
    snapshots = list_snapshots()
    if not snapshots:
        click.echo("No snapshots found.")
        return
    for s in snapshots:
        ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(s["created_at"]))
        desc = f" — {s['description']}" if s["description"] else ""
        click.echo(f"  {s['name']:20s} {ts}  ({s['var_count']} vars){desc}")


@cli.command("show")
@click.argument("name")
def show_cmd(name):
    """Show variables stored in a snapshot."""
    try:
        snap = load_snapshot(name)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    click.echo(f"Snapshot: {snap['name']}")
    if snap.get("description"):
        click.echo(f"Description: {snap['description']}")
    click.echo("Variables:")
    for k, v in sorted(snap["env"].items()):
        click.echo(f"  {k}={v}")


@cli.command("delete")
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to delete this snapshot?")
def delete_cmd(name):
    """Delete a snapshot."""
    if delete_snapshot(name):
        click.echo(f"✓ Deleted snapshot '{name}'.")
    else:
        raise click.ClickException(f"Snapshot '{name}' not found.")


if __name__ == "__main__":
    cli()
