"""Compute statistics and summaries for snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envforge.snapshot import load_snapshot, list_snapshots


@dataclass
class SnapshotStats:
    name: str
    total_keys: int
    empty_values: int
    avg_value_length: float
    longest_key: str
    longest_value_key: str
    tags: List[str] = field(default_factory=list)


def compute_stats(name: str, snapshot_dir: str | None = None) -> SnapshotStats:
    """Return statistics for a single snapshot."""
    data = load_snapshot(name, snapshot_dir=snapshot_dir)
    vars_: Dict[str, str] = data.get("vars", {})
    tags: List[str] = data.get("tags", [])

    total_keys = len(vars_)
    empty_values = sum(1 for v in vars_.values() if v == "")

    if total_keys == 0:
        avg_value_length = 0.0
        longest_key = ""
        longest_value_key = ""
    else:
        avg_value_length = sum(len(v) for v in vars_.values()) / total_keys
        longest_key = max(vars_.keys(), key=len)
        longest_value_key = max(vars_.keys(), key=lambda k: len(vars_[k]))

    return SnapshotStats(
        name=name,
        total_keys=total_keys,
        empty_values=empty_values,
        avg_value_length=round(avg_value_length, 2),
        longest_key=longest_key,
        longest_value_key=longest_value_key,
        tags=tags,
    )


def compute_all_stats(snapshot_dir: str | None = None) -> List[SnapshotStats]:
    """Return stats for every snapshot in the directory."""
    snapshots = list_snapshots(snapshot_dir=snapshot_dir)
    return [compute_stats(s["name"], snapshot_dir=snapshot_dir) for s in snapshots]


def format_stats(stats: SnapshotStats) -> str:
    """Human-readable summary of snapshot stats."""
    lines = [
        f"Snapshot : {stats.name}",
        f"  Total keys        : {stats.total_keys}",
        f"  Empty values      : {stats.empty_values}",
        f"  Avg value length  : {stats.avg_value_length}",
        f"  Longest key       : {stats.longest_key or '(none)'}",
        f"  Longest value key : {stats.longest_value_key or '(none)'}",
        f"  Tags              : {', '.join(stats.tags) if stats.tags else '(none)'}",
    ]
    return "\n".join(lines)
