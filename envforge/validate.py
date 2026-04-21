"""Validate a snapshot against a schema, with CLI-friendly result formatting."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from envforge.snapshot import load_snapshot
from envforge.schema import Schema, validate_snapshot, has_errors, format_results


def validate(
    name: str,
    schema: Schema,
    snapshot_dir: Optional[Path] = None,
) -> dict:
    """Load snapshot *name* and validate it against *schema*.

    Returns a dict with keys:
        snapshot  – snapshot name
        vars      – the raw env vars dict
        results   – list of ValidationResult
        passed    – bool
    """
    vars_ = load_snapshot(name, snapshot_dir=snapshot_dir)
    results = validate_snapshot(vars_, schema)
    return {
        "snapshot": name,
        "vars": vars_,
        "results": results,
        "passed": not has_errors(results),
    }


def validate_many(
    names: list[str],
    schema: Schema,
    snapshot_dir: Optional[Path] = None,
) -> list[dict]:
    """Validate multiple snapshots against the same schema."""
    return [validate(n, schema, snapshot_dir=snapshot_dir) for n in names]


def format_validate_report(result: dict) -> str:
    """Human-readable report for a single validate() result."""
    lines = [f"Snapshot : {result['snapshot']}"]
    if result["passed"]:
        lines.append("Status   : PASSED")
    else:
        lines.append("Status   : FAILED")
    body = format_results(result["results"])
    if body:
        lines.append(body)
    return "\n".join(lines)
