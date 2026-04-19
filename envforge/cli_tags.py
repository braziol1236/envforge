"""CLI commands for tag management."""
import click
from envforge.tags import add_tag, remove_tag, list_by_tag, get_tags


@click.group("tags")
def tags_cmd():
    """Manage snapshot tags."""
    pass


@tags_cmd.command("add")
@click.argument("name")
@click.argument("tag")
def add_tag_cmd(name, tag):
    """Add TAG to snapshot NAME."""
    try:
        add_tag(name, tag)
        click.echo(f"Tag '{tag}' added to snapshot '{name}'.")
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@tags_cmd.command("remove")
@click.argument("name")
@click.argument("tag")
def remove_tag_cmd(name, tag):
    """Remove TAG from snapshot NAME."""
    try:
        remove_tag(name, tag)
        click.echo(f"Tag '{tag}' removed from snapshot '{name}'.")
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@tags_cmd.command("list")
@click.argument("name")
def list_tags_cmd(name):
    """List tags for snapshot NAME."""
    try:
        tags = get_tags(name)
        if tags:
            click.echo("  ".join(tags))
        else:
            click.echo("No tags.")
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@tags_cmd.command("find")
@click.argument("tag")
def find_by_tag_cmd(tag):
    """Find snapshots with TAG."""
    names = list_by_tag(tag)
    if names:
        for n in names:
            click.echo(n)
    else:
        click.echo(f"No snapshots with tag '{tag}'.")
