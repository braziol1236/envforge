"""Export snapshots to various shell-compatible formats."""

from __future__ import annotations

from typing import Dict

SUPPORTED_FORMATS = ["bash", "dotenv", "fish"]


def to_bash(env: Dict[str, str]) -> str:
    """Export env vars as bash export statements."""
    lines = ["#!/usr/bin/env bash", ""]
    for key, value in sorted(env.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')
    return "\n".join(lines) + "\n"


def to_dotenv(env: Dict[str, str]) -> str:
    """Export env vars in .env format."""
    lines = []
    for key, value in sorted(env.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + "\n"


def to_fish(env: Dict[str, str]) -> str:
    """Export env vars as fish shell set statements."""
    lines = []
    for key, value in sorted(env.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'set -x {key} "{escaped}"')
    return "\n".join(lines) + "\n"


def export_snapshot(env: Dict[str, str], fmt: str) -> str:
    """Export a snapshot dict to the given format string."""
    if fmt == "bash":
        return to_bash(env)
    elif fmt == "dotenv":
        return to_dotenv(env)
    elif fmt == "fish":
        return to_fish(env)
    else:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")
