"""CLI tests for snapshot versioning commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_version import version_cmd
from envforge.snapshot import save_snapshot


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def tmp_snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envforge"
    d.mkdir()
    return d


def _dir_args(d: Path) -> list[str]:
    return ["--dir", str(d)]


def _save(name: str, d: Path, vars: dict) -> None:
    save_snapshot(name, vars, d)


def test_commit_and_list(runner, tmp_snapshot_dir):
    _save("mysnap", tmp_snapshot_dir, {"X": "1"})
    result = runner.invoke(version_cmd, ["commit", "mysnap", "-m", "first"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "version 1" in result.output

    result = runner.invoke(version_cmd, ["list", "mysnap"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "v1" in result.output
    assert "first" in result.output


def test_show_version(runner, tmp_snapshot_dir):
    _save("mysnap", tmp_snapshot_dir, {"KEY": "hello"})
    runner.invoke(version_cmd, ["commit", "mysnap"] + _dir_args(tmp_snapshot_dir))
    result = runner.invoke(version_cmd, ["show", "mysnap", "1"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "KEY=hello" in result.output


def test_show_missing_version_fails(runner, tmp_snapshot_dir):
    _save("mysnap", tmp_snapshot_dir, {"A": "b"})
    runner.invoke(version_cmd, ["commit", "mysnap"] + _dir_args(tmp_snapshot_dir))
    result = runner.invoke(version_cmd, ["show", "mysnap", "42"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code != 0


def test_restore_version(runner, tmp_snapshot_dir):
    _save("mysnap", tmp_snapshot_dir, {"ENV": "dev"})
    runner.invoke(version_cmd, ["commit", "mysnap"] + _dir_args(tmp_snapshot_dir))
    _save("mysnap", tmp_snapshot_dir, {"ENV": "prod"})
    runner.invoke(version_cmd, ["commit", "mysnap"] + _dir_args(tmp_snapshot_dir))

    result = runner.invoke(version_cmd, ["restore", "mysnap", "1"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "Restored" in result.output

    show = runner.invoke(version_cmd, ["show", "mysnap", "1"] + _dir_args(tmp_snapshot_dir))
    assert "ENV=dev" in show.output


def test_drop_versions(runner, tmp_snapshot_dir):
    _save("mysnap", tmp_snapshot_dir, {"A": "1"})
    runner.invoke(version_cmd, ["commit", "mysnap"] + _dir_args(tmp_snapshot_dir))
    runner.invoke(version_cmd, ["commit", "mysnap"] + _dir_args(tmp_snapshot_dir))
    result = runner.invoke(version_cmd, ["drop", "mysnap"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "2 version" in result.output

    result = runner.invoke(version_cmd, ["list", "mysnap"] + _dir_args(tmp_snapshot_dir))
    assert "No versions" in result.output
