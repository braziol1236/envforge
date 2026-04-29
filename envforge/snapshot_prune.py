"""Prune snapshots based on age, count limits, or expired TTLs."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from envforge.snapshot import list_snapshots, delete_snapshot
from envforge.snapshot_ttl import get_ttl


def prune_expired(snapshot_dir: str) -> List[str]:
    """Delete all snapshots whose TTL has passed. Returns list of deleted names."""
    deleted = []
    for meta in list_snapshots(snapshot_dir):
        name = meta["name"]
        expiry = get_ttl(name, snapshot_dir=snapshot_dir)
        if expiry is not None and datetime.now(timezone.utc) >= expiry:
            delete_snapshot(name, snapshot_dir=snapshot_dir)
            deleted.append(name)
    return deleted


def prune_oldest(snapshot_dir: str, keep: int) -> List[str]:
    """Keep only the *keep* most-recently saved snapshots; delete the rest."""
    if keep < 1:
        raise ValueError("keep must be >= 1")
    snapshots = sorted(
        list_snapshots(snapshot_dir),
        key=lambda m: m.get("saved_at", ""),
        reverse=True,
    )
    to_delete = snapshots[keep:]
    deleted = []
    for meta in to_delete:
        name = meta["name"]
        delete_snapshot(name, snapshot_dir=snapshot_dir)
        deleted.append(name)
    return deleted


def prune_before(
    snapshot_dir: str,
    cutoff: datetime,
    dry_run: bool = False,
) -> List[str]:
    """Delete snapshots saved before *cutoff*. Returns list of affected names."""
    affected = []
    for meta in list_snapshots(snapshot_dir):
        saved_at_str = meta.get("saved_at", "")
        if not saved_at_str:
            continue
        try:
            saved_at = datetime.fromisoformat(saved_at_str)
        except ValueError:
            continue
        if saved_at.tzinfo is None:
            saved_at = saved_at.replace(tzinfo=timezone.utc)
        if saved_at < cutoff:
            affected.append(meta["name"])
            if not dry_run:
                delete_snapshot(meta["name"], snapshot_dir=snapshot_dir)
    return affected


def format_prune_report(deleted: List[str], dry_run: bool = False) -> str:
    """Human-readable summary of a prune operation."""
    verb = "Would delete" if dry_run else "Deleted"
    if not deleted:
        return "Nothing to prune."
    lines = [f"{verb} {len(deleted)} snapshot(s):"]
    for name in deleted:
        lines.append(f"  - {name}")
    return "\n".join(lines)
