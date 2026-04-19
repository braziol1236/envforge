"""Audit log for envforge — tracks who saved/loaded/deleted snapshots."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any


def _audit_path(snapshot_dir: str) -> Path:
    return Path(snapshot_dir) / ".audit_log.json"


def _load_audit(snapshot_dir: str) -> List[Dict[str, Any]]:
    path = _audit_path(snapshot_dir)
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def _save_audit(snapshot_dir: str, entries: List[Dict[str, Any]]) -> None:
    path = _audit_path(snapshot_dir)
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)


def record_audit(
    snapshot_dir: str,
    action: str,
    snapshot_name: str,
    user: str | None = None,
    note: str | None = None,
) -> None:
    """Append an audit entry for the given action on a snapshot."""
    entries = _load_audit(snapshot_dir)
    entry: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "snapshot": snapshot_name,
        "user": user or os.environ.get("USER", "unknown"),
    }
    if note:
        entry["note"] = note
    entries.append(entry)
    _save_audit(snapshot_dir, entries)


def get_audit_log(
    snapshot_dir: str, snapshot_name: str | None = None
) -> List[Dict[str, Any]]:
    """Return audit entries, optionally filtered by snapshot name."""
    entries = _load_audit(snapshot_dir)
    if snapshot_name:
        entries = [e for e in entries if e["snapshot"] == snapshot_name]
    return entries


def clear_audit_log(snapshot_dir: str) -> None:
    path = _audit_path(snapshot_dir)
    if path.exists():
        path.unlink()
