"""CLI tests for the access sub-command group."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envforge.snapshot import save_snapshot
from envforge.cli_access import access_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    d = tmp_path / "snaps"
    d.mkdir()
    return str(d)


def _dir_args(snapshot_dir):
    return ["--dir", snapshot_dir]


def _save(name, vars_, snapshot_dir):
    save_snapshot(name, vars_, snapshot_dir)


def test_touch_records_access(runner, tmp_snapshot_dir):
    _save("mysnap", {"K": "v"}, tmp_snapshot_dir)
    result = runner.invoke(access_cmd, ["touch", "mysnap"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "mysnap" in result.output


def test_touch_missing_snapshot_fails(runner, tmp_snapshot_dir):
    result = runner.invoke(access_cmd, ["touch", "ghost"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code != 0


def test_show_no_access(runner, tmp_snapshot_dir):
    _save("mysnap", {"K": "v"}, tmp_snapshot_dir)
    result = runner.invoke(access_cmd, ["show", "mysnap"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "No access" in result.output


def test_show_after_touch(runner, tmp_snapshot_dir):
    _save("mysnap", {"K": "v"}, tmp_snapshot_dir)
    runner.invoke(access_cmd, ["touch", "mysnap"] + _dir_args(tmp_snapshot_dir))
    result = runner.invoke(access_cmd, ["show", "mysnap"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "mysnap" in result.output


def test_log_empty(runner, tmp_snapshot_dir):
    result = runner.invoke(access_cmd, ["log"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "No access" in result.output


def test_log_shows_entries(runner, tmp_snapshot_dir):
    _save("alpha", {"A": "1"}, tmp_snapshot_dir)
    runner.invoke(access_cmd, ["touch", "alpha"] + _dir_args(tmp_snapshot_dir))
    result = runner.invoke(access_cmd, ["log"] + _dir_args(tmp_snapshot_dir))
    assert "alpha" in result.output
