"""Diff utilities for comparing environment snapshots."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EnvDiff:
    added: dict[str, str]
    removed: dict[str, str]
    changed: dict[str, tuple[str, str]]  # key -> (old, new)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines = []
        for key, val in sorted(self.added.items()):
            lines.append(f"  + {key}={val}")
        for key, val in sorted(self.removed.items()):
            lines.append(f"  - {key}={val}")
        for key, (old, new) in sorted(self.changed.items()):
            lines.append(f"  ~ {key}: {old!r} -> {new!r}")
        return "\n".join(lines) if lines else "  (no differences)"


def diff_snapshots(snapshot_a: dict, snapshot_b: dict) -> EnvDiff:
    """Compare two snapshot dicts (as returned by load_snapshot)."""
    vars_a: dict[str, str] = snapshot_a.get("vars", {})
    vars_b: dict[str, str] = snapshot_b.get("vars", {})

    keys_a = set(vars_a)
    keys_b = set(vars_b)

    added = {k: vars_b[k] for k in keys_b - keys_a}
    removed = {k: vars_a[k] for k in keys_a - keys_b}
    changed = {
        k: (vars_a[k], vars_b[k])
        for k in keys_a & keys_b
        if vars_a[k] != vars_b[k]
    }

    return EnvDiff(added=added, removed=removed, changed=changed)


def diff_snapshot_with_env(snapshot: dict, env: Optional[dict[str, str]] = None) -> EnvDiff:
    """Compare a snapshot against the current (or provided) environment."""
    import os
    current = env if env is not None else dict(os.environ)
    return diff_snapshots(snapshot, {"vars": current})
