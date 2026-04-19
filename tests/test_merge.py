"""Tests for envforge.merge module."""
import pytest
from envforge.snapshot import save_snapshot, load_snapshot
from envforge.merge import merge_snapshots, merge_with_env


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def _dir(tmp_snapshot_dir):
    return {"snapshot_dir": tmp_snapshot_dir}


def test_merge_snapshots_overlay_wins(tmp_snapshot_dir):
    save_snapshot("base", {"A": "1", "B": "2"}, snapshot_dir=tmp_snapshot_dir)
    save_snapshot("overlay", {"B": "99", "C": "3"}, snapshot_dir=tmp_snapshot_dir)

    result = merge_snapshots("base", "overlay", "merged", snapshot_dir=tmp_snapshot_dir)

    assert result["env"]["A"] == "1"
    assert result["env"]["B"] == "99"  # overlay wins
    assert result["env"]["C"] == "3"


def test_merge_snapshots_saved(tmp_snapshot_dir):
    save_snapshot("base", {"X": "x"}, snapshot_dir=tmp_snapshot_dir)
    save_snapshot("over", {"Y": "y"}, snapshot_dir=tmp_snapshot_dir)
    merge_snapshots("base", "over", "out", snapshot_dir=tmp_snapshot_dir)

    loaded = load_snapshot("out", snapshot_dir=tmp_snapshot_dir)
    assert loaded["env"] == {"X": "x", "Y": "y"}


def test_merge_snapshots_missing_base_raises(tmp_snapshot_dir):
    save_snapshot("overlay", {"A": "1"}, snapshot_dir=tmp_snapshot_dir)
    with pytest.raises(FileNotFoundError):
        merge_snapshots("nonexistent", "overlay", "out", snapshot_dir=tmp_snapshot_dir)


def test_merge_snapshots_missing_overlay_raises(tmp_snapshot_dir):
    save_snapshot("base", {"A": "1"}, snapshot_dir=tmp_snapshot_dir)
    with pytest.raises(FileNotFoundError):
        merge_snapshots("base", "nonexistent", "out", snapshot_dir=tmp_snapshot_dir)


def test_merge_with_env(tmp_snapshot_dir):
    save_snapshot("base", {"A": "1", "B": "2"}, snapshot_dir=tmp_snapshot_dir)
    overrides = {"B": "override", "C": "new"}

    result = merge_with_env("base", "merged_env", overrides, snapshot_dir=tmp_snapshot_dir)

    assert result["env"]["A"] == "1"
    assert result["env"]["B"] == "override"
    assert result["env"]["C"] == "new"


def test_merge_with_env_saved(tmp_snapshot_dir):
    save_snapshot("base", {"K": "v"}, snapshot_dir=tmp_snapshot_dir)
    merge_with_env("base", "result", {"NEW": "val"}, snapshot_dir=tmp_snapshot_dir)

    loaded = load_snapshot("result", snapshot_dir=tmp_snapshot_dir)
    assert loaded["env"]["K"] == "v"
    assert loaded["env"]["NEW"] == "val"
