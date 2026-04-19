"""Register pin commands into the main CLI.

Import and call register(cli) from envforge/cli.py to attach pin subcommands.
"""
from envforge.cli_pin import pin_cmd


def register(cli_group):
    """Attach the pin command group to the root CLI."""
    cli_group.add_command(pin_cmd)
