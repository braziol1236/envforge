"""CLI commands for per-key snapshot comments."""

from __future__ import annotations

import click
from pathlib import Path

from envforge.snapshot_comment import (
    set_comment,
    get_comment,
    delete_comment,
    get_all_comments,
    CommentError,
)


@click.group("comment")
def comment_cmd():
    """Manage per-key comments on snapshots."""


@comment_cmd.command("set")
@click.argument("name")
@click.argument("key")
@click.argument("text")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def set_comment_cmd(name: str, key: str, text: str, snapshot_dir: str):
    """Attach TEXT as a comment on KEY in snapshot NAME."""
    try:
        set_comment(name, key, text, Path(snapshot_dir))
        click.echo(f"Comment set on '{key}' in snapshot '{name}'.")
    except CommentError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@comment_cmd.command("show")
@click.argument("name")
@click.argument("key")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def show_comment_cmd(name: str, key: str, snapshot_dir: str):
    """Show the comment for KEY in snapshot NAME."""
    comment = get_comment(name, key, Path(snapshot_dir))
    if comment is None:
        click.echo(f"No comment set for '{key}' in '{name}'.")
    else:
        click.echo(comment)


@comment_cmd.command("delete")
@click.argument("name")
@click.argument("key")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def delete_comment_cmd(name: str, key: str, snapshot_dir: str):
    """Remove the comment for KEY in snapshot NAME."""
    removed = delete_comment(name, key, Path(snapshot_dir))
    if removed:
        click.echo(f"Comment removed from '{key}' in '{name}'.")
    else:
        click.echo(f"No comment found for '{key}' in '{name}'.")


@comment_cmd.command("list")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def list_comments_cmd(name: str, snapshot_dir: str):
    """List all commented keys in snapshot NAME."""
    comments = get_all_comments(name, Path(snapshot_dir))
    if not comments:
        click.echo(f"No comments for snapshot '{name}'.")
        return
    for key, text in sorted(comments.items()):
        click.echo(f"  {key}: {text}")
