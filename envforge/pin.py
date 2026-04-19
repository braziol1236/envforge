"""Pin a snapshot as a named alias (e.g. 'stable', 'prod')."""
from __future__ import annotations

import json
from pathlib import Path

from envforge.snapshot import get_snapshot_path, load_snapshot


def _pins_path(snapshot_dir: str) -> Path:
    return Path(snapshot_dir) / "_pins.json"


def _load_pins(snapshot_dir: str) -> dict:
    p = _pins_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_pins(snapshot_dir: str, pins: dict) -> None:
    _pins_path(snapshot_dir).write_text(json.dumps(pins, indent=2))


def pin_snapshot(alias: str, name: str, snapshot_dir: str) -> None:
    """Create alias pointing to snapshot name."""
    # Validate snapshot exists
    load_snapshot(name, snapshot_dir)
    pins = _load_pins(snapshot_dir)
    pins[alias] = name
    _save_pins(snapshot_dir, pins)


def unpin(alias: str, snapshot_dir: str) -> None:
    """Remove a pin alias."""
    pins = _load_pins(snapshot_dir)
    if alias not in pins:
        raise KeyError(f"Pin '{alias}' not found.")
    del pins[alias]
    _save_pins(snapshot_dir, pins)


def resolve_pin(alias: str, snapshot_dir: str) -> str:
    """Return snapshot name for alias, or raise KeyError."""
    pins = _load_pins(snapshot_dir)
    if alias not in pins:
        raise KeyError(f"Pin '{alias}' not found.")
    return pins[alias]


def list_pins(snapshot_dir: str) -> dict:
    """Return all alias -> snapshot_name mappings."""
    return _load_pins(snapshot_dir)


def load_pinned(alias: str, snapshot_dir: str) -> dict:
    """Load the snapshot pointed to by alias."""
    name = resolve_pin(alias, snapshot_dir)
    return load_snapshot(name, snapshot_dir)
