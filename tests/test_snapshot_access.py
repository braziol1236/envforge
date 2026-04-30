"""Tests for envforge.snapshot_access."""
from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from envforge.snapshot import save_snapshot
from envforge.snapshot_access import (
    record_access,
    get_last_access,
    list_access_log,
    clear_access_log,
    AccessError,
)


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    d = tmp_path / "snaps"
    d.mkdir()
    return str(d)


def _save(name, vars_, snapshot_dir):
    save_snapshot(name, vars_, snapshot_dir)


def test_record_access_returns_datetime(tmp_snapshot_dir):
    _save("proj", {"A": "1"}, tmp_snapshot_dir)
    ts = record_access("proj", tmp_snapshot_dir)
    assert isinstance(ts, datetime)
    assert ts.tzinfo is not None


def test_get_last_access_none_before_recording(tmp_snapshot_dir):
    _save("proj", {"A": "1"}, tmp_snapshot_dir)
    assert get_last_access("proj", tmp_snapshot_dir) is None


def test_get_last_access_after_recording(tmp_snapshot_dir):
    _save("proj", {"A": "1"}, tmp_snapshot_dir)
    record_access("proj", tmp_snapshot_dir)
    ts = get_last_access("proj", tmp_snapshot_dir)
    assert isinstance(ts, datetime)


def test_record_access_missing_snapshot_raises(tmp_snapshot_dir):
    with pytest.raises(AccessError):
        record_access("ghost", tmp_snapshot_dir)


def test_list_access_log_empty(tmp_snapshot_dir):
    assert list_access_log(tmp_snapshot_dir) == []


def test_list_access_log_sorted_newest_first(tmp_snapshot_dir):
    _save("alpha", {"X": "1"}, tmp_snapshot_dir)
    _save("beta", {"Y": "2"}, tmp_snapshot_dir)
    record_access("alpha", tmp_snapshot_dir)
    time.sleep(0.01)
    record_access("beta", tmp_snapshot_dir)
    records = list_access_log(tmp_snapshot_dir)
    assert records[0]["name"] == "beta"
    assert records[1]["name"] == "alpha"


def test_clear_access_log_removes_all(tmp_snapshot_dir):
    _save("proj", {"A": "1"}, tmp_snapshot_dir)
    record_access("proj", tmp_snapshot_dir)
    clear_access_log(tmp_snapshot_dir)
    assert list_access_log(tmp_snapshot_dir) == []


def test_clear_access_log_noop_if_missing(tmp_snapshot_dir):
    clear_access_log(tmp_snapshot_dir)  # should not raise


def test_multiple_records_overwrite(tmp_snapshot_dir):
    _save("proj", {"A": "1"}, tmp_snapshot_dir)
    t1 = record_access("proj", tmp_snapshot_dir)
    time.sleep(0.01)
    t2 = record_access("proj", tmp_snapshot_dir)
    assert t2 > t1
    assert get_last_access("proj", tmp_snapshot_dir) == t2
