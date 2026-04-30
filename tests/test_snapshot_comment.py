"""Tests for envforge.snapshot_comment."""

from __future__ import annotations

import pytest
from pathlib import Path

from envforge.snapshot import save_snapshot
from envforge.snapshot_comment import (
    set_comment,
    get_comment,
    delete_comment,
    get_all_comments,
    CommentError,
)


@pytest.fixture
def tmp_snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(name: str, variables: dict, d: Path) -> None:
    save_snapshot(name, variables, d)


def test_set_and_get_comment(tmp_snapshot_dir):
    _save("dev", {"PORT": "8080", "HOST": "localhost"}, tmp_snapshot_dir)
    set_comment("dev", "PORT", "HTTP port for dev server", tmp_snapshot_dir)
    assert get_comment("dev", "PORT", tmp_snapshot_dir) == "HTTP port for dev server"


def test_get_comment_missing_returns_none(tmp_snapshot_dir):
    _save("dev", {"PORT": "8080"}, tmp_snapshot_dir)
    assert get_comment("dev", "PORT", tmp_snapshot_dir) is None


def test_set_comment_missing_key_raises(tmp_snapshot_dir):
    _save("dev", {"PORT": "8080"}, tmp_snapshot_dir)
    with pytest.raises(CommentError, match="MISSING"):
        set_comment("dev", "MISSING", "oops", tmp_snapshot_dir)


def test_delete_existing_comment(tmp_snapshot_dir):
    _save("dev", {"PORT": "8080"}, tmp_snapshot_dir)
    set_comment("dev", "PORT", "some note", tmp_snapshot_dir)
    assert delete_comment("dev", "PORT", tmp_snapshot_dir) is True
    assert get_comment("dev", "PORT", tmp_snapshot_dir) is None


def test_delete_nonexistent_comment_returns_false(tmp_snapshot_dir):
    _save("dev", {"PORT": "8080"}, tmp_snapshot_dir)
    assert delete_comment("dev", "PORT", tmp_snapshot_dir) is False


def test_get_all_comments_empty(tmp_snapshot_dir):
    _save("dev", {"PORT": "8080"}, tmp_snapshot_dir)
    assert get_all_comments("dev", tmp_snapshot_dir) == {}


def test_get_all_comments_multiple_keys(tmp_snapshot_dir):
    _save("dev", {"PORT": "8080", "HOST": "localhost", "DEBUG": "1"}, tmp_snapshot_dir)
    set_comment("dev", "PORT", "port note", tmp_snapshot_dir)
    set_comment("dev", "HOST", "host note", tmp_snapshot_dir)
    result = get_all_comments("dev", tmp_snapshot_dir)
    assert result == {"PORT": "port note", "HOST": "host note"}


def test_comments_are_isolated_per_snapshot(tmp_snapshot_dir):
    _save("dev", {"PORT": "8080"}, tmp_snapshot_dir)
    _save("prod", {"PORT": "443"}, tmp_snapshot_dir)
    set_comment("dev", "PORT", "dev port", tmp_snapshot_dir)
    assert get_comment("prod", "PORT", tmp_snapshot_dir) is None
    assert get_comment("dev", "PORT", tmp_snapshot_dir) == "dev port"


def test_overwrite_comment(tmp_snapshot_dir):
    _save("dev", {"PORT": "8080"}, tmp_snapshot_dir)
    set_comment("dev", "PORT", "first", tmp_snapshot_dir)
    set_comment("dev", "PORT", "second", tmp_snapshot_dir)
    assert get_comment("dev", "PORT", tmp_snapshot_dir) == "second"
