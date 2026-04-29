"""Register rating commands with the main CLI."""

from envforge.cli_rating import rating_cmd


def register(cli):
    cli.add_command(rating_cmd)
