"""CLI tests for snapshot group commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envforge.cli_snapshot_group import group_cmd
from envforge.snapshot import save_snapshot


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def _dir_args(snapshot_dir: str):
    return ["--dir", snapshot_dir]


def _save(name: str, snapshot_dir: str) -> None:
    save_snapshot(name, {"K": "v"}, snapshot_dir)


def test_add_and_show(runner, tmp_snapshot_dir):
    _save("snap1", tmp_snapshot_dir)
    result = runner.invoke(group_cmd, ["add", "mygroup", "snap1"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "Added" in result.output

    result = runner.invoke(group_cmd, ["show", "mygroup"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "snap1" in result.output


def test_list_groups(runner, tmp_snapshot_dir):
    _save("a", tmp_snapshot_dir)
    runner.invoke(group_cmd, ["add", "grp", "a"] + _dir_args(tmp_snapshot_dir))
    result = runner.invoke(group_cmd, ["list"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "grp" in result.output
    assert "a" in result.output


def test_remove_from_group(runner, tmp_snapshot_dir):
    _save("snap1", tmp_snapshot_dir)
    runner.invoke(group_cmd, ["add", "g", "snap1"] + _dir_args(tmp_snapshot_dir))
    result = runner.invoke(group_cmd, ["remove", "g", "snap1"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_delete_group(runner, tmp_snapshot_dir):
    _save("snap1", tmp_snapshot_dir)
    runner.invoke(group_cmd, ["add", "g", "snap1"] + _dir_args(tmp_snapshot_dir))
    result = runner.invoke(group_cmd, ["delete", "g"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "Deleted" in result.output


def test_add_missing_snapshot_fails(runner, tmp_snapshot_dir):
    result = runner.invoke(group_cmd, ["add", "g", "ghost"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "Error" in result.output


def test_show_empty_group(runner, tmp_snapshot_dir):
    result = runner.invoke(group_cmd, ["show", "nothing"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "empty" in result.output or "does not exist" in result.output
