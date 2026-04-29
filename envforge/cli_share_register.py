"""Registration helper so the main CLI can mount the share command group."""

from __future__ import annotations

from envforge.cli_share import share_cmd


def register(cli) -> None:
    """Attach the share command group to the root CLI."""
    cli.add_command(share_cmd)
