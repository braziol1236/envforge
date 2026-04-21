"""Import environment variables from external sources into a snapshot."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional

from envforge.snapshot import save_snapshot


class ImportError(Exception):
    """Raised when an import source cannot be parsed."""


def _parse_dotenv(text: str) -> Dict[str, str]:
    """Parse a .env-style file into a dict, skipping comments and blanks."""
    result: Dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip surrounding quotes (single or double)
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        if key:
            result[key] = value
    return result


def _parse_bash_export(text: str) -> Dict[str, str]:
    """Parse lines of the form 'export KEY=VALUE' from a bash script."""
    result: Dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        if key:
            result[key] = value
    return result


def import_from_file(
    path: Path,
    fmt: str = "dotenv",
    snapshot_dir: Optional[Path] = None,
) -> Dict[str, str]:
    """Read *path* and return the parsed env dict (does NOT save)."""
    if not path.exists():
        raise FileNotFoundError(f"Import source not found: {path}")
    text = path.read_text(encoding="utf-8")
    if fmt == "dotenv":
        return _parse_dotenv(text)
    if fmt == "bash":
        return _parse_bash_export(text)
    raise ImportError(f"Unknown import format: {fmt!r}. Choose 'dotenv' or 'bash'.")


def import_and_save(
    path: Path,
    name: str,
    fmt: str = "dotenv",
    snapshot_dir: Optional[Path] = None,
) -> Dict[str, str]:
    """Parse *path* and persist the result as snapshot *name*."""
    env = import_from_file(path, fmt=fmt)
    save_snapshot(name, env, snapshot_dir=snapshot_dir)
    return env
