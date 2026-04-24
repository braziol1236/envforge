"""Tests for envforge.snapshot_group."""

from __future__ import annotations

import pytest

from envforge.snapshot import save_snapshot
from envforge.snapshot_group import (
    add_to_group,
    delete_group,
    get_group_members,
    list_groups,
    load_group_snapshots,
    remove_from_group,
)


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def _save(name: str, snapshot_dir: str, vars_: dict | None = None) -> None:
    save_snapshot(name, vars_ or {"KEY": "val"}, snapshot_dir)


def test_add_to_group(tmp_snapshot_dir):
    _save("snap1", tmp_snapshot_dir)
    add_to_group("mygroup", "snap1", tmp_snapshot_dir)
    assert "snap1" in get_group_members("mygroup", tmp_snapshot_dir)


def test_add_to_group_idempotent(tmp_snapshot_dir):
    _save("snap1", tmp_snapshot_dir)
    add_to_group("mygroup", "snap1", tmp_snapshot_dir)
    add_to_group("mygroup", "snap1", tmp_snapshot_dir)
    assert get_group_members("mygroup", tmp_snapshot_dir).count("snap1") == 1


def test_add_missing_snapshot_raises(tmp_snapshot_dir):
    with pytest.raises(FileNotFoundError):
        add_to_group("mygroup", "ghost", tmp_snapshot_dir)


def test_remove_from_group(tmp_snapshot_dir):
    _save("snap1", tmp_snapshot_dir)
    add_to_group("mygroup", "snap1", tmp_snapshot_dir)
    result = remove_from_group("mygroup", "snap1", tmp_snapshot_dir)
    assert result is True
    assert get_group_members("mygroup", tmp_snapshot_dir) == []


def test_remove_nonexistent_returns_false(tmp_snapshot_dir):
    result = remove_from_group("mygroup", "nobody", tmp_snapshot_dir)
    assert result is False


def test_remove_last_member_deletes_group(tmp_snapshot_dir):
    _save("snap1", tmp_snapshot_dir)
    add_to_group("mygroup", "snap1", tmp_snapshot_dir)
    remove_from_group("mygroup", "snap1", tmp_snapshot_dir)
    assert "mygroup" not in list_groups(tmp_snapshot_dir)


def test_list_groups_empty(tmp_snapshot_dir):
    assert list_groups(tmp_snapshot_dir) == {}


def test_list_groups_multiple(tmp_snapshot_dir):
    _save("a", tmp_snapshot_dir)
    _save("b", tmp_snapshot_dir)
    add_to_group("g1", "a", tmp_snapshot_dir)
    add_to_group("g2", "b", tmp_snapshot_dir)
    groups = list_groups(tmp_snapshot_dir)
    assert set(groups.keys()) == {"g1", "g2"}


def test_delete_group(tmp_snapshot_dir):
    _save("snap1", tmp_snapshot_dir)
    add_to_group("mygroup", "snap1", tmp_snapshot_dir)
    assert delete_group("mygroup", tmp_snapshot_dir) is True
    assert "mygroup" not in list_groups(tmp_snapshot_dir)


def test_delete_missing_group_returns_false(tmp_snapshot_dir):
    assert delete_group("ghost", tmp_snapshot_dir) is False


def test_load_group_snapshots(tmp_snapshot_dir):
    _save("snap1", tmp_snapshot_dir, {"A": "1"})
    _save("snap2", tmp_snapshot_dir, {"B": "2"})
    add_to_group("g", "snap1", tmp_snapshot_dir)
    add_to_group("g", "snap2", tmp_snapshot_dir)
    result = load_group_snapshots("g", tmp_snapshot_dir)
    assert result["snap1"] == {"A": "1"}
    assert result["snap2"] == {"B": "2"}
