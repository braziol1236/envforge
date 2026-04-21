"""Notification hooks for snapshot events."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Callable, Optional

_HOOKS_FILE = ".envforge_hooks.json"


def _hooks_path(snapshot_dir: Optional[Path] = None) -> Path:
    base = snapshot_dir or Path.home() / ".envforge"
    return base / _HOOKS_FILE


def _load_hooks(snapshot_dir: Optional[Path] = None) -> dict:
    path = _hooks_path(snapshot_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_hooks(hooks: dict, snapshot_dir: Optional[Path] = None) -> None:
    path = _hooks_path(snapshot_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(hooks, f, indent=2)


def register_hook(event: str, command: str, snapshot_dir: Optional[Path] = None) -> None:
    """Register a shell command to run when *event* fires."""
    hooks = _load_hooks(snapshot_dir)
    hooks.setdefault(event, [])
    if command not in hooks[event]:
        hooks[event].append(command)
    _save_hooks(hooks, snapshot_dir)


def unregister_hook(event: str, command: str, snapshot_dir: Optional[Path] = None) -> bool:
    """Remove a hook. Returns True if it existed."""
    hooks = _load_hooks(snapshot_dir)
    cmds = hooks.get(event, [])
    if command not in cmds:
        return False
    cmds.remove(command)
    hooks[event] = cmds
    _save_hooks(hooks, snapshot_dir)
    return True


def list_hooks(snapshot_dir: Optional[Path] = None) -> dict[str, list[str]]:
    return _load_hooks(snapshot_dir)


def fire_event(
    event: str,
    context: Optional[dict] = None,
    snapshot_dir: Optional[Path] = None,
) -> list[str]:
    """Run all hooks registered for *event*. Returns list of commands executed."""
    hooks = _load_hooks(snapshot_dir)
    commands = hooks.get(event, [])
    env_vars = {}
    if context:
        env_vars = {f"ENVFORGE_{k.upper()}": str(v) for k, v in context.items()}

    import os
    full_env = {**os.environ, **env_vars}

    for cmd in commands:
        subprocess.run(cmd, shell=True, env=full_env)
    return commands
