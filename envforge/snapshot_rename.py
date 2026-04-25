"""Rename snapshots with optional history and alias migration."""

from pathlib import Path
from envforge.snapshot import get_snapshot_path, load_snapshot, save_snapshot, delete_snapshot


class RenameError(Exception):
    pass


def rename_snapshot(
    old_name: str,
    new_name: str,
    snapshot_dir: Path,
    *,
    migrate_aliases: bool = True,
    overwrite: bool = False,
) -> None:
    """Rename a snapshot from old_name to new_name.

    Args:
        old_name: Existing snapshot name.
        new_name: Target snapshot name.
        snapshot_dir: Directory containing snapshots.
        migrate_aliases: If True, update any aliases pointing to old_name.
        overwrite: If True, overwrite an existing snapshot with new_name.
    """
    old_path = get_snapshot_path(old_name, snapshot_dir)
    if not old_path.exists():
        raise RenameError(f"Snapshot '{old_name}' does not exist.")

    new_path = get_snapshot_path(new_name, snapshot_dir)
    if new_path.exists() and not overwrite:
        raise RenameError(
            f"Snapshot '{new_name}' already exists. Use overwrite=True to replace it."
        )

    data = load_snapshot(old_name, snapshot_dir)
    save_snapshot(new_name, data["vars"], snapshot_dir)
    delete_snapshot(old_name, snapshot_dir)

    if migrate_aliases:
        _migrate_aliases(old_name, new_name, snapshot_dir)


def _migrate_aliases(old_name: str, new_name: str, snapshot_dir: Path) -> None:
    """Update alias records that reference old_name to point to new_name."""
    try:
        from envforge.alias import _aliases_path, _load_aliases, _save_aliases
    except ImportError:
        return

    path = _aliases_path(snapshot_dir)
    aliases = _load_aliases(path)
    updated = False
    for alias, target in list(aliases.items()):
        if target == old_name:
            aliases[alias] = new_name
            updated = True
    if updated:
        _save_aliases(path, aliases)
