"""Tests for envforge.snapshot_prune."""
from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone
from click.testing import CliRunner

from envforge.snapshot import save_snapshot, list_snapshots
from envforge.snapshot_ttl import set_ttl
from envforge.snapshot_prune import (
    prune_expired,
    prune_oldest,
    prune_before,
    format_prune_report,
)
from envforge.cli_prune import prune_cmd


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def _save(name, vars_, snapshot_dir):
    save_snapshot(name, vars_, snapshot_dir=snapshot_dir)


# ---------------------------------------------------------------------------
# prune_expired
# ---------------------------------------------------------------------------

def test_prune_expired_removes_only_expired(tmp_snapshot_dir):
    _save("old", {"A": "1"}, tmp_snapshot_dir)
    _save("fresh", {"B": "2"}, tmp_snapshot_dir)
    # set TTL in the past for 'old'
    set_ttl("old", seconds=-1, snapshot_dir=tmp_snapshot_dir)
    deleted = prune_expired(snapshot_dir=tmp_snapshot_dir)
    assert "old" in deleted
    assert "fresh" not in deleted
    names = [m["name"] for m in list_snapshots(tmp_snapshot_dir)]
    assert "old" not in names
    assert "fresh" in names


def test_prune_expired_nothing_to_do(tmp_snapshot_dir):
    _save("keep", {"X": "y"}, tmp_snapshot_dir)
    deleted = prune_expired(snapshot_dir=tmp_snapshot_dir)
    assert deleted == []


# ---------------------------------------------------------------------------
# prune_oldest
# ---------------------------------------------------------------------------

def test_prune_oldest_keeps_correct_count(tmp_snapshot_dir):
    for i in range(5):
        _save(f"snap{i}", {"I": str(i)}, tmp_snapshot_dir)
    deleted = prune_oldest(snapshot_dir=tmp_snapshot_dir, keep=3)
    assert len(deleted) == 2
    remaining = list_snapshots(tmp_snapshot_dir)
    assert len(remaining) == 3


def test_prune_oldest_keep_more_than_existing(tmp_snapshot_dir):
    _save("a", {}, tmp_snapshot_dir)
    _save("b", {}, tmp_snapshot_dir)
    deleted = prune_oldest(snapshot_dir=tmp_snapshot_dir, keep=10)
    assert deleted == []


def test_prune_oldest_invalid_keep_raises(tmp_snapshot_dir):
    with pytest.raises(ValueError):
        prune_oldest(snapshot_dir=tmp_snapshot_dir, keep=0)


# ---------------------------------------------------------------------------
# prune_before
# ---------------------------------------------------------------------------

def test_prune_before_dry_run_does_not_delete(tmp_snapshot_dir):
    _save("snap", {"K": "v"}, tmp_snapshot_dir)
    future = datetime.now(timezone.utc) + timedelta(days=1)
    affected = prune_before(snapshot_dir=tmp_snapshot_dir, cutoff=future, dry_run=True)
    assert "snap" in affected
    names = [m["name"] for m in list_snapshots(tmp_snapshot_dir)]
    assert "snap" in names  # still exists


def test_prune_before_deletes_old_snapshots(tmp_snapshot_dir):
    _save("old", {"A": "1"}, tmp_snapshot_dir)
    future = datetime.now(timezone.utc) + timedelta(days=1)
    deleted = prune_before(snapshot_dir=tmp_snapshot_dir, cutoff=future)
    assert "old" in deleted
    assert list_snapshots(tmp_snapshot_dir) == []


# ---------------------------------------------------------------------------
# format_prune_report
# ---------------------------------------------------------------------------

def test_format_prune_report_empty():
    assert format_prune_report([]) == "Nothing to prune."


def test_format_prune_report_lists_names():
    report = format_prune_report(["a", "b"])
    assert "a" in report
    assert "b" in report
    assert "2" in report


def test_format_prune_report_dry_run():
    report = format_prune_report(["x"], dry_run=True)
    assert "Would delete" in report


# ---------------------------------------------------------------------------
# CLI smoke tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner():
    return CliRunner()


def _dir_args(d):
    return ["--dir", d]


def test_cli_expired(runner, tmp_snapshot_dir):
    _save("exp", {"Z": "1"}, tmp_snapshot_dir)
    set_ttl("exp", seconds=-1, snapshot_dir=tmp_snapshot_dir)
    result = runner.invoke(prune_cmd, ["expired"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert "exp" in result.output


def test_cli_oldest(runner, tmp_snapshot_dir):
    for i in range(4):
        _save(f"s{i}", {"i": str(i)}, tmp_snapshot_dir)
    result = runner.invoke(prune_cmd, ["oldest", "2"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    assert len(list_snapshots(tmp_snapshot_dir)) == 2


def test_cli_before_invalid_date(runner, tmp_snapshot_dir):
    result = runner.invoke(prune_cmd, ["before", "not-a-date"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code != 0
