import click
from envforge.lint import lint_snapshot, has_warnings, format_lint_results


@click.group("lint")
def lint_cmd():
    """Lint snapshots for potential issues."""


@lint_cmd.command("run")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
@click.option("--strict", is_flag=True, help="Exit with code 1 if warnings found.")
def run_lint_cmd(name: str, snapshot_dir: str, strict: bool):
    """Run lint checks on a snapshot."""
    try:
        results = lint_snapshot(name, snapshot_dir)
    except FileNotFoundError:
        click.echo(f"Snapshot '{name}' not found.", err=True)
        raise SystemExit(1)

    output = format_lint_results(results)
    click.echo(output)

    if strict and has_warnings(results):
        raise SystemExit(1)
