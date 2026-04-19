"""Tag management for snapshots."""
import json
from pathlib import Path
from typing import List

from envforge.snapshot import get_snapshot_path, load_snapshot, save_snapshot


def add_tag(name: str, tag: str, snapshot_dir: Path = None) -> None:
    """Add a tag to an existing snapshot."""
    snapshot = load_snapshot(name, snapshot_dir)
    tags = snapshot.get("tags", [])
    if tag not in tags:
        tags.append(tag)
    snapshot["tags"] = tags
    save_snapshot(name, snapshot["vars"], snapshot_dir, extra={"tags": tags})


def remove_tag(name: str, tag: str, snapshot_dir: Path = None) -> None:
    """Remove a tag from a snapshot."""
    snapshot = load_snapshot(name, snapshot_dir)
    tags = snapshot.get("tags", [])
    tags = [t for t in tags if t != tag]
    snapshot["tags"] = tags
    save_snapshot(name, snapshot["vars"], snapshot_dir, extra={"tags": tags})


def list_by_tag(tag: str, snapshot_dir: Path = None) -> List[str]:
    """Return snapshot names that have the given tag."""
    from envforge.snapshot import list_snapshots
    snapshots = list_snapshots(snapshot_dir)
    result = []
    for s in snapshots:
        if tag in s.get("tags", []):
            result.append(s["name"])
    return result


def get_tags(name: str, snapshot_dir: Path = None) -> List[str]:
    """Get all tags for a snapshot."""
    snapshot = load_snapshot(name, snapshot_dir)
    return snapshot.get("tags", [])
