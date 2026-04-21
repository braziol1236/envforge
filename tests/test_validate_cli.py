"""CLI tests for envforge validate commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envforge.snapshot import save_snapshot
from envforge.cli_validate import validate_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return tmp_path


@pytest.fixture()
def _dir_args(tmp_snapshot_dir):
    return ["--dir", str(tmp_snapshot_dir)]


def test_run_passes(runner, tmp_snapshot_dir, _dir_args):
    save_snapshot("mysnap", {"PORT": "3000"}, snapshot_dir=tmp_snapshot_dir)
    result = runner.invoke(
        validate_cmd,
        ["run", "mysnap", "--require", "PORT"] + _dir_args,
    )
    assert result.exit_code == 0
    assert "PASSED" in result.output


def test_run_fails_missing_key(runner, tmp_snapshot_dir, _dir_args):
    save_snapshot("mysnap", {"HOST": "localhost"}, snapshot_dir=tmp_snapshot_dir)
    result = runner.invoke(
        validate_cmd,
        ["run", "mysnap", "--require", "PORT"] + _dir_args,
    )
    assert result.exit_code != 0
    assert "FAILED" in result.output


def test_run_pattern_ok(runner, tmp_snapshot_dir, _dir_args):
    save_snapshot("psnap", {"PORT": "8080"}, snapshot_dir=tmp_snapshot_dir)
    result = runner.invoke(
        validate_cmd,
        ["run", "psnap", "--pattern", r"PORT=^\d+$"] + _dir_args,
    )
    assert result.exit_code == 0


def test_run_pattern_fail(runner, tmp_snapshot_dir, _dir_args):
    save_snapshot("psnap", {"PORT": "abc"}, snapshot_dir=tmp_snapshot_dir)
    result = runner.invoke(
        validate_cmd,
        ["run", "psnap", "--pattern", r"PORT=^\d+$"] + _dir_args,
    )
    assert result.exit_code != 0


def test_all_no_snapshots(runner, tmp_snapshot_dir, _dir_args):
    result = runner.invoke(validate_cmd, ["all"] + _dir_args)
    assert result.exit_code == 0
    assert "No snapshots" in result.output


def test_all_mixed_results(runner, tmp_snapshot_dir, _dir_args):
    save_snapshot("good", {"PORT": "80"}, snapshot_dir=tmp_snapshot_dir)
    save_snapshot("bad", {"OTHER": "x"}, snapshot_dir=tmp_snapshot_dir)
    result = runner.invoke(
        validate_cmd,
        ["all", "--require", "PORT"] + _dir_args,
    )
    assert result.exit_code != 0
    assert "PASSED" in result.output
    assert "FAILED" in result.output
