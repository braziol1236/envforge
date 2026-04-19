"""CLI tests for the audit commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envforge.cli_audit import audit_cmd
from envforge.audit import record_audit


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    d = tmp_path / ".envforge"
    d.mkdir()
    return str(d)


def _dir_args(d):
    return ["--dir", d]


def test_log_empty(runner, tmp_snapshot_dir):
    result = runner.invoke(audit_cmd, ["log"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "No audit entries" in result.output


def test_log_shows_entries(runner, tmp_snapshot_dir):
    record_audit(tmp_snapshot_dir, "save", "mysnap", user="alice")
    result = runner.invoke(audit_cmd, ["log"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "save" in result.output
    assert "mysnap" in result.output
    assert "alice" in result.output


def test_log_filter_by_snapshot(runner, tmp_snapshot_dir):
    record_audit(tmp_snapshot_dir, "save", "snap_a", user="alice")
    record_audit(tmp_snapshot_dir, "load", "snap_b", user="bob")
    result = runner.invoke(
        audit_cmd, ["log"] + _dir_args(tmp_snapshot_dir) + ["--snapshot", "snap_b"]
    )
    assert "snap_b" in result.output
    assert "snap_a" not in result.output


def test_record_cmd(runner, tmp_snapshot_dir):
    result = runner.invoke(
        audit_cmd,
        ["record", "deploy", "prod_snap"] + _dir_args(tmp_snapshot_dir) + ["--note", "release"],
    )
    assert result.exit_code == 0
    assert "Recorded" in result.output


def test_clear_cmd(runner, tmp_snapshot_dir):
    record_audit(tmp_snapshot_dir, "save", "snap", user="x")
    result = runner.invoke(audit_cmd, ["clear"] + _dir_args(tmp_snapshot_dir), input="y\n")
    assert result.exit_code == 0
    assert "cleared" in result.output
