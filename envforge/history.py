"""Track snapshot access and modification history."""

import json
from datetime import datetime
from pathlib import Path

from envforge.snapshot import get_snapshot_path


def get_history_path(snapshot_dir: Path, name: str) -> Path:
    return snapshot_dir / f"{name}.history.json"


def record_event(snapshot_dir: Path, name: str, event: str) -> None:
    """Append a timestamped event to the snapshot's history log."""
    path = get_history_path(snapshot_dir, name)
    history = _load_history(path)
    history.append({"event": event, "timestamp": datetime.utcnow().isoformat()})
    path.write_text(json.dumps(history, indent=2))


def _load_history(path: Path) -> list:
    if path.exists():
        return json.loads(path.read_text())
    return []


def get_history(snapshot_dir: Path, name: str) -> list:
    """Return list of history events for a snapshot."""
    path = get_history_path(snapshot_dir, name)
    return _load_history(path)


def clear_history(snapshot_dir: Path, name: str) -> None:
    path = get_history_path(snapshot_dir, name)
    if path.exists():
        path.unlink()
