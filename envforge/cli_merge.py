"""CLI commands for merging snapshots."""
import os
import click
from envforge.merge import merge_snapshots, merge_with_env


@click.group("merge")
def merge_cmd():
    """Merge snapshots together."""
    pass


@merge_cmd.command("snapshots")
@click.argument("base")
@click.argument("overlay")
@click.argument("output")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite output if exists")
def merge_snapshots_cmd(base, overlay, output, snapshot_dir, overwrite):
    """Merge OVERLAY snapshot on top of BASE, saving as OUTPUT."""
    try:
        result = merge_snapshots(base, overlay, output, snapshot_dir=snapshot_dir, overwrite=overwrite)
        count = len(result["env"])
        click.echo(f"Merged '{base}' + '{overlay}' -> '{output}' ({count} keys)")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@merge_cmd.command("with-env")
@click.argument("base")
@click.argument("output")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory")
@click.option("--prefix", default=None, help="Only include env vars with this prefix")
def merge_with_env_cmd(base, output, snapshot_dir, prefix):
    """Merge BASE snapshot with current environment variables, saving as OUTPUT."""
    env = dict(os.environ)
    if prefix:
        env = {k: v for k, v in env.items() if k.startswith(prefix)}
    try:
        result = merge_with_env(base, output, env, snapshot_dir=snapshot_dir)
        count = len(result["env"])
        click.echo(f"Merged '{base}' + env -> '{output}' ({count} keys)")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
