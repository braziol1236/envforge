"""Arbitrary key-value label support for snapshots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envforge.snapshot import get_snapshot_path


class LabelError(Exception):
    pass


def _labels_path(snapshot_dir: str) -> Path:
    return Path(snapshot_dir) / ".labels.json"


def _load_labels(snapshot_dir: str) -> Dict[str, Dict[str, str]]:
    p = _labels_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_labels(snapshot_dir: str, data: Dict[str, Dict[str, str]]) -> None:
    _labels_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def set_label(snapshot_dir: str, name: str, key: str, value: str) -> None:
    """Attach a label key=value to a snapshot."""
    if not get_snapshot_path(snapshot_dir, name).exists():
        raise LabelError(f"Snapshot '{name}' not found.")
    data = _load_labels(snapshot_dir)
    data.setdefault(name, {})[key] = value
    _save_labels(snapshot_dir, data)


def remove_label(snapshot_dir: str, name: str, key: str) -> bool:
    """Remove a label key from a snapshot. Returns True if removed."""
    data = _load_labels(snapshot_dir)
    if name not in data or key not in data[name]:
        return False
    del data[name][key]
    if not data[name]:
        del data[name]
    _save_labels(snapshot_dir, data)
    return True


def get_labels(snapshot_dir: str, name: str) -> Dict[str, str]:
    """Return all labels for a snapshot."""
    return _load_labels(snapshot_dir).get(name, {})


def find_by_label(
    snapshot_dir: str, key: str, value: Optional[str] = None
) -> list[str]:
    """Return snapshot names that have a given label key (optionally matching value)."""
    data = _load_labels(snapshot_dir)
    results = []
    for snap, labels in data.items():
        if key in labels:
            if value is None or labels[key] == value:
                results.append(snap)
    return sorted(results)
