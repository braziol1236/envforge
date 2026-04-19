"""CLI commands for comparing snapshots."""
import os
import click
from envforge.compare import compare_two, compare_with_env, format_diff


@click.group("compare")
def compare_cmd():
    """Compare snapshots or snapshot vs current env."""
    pass


@compare_cmd.command("snapshots")
@click.argument("name_a")
@click.argument("name_b")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory.")
@click.option("--verbose", "-v", is_flag=True, default=False)
def compare_snapshots_cmd(name_a: str, name_b: str, snapshot_dir, verbose: bool):
    """Compare two named snapshots."""
    try:
        diff = compare_two(name_a, name_b, snapshot_dir=snapshot_dir)
        click.echo(format_diff(diff, verbose=verbose))
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@compare_cmd.command("env")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory.")
@click.option("--verbose", "-v", is_flag=True, default=False)
def compare_env_cmd(name: str, snapshot_dir, verbose: bool):
    """Compare a snapshot against the current environment."""
    try:
        diff = compare_with_env(name, snapshot_dir=snapshot_dir)
        click.echo(format_diff(diff, verbose=verbose))
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
