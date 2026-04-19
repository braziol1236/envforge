"""Tests for tag management."""
import pytest
from pathlib import Path
from envforge.snapshot import save_snapshot
from envforge.tags import add_tag, remove_tag, list_by_tag, get_tags


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    return tmp_path


def test_add_tag(tmp_snapshot_dir):
    save_snapshot("s1", {"A": "1"}, tmp_snapshot_dir)
    add_tag("s1", "prod", tmp_snapshot_dir)
    assert "prod" in get_tags("s1", tmp_snapshot_dir)


def test_add_tag_idempotent(tmp_snapshot_dir):
    save_snapshot("s1", {"A": "1"}, tmp_snapshot_dir)
    add_tag("s1", "prod", tmp_snapshot_dir)
    add_tag("s1", "prod", tmp_snapshot_dir)
    assert get_tags("s1", tmp_snapshot_dir).count("prod") == 1


def test_remove_tag(tmp_snapshot_dir):
    save_snapshot("s1", {"A": "1"}, tmp_snapshot_dir)
    add_tag("s1", "prod", tmp_snapshot_dir)
    remove_tag("s1", "prod", tmp_snapshot_dir)
    assert "prod" not in get_tags("s1", tmp_snapshot_dir)


def test_remove_nonexistent_tag_noop(tmp_snapshot_dir):
    save_snapshot("s1", {"A": "1"}, tmp_snapshot_dir)
    remove_tag("s1", "ghost", tmp_snapshot_dir)
    assert get_tags("s1", tmp_snapshot_dir) == []


def test_list_by_tag(tmp_snapshot_dir):
    save_snapshot("s1", {"A": "1"}, tmp_snapshot_dir)
    save_snapshot("s2", {"B": "2"}, tmp_snapshot_dir)
    save_snapshot("s3", {"C": "3"}, tmp_snapshot_dir)
    add_tag("s1", "prod", tmp_snapshot_dir)
    add_tag("s3", "prod", tmp_snapshot_dir)
    add_tag("s2", "dev", tmp_snapshot_dir)
    result = list_by_tag("prod", tmp_snapshot_dir)
    assert set(result) == {"s1", "s3"}


def test_list_by_tag_empty(tmp_snapshot_dir):
    save_snapshot("s1", {"A": "1"}, tmp_snapshot_dir)
    assert list_by_tag("nope", tmp_snapshot_dir) == []


def test_add_tag_missing_snapshot(tmp_snapshot_dir):
    with pytest.raises(FileNotFoundError):
        add_tag("ghost", "tag", tmp_snapshot_dir)
