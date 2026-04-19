"""Template support: create snapshots from variable templates with defaults."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

DEFAULT_TEMPLATES_DIR = Path.home() / ".envforge" / "templates"


def _templates_dir(base: Path | None = None) -> Path:
    d = base or DEFAULT_TEMPLATES_DIR
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_template(name: str, variables: dict[str, str], base: Path | None = None) -> Path:
    """Save a template (name -> default value map)."""
    path = _templates_dir(base) / f"{name}.json"
    path.write_text(json.dumps({"name": name, "variables": variables}, indent=2))
    return path


def load_template(name: str, base: Path | None = None) -> dict[str, Any]:
    path = _templates_dir(base) / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Template '{name}' not found.")
    return json.loads(path.read_text())


def list_templates(base: Path | None = None) -> list[str]:
    return [p.stem for p in _templates_dir(base).glob("*.json")]


def delete_template(name: str, base: Path | None = None) -> None:
    path = _templates_dir(base) / f"{name}.json"
    if path.exists():
        path.unlink()


def instantiate_template(name: str, overrides: dict[str, str] | None = None, base: Path | None = None) -> dict[str, str]:
    """Return a variable dict from a template, with optional overrides applied."""
    tmpl = load_template(name, base)
    variables = dict(tmpl["variables"])
    if overrides:
        variables.update(overrides)
    return variables
