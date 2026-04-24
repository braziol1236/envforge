"""Archive and restore snapshots as compressed zip bundles."""

import json
import zipfile
from pathlib import Path
from typing import List

from envforge.snapshot import get_snapshot_path, save_snapshot, load_snapshot


def archive_snapshots(names: List[str], output_path: Path, snapshot_dir: Path) -> Path:
    """Bundle one or more snapshots into a single .zip archive."""
    output_path = Path(output_path)
    if not output_path.suffix:
        output_path = output_path.with_suffix(".zip")

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        manifest = {"snapshots": []}
        for name in names:
            snap = load_snapshot(name, snapshot_dir=snapshot_dir)
            entry = {"name": name, "vars": snap}
            manifest["snapshots"].append(entry)
            zf.writestr(f"{name}.json", json.dumps(snap, indent=2))
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))

    return output_path


def restore_archive(archive_path: Path, snapshot_dir: Path, overwrite: bool = False) -> List[str]:
    """Restore snapshots from a .zip archive. Returns list of restored names."""
    archive_path = Path(archive_path)
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    restored = []
    with zipfile.ZipFile(archive_path, "r") as zf:
        names = [n for n in zf.namelist() if n != "manifest.json"]
        for entry_name in names:
            snap_name = entry_name.removesuffix(".json")
            existing = get_snapshot_path(snap_name, snapshot_dir=snapshot_dir)
            if existing.exists() and not overwrite:
                raise FileExistsError(
                    f"Snapshot '{snap_name}' already exists. Use overwrite=True to replace."
                )
            data = json.loads(zf.read(entry_name))
            save_snapshot(snap_name, data, snapshot_dir=snapshot_dir)
            restored.append(snap_name)

    return restored


def list_archive_contents(archive_path: Path) -> List[str]:
    """Return the list of snapshot names stored inside an archive."""
    archive_path = Path(archive_path)
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    with zipfile.ZipFile(archive_path, "r") as zf:
        return [
            n.removesuffix(".json")
            for n in zf.namelist()
            if n != "manifest.json"
        ]
