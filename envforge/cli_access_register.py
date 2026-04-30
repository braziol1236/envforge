"""Register the access command group with the root CLI."""
from envforge.cli_access import access_cmd


def register(cli):
    cli.add_command(access_cmd)
