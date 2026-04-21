"""Scheduled auto-snapshot support: define cron-like rules per project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envforge.snapshot import get_snapshot_path


def _schedule_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "_schedules.json"


def _load_schedules(snapshot_dir: Path) -> dict[str, Any]:
    p = _schedule_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_schedules(snapshot_dir: Path, data: dict[str, Any]) -> None:
    _schedule_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def set_schedule(snapshot_dir: Path, name: str, cron: str, label: str = "") -> None:
    """Attach a cron expression to a named snapshot slot.

    Raises FileNotFoundError if the snapshot does not exist.
    Raises ValueError if *cron* is an empty string.
    """
    if not cron.strip():
        raise ValueError("cron expression must not be empty.")
    snap_path = get_snapshot_path(snapshot_dir, name)
    if not snap_path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found.")
    schedules = _load_schedules(snapshot_dir)
    schedules[name] = {"cron": cron, "label": label}
    _save_schedules(snapshot_dir, schedules)


def remove_schedule(snapshot_dir: Path, name: str) -> None:
    """Remove the schedule for a snapshot slot (no-op if absent)."""
    schedules = _load_schedules(snapshot_dir)
    schedules.pop(name, None)
    _save_schedules(snapshot_dir, schedules)


def get_schedule(snapshot_dir: Path, name: str) -> dict[str, str] | None:
    """Return the schedule entry for *name*, or None if not set."""
    return _load_schedules(snapshot_dir).get(name)


def list_schedules(snapshot_dir: Path) -> dict[str, Any]:
    """Return all scheduled snapshot entries."""
    return _load_schedules(snapshot_dir)
