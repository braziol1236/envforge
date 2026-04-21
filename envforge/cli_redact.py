"""CLI commands for redacting sensitive keys in snapshots."""

from __future__ import annotations

import click

from envforge.redact import (
    DEFAULT_SENSITIVE_PATTERNS,
    format_redacted,
    list_sensitive_keys,
    redact_snapshot,
)
from envforge.snapshot import load_snapshot


@click.group("redact")
def redact_cmd():
    """Redact sensitive environment variable values."""


@redact_cmd.command("show")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory.")
@click.option(
    "--pattern",
    "patterns",
    multiple=True,
    help="Extra regex patterns for sensitive keys (can repeat).",
)
def show_redacted_cmd(name: str, snapshot_dir, patterns):
    """Show snapshot with sensitive values redacted."""
    snap = load_snapshot(name, snapshot_dir=snapshot_dir)
    all_patterns = list(DEFAULT_SENSITIVE_PATTERNS) + list(patterns)
    output = format_redacted(snap["variables"], patterns=all_patterns)
    if output:
        click.echo(output)
    else:
        click.echo("(no variables)")


@redact_cmd.command("list-sensitive")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=None, help="Snapshot directory.")
@click.option(
    "--pattern",
    "patterns",
    multiple=True,
    help="Extra regex patterns for sensitive keys (can repeat).",
)
def list_sensitive_cmd(name: str, snapshot_dir, patterns):
    """List keys detected as sensitive in a snapshot."""
    snap = load_snapshot(name, snapshot_dir=snapshot_dir)
    all_patterns = list(DEFAULT_SENSITIVE_PATTERNS) + list(patterns)
    keys = list_sensitive_keys(snap["variables"], patterns=all_patterns)
    if keys:
        for k in keys:
            click.echo(k)
    else:
        click.echo("No sensitive keys detected.")
