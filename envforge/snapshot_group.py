"""Snapshot grouping: organize snapshots into named groups."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envforge.snapshot import get_snapshot_path, load_snapshot


def _groups_path(snapshot_dir: str) -> Path:
    return Path(snapshot_dir) / "_groups.json"


def _load_groups(snapshot_dir: str) -> Dict[str, List[str]]:
    path = _groups_path(snapshot_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_groups(snapshot_dir: str, data: Dict[str, List[str]]) -> None:
    _groups_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def add_to_group(group: str, snapshot_name: str, snapshot_dir: str) -> None:
    """Add a snapshot to a group, raising if snapshot does not exist."""
    snap_path = get_snapshot_path(snapshot_name, snapshot_dir)
    if not snap_path.exists():
        raise FileNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    groups = _load_groups(snapshot_dir)
    members = groups.get(group, [])
    if snapshot_name not in members:
        members.append(snapshot_name)
    groups[group] = members
    _save_groups(snapshot_dir, groups)


def remove_from_group(group: str, snapshot_name: str, snapshot_dir: str) -> bool:
    """Remove a snapshot from a group. Returns True if it was present."""
    groups = _load_groups(snapshot_dir)
    members = groups.get(group, [])
    if snapshot_name not in members:
        return False
    members.remove(snapshot_name)
    if members:
        groups[group] = members
    else:
        del groups[group]
    _save_groups(snapshot_dir, groups)
    return True


def list_groups(snapshot_dir: str) -> Dict[str, List[str]]:
    """Return all groups and their member snapshot names."""
    return _load_groups(snapshot_dir)


def get_group_members(group: str, snapshot_dir: str) -> List[str]:
    """Return member names for a group, empty list if group missing."""
    return _load_groups(snapshot_dir).get(group, [])


def delete_group(group: str, snapshot_dir: str) -> bool:
    """Delete an entire group. Returns True if it existed."""
    groups = _load_groups(snapshot_dir)
    if group not in groups:
        return False
    del groups[group]
    _save_groups(snapshot_dir, groups)
    return True


def load_group_snapshots(group: str, snapshot_dir: str) -> Dict[str, dict]:
    """Load and return the env vars for every snapshot in the group."""
    members = get_group_members(group, snapshot_dir)
    return {name: load_snapshot(name, snapshot_dir)["vars"] for name in members}
