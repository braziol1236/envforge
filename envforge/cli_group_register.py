"""Register snapshot group commands with the main CLI."""

from __future__ import annotations

from envforge.cli_snapshot_group import group_cmd


def register(cli) -> None:
    """Attach the group sub-command group to *cli*."""
    cli.add_command(group_cmd)
