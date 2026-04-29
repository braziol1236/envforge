"""snapshot_chain.py — link snapshots into ordered chains (parent → child).

A chain lets you model environment progression, e.g.:
  base → staging → production

Each snapshot can have at most one parent.  Walking the chain gives the
full ancestry so callers can reconstruct a merged view or audit the
evolution of variables over time.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envforge.snapshot import get_snapshot_path, load_snapshot


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _chain_path(snapshot_dir: Path) -> Path:
    """Return the path to the chains metadata file."""
    return snapshot_dir / ".chains.json"


def _load_chains(snapshot_dir: Path) -> Dict[str, str]:
    """Load the child→parent mapping from disk.  Returns {} if missing."""
    p = _chain_path(snapshot_dir)
    if not p.exists():
        return {}
    with p.open() as fh:
        return json.load(fh)


def _save_chains(snapshot_dir: Path, data: Dict[str, str]) -> None:
    """Persist the child→parent mapping to disk."""
    with _chain_path(snapshot_dir).open("w") as fh:
        json.dump(data, fh, indent=2)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class ChainError(Exception):
    """Raised when a chain operation cannot be completed."""


def set_parent(child: str, parent: str, snapshot_dir: Path) -> None:
    """Link *child* snapshot to *parent*.

    Both snapshots must exist.  A snapshot cannot be its own parent, and
    the operation is rejected if it would create a cycle.
    """
    if child == parent:
        raise ChainError(f"A snapshot cannot be its own parent: '{child}'")

    # Verify both snapshots exist.
    for name in (child, parent):
        if not get_snapshot_path(name, snapshot_dir).exists():
            raise ChainError(f"Snapshot not found: '{name}'")

    chains = _load_chains(snapshot_dir)

    # Cycle detection: walk parent's ancestry — if we encounter *child* we
    # would create a loop.
    cursor: Optional[str] = parent
    visited = set()
    while cursor is not None:
        if cursor in visited:
            break  # already a cycle in existing data; stop
        if cursor == child:
            raise ChainError(
                f"Setting '{parent}' as parent of '{child}' would create a cycle."
            )
        visited.add(cursor)
        cursor = chains.get(cursor)

    chains[child] = parent
    _save_chains(snapshot_dir, chains)


def remove_parent(child: str, snapshot_dir: Path) -> bool:
    """Remove the parent link for *child*.  Returns True if a link existed."""
    chains = _load_chains(snapshot_dir)
    if child not in chains:
        return False
    del chains[child]
    _save_chains(snapshot_dir, chains)
    return True


def get_parent(child: str, snapshot_dir: Path) -> Optional[str]:
    """Return the direct parent name for *child*, or None."""
    return _load_chains(snapshot_dir).get(child)


def get_ancestors(name: str, snapshot_dir: Path) -> List[str]:
    """Return the ordered list of ancestors, nearest first.

    Example: if C → B → A, ``get_ancestors('C', ...)`` returns ['B', 'A'].
    """
    chains = _load_chains(snapshot_dir)
    ancestors: List[str] = []
    cursor: Optional[str] = chains.get(name)
    seen = {name}
    while cursor is not None and cursor not in seen:
        ancestors.append(cursor)
        seen.add(cursor)
        cursor = chains.get(cursor)
    return ancestors


def get_children(name: str, snapshot_dir: Path) -> List[str]:
    """Return all snapshots that have *name* as their direct parent."""
    chains = _load_chains(snapshot_dir)
    return [child for child, parent in chains.items() if parent == name]


def merged_vars(name: str, snapshot_dir: Path) -> Dict[str, str]:
    """Return variables for *name* with ancestor values as defaults.

    Ancestors are applied root-first so that closer ancestors (and the
    snapshot itself) override more distant ones.
    """
    ancestors = get_ancestors(name, snapshot_dir)
    # Build from oldest ancestor down to the snapshot itself.
    combined: Dict[str, str] = {}
    for ancestor in reversed(ancestors):
        combined.update(load_snapshot(ancestor, snapshot_dir)["vars"])
    combined.update(load_snapshot(name, snapshot_dir)["vars"])
    return combined


def list_chains(snapshot_dir: Path) -> Dict[str, str]:
    """Return the raw child→parent mapping for inspection."""
    return dict(_load_chains(snapshot_dir))
