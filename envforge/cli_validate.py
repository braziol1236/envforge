"""CLI commands for snapshot schema validation."""

from __future__ import annotations

from pathlib import Path

import click

from envforge.schema import Schema, KeyRule
from envforge.validate import validate, validate_many, format_validate_report
from envforge.snapshot import list_snapshots


@click.group("validate")
def validate_cmd():
    """Validate snapshots against a schema."""


@validate_cmd.command("run")
@click.argument("name")
@click.option("--require", "required_keys", multiple=True, metavar="KEY",
              help="Keys that must be present.")
@click.option("--pattern", "patterns", multiple=True, metavar="KEY=REGEX",
              help="KEY=REGEX pairs enforcing value patterns.")
@click.option("--dir", "snapshot_dir", default=None, type=click.Path(),
              help="Custom snapshot directory.")
def run_cmd(name, required_keys, patterns, snapshot_dir):
    """Validate snapshot NAME against the supplied schema rules."""
    sdir = Path(snapshot_dir) if snapshot_dir else None
    rules: dict[str, KeyRule] = {}
    for k in required_keys:
        rules[k] = KeyRule(required=True)
    for pair in patterns:
        if "=" not in pair:
            raise click.BadParameter(f"Expected KEY=REGEX, got: {pair!r}")
        k, regex = pair.split("=", 1)
        existing = rules.get(k, KeyRule())
        rules[k] = KeyRule(required=existing.required, pattern=regex)
    schema = Schema(rules=rules)
    result = validate(name, schema, snapshot_dir=sdir)
    click.echo(format_validate_report(result))
    if not result["passed"]:
        raise SystemExit(1)


@validate_cmd.command("all")
@click.option("--require", "required_keys", multiple=True, metavar="KEY")
@click.option("--pattern", "patterns", multiple=True, metavar="KEY=REGEX")
@click.option("--dir", "snapshot_dir", default=None, type=click.Path())
def all_cmd(required_keys, patterns, snapshot_dir):
    """Validate ALL snapshots against the supplied schema rules."""
    sdir = Path(snapshot_dir) if snapshot_dir else None
    rules: dict[str, KeyRule] = {}
    for k in required_keys:
        rules[k] = KeyRule(required=True)
    for pair in patterns:
        if "=" not in pair:
            raise click.BadParameter(f"Expected KEY=REGEX, got: {pair!r}")
        k, regex = pair.split("=", 1)
        existing = rules.get(k, KeyRule())
        rules[k] = KeyRule(required=existing.required, pattern=regex)
    schema = Schema(rules=rules)
    names = [s["name"] for s in list_snapshots(snapshot_dir=sdir)]
    if not names:
        click.echo("No snapshots found.")
        return
    any_failed = False
    for result in validate_many(names, schema, snapshot_dir=sdir):
        click.echo(format_validate_report(result))
        click.echo()
        if not result["passed"]:
            any_failed = True
    if any_failed:
        raise SystemExit(1)
