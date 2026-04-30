"""CLI tests for snapshot comment commands."""

from __future__ import annotations

import pytest
from pathlib import Path
from click.testing import CliRunner

from envforge.snapshot import save_snapshot
from envforge.cli_comment import comment_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _dir_args(d: Path):
    return ["--dir", str(d)]


def _save(name: str, variables: dict, d: Path) -> None:
    save_snapshot(name, variables, d)


def test_set_and_show_comment(runner, tmp_snapshot_dir):
    _save("dev", {"PORT": "8080"}, tmp_snapshot_dir)
    result = runner.invoke(
        comment_cmd, ["set", "dev", "PORT", "HTTP port"] + _dir_args(tmp_snapshot_dir)
    )
    assert result.exit_code == 0
    assert "Comment set" in result.output

    result = runner.invoke(
        comment_cmd, ["show", "dev", "PORT"] + _dir_args(tmp_snapshot_dir)
    )
    assert result.exit_code == 0
    assert "HTTP port" in result.output


def test_show_missing_comment(runner, tmp_snapshot_dir):
    _save("dev", {"PORT": "8080"}, tmp_snapshot_dir)
    result = runner.invoke(
        comment_cmd, ["show", "dev", "PORT"] + _dir_args(tmp_snapshot_dir)
    )
    assert "No comment" in result.output


def test_delete_comment(runner, tmp_snapshot_dir):
    _save("dev", {"PORT": "8080"}, tmp_snapshot_dir)
    runner.invoke(
        comment_cmd, ["set", "dev", "PORT", "to remove"] + _dir_args(tmp_snapshot_dir)
    )
    result = runner.invoke(
        comment_cmd, ["delete", "dev", "PORT"] + _dir_args(tmp_snapshot_dir)
    )
    assert result.exit_code == 0
    assert "removed" in result.output


def test_list_comments(runner, tmp_snapshot_dir):
    _save("dev", {"PORT": "8080", "HOST": "localhost"}, tmp_snapshot_dir)
    runner.invoke(
        comment_cmd, ["set", "dev", "PORT", "port note"] + _dir_args(tmp_snapshot_dir)
    )
    runner.invoke(
        comment_cmd, ["set", "dev", "HOST", "host note"] + _dir_args(tmp_snapshot_dir)
    )
    result = runner.invoke(
        comment_cmd, ["list", "dev"] + _dir_args(tmp_snapshot_dir)
    )
    assert result.exit_code == 0
    assert "PORT" in result.output
    assert "HOST" in result.output


def test_set_comment_bad_key_exits_nonzero(runner, tmp_snapshot_dir):
    _save("dev", {"PORT": "8080"}, tmp_snapshot_dir)
    result = runner.invoke(
        comment_cmd, ["set", "dev", "NOPE", "note"] + _dir_args(tmp_snapshot_dir)
    )
    assert result.exit_code != 0
