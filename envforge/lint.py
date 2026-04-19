"""Lint snapshots for common issues like empty values, duplicates, or suspicious keys."""

from typing import Any
from envforge.snapshot import load_snapshot

LINT_RULES = [
    "empty_values",
    "keys_with_spaces",
    "overlong_values",
    "suspicious_keys",
]

SUSPICIOUS_PATTERNS = ["password", "secret", "token", "apikey", "api_key", "private"]


def lint_snapshot(name: str, snapshot_dir: str) -> dict[str, list[str]]:
    """Run all lint checks on a snapshot. Returns dict of rule -> list of warnings."""
    data = load_snapshot(name, snapshot_dir)
    env: dict[str, Any] = data.get("env", {})

    warnings: dict[str, list[str]] = {rule: [] for rule in LINT_RULES}

    for key, value in env.items():
        if value == "" or value is None:
            warnings["empty_values"].append(key)

        if " " in key:
            warnings["keys_with_spaces"].append(key)

        if isinstance(value, str) and len(value) > 512:
            warnings["overlong_values"].append(key)

        lower_key = key.lower()
        if any(pat in lower_key for pat in SUSPICIOUS_PATTERNS):
            warnings["suspicious_keys"].append(key)

    return warnings


def has_warnings(results: dict[str, list[str]]) -> bool:
    return any(len(v) > 0 for v in results.values())


def format_lint_results(results: dict[str, list[str]]) -> str:
    lines = []
    for rule, keys in results.items():
        if keys:
            lines.append(f"[{rule}]")
            for k in keys:
                lines.append(f"  - {k}")
    return "\n".join(lines) if lines else "No issues found."
