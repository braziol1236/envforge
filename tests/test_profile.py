import pytest
from pathlib import Path
from envforge.profile import (
    add_to_profile,
    remove_from_profile,
    list_profiles,
    get_profile_members,
    delete_profile,
)


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    return tmp_path


def test_add_to_profile(tmp_snapshot_dir):
    add_to_profile(tmp_snapshot_dir, "work", "snap1")
    members = get_profile_members(tmp_snapshot_dir, "work")
    assert "snap1" in members


def test_add_to_profile_idempotent(tmp_snapshot_dir):
    add_to_profile(tmp_snapshot_dir, "work", "snap1")
    add_to_profile(tmp_snapshot_dir, "work", "snap1")
    assert get_profile_members(tmp_snapshot_dir, "work").count("snap1") == 1


def test_add_multiple_snapshots(tmp_snapshot_dir):
    add_to_profile(tmp_snapshot_dir, "work", "snap1")
    add_to_profile(tmp_snapshot_dir, "work", "snap2")
    members = get_profile_members(tmp_snapshot_dir, "work")
    assert members == ["snap1", "snap2"]


def test_remove_from_profile(tmp_snapshot_dir):
    add_to_profile(tmp_snapshot_dir, "work", "snap1")
    add_to_profile(tmp_snapshot_dir, "work", "snap2")
    remove_from_profile(tmp_snapshot_dir, "work", "snap1")
    assert "snap1" not in get_profile_members(tmp_snapshot_dir, "work")
    assert "snap2" in get_profile_members(tmp_snapshot_dir, "work")


def test_remove_last_member_deletes_profile(tmp_snapshot_dir):
    add_to_profile(tmp_snapshot_dir, "work", "snap1")
    remove_from_profile(tmp_snapshot_dir, "work", "snap1")
    assert "work" not in list_profiles(tmp_snapshot_dir)


def test_remove_nonexistent_noop(tmp_snapshot_dir):
    add_to_profile(tmp_snapshot_dir, "work", "snap1")
    remove_from_profile(tmp_snapshot_dir, "work", "ghost")
    assert get_profile_members(tmp_snapshot_dir, "work") == ["snap1"]


def test_list_profiles_empty(tmp_snapshot_dir):
    assert list_profiles(tmp_snapshot_dir) == {}


def test_list_profiles_multiple(tmp_snapshot_dir):
    add_to_profile(tmp_snapshot_dir, "work", "snap1")
    add_to_profile(tmp_snapshot_dir, "personal", "snap2")
    profiles = list_profiles(tmp_snapshot_dir)
    assert "work" in profiles
    assert "personal" in profiles


def test_delete_profile(tmp_snapshot_dir):
    add_to_profile(tmp_snapshot_dir, "work", "snap1")
    delete_profile(tmp_snapshot_dir, "work")
    assert "work" not in list_profiles(tmp_snapshot_dir)


def test_delete_nonexistent_profile_noop(tmp_snapshot_dir):
    delete_profile(tmp_snapshot_dir, "ghost")  # should not raise
