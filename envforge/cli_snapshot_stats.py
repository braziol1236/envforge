"""CLI commands for snapshot statistics."""

import click
from . import snapshot_stats as stats_mod
from .snapshot import list_snapshots


@click.group("stats")
def stats_cmd():
    """View statistics about snapshots."""


@stats_cmd.command("show")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory.")
def show_stats_cmd(name: str, snapshot_dir: str):
    """Show statistics for a single snapshot."""
    try:
        result = stats_mod.compute_stats(name, snapshot_dir=snapshot_dir)
    except FileNotFoundError:
        click.echo(f"Snapshot '{name}' not found.", err=True)
        raise SystemExit(1)

    click.echo(stats_mod.format_stats(result))


@stats_cmd.command("all")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory.")
@click.option(
    "--sort",
    "sort_by",
    type=click.Choice(["name", "keys", "empty", "sensitive"], case_sensitive=False),
    default="name",
    show_default=True,
    help="Sort results by this field.",
)
@click.option("--reverse", is_flag=True, default=False, help="Reverse sort order.")
def all_stats_cmd(snapshot_dir: str, sort_by: str, reverse: bool):
    """Show statistics for all snapshots."""
    snapshots = list_snapshots(snapshot_dir=snapshot_dir)
    if not snapshots:
        click.echo("No snapshots found.")
        return

    results = stats_mod.compute_all_stats(snapshot_dir=snapshot_dir)

    sort_key_map = {
        "name": lambda s: s.name,
        "keys": lambda s: s.total_keys,
        "empty": lambda s: s.empty_values,
        "sensitive": lambda s: s.sensitive_keys,
    }
    results.sort(key=sort_key_map[sort_by.lower()], reverse=reverse)

    for i, result in enumerate(results):
        if i > 0:
            click.echo("")
        click.echo(stats_mod.format_stats(result))


@stats_cmd.command("summary")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory.")
def summary_cmd(snapshot_dir: str):
    """Print an aggregate summary across all snapshots."""
    results = stats_mod.compute_all_stats(snapshot_dir=snapshot_dir)
    if not results:
        click.echo("No snapshots found.")
        return

    total_snapshots = len(results)
    total_keys = sum(r.total_keys for r in results)
    total_empty = sum(r.empty_values for r in results)
    total_sensitive = sum(r.sensitive_keys for r in results)
    avg_keys = total_keys / total_snapshots if total_snapshots else 0

    largest = max(results, key=lambda r: r.total_keys)
    smallest = min(results, key=lambda r: r.total_keys)

    click.echo(f"Snapshots     : {total_snapshots}")
    click.echo(f"Total keys    : {total_keys}")
    click.echo(f"Avg keys      : {avg_keys:.1f}")
    click.echo(f"Empty values  : {total_empty}")
    click.echo(f"Sensitive keys: {total_sensitive}")
    click.echo(f"Largest       : {largest.name} ({largest.total_keys} keys)")
    click.echo(f"Smallest      : {smallest.name} ({smallest.total_keys} keys)")
