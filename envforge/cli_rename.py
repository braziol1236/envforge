"""CLI commands for renaming snapshots."""

import click
from pathlib import Path
from envforge.snapshot_rename import rename_snapshot, RenameError


@click.group("rename")
def rename_cmd():
    """Rename a snapshot."""


@rename_cmd.command("run")
@click.argument("old_name")
@click.argument("new_name")
@click.option(
    "--dir",
    "snapshot_dir",
    default=None,
    help="Snapshot storage directory.",
    type=click.Path(),
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite target if it already exists.",
)
@click.option(
    "--no-migrate-aliases",
    is_flag=True,
    default=False,
    help="Skip migrating aliases that reference the old name.",
)
def run_cmd(old_name, new_name, snapshot_dir, overwrite, no_migrate_aliases):
    """Rename OLD_NAME to NEW_NAME."""
    from envforge.snapshot import get_snapshot_path

    if snapshot_dir is None:
        base = Path.home() / ".envforge"
    else:
        base = Path(snapshot_dir)

    try:
        rename_snapshot(
            old_name,
            new_name,
            base,
            migrate_aliases=not no_migrate_aliases,
            overwrite=overwrite,
        )
        click.echo(f"Renamed '{old_name}' → '{new_name}'.")
    except RenameError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
