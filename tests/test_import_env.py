"""Tests for envforge.import_env."""

from __future__ import annotations

from pathlib import Path

import pytest

from envforge.import_env import (
    ImportError,
    _parse_bash_export,
    _parse_dotenv,
    import_and_save,
    import_from_file,
)
from envforge.snapshot import load_snapshot


# ---------------------------------------------------------------------------
# Unit tests for parsers
# ---------------------------------------------------------------------------


def test_parse_dotenv_basic():
    text = "KEY=value\nANOTHER=hello"
    assert _parse_dotenv(text) == {"KEY": "value", "ANOTHER": "hello"}


def test_parse_dotenv_skips_comments_and_blanks():
    text = "# comment\n\nKEY=value\n"
    assert _parse_dotenv(text) == {"KEY": "value"}


def test_parse_dotenv_strips_quotes():
    text = 'QUOTED="hello world"\nSINGLE=\'foo\''
    result = _parse_dotenv(text)
    assert result["QUOTED"] == "hello world"
    assert result["SINGLE"] == "foo"


def test_parse_dotenv_skips_lines_without_equals():
    text = "NOEQUALS\nKEY=val"
    assert _parse_dotenv(text) == {"KEY": "val"}


def test_parse_bash_export_basic():
    text = "export FOO=bar\nexport BAZ=qux"
    assert _parse_bash_export(text) == {"FOO": "bar", "BAZ": "qux"}


def test_parse_bash_export_without_keyword():
    """Lines without 'export' prefix should still be parsed."""
    text = "PLAIN=value"
    assert _parse_bash_export(text) == {"PLAIN": "value"}


def test_parse_bash_export_strips_quotes():
    text = 'export MSG="hello there"'
    assert _parse_bash_export(text) == {"MSG": "hello there"}


# ---------------------------------------------------------------------------
# Integration tests using temp directory
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def test_import_from_file_dotenv(tmp_path: Path):
    src = tmp_path / ".env"
    src.write_text("APP=myapp\nDEBUG=true\n")
    result = import_from_file(src, fmt="dotenv")
    assert result == {"APP": "myapp", "DEBUG": "true"}


def test_import_from_file_bash(tmp_path: Path):
    src = tmp_path / "env.sh"
    src.write_text("#!/bin/bash\nexport HOST=localhost\nexport PORT=5432\n")
    result = import_from_file(src, fmt="bash")
    assert result["HOST"] == "localhost"
    assert result["PORT"] == "5432"


def test_import_from_file_missing_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        import_from_file(tmp_path / "nonexistent.env")


def test_import_from_file_unknown_format_raises(tmp_path: Path):
    src = tmp_path / "file.txt"
    src.write_text("KEY=val")
    with pytest.raises(ImportError, match="Unknown import format"):
        import_from_file(src, fmt="toml")


def test_import_and_save_persists_snapshot(tmp_path: Path, tmp_snapshot_dir: Path):
    src = tmp_path / ".env"
    src.write_text("DB=postgres\nUSER=admin\n")
    env = import_and_save(src, "mysnap", fmt="dotenv", snapshot_dir=tmp_snapshot_dir)
    assert env == {"DB": "postgres", "USER": "admin"}
    loaded = load_snapshot("mysnap", snapshot_dir=tmp_snapshot_dir)
    assert loaded["vars"] == {"DB": "postgres", "USER": "admin"}
