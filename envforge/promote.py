"""Promote a snapshot to a named environment tier (e.g. dev -> staging -> prod)."""

from __future__ import annotations

from typing import Optional

from envforge.snapshot import load_snapshot, save_snapshot
from envforge.history import record_event

DEFAULT_TIERS = ["dev", "staging", "prod"]


def _tier_snapshot_name(name: str, tier: str) -> str:
    """Return a snapshot name scoped to a tier, e.g. 'myapp' -> 'myapp:staging'."""
    return f"{name}:{tier}"


def promote_snapshot(
    name: str,
    from_tier: str,
    to_tier: str,
    overrides: Optional[dict[str, str]] = None,
    *,
    snapshot_dir: Optional[str] = None,
) -> dict[str, str]:
    """Copy a snapshot from one tier to another, optionally applying overrides.

    Args:
        name: Base snapshot name (without tier suffix).
        from_tier: Source tier name.
        to_tier: Destination tier name.
        overrides: Key/value pairs to merge on top before saving.
        snapshot_dir: Optional directory for snapshot storage.

    Returns:
        The vars dict that was saved to the destination tier.

    Raises:
        FileNotFoundError: If the source tier snapshot does not exist.
    """
    kwargs = {"snapshot_dir": snapshot_dir} if snapshot_dir else {}

    src_name = _tier_snapshot_name(name, from_tier)
    dst_name = _tier_snapshot_name(name, to_tier)

    vars_ = load_snapshot(src_name, **kwargs)
    if overrides:
        vars_ = {**vars_, **overrides}

    save_snapshot(dst_name, vars_, **kwargs)
    record_event(
        dst_name,
        "promote",
        detail=f"promoted from {from_tier} to {to_tier}",
        **kwargs,
    )
    return vars_


def list_tiers(name: str, tiers: Optional[list[str]] = None, *, snapshot_dir: Optional[str] = None) -> list[str]:
    """Return which tiers exist for the given base snapshot name."""
    from envforge.snapshot import list_snapshots

    tiers = tiers or DEFAULT_TIERS
    kwargs = {"snapshot_dir": snapshot_dir} if snapshot_dir else {}
    all_snapshots = {s["name"] for s in list_snapshots(**kwargs)}
    return [t for t in tiers if _tier_snapshot_name(name, t) in all_snapshots]
