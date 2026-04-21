"""Snapshot aliasing — give a snapshot a human-friendly short name."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envforge.snapshot import get_snapshot_path, load_snapshot


def _aliases_path(snapshot_dir: str) -> Path:
    return Path(snapshot_dir) / "_aliases.json"


def _load_aliases(snapshot_dir: str) -> Dict[str, str]:
    p = _aliases_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_aliases(snapshot_dir: str, aliases: Dict[str, str]) -> None:
    _aliases_path(snapshot_dir).write_text(json.dumps(aliases, indent=2))


def set_alias(alias: str, snapshot_name: str, snapshot_dir: str) -> None:
    """Map *alias* to *snapshot_name*.  Raises FileNotFoundError if the target snapshot doesn't exist."""
    # Validate target exists
    load_snapshot(snapshot_name, snapshot_dir)
    aliases = _load_aliases(snapshot_dir)
    aliases[alias] = snapshot_name
    _save_aliases(snapshot_dir, aliases)


def remove_alias(alias: str, snapshot_dir: str) -> bool:
    """Remove *alias*.  Returns True if it existed, False otherwise."""
    aliases = _load_aliases(snapshot_dir)
    if alias not in aliases:
        return False
    del aliases[alias]
    _save_aliases(snapshot_dir, aliases)
    return True


def resolve_alias(alias: str, snapshot_dir: str) -> Optional[str]:
    """Return the snapshot name for *alias*, or None if not found."""
    return _load_aliases(snapshot_dir).get(alias)


def list_aliases(snapshot_dir: str) -> Dict[str, str]:
    """Return all alias -> snapshot_name mappings."""
    return dict(_load_aliases(snapshot_dir))


def resolve_name_or_alias(name_or_alias: str, snapshot_dir: str) -> str:
    """Return the canonical snapshot name, resolving an alias if necessary."""
    resolved = resolve_alias(name_or_alias, snapshot_dir)
    return resolved if resolved is not None else name_or_alias
