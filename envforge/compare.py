"""Compare two snapshots or a snapshot against current environment."""
from __future__ import annotations

from typing import Optional

from envforge.snapshot import load_snapshot
from envforge.diff import diff_snapshots, diff_snapshot_with_env, EnvDiff


def compare_two(name_a: str, name_b: str, snapshot_dir: Optional[str] = None) -> EnvDiff:
    """Return diff between snapshot A and snapshot B."""
    snap_a = load_snapshot(name_a, snapshot_dir=snapshot_dir)
    snap_b = load_snapshot(name_b, snapshot_dir=snapshot_dir)
    return diff_snapshots(snap_a, snap_b)


def compare_with_env(name: str, snapshot_dir: Optional[str] = None) -> EnvDiff:
    """Return diff between a snapshot and the current environment."""
    import os
    snap = load_snapshot(name, snapshot_dir=snapshot_dir)
    return diff_snapshot_with_env(snap, dict(os.environ))


def format_diff(diff: EnvDiff, verbose: bool = False) -> str:
    """Format an EnvDiff for human-readable output."""
    lines = []
    for key, new_val in sorted(diff.added.items()):
        lines.append(f"+ {key}={new_val}")
    for key in sorted(diff.removed):
        lines.append(f"- {key}")
    for key, (old_val, new_val) in sorted(diff.changed.items()):
        if verbose:
            lines.append(f"~ {key}: {old_val!r} -> {new_val!r}")
        else:
            lines.append(f"~ {key}")
    if not lines:
        return "No differences found."
    return "\n".join(lines)
