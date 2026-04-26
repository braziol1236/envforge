"""CLI tests for the bookmark command group."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envforge.cli_bookmark import bookmark_cmd
from envforge.snapshot import save_snapshot


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def _dir_args(d: str):
    return ["--dir", d]


def _save(name: str, d: str) -> None:
    save_snapshot(name, {"X": "1"}, d)


def test_set_and_show(runner, tmp_snapshot_dir):
    _save("mysnap", tmp_snapshot_dir)
    result = runner.invoke(bookmark_cmd, ["set", "quick", "mysnap"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "quick" in result.output

    result = runner.invoke(bookmark_cmd, ["show", "quick"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "mysnap" in result.output


def test_list_bookmarks(runner, tmp_snapshot_dir):
    _save("s", tmp_snapshot_dir)
    runner.invoke(bookmark_cmd, ["set", "bm1", "s"] + _dir_args(tmp_snapshot_dir))
    result = runner.invoke(bookmark_cmd, ["list"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "bm1" in result.output
    assert "s" in result.output


def test_list_empty(runner, tmp_snapshot_dir):
    result = runner.invoke(bookmark_cmd, ["list"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "No bookmarks" in result.output


def test_remove_bookmark(runner, tmp_snapshot_dir):
    _save("snap", tmp_snapshot_dir)
    runner.invoke(bookmark_cmd, ["set", "bm", "snap"] + _dir_args(tmp_snapshot_dir))
    result = runner.invoke(bookmark_cmd, ["remove", "bm"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "removed" in result.output


def test_show_missing_bookmark_fails(runner, tmp_snapshot_dir):
    result = runner.invoke(bookmark_cmd, ["show", "ghost"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code != 0


def test_set_missing_snapshot_fails(runner, tmp_snapshot_dir):
    result = runner.invoke(bookmark_cmd, ["set", "bm", "nope"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code != 0
    assert "does not exist" in result.output
