"""CLI commands for searching snapshots."""

import click

from envforge.search import format_results, search_by_key, search_by_value


@click.group(name="search")
def search_cmd():
    """Search snapshots by key or value."""


@search_cmd.command(name="key")
@click.argument("pattern")
@click.option(
    "--dir",
    "snapshot_dir",
    default=None,
    help="Custom snapshot directory.",
)
def search_key_cmd(pattern: str, snapshot_dir: str | None):
    """Find snapshots containing keys matching PATTERN (glob).

    Example: envforge search key 'AWS_*'
    """
    results = search_by_key(pattern, snapshot_dir=snapshot_dir)
    click.echo(format_results(results))


@search_cmd.command(name="value")
@click.argument("pattern")
@click.option(
    "--dir",
    "snapshot_dir",
    default=None,
    help="Custom snapshot directory.",
)
def search_value_cmd(pattern: str, snapshot_dir: str | None):
    """Find snapshots whose values match PATTERN (regex).

    Example: envforge search value 'prod'
    """
    results = search_by_value(pattern, snapshot_dir=snapshot_dir)
    click.echo(format_results(results))
