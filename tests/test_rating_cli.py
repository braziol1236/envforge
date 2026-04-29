"""CLI tests for snapshot rating commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_rating import rating_cmd
from envforge.snapshot import save_snapshot


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def tmp_snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _dir_args(d: Path):
    return ["--dir", str(d)]


def _save(name: str, d: Path):
    save_snapshot(name, {"K": "v"}, snapshot_dir=d)


def test_set_and_show_rating(runner, tmp_snapshot_dir):
    _save("mysnap", tmp_snapshot_dir)
    result = runner.invoke(rating_cmd, ["set", "mysnap", "4"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "★★★★" in result.output

    result = runner.invoke(rating_cmd, ["show", "mysnap"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "4/5" in result.output


def test_set_rating_with_comment(runner, tmp_snapshot_dir):
    _save("cs", tmp_snapshot_dir)
    result = runner.invoke(
        rating_cmd,
        ["set", "cs", "5", "--comment", "perfect"] + _dir_args(tmp_snapshot_dir),
    )
    assert result.exit_code == 0
    assert "perfect" in result.output


def test_set_invalid_stars_fails(runner, tmp_snapshot_dir):
    _save("bad", tmp_snapshot_dir)
    result = runner.invoke(rating_cmd, ["set", "bad", "9"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code != 0


def test_show_unrated_snapshot(runner, tmp_snapshot_dir):
    _save("plain", tmp_snapshot_dir)
    result = runner.invoke(rating_cmd, ["show", "plain"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "No rating" in result.output


def test_remove_rating(runner, tmp_snapshot_dir):
    _save("rem", tmp_snapshot_dir)
    runner.invoke(rating_cmd, ["set", "rem", "2"] + _dir_args(tmp_snapshot_dir))
    result = runner.invoke(rating_cmd, ["remove", "rem"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "removed" in result.output


def test_list_ratings(runner, tmp_snapshot_dir):
    _save("x", tmp_snapshot_dir)
    _save("y", tmp_snapshot_dir)
    runner.invoke(rating_cmd, ["set", "x", "3"] + _dir_args(tmp_snapshot_dir))
    runner.invoke(rating_cmd, ["set", "y", "1"] + _dir_args(tmp_snapshot_dir))
    result = runner.invoke(rating_cmd, ["list"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "x" in result.output
    assert "y" in result.output
