"""CLI commands for snapshot ratings."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import click

from envforge.snapshot_rating import (
    RatingError,
    get_rating,
    list_ratings,
    remove_rating,
    set_rating,
)


@click.group("rating")
def rating_cmd():
    """Rate snapshots with 1-5 stars."""


@rating_cmd.command("set")
@click.argument("name")
@click.argument("stars", type=int)
@click.option("--comment", "-c", default=None, help="Optional comment")
@click.option("--dir", "snapshot_dir", default=None, type=click.Path())
def set_rating_cmd(name: str, stars: int, comment: Optional[str], snapshot_dir: Optional[str]):
    """Set a star rating (1-5) for a snapshot."""
    d = Path(snapshot_dir) if snapshot_dir else None
    try:
        entry = set_rating(name, stars, comment=comment, snapshot_dir=d)
        msg = f"Rated '{name}': {'★' * entry['stars']}{'☆' * (5 - entry['stars'])}"
        if entry.get("comment"):
            msg += f"  — {entry['comment']}"
        click.echo(msg)
    except RatingError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@rating_cmd.command("show")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=None, type=click.Path())
def show_rating_cmd(name: str, snapshot_dir: Optional[str]):
    """Show the rating for a snapshot."""
    d = Path(snapshot_dir) if snapshot_dir else None
    entry = get_rating(name, snapshot_dir=d)
    if entry is None:
        click.echo(f"No rating for '{name}'")
    else:
        stars = entry["stars"]
        click.echo(f"{name}: {'★' * stars}{'☆' * (5 - stars)} ({stars}/5)")
        if entry.get("comment"):
            click.echo(f"  Comment: {entry['comment']}")


@rating_cmd.command("remove")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=None, type=click.Path())
def remove_rating_cmd(name: str, snapshot_dir: Optional[str]):
    """Remove the rating from a snapshot."""
    d = Path(snapshot_dir) if snapshot_dir else None
    removed = remove_rating(name, snapshot_dir=d)
    if removed:
        click.echo(f"Rating removed for '{name}'")
    else:
        click.echo(f"No rating found for '{name}'")


@rating_cmd.command("list")
@click.option("--dir", "snapshot_dir", default=None, type=click.Path())
def list_ratings_cmd(snapshot_dir: Optional[str]):
    """List all rated snapshots."""
    d = Path(snapshot_dir) if snapshot_dir else None
    ratings = list_ratings(snapshot_dir=d)
    if not ratings:
        click.echo("No ratings recorded.")
        return
    for name, entry in sorted(ratings.items()):
        stars = entry["stars"]
        line = f"{name}: {'★' * stars}{'☆' * (5 - stars)}"
        if entry.get("comment"):
            line += f"  — {entry['comment']}"
        click.echo(line)
