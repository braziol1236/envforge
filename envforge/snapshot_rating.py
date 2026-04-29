"""Rate snapshots with a 1-5 star score and optional comment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envforge.snapshot import get_snapshot_path


class RatingError(Exception):
    pass


def _ratings_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "_ratings.json"


def _load_ratings(snapshot_dir: Path) -> dict:
    p = _ratings_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ratings(snapshot_dir: Path, data: dict) -> None:
    _ratings_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def set_rating(
    name: str,
    stars: int,
    comment: Optional[str] = None,
    snapshot_dir: Optional[Path] = None,
) -> dict:
    """Rate a snapshot 1-5 stars with an optional comment."""
    if not 1 <= stars <= 5:
        raise RatingError(f"Stars must be between 1 and 5, got {stars}")

    snap_path = get_snapshot_path(name, snapshot_dir)
    if not snap_path.exists():
        raise RatingError(f"Snapshot '{name}' does not exist")

    ratings = _load_ratings(snap_path.parent)
    entry = {"stars": stars}
    if comment is not None:
        entry["comment"] = comment
    ratings[name] = entry
    _save_ratings(snap_path.parent, ratings)
    return entry


def get_rating(name: str, snapshot_dir: Optional[Path] = None) -> Optional[dict]:
    """Return rating entry for a snapshot, or None if not rated."""
    snap_path = get_snapshot_path(name, snapshot_dir)
    ratings = _load_ratings(snap_path.parent)
    return ratings.get(name)


def remove_rating(name: str, snapshot_dir: Optional[Path] = None) -> bool:
    """Remove a rating. Returns True if it existed."""
    snap_path = get_snapshot_path(name, snapshot_dir)
    ratings = _load_ratings(snap_path.parent)
    if name not in ratings:
        return False
    del ratings[name]
    _save_ratings(snap_path.parent, ratings)
    return True


def list_ratings(snapshot_dir: Optional[Path] = None) -> dict:
    """Return all ratings keyed by snapshot name."""
    from envforge.snapshot import list_snapshots
    snaps = list_snapshots(snapshot_dir)
    if not snaps:
        return {}
    base = get_snapshot_path(snaps[0]["name"], snapshot_dir).parent
    return _load_ratings(base)
