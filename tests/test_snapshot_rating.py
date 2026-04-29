"""Tests for envforge.snapshot_rating."""

from __future__ import annotations

import pytest
from pathlib import Path

from envforge.snapshot import save_snapshot
from envforge.snapshot_rating import (
    RatingError,
    get_rating,
    list_ratings,
    remove_rating,
    set_rating,
)


@pytest.fixture()
def tmp_snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(name: str, d: Path, vars: dict | None = None):
    save_snapshot(name, vars or {"KEY": "val"}, snapshot_dir=d)


def _dir(d: Path):
    return {"snapshot_dir": d}


def test_set_and_get_rating(tmp_snapshot_dir):
    _save("snap1", tmp_snapshot_dir)
    entry = set_rating("snap1", 4, **_dir(tmp_snapshot_dir))
    assert entry["stars"] == 4
    assert get_rating("snap1", **_dir(tmp_snapshot_dir)) == {"stars": 4}


def test_set_rating_with_comment(tmp_snapshot_dir):
    _save("snap2", tmp_snapshot_dir)
    set_rating("snap2", 5, comment="excellent", **_dir(tmp_snapshot_dir))
    entry = get_rating("snap2", **_dir(tmp_snapshot_dir))
    assert entry["stars"] == 5
    assert entry["comment"] == "excellent"


def test_rating_invalid_stars_raises(tmp_snapshot_dir):
    _save("snap3", tmp_snapshot_dir)
    with pytest.raises(RatingError, match="Stars must be between"):
        set_rating("snap3", 6, **_dir(tmp_snapshot_dir))
    with pytest.raises(RatingError):
        set_rating("snap3", 0, **_dir(tmp_snapshot_dir))


def test_rating_missing_snapshot_raises(tmp_snapshot_dir):
    with pytest.raises(RatingError, match="does not exist"):
        set_rating("ghost", 3, **_dir(tmp_snapshot_dir))


def test_get_rating_none_when_not_set(tmp_snapshot_dir):
    _save("snap4", tmp_snapshot_dir)
    assert get_rating("snap4", **_dir(tmp_snapshot_dir)) is None


def test_remove_rating(tmp_snapshot_dir):
    _save("snap5", tmp_snapshot_dir)
    set_rating("snap5", 2, **_dir(tmp_snapshot_dir))
    assert remove_rating("snap5", **_dir(tmp_snapshot_dir)) is True
    assert get_rating("snap5", **_dir(tmp_snapshot_dir)) is None


def test_remove_nonexistent_rating_returns_false(tmp_snapshot_dir):
    _save("snap6", tmp_snapshot_dir)
    assert remove_rating("snap6", **_dir(tmp_snapshot_dir)) is False


def test_list_ratings_empty(tmp_snapshot_dir):
    _save("snap7", tmp_snapshot_dir)
    assert list_ratings(**_dir(tmp_snapshot_dir)) == {}


def test_list_ratings_returns_all(tmp_snapshot_dir):
    _save("a", tmp_snapshot_dir)
    _save("b", tmp_snapshot_dir)
    set_rating("a", 3, **_dir(tmp_snapshot_dir))
    set_rating("b", 5, comment="great", **_dir(tmp_snapshot_dir))
    ratings = list_ratings(**_dir(tmp_snapshot_dir))
    assert ratings["a"]["stars"] == 3
    assert ratings["b"]["stars"] == 5
    assert ratings["b"]["comment"] == "great"


def test_overwrite_rating(tmp_snapshot_dir):
    _save("snap8", tmp_snapshot_dir)
    set_rating("snap8", 1, **_dir(tmp_snapshot_dir))
    set_rating("snap8", 5, comment="changed mind", **_dir(tmp_snapshot_dir))
    entry = get_rating("snap8", **_dir(tmp_snapshot_dir))
    assert entry["stars"] == 5
    assert entry["comment"] == "changed mind"
