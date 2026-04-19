"""Schema validation for snapshots — enforce required keys, types, patterns."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class KeyRule:
    key: str
    required: bool = False
    pattern: Optional[str] = None  # regex the value must match
    description: str = ""


@dataclass
class Schema:
    name: str
    rules: list[KeyRule] = field(default_factory=list)


@dataclass
class ValidationResult:
    key: str
    rule: str
    message: str
    error: bool = True  # True = error, False = warning


def validate_snapshot(env: dict[str, str], schema: Schema) -> list[ValidationResult]:
    results: list[ValidationResult] = []

    for rule in schema.rules:
        value = env.get(rule.key)

        if rule.required and value is None:
            results.append(ValidationResult(
                key=rule.key,
                rule="required",
                message=f"Required key '{rule.key}' is missing.",
                error=True,
            ))
            continue

        if value is not None and rule.pattern:
            if not re.fullmatch(rule.pattern, value):
                results.append(ValidationResult(
                    key=rule.key,
                    rule="pattern",
                    message=f"Key '{rule.key}' value {value!r} does not match pattern '{rule.pattern}'.",
                    error=True,
                ))

    return results


def has_errors(results: list[ValidationResult]) -> bool:
    return any(r.error for r in results)


def format_results(results: list[ValidationResult]) -> str:
    if not results:
        return "Schema validation passed."
    lines = []
    for r in results:
        prefix = "ERROR" if r.error else "WARN"
        lines.append(f"[{prefix}] {r.message}")
    return "\n".join(lines)
