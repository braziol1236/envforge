"""CLI commands for watching environment changes."""

import click
from envforge.watch import watch_env


@click.group("watch")
def watch_cmd():
    """Watch environment for changes against a snapshot."""
    pass


@watch_cmd.command("start")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True, help="Snapshot directory")
@click.option("--interval", default=5, show_default=True, help="Poll interval in seconds")
@click.option("--auto-save", is_flag=True, default=False, help="Auto-save snapshot on change")
def start_watch_cmd(name: str, snapshot_dir: str, interval: int, auto_save: bool):
    """Start watching the environment against snapshot NAME."""
    try:
        watch_env(
            snapshot_dir=snapshot_dir,
            name=name,
            interval=interval,
            auto_save=auto_save,
        )
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{name}' not found in '{snapshot_dir}'.")
    except KeyboardInterrupt:
        click.echo("\nWatch stopped.")
