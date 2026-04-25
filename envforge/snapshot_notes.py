"""Attach and retrieve freeform notes for snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envforge.snapshot import get_snapshot_path


def _notes_path(snapshot_dir: str) -> Path:
    return Path(snapshot_dir) / "_notes.json"


def _load_notes(snapshot_dir: str) -> dict[str, str]:
    p = _notes_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_notes(snapshot_dir: str, notes: dict[str, str]) -> None:
    _notes_path(snapshot_dir).write_text(json.dumps(notes, indent=2))


def set_note(name: str, note: str, snapshot_dir: str) -> None:
    """Attach a note to a snapshot. Raises FileNotFoundError if snapshot missing."""
    snap_path = get_snapshot_path(name, snapshot_dir)
    if not snap_path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found.")
    notes = _load_notes(snapshot_dir)
    notes[name] = note
    _save_notes(snapshot_dir, notes)


def get_note(name: str, snapshot_dir: str) -> Optional[str]:
    """Return the note for a snapshot, or None if no note exists."""
    return _load_notes(snapshot_dir).get(name)


def delete_note(name: str, snapshot_dir: str) -> bool:
    """Remove the note for a snapshot. Returns True if a note was removed."""
    notes = _load_notes(snapshot_dir)
    if name not in notes:
        return False
    del notes[name]
    _save_notes(snapshot_dir, notes)
    return True


def list_notes(snapshot_dir: str) -> dict[str, str]:
    """Return all snapshot notes as a dict of {name: note}."""
    return dict(_load_notes(snapshot_dir))
