"""TTL (time-to-live) support for snapshots — expire old snapshots automatically."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from envforge.snapshot import get_snapshot_path, load_snapshot


def _ttl_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "_ttls.json"


def _load_ttls(snapshot_dir: Path) -> dict:
    p = _ttl_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ttls(snapshot_dir: Path, data: dict) -> None:
    _ttl_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def set_ttl(name: str, seconds: int, snapshot_dir: Path) -> datetime:
    """Attach a TTL to a snapshot. Raises FileNotFoundError if snapshot missing."""
    get_snapshot_path(name, snapshot_dir)  # validates existence
    load_snapshot(name, snapshot_dir)      # double-check readable
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    ttls = _load_ttls(snapshot_dir)
    ttls[name] = expires_at.isoformat()
    _save_ttls(snapshot_dir, ttls)
    return expires_at


def remove_ttl(name: str, snapshot_dir: Path) -> bool:
    """Remove TTL for a snapshot. Returns True if one existed."""
    ttls = _load_ttls(snapshot_dir)
    if name in ttls:
        del ttls[name]
        _save_ttls(snapshot_dir, ttls)
        return True
    return False


def get_ttl(name: str, snapshot_dir: Path) -> Optional[datetime]:
    """Return the expiry datetime for a snapshot, or None if no TTL set."""
    ttls = _load_ttls(snapshot_dir)
    if name not in ttls:
        return None
    return datetime.fromisoformat(ttls[name])


def is_expired(name: str, snapshot_dir: Path) -> bool:
    """Return True if the snapshot has a TTL that has passed."""
    expiry = get_ttl(name, snapshot_dir)
    if expiry is None:
        return False
    return datetime.now(timezone.utc) >= expiry


def list_expired(snapshot_dir: Path) -> list[str]:
    """Return names of all snapshots whose TTL has expired."""
    ttls = _load_ttls(snapshot_dir)
    now = datetime.now(timezone.utc)
    return [
        name
        for name, iso in ttls.items()
        if now >= datetime.fromisoformat(iso)
    ]


def purge_expired(snapshot_dir: Path) -> list[str]:
    """Delete all expired snapshots and remove their TTL entries. Returns purged names."""
    from envforge.snapshot import delete_snapshot

    expired = list_expired(snapshot_dir)
    ttls = _load_ttls(snapshot_dir)
    for name in expired:
        try:
            delete_snapshot(name, snapshot_dir)
        except FileNotFoundError:
            pass
        ttls.pop(name, None)
    _save_ttls(snapshot_dir, ttls)
    return expired
