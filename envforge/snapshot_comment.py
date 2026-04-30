"""Inline per-key comments for snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envforge.snapshot import get_snapshot_path, load_snapshot


class CommentError(Exception):
    pass


def _comments_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "_comments.json"


def _load_comments(snapshot_dir: Path) -> dict:
    p = _comments_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_comments(snapshot_dir: Path, data: dict) -> None:
    _comments_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def set_comment(name: str, key: str, comment: str, snapshot_dir: Path) -> None:
    """Attach a comment to a specific key in a snapshot."""
    snap = load_snapshot(name, snapshot_dir)
    if key not in snap["vars"]:
        raise CommentError(f"Key '{key}' not found in snapshot '{name}'")
    all_comments = _load_comments(snapshot_dir)
    all_comments.setdefault(name, {})[key] = comment
    _save_comments(snapshot_dir, all_comments)


def get_comment(name: str, key: str, snapshot_dir: Path) -> Optional[str]:
    """Return the comment for a key, or None if not set."""
    return _load_comments(snapshot_dir).get(name, {}).get(key)


def delete_comment(name: str, key: str, snapshot_dir: Path) -> bool:
    """Remove a comment. Returns True if it existed."""
    all_comments = _load_comments(snapshot_dir)
    if key in all_comments.get(name, {}):
        del all_comments[name][key]
        if not all_comments[name]:
            del all_comments[name]
        _save_comments(snapshot_dir, all_comments)
        return True
    return False


def get_all_comments(name: str, snapshot_dir: Path) -> dict[str, str]:
    """Return all key->comment mappings for a snapshot."""
    return dict(_load_comments(snapshot_dir).get(name, {}))
