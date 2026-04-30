"""Register the version command group with the main CLI."""

from envforge.cli_version import version_cmd


def register(cli) -> None:  # noqa: ANN001
    cli.add_command(version_cmd)
