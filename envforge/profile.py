"""Profile support: group snapshots under a named profile."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def _profiles_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "_profiles.json"


def _load_profiles(snapshot_dir: Path) -> Dict[str, List[str]]:
    p = _profiles_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_profiles(snapshot_dir: Path, data: Dict[str, List[str]]) -> None:
    _profiles_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def add_to_profile(snapshot_dir: Path, profile: str, snapshot_name: str) -> None:
    data = _load_profiles(snapshot_dir)
    members = data.setdefault(profile, [])
    if snapshot_name not in members:
        members.append(snapshot_name)
    _save_profiles(snapshot_dir, data)


def remove_from_profile(snapshot_dir: Path, profile: str, snapshot_name: str) -> None:
    data = _load_profiles(snapshot_dir)
    if profile in data:
        data[profile] = [s for s in data[profile] if s != snapshot_name]
        if not data[profile]:
            del data[profile]
    _save_profiles(snapshot_dir, data)


def list_profiles(snapshot_dir: Path) -> Dict[str, List[str]]:
    return _load_profiles(snapshot_dir)


def get_profile_members(snapshot_dir: Path, profile: str) -> List[str]:
    return _load_profiles(snapshot_dir).get(profile, [])


def delete_profile(snapshot_dir: Path, profile: str) -> None:
    data = _load_profiles(snapshot_dir)
    data.pop(profile, None)
    _save_profiles(snapshot_dir, data)
