"""Search snapshots by key name, value pattern, or metadata."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from typing import Optional

from envforge.snapshot import list_snapshots, load_snapshot


@dataclass
class SearchResult:
    name: str
    saved_at: str
    matches: dict[str, str] = field(default_factory=dict)


def search_by_key(
    pattern: str,
    snapshot_dir: Optional[str] = None,
) -> list[SearchResult]:
    """Return snapshots that contain keys matching *pattern* (glob-style)."""
    results: list[SearchResult] = []
    for meta in list_snapshots(snapshot_dir=snapshot_dir):
        snap = load_snapshot(meta["name"], snapshot_dir=snapshot_dir)
        matches = {
            k: v for k, v in snap["vars"].items() if fnmatch.fnmatch(k, pattern)
        }
        if matches:
            results.append(
                SearchResult(name=meta["name"], saved_at=meta["saved_at"], matches=matches)
            )
    return results


def search_by_value(
    pattern: str,
    snapshot_dir: Optional[str] = None,
) -> list[SearchResult]:
    """Return snapshots whose values match *pattern* (regex)."""
    regex = re.compile(pattern)
    results: list[SearchResult] = []
    for meta in list_snapshots(snapshot_dir=snapshot_dir):
        snap = load_snapshot(meta["name"], snapshot_dir=snapshot_dir)
        matches = {
            k: v for k, v in snap["vars"].items() if regex.search(v)
        }
        if matches:
            results.append(
                SearchResult(name=meta["name"], saved_at=meta["saved_at"], matches=matches)
            )
    return results


def format_results(results: list[SearchResult]) -> str:
    if not results:
        return "No matches found."
    lines: list[str] = []
    for r in results:
        lines.append(f"[{r.name}]  saved: {r.saved_at}")
        for k, v in r.matches.items():
            lines.append(f"  {k}={v}")
    return "\n".join(lines)
