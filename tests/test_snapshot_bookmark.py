"""Tests for envforge.snapshot_bookmark."""

from __future__ import annotations

import json
import pytest

from envforge.snapshot_bookmark import (
    list_bookmarks,
    remove_bookmark,
    resolve_bookmark,
    set_bookmark,
)
from envforge.snapshot import save_snapshot


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def _save(name: str, d: str, vars: dict | None = None) -> None:
    save_snapshot(name, vars or {"KEY": "val"}, d)


def test_set_and_resolve_bookmark(tmp_snapshot_dir):
    _save("prod", tmp_snapshot_dir)
    set_bookmark("live", "prod", tmp_snapshot_dir)
    assert resolve_bookmark("live", tmp_snapshot_dir) == "prod"


def test_resolve_missing_bookmark_returns_none(tmp_snapshot_dir):
    assert resolve_bookmark("ghost", tmp_snapshot_dir) is None


def test_set_bookmark_missing_snapshot_raises(tmp_snapshot_dir):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        set_bookmark("oops", "nonexistent", tmp_snapshot_dir)


def test_remove_existing_bookmark(tmp_snapshot_dir):
    _save("snap1", tmp_snapshot_dir)
    set_bookmark("bm", "snap1", tmp_snapshot_dir)
    result = remove_bookmark("bm", tmp_snapshot_dir)
    assert result is True
    assert resolve_bookmark("bm", tmp_snapshot_dir) is None


def test_remove_nonexistent_bookmark_returns_false(tmp_snapshot_dir):
    assert remove_bookmark("nope", tmp_snapshot_dir) is False


def test_list_bookmarks_empty(tmp_snapshot_dir):
    assert list_bookmarks(tmp_snapshot_dir) == []


def test_list_bookmarks_sorted(tmp_snapshot_dir):
    _save("s1", tmp_snapshot_dir)
    _save("s2", tmp_snapshot_dir)
    set_bookmark("zebra", "s1", tmp_snapshot_dir)
    set_bookmark("alpha", "s2", tmp_snapshot_dir)
    entries = list_bookmarks(tmp_snapshot_dir)
    names = [e["name"] for e in entries]
    assert names == sorted(names)


def test_overwrite_bookmark(tmp_snapshot_dir):
    _save("s1", tmp_snapshot_dir)
    _save("s2", tmp_snapshot_dir)
    set_bookmark("bm", "s1", tmp_snapshot_dir)
    set_bookmark("bm", "s2", tmp_snapshot_dir)
    assert resolve_bookmark("bm", tmp_snapshot_dir) == "s2"
    assert len(list_bookmarks(tmp_snapshot_dir)) == 1


def test_bookmarks_persisted_to_disk(tmp_snapshot_dir):
    _save("snap", tmp_snapshot_dir)
    set_bookmark("disk_bm", "snap", tmp_snapshot_dir)
    bm_file = tmp_snapshot_dir + "/.bookmarks.json"
    data = json.loads(open(bm_file).read())
    assert data["disk_bm"] == "snap"
