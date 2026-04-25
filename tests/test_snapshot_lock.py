"""Tests for envforge.snapshot_lock."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envforge.snapshot import save_snapshot
from envforge.snapshot_lock import (
    lock_snapshot,
    unlock_snapshot,
    is_locked,
    list_locked,
    assert_unlocked,
)
from envforge.cli_lock import lock_cmd


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def _dir(tmp_snapshot_dir):
    return {"snapshot_dir": tmp_snapshot_dir}


def _save(name, vars_, snapshot_dir):
    save_snapshot(name, vars_, snapshot_dir)


def test_lock_and_check(tmp_snapshot_dir):
    _save("prod", {"KEY": "val"}, tmp_snapshot_dir)
    lock_snapshot("prod", tmp_snapshot_dir)
    assert is_locked("prod", tmp_snapshot_dir) is True


def test_lock_missing_snapshot_raises(tmp_snapshot_dir):
    with pytest.raises(FileNotFoundError):
        lock_snapshot("ghost", tmp_snapshot_dir)


def test_unlock_existing(tmp_snapshot_dir):
    _save("prod", {"KEY": "val"}, tmp_snapshot_dir)
    lock_snapshot("prod", tmp_snapshot_dir)
    result = unlock_snapshot("prod", tmp_snapshot_dir)
    assert result is True
    assert is_locked("prod", tmp_snapshot_dir) is False


def test_unlock_not_locked_returns_false(tmp_snapshot_dir):
    _save("prod", {"KEY": "val"}, tmp_snapshot_dir)
    result = unlock_snapshot("prod", tmp_snapshot_dir)
    assert result is False


def test_list_locked_empty(tmp_snapshot_dir):
    assert list_locked(tmp_snapshot_dir) == []


def test_list_locked_multiple(tmp_snapshot_dir):
    for name in ("a", "b", "c"):
        _save(name, {"X": "1"}, tmp_snapshot_dir)
        lock_snapshot(name, tmp_snapshot_dir)
    locked = list_locked(tmp_snapshot_dir)
    assert set(locked) == {"a", "b", "c"}


def test_assert_unlocked_passes(tmp_snapshot_dir):
    _save("dev", {"K": "v"}, tmp_snapshot_dir)
    assert_unlocked("dev", tmp_snapshot_dir)  # should not raise


def test_assert_unlocked_raises_when_locked(tmp_snapshot_dir):
    _save("dev", {"K": "v"}, tmp_snapshot_dir)
    lock_snapshot("dev", tmp_snapshot_dir)
    with pytest.raises(RuntimeError, match="locked"):
        assert_unlocked("dev", tmp_snapshot_dir)


def test_cli_set_and_list(tmp_snapshot_dir):
    runner = CliRunner()
    _save("staging", {"ENV": "stage"}, tmp_snapshot_dir)
    result = runner.invoke(lock_cmd, ["set", "staging", "--dir", tmp_snapshot_dir])
    assert result.exit_code == 0
    assert "locked" in result.output
    result = runner.invoke(lock_cmd, ["list", "--dir", tmp_snapshot_dir])
    assert "staging" in result.output


def test_cli_remove_lock(tmp_snapshot_dir):
    runner = CliRunner()
    _save("staging", {"ENV": "stage"}, tmp_snapshot_dir)
    lock_snapshot("staging", tmp_snapshot_dir)
    result = runner.invoke(lock_cmd, ["remove", "staging", "--dir", tmp_snapshot_dir])
    assert result.exit_code == 0
    assert "unlocked" in result.output
