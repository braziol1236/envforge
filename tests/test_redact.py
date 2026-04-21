"""Tests for envforge.redact module and its CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envforge.cli_redact import redact_cmd
from envforge.redact import (
    REDACTED_PLACEHOLDER,
    format_redacted,
    is_sensitive,
    list_sensitive_keys,
    redact_snapshot,
)
from envforge.snapshot import save_snapshot


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

def test_is_sensitive_default_patterns():
    assert is_sensitive("AWS_SECRET_ACCESS_KEY") is True
    assert is_sensitive("DB_PASSWORD") is True
    assert is_sensitive("GITHUB_TOKEN") is True
    assert is_sensitive("API_KEY") is True
    assert is_sensitive("HOME") is False
    assert is_sensitive("PATH") is False


def test_is_sensitive_custom_pattern():
    assert is_sensitive("MY_MAGIC", patterns=[r".*MAGIC.*"]) is True
    assert is_sensitive("HOME", patterns=[r".*MAGIC.*"]) is False


def test_redact_snapshot_replaces_sensitive():
    variables = {"HOME": "/home/user", "DB_PASSWORD": "s3cr3t", "PATH": "/usr/bin"}
    result = redact_snapshot(variables)
    assert result["HOME"] == "/home/user"
    assert result["PATH"] == "/usr/bin"
    assert result["DB_PASSWORD"] == REDACTED_PLACEHOLDER


def test_redact_snapshot_custom_placeholder():
    variables = {"API_KEY": "abc123"}
    result = redact_snapshot(variables, placeholder="<hidden>")
    assert result["API_KEY"] == "<hidden>"


def test_redact_snapshot_does_not_mutate_original():
    variables = {"DB_PASSWORD": "secret"}
    redact_snapshot(variables)
    assert variables["DB_PASSWORD"] == "secret"


def test_list_sensitive_keys():
    variables = {"HOME": "/home", "AUTH_TOKEN": "tok", "PATH": "/usr"}
    keys = list_sensitive_keys(variables)
    assert keys == ["AUTH_TOKEN"]


def test_format_redacted_output():
    variables = {"HOME": "/home", "DB_PASSWORD": "secret"}
    output = format_redacted(variables)
    assert "DB_PASSWORD=***REDACTED***" in output
    assert "HOME=/home" in output


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return tmp_path


def _dir_args(tmp_snapshot_dir):
    return ["--dir", str(tmp_snapshot_dir)]


def test_cli_show_redacted(runner, tmp_snapshot_dir):
    save_snapshot("mysnap", {"HOME": "/home", "DB_PASSWORD": "s3cr3t"}, snapshot_dir=tmp_snapshot_dir)
    result = runner.invoke(redact_cmd, ["show", "mysnap"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "DB_PASSWORD=***REDACTED***" in result.output
    assert "HOME=/home" in result.output


def test_cli_list_sensitive(runner, tmp_snapshot_dir):
    save_snapshot("mysnap", {"HOME": "/home", "GITHUB_TOKEN": "tok"}, snapshot_dir=tmp_snapshot_dir)
    result = runner.invoke(redact_cmd, ["list-sensitive", "mysnap"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "GITHUB_TOKEN" in result.output


def test_cli_list_sensitive_none_found(runner, tmp_snapshot_dir):
    save_snapshot("clean", {"HOME": "/home", "EDITOR": "vim"}, snapshot_dir=tmp_snapshot_dir)
    result = runner.invoke(redact_cmd, ["list-sensitive", "clean"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "No sensitive keys" in result.output
