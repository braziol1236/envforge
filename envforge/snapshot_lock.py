"""Lock/unlock snapshots to prevent accidental modification or deletion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from envforge.snapshot import get_snapshot_path


def _locks_path(snapshot_dir: str) -> Path:
    return Path(snapshot_dir) / ".locks.json"


def _load_locks(snapshot_dir: str) -> List[str]:
    p = _locks_path(snapshot_dir)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_locks(snapshot_dir: str, locks: List[str]) -> None:
    _locks_path(snapshot_dir).write_text(json.dumps(sorted(set(locks)), indent=2))


def lock_snapshot(name: str, snapshot_dir: str) -> None:
    """Mark a snapshot as locked."""
    snap_path = get_snapshot_path(name, snapshot_dir)
    if not snap_path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' does not exist.")
    locks = _load_locks(snapshot_dir)
    if name not in locks:
        locks.append(name)
        _save_locks(snapshot_dir, locks)


def unlock_snapshot(name: str, snapshot_dir: str) -> bool:
    """Remove lock from a snapshot. Returns True if it was locked."""
    locks = _load_locks(snapshot_dir)
    if name in locks:
        locks.remove(name)
        _save_locks(snapshot_dir, locks)
        return True
    return False


def is_locked(name: str, snapshot_dir: str) -> bool:
    """Return True if the snapshot is currently locked."""
    return name in _load_locks(snapshot_dir)


def list_locked(snapshot_dir: str) -> List[str]:
    """Return all locked snapshot names."""
    return _load_locks(snapshot_dir)


def assert_unlocked(name: str, snapshot_dir: str) -> None:
    """Raise RuntimeError if the snapshot is locked."""
    if is_locked(name, snapshot_dir):
        raise RuntimeError(
            f"Snapshot '{name}' is locked. Unlock it first with `envforge lock remove {name}`."
        )
