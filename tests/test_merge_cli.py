"""Tests for merge CLI commands."""
import pytest
from click.testing import CliRunner
from envforge.cli_merge import merge_cmd
from envforge.snapshot import save_snapshot


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def _dir_args(d):
    return ["--dir", d]


def test_merge_two_snapshots(runner, tmp_snapshot_dir):
    save_snapshot("base", {"A": "1"}, snapshot_dir=tmp_snapshot_dir)
    save_snapshot("over", {"B": "2"}, snapshot_dir=tmp_snapshot_dir)

    result = runner.invoke(
        merge_cmd,
        ["snapshots", "base", "over", "merged"] + _dir_args(tmp_snapshot_dir),
    )
    assert result.exit_code == 0
    assert "merged" in result.output


def test_merge_missing_snapshot_fails(runner, tmp_snapshot_dir):
    save_snapshot("base", {"A": "1"}, snapshot_dir=tmp_snapshot_dir)

    result = runner.invoke(
        merge_cmd,
        ["snapshots", "base", "ghost", "out"] + _dir_args(tmp_snapshot_dir),
    )
    assert result.exit_code != 0


def test_merge_with_env_cmd(runner, tmp_snapshot_dir):
    save_snapshot("base", {"EXISTING": "val"}, snapshot_dir=tmp_snapshot_dir)

    result = runner.invoke(
        merge_cmd,
        ["with-env", "base", "merged_out"] + _dir_args(tmp_snapshot_dir),
    )
    assert result.exit_code == 0
    assert "merged_out" in result.output


def test_merge_with_env_prefix(runner, tmp_snapshot_dir):
    save_snapshot("base", {"BASE_KEY": "1"}, snapshot_dir=tmp_snapshot_dir)

    result = runner.invoke(
        merge_cmd,
        ["with-env", "base", "filtered", "--prefix", "NONEXISTENT_PREFIX_XYZ"]
        + _dir_args(tmp_snapshot_dir),
    )
    assert result.exit_code == 0
