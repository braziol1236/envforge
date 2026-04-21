"""CLI commands for template management."""
from __future__ import annotations
import click
from pathlib import Path
from envforge.template import save_template, load_template, list_templates, delete_template, instantiate_template
from envforge.snapshot import save_snapshot


@click.group("template")
def template_cmd():
    """Manage env variable templates."""


@template_cmd.command("create")
@click.argument("name")
@click.option("--var", "-v", multiple=True, help="KEY=VALUE pairs (value is the default)")
@click.option("--dir", "base", default=None, help="Templates directory")
def create_cmd(name, var, base):
    """Create a new template."""
    base_path = Path(base) if base else None
    variables = {}
    for item in var:
        if "=" not in item:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {item}")
        k, v = item.split("=", 1)
        variables[k] = v
    path = save_template(name, variables, base_path)
    click.echo(f"Template '{name}' saved to {path}")


@template_cmd.command("list")
@click.option("--dir", "base", default=None)
def list_cmd(base):
    """List all templates."""
    base_path = Path(base) if base else None
    templates = list_templates(base_path)
    if not templates:
        click.echo("No templates found.")
    for t in templates:
        click.echo(t)


@template_cmd.command("show")
@click.argument("name")
@click.option("--dir", "base", default=None)
def show_cmd(name, base):
    """Show a template's variables."""
    base_path = Path(base) if base else None
    tmpl = load_template(name, base_path)
    for k, v in tmpl["variables"].items():
        click.echo(f"{k}={v}")


@template_cmd.command("delete")
@click.argument("name")
@click.option("--dir", "base", default=None)
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmation prompt")
def delete_cmd(name, base, yes):
    """Delete a template."""
    base_path = Path(base) if base else None
    if not yes:
        click.confirm(f"Delete template '{name}'?", abort=True)
    delete_template(name, base_path)
    click.echo(f"Template '{name}' deleted.")


@template_cmd.command("apply")
@click.argument("template_name")
@click.argument("snapshot_name")
@click.option("--var", "-v", multiple=True, help="Override KEY=VALUE")
@click.option("--dir", "base", default=None)
@click.option("--snapshot-dir", "snap_dir", default=None)
def apply_cmd(template_name, snapshot_name, var, base, snap_dir):
    """Instantiate a template into a new snapshot."""
    base_path = Path(base) if base else None
    snap_path = Path(snap_dir) if snap_dir else None
    overrides = {}
    for item in var:
        k, v = item.split("=", 1)
        overrides[k] = v
    variables = instantiate_template(template_name, overrides, base_path)
    save_snapshot(snapshot_name, variables, snap_path)
    click.echo(f"Snapshot '{snapshot_name}' created from template '{template_name}'.")
