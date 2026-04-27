"""Mirror (sync) a snapshot to a remote directory or path."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from envforge.snapshot import load_snapshot, get_snapshot_path


class MirrorError(Exception):
    pass


def mirror_to_path(name: str, dest_dir: str | Path, *, snapshot_dir: Path | None = None) -> Path:
    """Copy a snapshot file to dest_dir, returning the destination path."""
    src = get_snapshot_path(name, base_dir=snapshot_dir)
    if not src.exists():
        raise MirrorError(f"Snapshot '{name}' does not exist.")

    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    dest_file = dest / src.name
    shutil.copy2(src, dest_file)
    return dest_file


def mirror_all(dest_dir: str | Path, *, snapshot_dir: Path | None = None) -> list[Path]:
    """Mirror every snapshot in snapshot_dir to dest_dir."""
    from envforge.snapshot import list_snapshots

    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for meta in list_snapshots(base_dir=snapshot_dir):
        dest_file = mirror_to_path(
            meta["name"], dest_dir=dest, snapshot_dir=snapshot_dir
        )
        copied.append(dest_file)
    return copied


def restore_from_mirror(name: str, src_dir: str | Path, *, snapshot_dir: Path | None = None) -> dict:
    """Load a snapshot from a mirror directory and save it locally."""
    from envforge.snapshot import save_snapshot

    src = Path(src_dir) / f"{name}.json"
    if not src.exists():
        raise MirrorError(f"Snapshot '{name}' not found in mirror at {src_dir}.")

    data = json.loads(src.read_text())
    vars_ = data.get("vars", {})
    save_snapshot(name, vars_, base_dir=snapshot_dir)
    return vars_


def list_mirror_contents(src_dir: str | Path) -> list[str]:
    """Return names of snapshots available in a mirror directory."""
    src = Path(src_dir)
    if not src.exists():
        return []
    return sorted(
        p.stem for p in src.glob("*.json")
    )
