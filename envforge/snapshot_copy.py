"""Copy snapshot vars selectively into a new or existing snapshot."""
from __future__ import annotations

from typing import Optional

from envforge.snapshot import load_snapshot, save_snapshot, get_snapshot_path


class CopyError(Exception):
    pass


def copy_keys(
    src_name: str,
    dst_name: str,
    keys: list[str],
    *,
    snapshot_dir: Optional[str] = None,
    overwrite: bool = True,
) -> dict[str, str]:
    """Copy specific keys from src snapshot into dst snapshot.

    If dst snapshot does not exist it is created.  Returns the final
    vars dict of the destination snapshot.
    """
    src = load_snapshot(src_name, snapshot_dir=snapshot_dir)
    missing = [k for k in keys if k not in src["vars"]]
    if missing:
        raise CopyError(f"Keys not found in '{src_name}': {', '.join(missing)}")

    dst_path = get_snapshot_path(dst_name, snapshot_dir=snapshot_dir)
    if dst_path.exists():
        dst = load_snapshot(dst_name, snapshot_dir=snapshot_dir)
    else:
        dst = {"name": dst_name, "vars": {}}

    for key in keys:
        if key in dst["vars"] and not overwrite:
            continue
        dst["vars"][key] = src["vars"][key]

    save_snapshot(dst_name, dst["vars"], snapshot_dir=snapshot_dir)
    return dst["vars"]


def copy_all(
    src_name: str,
    dst_name: str,
    *,
    snapshot_dir: Optional[str] = None,
    overwrite: bool = True,
) -> dict[str, str]:
    """Copy all vars from src into dst (merge, not replace)."""
    src = load_snapshot(src_name, snapshot_dir=snapshot_dir)
    return copy_keys(
        src_name,
        dst_name,
        list(src["vars"].keys()),
        snapshot_dir=snapshot_dir,
        overwrite=overwrite,
    )
