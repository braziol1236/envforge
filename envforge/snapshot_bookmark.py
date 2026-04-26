"""Bookmark management for snapshots — quick-access named shortcuts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envforge.snapshot import get_snapshot_path


def _bookmarks_path(snapshot_dir: str) -> Path:
    return Path(snapshot_dir) / ".bookmarks.json"


def _load_bookmarks(snapshot_dir: str) -> Dict[str, str]:
    p = _bookmarks_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_bookmarks(snapshot_dir: str, data: Dict[str, str]) -> None:
    _bookmarks_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def set_bookmark(name: str, snapshot_name: str, snapshot_dir: str) -> None:
    """Create or update a bookmark pointing to *snapshot_name*."""
    snap_path = get_snapshot_path(snapshot_name, snapshot_dir)
    if not snap_path.exists():
        raise FileNotFoundError(f"Snapshot '{snapshot_name}' does not exist.")
    bookmarks = _load_bookmarks(snapshot_dir)
    bookmarks[name] = snapshot_name
    _save_bookmarks(snapshot_dir, bookmarks)


def remove_bookmark(name: str, snapshot_dir: str) -> bool:
    """Remove a bookmark by *name*. Returns True if it existed."""
    bookmarks = _load_bookmarks(snapshot_dir)
    if name not in bookmarks:
        return False
    del bookmarks[name]
    _save_bookmarks(snapshot_dir, bookmarks)
    return True


def resolve_bookmark(name: str, snapshot_dir: str) -> Optional[str]:
    """Return the snapshot name a bookmark points to, or None."""
    return _load_bookmarks(snapshot_dir).get(name)


def list_bookmarks(snapshot_dir: str) -> List[Dict[str, str]]:
    """Return all bookmarks as a list of {name, snapshot} dicts."""
    return [
        {"name": k, "snapshot": v}
        for k, v in sorted(_load_bookmarks(snapshot_dir).items())
    ]
