"""Resolve environment variable references within a snapshot.

Supports ${VAR} and $VAR style references between keys in the same snapshot.
"""

from __future__ import annotations

import re
from typing import Dict, Optional

from envforge.snapshot import load_snapshot, save_snapshot

_VAR_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


def resolve_value(value: str, env: Dict[str, str], *, max_depth: int = 10) -> str:
    """Recursively expand variable references in *value* using *env*.

    Raises ValueError if a circular reference is detected or *max_depth* is
    exceeded.
    """
    for _ in range(max_depth):
        new_value = _VAR_RE.sub(lambda m: env.get(m.group(1) or m.group(2), m.group(0)), value)
        if new_value == value:
            return new_value
        value = new_value
    raise ValueError(f"Max resolution depth ({max_depth}) exceeded — possible circular reference")


def resolve_snapshot(
    vars: Dict[str, str],
    *,
    extra_env: Optional[Dict[str, str]] = None,
    max_depth: int = 10,
) -> Dict[str, str]:
    """Return a new dict with all variable references expanded.

    Resolution order: keys within the snapshot, then *extra_env* fallback.
    """
    base = dict(extra_env or {})
    base.update(vars)  # snapshot keys take priority for lookup
    return {k: resolve_value(v, base, max_depth=max_depth) for k, v in vars.items()}


def resolve_and_save(
    name: str,
    dest: str,
    *,
    snapshot_dir: Optional[str] = None,
    extra_env: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Load *name*, resolve references, and save result as *dest*."""
    data = load_snapshot(name, snapshot_dir=snapshot_dir)
    resolved = resolve_snapshot(data["vars"], extra_env=extra_env)
    save_snapshot(dest, resolved, snapshot_dir=snapshot_dir)
    return resolved
