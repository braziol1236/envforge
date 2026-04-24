"""CLI commands for archiving and restoring snapshot bundles."""

from pathlib import Path

import click

from envforge.archive import archive_snapshots, restore_archive, list_archive_contents


@click.group("archive")
def archive_cmd():
    """Pack and unpack snapshot archives."""


@archive_cmd.command("pack")
@click.argument("names", nargs=-1, required=True)
@click.option("--output", "-o", required=True, help="Output .zip file path.")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot storage directory.")
def pack_cmd(names, output, snapshot_dir):
    """Pack one or more snapshots into a zip archive."""
    kwargs = {"snapshot_dir": Path(snapshot_dir)} if snapshot_dir else {}
    try:
        out = archive_snapshots(list(names), Path(output), **kwargs)
        click.echo(f"Archived {len(names)} snapshot(s) to {out}")
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@archive_cmd.command("unpack")
@click.argument("archive")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing snapshots.")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot storage directory.")
def unpack_cmd(archive, overwrite, snapshot_dir):
    """Restore snapshots from a zip archive."""
    kwargs = {"snapshot_dir": Path(snapshot_dir)} if snapshot_dir else {}
    try:
        restored = restore_archive(Path(archive), overwrite=overwrite, **kwargs)
        for name in restored:
            click.echo(f"Restored: {name}")
        click.echo(f"Total restored: {len(restored)}")
    except (FileNotFoundError, FileExistsError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@archive_cmd.command("list")
@click.argument("archive")
def list_cmd(archive):
    """List snapshots contained in an archive without extracting."""
    try:
        names = list_archive_contents(Path(archive))
        if not names:
            click.echo("Archive is empty.")
        else:
            for name in names:
                click.echo(name)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
