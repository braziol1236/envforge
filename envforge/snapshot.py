"""Snapshot storage and retrieval."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_SNAPSHOT_DIR = Path.home() / ".envforge" / "snapshots"


def get_snapshot_path(name: str, snapshot_dir: Path = None) -> Path:
    base = snapshot_dir or DEFAULT_SNAPSHOT_DIR
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{name}.json"


def save_snapshot(
    name: str,
    env_vars: Dict[str, str],
    snapshot_dir: Path = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Path:
    path = get_snapshot_path(name, snapshot_dir)
    existing = {}
    if path.exists():
        with open(path) as f:
            existing = json.load(f)
    data = {
        "name": name,
        "created_at": existing.get("created_at", datetime.now(timezone.utc).isoformat()),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "vars": env_vars,
        "tags": existing.get("tags", []),
    }
    if extra:
        data.update(extra)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path


def load_snapshot(name: str, snapshot_dir: Path = None) -> Dict[str, Any]:
    path = get_snapshot_path(name, snapshot_dir)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found.")
    with open(path) as f:
        return json.load(f)


def list_snapshots(snapshot_dir: Path = None) -> List[Dict[str, Any]]:
    base = snapshot_dir or DEFAULT_SNAPSHOT_DIR
    if not base.exists():
        return []
    results = []
    for p in sorted(base.glob("*.json")):
        try:
            with open(p) as f:
                data = json.load(f)
            results.append(data)
        except Exception:
            continue
    return results


def delete_snapshot(name: str, snapshot_dir: Path = None) -> None:
    path = get_snapshot_path(name, snapshot_dir)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found.")
    path.unlink()
