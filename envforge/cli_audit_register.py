"""Register audit commands with the main CLI."""

from __future__ import annotations

from envforge.cli_audit import audit_cmd


def register(cli):
    """Attach audit_cmd group to the root CLI."""
    cli.add_command(audit_cmd)
