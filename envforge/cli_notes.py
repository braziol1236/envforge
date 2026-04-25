"""CLI commands for snapshot notes."""

from __future__ import annotations

import click

from envforge.snapshot_notes import set_note, get_note, delete_note, list_notes


@click.group("notes")
def notes_cmd() -> None:
    """Manage notes attached to snapshots."""


@notes_cmd.command("set")
@click.argument("name")
@click.argument("note")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def set_note_cmd(name: str, note: str, snapshot_dir: str) -> None:
    """Attach NOTE to snapshot NAME."""
    try:
        set_note(name, note, snapshot_dir)
        click.echo(f"Note set for '{name}'.")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))


@notes_cmd.command("show")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def show_note_cmd(name: str, snapshot_dir: str) -> None:
    """Show the note for snapshot NAME."""
    note = get_note(name, snapshot_dir)
    if note is None:
        click.echo(f"No note for '{name}'.")
    else:
        click.echo(note)


@notes_cmd.command("delete")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def delete_note_cmd(name: str, snapshot_dir: str) -> None:
    """Remove the note for snapshot NAME."""
    removed = delete_note(name, snapshot_dir)
    if removed:
        click.echo(f"Note removed for '{name}'.")
    else:
        click.echo(f"No note found for '{name}'.")


@notes_cmd.command("list")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def list_notes_cmd(snapshot_dir: str) -> None:
    """List all snapshot notes."""
    notes = list_notes(snapshot_dir)
    if not notes:
        click.echo("No notes recorded.")
        return
    for snap_name, note in sorted(notes.items()):
        click.echo(f"{snap_name}: {note}")
