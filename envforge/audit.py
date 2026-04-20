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
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


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


def get_audit_summary(snapshot_dir: str) -> Dict[str, Dict[str, int]]:
    """Return a summary of action counts per snapshot.

    Returns a dict mapping snapshot name to a dict of action -> count.
    Useful for quickly seeing how many times each snapshot was saved,
    loaded, deleted, etc.
    """
    entries = _load_audit(snapshot_dir)
    summary: Dict[str, Dict[str, int]] = {}
    for entry in entries:
        name = entry.get("snapshot", "unknown")
        action = entry.get("action", "unknown")
        summary.setdefault(name, {})
        summary[name][action] = summary[name].get(action, 0) + 1
    return summary


def clear_audit_log(snapshot_dir: str) -> None:
    path = _audit_path(snapshot_dir)
    if path.exists():
        path.unlink()
