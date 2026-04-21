"""CLI commands for managing notification hooks."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import click

from envforge.notify import register_hook, unregister_hook, list_hooks


@click.group("notify")
def notify_cmd():
    """Manage event notification hooks."""


@notify_cmd.command("add")
@click.argument("event")
@click.argument("command")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory")
def add_hook_cmd(event: str, command: str, snapshot_dir: Optional[str]):
    """Register COMMAND to run when EVENT fires."""
    d = Path(snapshot_dir) if snapshot_dir else None
    register_hook(event, command, d)
    click.echo(f"Hook registered: [{event}] -> {command}")


@notify_cmd.command("remove")
@click.argument("event")
@click.argument("command")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory")
def remove_hook_cmd(event: str, command: str, snapshot_dir: Optional[str]):
    """Remove a registered hook."""
    d = Path(snapshot_dir) if snapshot_dir else None
    removed = unregister_hook(event, command, d)
    if removed:
        click.echo(f"Hook removed: [{event}] -> {command}")
    else:
        click.echo(f"Hook not found: [{event}] -> {command}")


@notify_cmd.command("list")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory")
def list_hooks_cmd(snapshot_dir: Optional[str]):
    """List all registered hooks."""
    d = Path(snapshot_dir) if snapshot_dir else None
    hooks = list_hooks(d)
    if not hooks:
        click.echo("No hooks registered.")
        return
    for event, commands in hooks.items():
        for cmd in commands:
            click.echo(f"  [{event}] {cmd}")
