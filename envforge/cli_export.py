"""CLI command for exporting snapshots."""

from __future__ import annotations

import sys
import click

from envforge.snapshot import load_snapshot
from envforge.export import export_snapshot, SUPPORTED_FORMATS


@click.command("export")
@click.argument("name")
@click.option(
    "--format",
    "fmt",
    default="bash",
    show_default=True,
    type=click.Choice(SUPPORTED_FORMATS),
    help="Output format for the exported environment.",
)
@click.option(
    "--output",
    "-o",
    default=None,
    help="Write output to a file instead of stdout.",
    type=click.Path(),
)
def export_cmd(name: str, fmt: str, output: str | None) -> None:
    """Export a snapshot to a shell-compatible format."""
    try:
        snapshot = load_snapshot(name)
    except FileNotFoundError:
        click.echo(f"Snapshot '{name}' not found.", err=True)
        sys.exit(1)

    env = snapshot.get("env", {})
    content = export_snapshot(env, fmt)

    if output:
        with open(output, "w") as fh:
            fh.write(content)
        click.echo(f"Exported '{name}' ({fmt}) → {output}")
    else:
        click.echo(content, nl=False)
