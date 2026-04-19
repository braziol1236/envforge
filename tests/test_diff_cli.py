"""Integration tests for the diff CLI command."""

import os
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envforge.cli import cli
from envforge.snapshot import save_snapshot


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVFORGE_SNAPSHOT_DIR", str(tmp_path))
    return tmp_path


def test_diff_two_snapshots(runner, tmp_snapshot_dir):
    save_snapshot("snap1", {"FOO": "aaa", "SHARED": "same"})
    save_snapshot("snap2", {"BAR": "bbb", "SHARED": "same"})

    result = runner.invoke(cli, ["diff", "snap1", "snap2"])
    assert result.exit_code == 0
    assert "+ BAR=bbb" in result.output
    assert "- FOO=aaa" in result.output


def test_diff_snapshot_vs_env(runner, tmp_snapshot_dir):
    save_snapshot("mysnap", {"ONLY_IN_SNAP": "yes"})
    fake_env = {"ONLY_IN_ENV": "no", "ENVFORGE_SNAPSHOT_DIR": str(tmp_snapshot_dir)}

    with patch.dict(os.environ, fake_env, clear=True):
        result = runner.invoke(cli, ["diff", "mysnap"])

    assert result.exit_code == 0
    assert "current environment" in result.output


def test_diff_identical_snapshots(runner, tmp_snapshot_dir):
    save_snapshot("same1", {"X": "1"})
    save_snapshot("same2", {"X": "1"})

    result = runner.invoke(cli, ["diff", "same1", "same2"])
    assert result.exit_code == 0
    assert "(no differences)" in result.output


def test_diff_missing_snapshot(runner, tmp_snapshot_dir):
    result = runner.invoke(cli, ["diff", "ghost", "also_ghost"])
    assert result.exit_code != 0 or "Error" in result.output or result.exception is not None
