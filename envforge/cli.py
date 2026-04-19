"""CLI entry point for envforge."""

import os
import click
from envforge.snapshot import save_snapshot, load_snapshot, list_snapshots, delete_snapshot
from envforge.diff import diff_snapshots, diff_snapshot_with_env


@click.group()
def cli():
    """envforge — snapshot and restore local environment variables."""
    pass


@cli.command("save")
@click.argument("name")
@click.option("--project", default=None, help="Project tag for the snapshot.")
def save_cmd(name, project):
    """Save current environment as a named snapshot."""
    env_vars = dict(os.environ)
    save_snapshot(name, env_vars, project=project)
    click.echo(f"Snapshot '{name}' saved ({len(env_vars)} variables).")


@cli.command("list")
@click.option("--project", default=None, help="Filter by project tag.")
def list_cmd(project):
    """List all saved snapshots."""
    snapshots = list_snapshots(project=project)
    if not snapshots:
        click.echo("No snapshots found.")
        return
    for s in snapshots:
        tag = f"  [{s['project']}]" if s.get("project") else ""
        click.echo(f"  {s['name']}  ({s['created_at']}){tag}")


@cli.command("show")
@click.argument("name")
def show_cmd(name):
    """Show variables stored in a snapshot."""
    snap = load_snapshot(name)
    for key, val in sorted(snap["vars"].items()):
        click.echo(f"{key}={val}")


@cli.command("delete")
@click.argument("name")
@click.confirmation_option(prompt=f"Are you sure you want to delete this snapshot?")
def delete_cmd(name):
    """Delete a named snapshot."""
    delete_snapshot(name)
    click.echo(f"Snapshot '{name}' deleted.")


@cli.command("diff")
@click.argument("name_a")
@click.argument("name_b", required=False, default=None)
def diff_cmd(name_a, name_b):
    """Diff two snapshots, or a snapshot against the current environment."""
    snap_a = load_snapshot(name_a)
    if name_b:
        snap_b = load_snapshot(name_b)
        result = diff_snapshots(snap_a, snap_b)
        label = f"'{name_a}' vs '{name_b}'"
    else:
        result = diff_snapshot_with_env(snap_a)
        label = f"'{name_a}' vs current environment"

    click.echo(f"Diff {label}:")
    click.echo(result.summary())
