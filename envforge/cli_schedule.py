"""CLI commands for managing snapshot schedules."""

from __future__ import annotations

from pathlib import Path

import click

from envforge.schedule import (
    get_schedule,
    list_schedules,
    remove_schedule,
    set_schedule,
)


@click.group("schedule")
def schedule_cmd() -> None:
    """Manage auto-snapshot schedules."""


@schedule_cmd.command("set")
@click.argument("name")
@click.argument("cron")
@click.option("--label", default="", help="Human-readable description.")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def set_schedule_cmd(name: str, cron: str, label: str, snapshot_dir: str) -> None:
    """Attach CRON expression to snapshot NAME."""
    try:
        set_schedule(Path(snapshot_dir), name, cron, label)
        click.echo(f"Schedule set for '{name}': {cron}" + (f" ({label})" if label else ""))
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc


@schedule_cmd.command("remove")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def remove_schedule_cmd(name: str, snapshot_dir: str) -> None:
    """Remove the schedule for snapshot NAME."""
    remove_schedule(Path(snapshot_dir), name)
    click.echo(f"Schedule removed for '{name}'.")


@schedule_cmd.command("show")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def show_schedule_cmd(name: str, snapshot_dir: str) -> None:
    """Show the schedule for snapshot NAME."""
    entry = get_schedule(Path(snapshot_dir), name)
    if entry is None:
        click.echo(f"No schedule set for '{name}'.")
    else:
        label = f"  label : {entry['label']}" if entry.get("label") else ""
        click.echo(f"name  : {name}\ncron  : {entry['cron']}" + (f"\n{label}" if label else ""))


@schedule_cmd.command("list")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def list_schedules_cmd(snapshot_dir: str) -> None:
    """List all snapshot schedules."""
    schedules = list_schedules(Path(snapshot_dir))
    if not schedules:
        click.echo("No schedules defined.")
        return
    for name, entry in schedules.items():
        label = f" ({entry['label']}" + ")" if entry.get("label") else ""
        click.echo(f"{name}: {entry['cron']}{label}")
