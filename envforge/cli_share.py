"""CLI commands for snapshot sharing (export/import tokens)."""

from __future__ import annotations

import click

from envforge.snapshot_share import export_token, import_token, token_metadata, ShareError


@click.group("share")
def share_cmd() -> None:
    """Share snapshots via portable tokens."""


@share_cmd.command("export")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory.")
@click.option("--no-redact", is_flag=True, default=False, help="Include sensitive values (unsafe).")
def export_cmd(name: str, snapshot_dir: str | None, no_redact: bool) -> None:
    """Export a snapshot as a shareable token."""
    try:
        token = export_token(name, snapshot_dir=snapshot_dir, redact=not no_redact)
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{name}' not found.")
    click.echo(token)


@share_cmd.command("import")
@click.argument("token")
@click.option("--as", "target_name", default=None, help="Override snapshot name.")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory.")
def import_cmd(token: str, target_name: str | None, snapshot_dir: str | None) -> None:
    """Import a snapshot from a share token."""
    try:
        saved = import_token(token, target_name=target_name, snapshot_dir=snapshot_dir)
    except ShareError as exc:
        raise click.ClickException(str(exc))
    click.echo(f"Imported snapshot '{saved}'.")


@share_cmd.command("inspect")
@click.argument("token")
def inspect_cmd(token: str) -> None:
    """Show metadata encoded in a share token without importing it."""
    try:
        meta = token_metadata(token)
    except ShareError as exc:
        raise click.ClickException(str(exc))
    click.echo(f"Name       : {meta['name']}")
    click.echo(f"Exported at: {meta['exported_at']}")
    click.echo(f"Keys       : {meta['key_count']}")
    click.echo(f"Version    : {meta['version']}")
