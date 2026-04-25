"""CLI tests for the rename command."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from envforge.snapshot import save_snapshot, get_snapshot_path
from envforge.cli_rename import rename_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _dir_args(d):
    return ["--dir", str(d)]


def _save(name, vars_, d):
    save_snapshot(name, vars_, d)


def test_rename_success(runner, tmp_snapshot_dir):
    _save("old", {"K": "v"}, tmp_snapshot_dir)
    result = runner.invoke(rename_cmd, ["run", "old", "new"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "old" in result.output
    assert "new" in result.output
    assert not get_snapshot_path("old", tmp_snapshot_dir).exists()
    assert get_snapshot_path("new", tmp_snapshot_dir).exists()


def test_rename_missing_source_fails(runner, tmp_snapshot_dir):
    result = runner.invoke(rename_cmd, ["run", "ghost", "new"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code != 0
    assert "Error" in result.output


def test_rename_target_exists_without_overwrite_fails(runner, tmp_snapshot_dir):
    _save("a", {"X": "1"}, tmp_snapshot_dir)
    _save("b", {"Y": "2"}, tmp_snapshot_dir)
    result = runner.invoke(rename_cmd, ["run", "a", "b"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code != 0


def test_rename_target_exists_with_overwrite(runner, tmp_snapshot_dir):
    _save("a", {"X": "1"}, tmp_snapshot_dir)
    _save("b", {"Y": "2"}, tmp_snapshot_dir)
    result = runner.invoke(
        rename_cmd, ["run", "a", "b", "--overwrite"] + _dir_args(tmp_snapshot_dir)
    )
    assert result.exit_code == 0
    assert get_snapshot_path("b", tmp_snapshot_dir).exists()
    assert not get_snapshot_path("a", tmp_snapshot_dir).exists()
