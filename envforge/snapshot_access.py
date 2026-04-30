"""Track and query last-access times for snapshots."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envforge.snapshot import get_snapshot_path, load_snapshot


class AccessError(Exception):
    pass


def _access_path(snapshot_dir: str) -> Path:
    return Path(snapshot_dir) / ".access_log.json"


def _load_access(snapshot_dir: str) -> dict:
    p = _access_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_access(snapshot_dir: str, data: dict) -> None:
    _access_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def record_access(name: str, snapshot_dir: str) -> datetime:
    """Record that *name* was accessed right now; returns the timestamp."""
    snap_path = get_snapshot_path(name, snapshot_dir)
    if not snap_path.exists():
        raise AccessError(f"Snapshot '{name}' does not exist.")
    data = _load_access(snapshot_dir)
    now = datetime.now(timezone.utc)
    data[name] = now.isoformat()
    _save_access(snapshot_dir, data)
    return now


def get_last_access(name: str, snapshot_dir: str) -> Optional[datetime]:
    """Return the last-access datetime for *name*, or None if never accessed."""
    data = _load_access(snapshot_dir)
    raw = data.get(name)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def list_access_log(snapshot_dir: str) -> list[dict]:
    """Return all access records sorted newest-first."""
    data = _load_access(snapshot_dir)
    records = [
        {"name": k, "last_access": datetime.fromisoformat(v)}
        for k, v in data.items()
    ]
    records.sort(key=lambda r: r["last_access"], reverse=True)
    return records


def clear_access_log(snapshot_dir: str) -> None:
    """Remove the entire access log."""
    p = _access_path(snapshot_dir)
    if p.exists():
        p.unlink()
