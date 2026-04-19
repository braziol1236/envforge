"""CLI commands for the audit log feature."""

from __future__ import annotations

import click

from envforge.audit import get_audit_log, clear_audit_log, record_audit


@click.group("audit")
def audit_cmd():
    """View and manage the audit log."""


@audit_cmd.command("log")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
@click.option("--snapshot", default=None, help="Filter by snapshot name")
def show_audit_cmd(snapshot_dir: str, snapshot: str | None):
    """Show audit log entries."""
    entries = get_audit_log(snapshot_dir, snapshot_name=snapshot)
    if not entries:
        click.echo("No audit entries found.")
        return
    for e in entries:
        note = f"  # {e['note']}" if e.get("note") else ""
        click.echo(f"[{e['timestamp']}] {e['action']:10s} {e['snapshot']} (by {e['user']}){note}")


@audit_cmd.command("record")
@click.argument("action")
@click.argument("snapshot_name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
@click.option("--note", default=None)
def record_cmd(action: str, snapshot_name: str, snapshot_dir: str, note: str | None):
    """Manually record an audit entry."""
    record_audit(snapshot_dir, action, snapshot_name, note=note)
    click.echo(f"Recorded '{action}' for snapshot '{snapshot_name}'.")


@audit_cmd.command("clear")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
@click.confirmation_option(prompt="Clear the entire audit log?")
def clear_cmd(snapshot_dir: str):
    """Clear the audit log."""
    clear_audit_log(snapshot_dir)
    click.echo("Audit log cleared.")
