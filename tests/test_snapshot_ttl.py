"""Tests for envforge.snapshot_ttl."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envforge.snapshot import save_snapshot
from envforge.snapshot_ttl import (
    get_ttl,
    is_expired,
    list_expired,
    purge_expired,
    remove_ttl,
    set_ttl,
)


@pytest.fixture()
def tmp_snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(name: str, d: Path, vars: dict | None = None) -> None:
    save_snapshot(name, vars or {"KEY": "val"}, snapshot_dir=d)


def test_set_ttl_returns_future_datetime(tmp_snapshot_dir):
    _save("snap", tmp_snapshot_dir)
    expiry = set_ttl("snap", 3600, tmp_snapshot_dir)
    from datetime import datetime, timezone
    assert expiry > datetime.now(timezone.utc)


def test_get_ttl_none_when_not_set(tmp_snapshot_dir):
    _save("snap", tmp_snapshot_dir)
    assert get_ttl("snap", tmp_snapshot_dir) is None


def test_get_ttl_returns_stored_expiry(tmp_snapshot_dir):
    _save("snap", tmp_snapshot_dir)
    expiry = set_ttl("snap", 60, tmp_snapshot_dir)
    assert get_ttl("snap", tmp_snapshot_dir) == expiry


def test_set_ttl_missing_snapshot_raises(tmp_snapshot_dir):
    with pytest.raises(FileNotFoundError):
        set_ttl("ghost", 60, tmp_snapshot_dir)


def test_is_expired_false_for_future_ttl(tmp_snapshot_dir):
    _save("snap", tmp_snapshot_dir)
    set_ttl("snap", 9999, tmp_snapshot_dir)
    assert is_expired("snap", tmp_snapshot_dir) is False


def test_is_expired_true_for_past_ttl(tmp_snapshot_dir):
    _save("snap", tmp_snapshot_dir)
    set_ttl("snap", 0, tmp_snapshot_dir)
    time.sleep(0.05)
    assert is_expired("snap", tmp_snapshot_dir) is True


def test_is_expired_false_when_no_ttl(tmp_snapshot_dir):
    _save("snap", tmp_snapshot_dir)
    assert is_expired("snap", tmp_snapshot_dir) is False


def test_remove_ttl_returns_true_when_existed(tmp_snapshot_dir):
    _save("snap", tmp_snapshot_dir)
    set_ttl("snap", 60, tmp_snapshot_dir)
    assert remove_ttl("snap", tmp_snapshot_dir) is True
    assert get_ttl("snap", tmp_snapshot_dir) is None


def test_remove_ttl_returns_false_when_absent(tmp_snapshot_dir):
    _save("snap", tmp_snapshot_dir)
    assert remove_ttl("snap", tmp_snapshot_dir) is False


def test_list_expired_returns_only_expired(tmp_snapshot_dir):
    _save("old", tmp_snapshot_dir)
    _save("fresh", tmp_snapshot_dir)
    set_ttl("old", 0, tmp_snapshot_dir)
    set_ttl("fresh", 9999, tmp_snapshot_dir)
    time.sleep(0.05)
    expired = list_expired(tmp_snapshot_dir)
    assert "old" in expired
    assert "fresh" not in expired


def test_purge_expired_deletes_snapshots(tmp_snapshot_dir):
    _save("stale", tmp_snapshot_dir)
    _save("alive", tmp_snapshot_dir)
    set_ttl("stale", 0, tmp_snapshot_dir)
    set_ttl("alive", 9999, tmp_snapshot_dir)
    time.sleep(0.05)
    purged = purge_expired(tmp_snapshot_dir)
    assert purged == ["stale"]
    assert get_ttl("stale", tmp_snapshot_dir) is None
    # alive snapshot ttl still intact
    assert get_ttl("alive", tmp_snapshot_dir) is not None
