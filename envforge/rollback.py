"""Rollback support: restore a previous snapshot version from history."""

from __future__ import annotations

from typing import Optional

from envforge.history import get_history, record_event
from envforge.snapshot import load_snapshot, save_snapshot


def get_rollback_candidates(name: str, snapshot_dir: str) -> list[dict]:
    """Return history events for a snapshot that can be rolled back to."""
    history = get_history(snapshot_dir)
    return [
        entry
        for entry in history
        if entry.get("snapshot") == name and "vars" in entry
    ]


def rollback_snapshot(
    name: str,
    snapshot_dir: str,
    steps: int = 1,
) -> dict:
    """Restore snapshot `name` to a previous state.

    Args:
        name: snapshot name to roll back.
        snapshot_dir: base directory for snapshots.
        steps: how many history entries to go back (default 1).

    Returns:
        The restored vars dict.

    Raises:
        ValueError: if not enough history exists.
    """
    candidates = get_rollback_candidates(name, snapshot_dir)
    if len(candidates) < steps:
        raise ValueError(
            f"Not enough history to roll back {steps} step(s) for '{name}'. "
            f"Only {len(candidates)} rollback point(s) available."
        )

    target = candidates[-steps]
    vars_to_restore: dict = target["vars"]

    # Save current state to history before overwriting
    try:
        current = load_snapshot(name, snapshot_dir)
        record_event(snapshot_dir, name, "pre_rollback", vars=current)
    except FileNotFoundError:
        pass

    save_snapshot(name, vars_to_restore, snapshot_dir)
    record_event(snapshot_dir, name, "rollback", steps=steps)
    return vars_to_restore
