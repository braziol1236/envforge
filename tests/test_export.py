"""Tests for envforge.export module."""

import pytest
from envforge.export import export_snapshot, to_bash, to_dotenv, to_fish


SAMPLE_ENV = {
    "HOME": "/home/user",
    "PATH": "/usr/bin:/bin",
    "GREETING": 'say "hello"',
}


def test_to_bash_contains_exports():
    result = to_bash(SAMPLE_ENV)
    assert 'export HOME="/home/user"' in result
    assert 'export PATH="/usr/bin:/bin"' in result


def test_to_bash_escapes_quotes():
    result = to_bash(SAMPLE_ENV)
    assert 'export GREETING="say \\"hello\\""' in result


def test_to_bash_has_shebang():
    result = to_bash(SAMPLE_ENV)
    assert result.startswith("#!/usr/bin/env bash")


def test_to_dotenv_format():
    result = to_dotenv({"FOO": "bar", "BAZ": "qux"})
    assert 'FOO="bar"' in result
    assert 'BAZ="qux"' in result
    assert "export" not in result


def test_to_fish_format():
    result = to_fish({"FOO": "bar"})
    assert 'set -x FOO "bar"' in result


def test_export_snapshot_bash():
    result = export_snapshot({"X": "1"}, "bash")
    assert 'export X="1"' in result


def test_export_snapshot_dotenv():
    result = export_snapshot({"X": "1"}, "dotenv")
    assert 'X="1"' in result


def test_export_snapshot_fish():
    result = export_snapshot({"X": "1"}, "fish")
    assert 'set -x X "1"' in result


def test_export_snapshot_invalid_format():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_snapshot({"X": "1"}, "powershell")
