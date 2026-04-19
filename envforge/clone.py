"""Clone a snapshot under a new name, optionally overriding variables."""

from __future__ import annotations

from typing import Optional

from envforge.snapshot import load_snapshot, save_snapshot


def clone_snapshot(
    source_name: str,
    dest_name: str,
    overrides: Optional[dict[str, str]] = None,
    snapshot_dir: Optional[str] = None,
) -> dict:
    """Clone *source_name* into *dest_name*, applying optional key overrides.

    Returns the env dict that was saved.
    """
    kwargs = {"snapshot_dir": snapshot_dir} if snapshot_dir else {}
    source = load_snapshot(source_name, **kwargs)
    env = dict(source["env"])

    if overrides:
        env.update(overrides)

    save_snapshot(dest_name, env, **kwargs)
    return env


def rename_snapshot(
    old_name: str,
    new_name: str,
    snapshot_dir: Optional[str] = None,
) -> None:
    """Rename a snapshot by cloning it then deleting the original."""
    from envforge.snapshot import delete_snapshot

    kwargs = {"snapshot_dir": snapshot_dir} if snapshot_dir else {}
    clone_snapshot(old_name, new_name, snapshot_dir=snapshot_dir)
    delete_snapshot(old_name, **kwargs)
