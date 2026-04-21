"""Redact sensitive keys from snapshots before display or export."""

from __future__ import annotations

import re
from typing import Dict, List, Optional

# Default patterns that suggest a value is sensitive
DEFAULT_SENSITIVE_PATTERNS: List[str] = [
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*PASSWD.*",
    r".*TOKEN.*",
    r".*API_KEY.*",
    r".*PRIVATE_KEY.*",
    r".*CREDENTIALS.*",
    r".*AUTH.*",
]

REDACTED_PLACEHOLDER = "***REDACTED***"


def _compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def is_sensitive(key: str, patterns: Optional[List[str]] = None) -> bool:
    """Return True if the key matches any sensitive pattern."""
    compiled = _compile_patterns(patterns or DEFAULT_SENSITIVE_PATTERNS)
    return any(pat.fullmatch(key) for pat in compiled)


def redact_snapshot(
    variables: Dict[str, str],
    patterns: Optional[List[str]] = None,
    placeholder: str = REDACTED_PLACEHOLDER,
) -> Dict[str, str]:
    """Return a copy of variables with sensitive values replaced by placeholder."""
    return {
        k: (placeholder if is_sensitive(k, patterns) else v)
        for k, v in variables.items()
    }


def list_sensitive_keys(
    variables: Dict[str, str],
    patterns: Optional[List[str]] = None,
) -> List[str]:
    """Return a sorted list of keys considered sensitive."""
    return sorted(k for k in variables if is_sensitive(k, patterns))


def format_redacted(
    variables: Dict[str, str],
    patterns: Optional[List[str]] = None,
    placeholder: str = REDACTED_PLACEHOLDER,
) -> str:
    """Format redacted variables as KEY=value lines."""
    redacted = redact_snapshot(variables, patterns, placeholder)
    lines = [f"{k}={v}" for k, v in sorted(redacted.items())]
    return "\n".join(lines)
