"""Snapshot versioning — maintain numbered versions of a snapshot over time."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from envforge.snapshot import get_snapshot_path, load_snapshot, save_snapshot


class VersionError(Exception):
    pass


def _versions_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / ".versions.json"


def _load_versions(snapshot_dir: Path) -> dict[str, list[dict[str, Any]]]:
    p = _versions_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_versions(snapshot_dir: Path, data: dict[str, list[dict[str, Any]]]) -> None:
    _versions_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def commit_version(name: str, snapshot_dir: Path, message: str = "") -> int:
    """Save current snapshot state as a new version. Returns the version number."""
    snap = load_snapshot(name, snapshot_dir)
    versions = _load_versions(snapshot_dir)
    history = versions.setdefault(name, [])
    version_num = len(history) + 1
    history.append({
        "version": version_num,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": message,
        "vars": snap["vars"],
    })
    _save_versions(snapshot_dir, versions)
    return version_num


def list_versions(name: str, snapshot_dir: Path) -> list[dict[str, Any]]:
    """Return all committed versions for a snapshot, oldest first."""
    versions = _load_versions(snapshot_dir)
    return versions.get(name, [])


def get_version(name: str, version: int, snapshot_dir: Path) -> dict[str, Any]:
    """Return the vars dict for a specific version number."""
    for v in list_versions(name, snapshot_dir):
        if v["version"] == version:
            return v
    raise VersionError(f"Version {version} not found for snapshot '{name}'")


def restore_version(name: str, version: int, snapshot_dir: Path) -> None:
    """Overwrite the live snapshot with vars from a specific version."""
    v = get_version(name, version, snapshot_dir)
    save_snapshot(name, v["vars"], snapshot_dir)


def delete_versions(name: str, snapshot_dir: Path) -> int:
    """Remove all version history for a snapshot. Returns count removed."""
    versions = _load_versions(snapshot_dir)
    removed = len(versions.pop(name, []))
    _save_versions(snapshot_dir, versions)
    return removed
