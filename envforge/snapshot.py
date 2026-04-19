"""Core snapshot functionality for capturing and storing env var snapshots."""

import json
import os
import time
from pathlib import Path
from typing import Optional

SNAPSHOT_DIR = Path.home() / ".envforge" / "snapshots"


def get_snapshot_path(name: str) -> Path:
    return SNAPSHOT_DIR / f"{name}.json"


def save_snapshot(name: str, env: dict, description: Optional[str] = None) -> Path:
    """Save current environment variables as a named snapshot."""
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "name": name,
        "description": description or "",
        "created_at": time.time(),
        "env": env,
    }
    path = get_snapshot_path(name)
    with open(path, "w") as f:
        json.dump(snapshot, f, indent=2)
    return path


def load_snapshot(name: str) -> dict:
    """Load a snapshot by name. Raises FileNotFoundError if not found."""
    path = get_snapshot_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found.")
    with open(path) as f:
        return json.load(f)


def list_snapshots() -> list[dict]:
    """Return metadata for all saved snapshots."""
    if not SNAPSHOT_DIR.exists():
        return []
    snapshots = []
    for p in sorted(SNAPSHOT_DIR.glob("*.json")):
        with open(p) as f:
            data = json.load(f)
        snapshots.append({
            "name": data["name"],
            "description": data.get("description", ""),
            "created_at": data["created_at"],
            "var_count": len(data["env"]),
        })
    return snapshots


def delete_snapshot(name: str) -> bool:
    """Delete a snapshot by name. Returns True if deleted."""
    path = get_snapshot_path(name)
    if not path.exists():
        return False
    path.unlink()
    return True


def capture_env(keys: Optional[list[str]] = None) -> dict:
    """Capture current env vars, optionally filtering to specific keys."""
    env = dict(os.environ)
    if keys:
        env = {k: v for k, v in env.items() if k in keys}
    return env
