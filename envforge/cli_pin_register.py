"""Register pin commands into the main CLI.

Import and call register(cli) from envforge/cli.py to attach pin subcommands.
"""
from envforge.cli_pin import pin_cmd


def register(cli_group):
    """Attach the pin command group to the root CLI.

    Args:
        cli_group: The root Click group to attach the pin subcommands to.

    Raises:
        TypeError: If cli_group is not a Click group or does not support
            add_command.
    """
    if not hasattr(cli_group, "add_command"):
        raise TypeError(
            f"Expected a Click group with add_command, got {type(cli_group).__name__!r}"
        )
    cli_group.add_command(pin_cmd)
